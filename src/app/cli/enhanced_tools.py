"""
Enhanced tools for the cria AI agent with MCP-like capabilities.
Provides intelligent codebase navigation and analysis.
"""

import os
import subprocess
import json
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .context import ContextManager

class EnhancedTools:
    """Enhanced tools with MCP-like capabilities for codebase understanding."""
    
    def __init__(self, root_path: str = "."):
        self.context_manager = ContextManager(root_path)
        self.current_working_dir = Path.cwd()
    
    def get_project_overview(self) -> str:
        """Get a comprehensive overview of the current project."""
        return self.context_manager.get_project_overview()
    
    def explore_codebase(self, pattern: str = "*", file_type: str = None, max_files: int = 20) -> str:
        """
        Explore the codebase with intelligent filtering and analysis.
        
        Args:
            pattern: Glob pattern to match files
            file_type: File extension to filter by (e.g., 'py', 'js')
            max_files: Maximum number of files to return
        """
        # If pattern is just "*" and file_type is specified, use a more specific pattern
        if pattern == "*" and file_type:
            pattern = f"**/*.{file_type}"
        
        files = self.context_manager.find_files_by_pattern(pattern, file_type)
        
        if not files:
            return f"No files found matching pattern '{pattern}' with type '{file_type or 'any'}'"
        
        # Limit results
        files = files[:max_files]
        
        result = f"Found {len(files)} files matching '{pattern}':\n\n"
        
        # Group by directory
        by_dir = {}
        for file_path in files:
            dir_path = str(Path(file_path).parent)
            if dir_path not in by_dir:
                by_dir[dir_path] = []
            by_dir[dir_path].append(Path(file_path).name)
        
        for dir_path, file_list in sorted(by_dir.items()):
            result += f"📁 {dir_path or '.'}/\n"
            for filename in sorted(file_list):
                result += f"  📄 {filename}\n"
            result += "\n"
        
        return result.strip()
    
    def analyze_file(self, file_path: str, include_content: bool = False) -> str:
        """
        Analyze a file and provide detailed information about its structure.
        
        Args:
            file_path: Path to the file to analyze
            include_content: Whether to include file content in the analysis
        """
        if not file_path.startswith('/'):
            file_path = str(self.current_working_dir / file_path)
        
        analysis = self.context_manager.analyze_python_file(file_path)
        
        if "error" in analysis:
            return f"Error analyzing {file_path}: {analysis['error']}"
        
        result = f"Analysis of {file_path}:\n"
        result += f"Lines: {analysis['lines']}\n"
        result += f"Classes: {len(analysis['classes'])}\n"
        result += f"Functions: {len(analysis['functions'])}\n"
        result += f"Imports: {len(analysis['imports'])}\n\n"
        
        if analysis['classes']:
            result += "Classes:\n"
            for cls in analysis['classes']:
                result += f"  📦 {cls['name']} (line {cls['line']})\n"
                if cls['docstring']:
                    result += f"      {cls['docstring'][:100]}...\n"
                if cls['methods']:
                    result += f"      Methods: {', '.join(cls['methods'])}\n"
            result += "\n"
        
        if analysis['functions']:
            result += "Functions:\n"
            for func in analysis['functions']:
                result += f"  🔧 {func['name']}({', '.join(func['args'])}) (line {func['line']})\n"
                if func['docstring']:
                    result += f"      {func['docstring'][:100]}...\n"
            result += "\n"
        
        if analysis['imports']:
            result += "Imports:\n"
            for imp in analysis['imports'][:10]:  # Limit to first 10
                result += f"  📥 {imp}\n"
            if len(analysis['imports']) > 10:
                result += f"  ... and {len(analysis['imports']) - 10} more\n"
        
        if include_content:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result += f"\nFile Content:\n{content}"
            except Exception as e:
                result += f"\nError reading content: {e}"
        
        return result
    
    def find_code_patterns(self, pattern: str, file_types: List[str] = None, context_lines: int = 2) -> str:
        """
        Find specific code patterns across the codebase.
        
        Args:
            pattern: Regex pattern to search for
            file_types: List of file extensions to search in
            context_lines: Number of context lines to include
        """
        file_types = file_types or ['.py', '.js', '.ts', '.md']
        results = self.context_manager.find_files_by_content(pattern, file_types)
        
        if not results:
            return f"No matches found for pattern '{pattern}'"
        
        result = f"Found {len(results)} matches for '{pattern}':\n\n"
        
        current_file = None
        for file_path, line_num, line_content in results:
            if file_path != current_file:
                current_file = file_path
                result += f"📄 {file_path}:\n"
            
            # Get context around the line
            context = self.context_manager.get_context_around_line(file_path, line_num, context_lines)
            result += f"  {context}\n"
        
        return result
    
    def get_file_dependencies(self, file_path: str) -> str:
        """Get dependencies and references for a specific file."""
        if not file_path.startswith('/'):
            file_path = str(self.current_working_dir / file_path)
        
        dependencies = self.context_manager.get_file_dependencies(file_path)
        
        if not dependencies:
            return f"No dependencies found for {file_path}"
        
        result = f"Dependencies for {file_path}:\n\n"
        for dep in dependencies:
            result += f"  📄 {dep}\n"
        
        return result
    
    def navigate_to_symbol(self, symbol_name: str, file_hint: str = None) -> str:
        """
        Navigate to a specific symbol (function, class, variable) in the codebase.
        
        Args:
            symbol_name: Name of the symbol to find
            file_hint: Optional file to start searching from
        """
        # First, try to find in the hinted file
        if file_hint:
            analysis = self.context_manager.analyze_python_file(file_hint)
            if "error" not in analysis:
                # Check classes
                for cls in analysis['classes']:
                    if symbol_name.lower() in cls['name'].lower():
                        return f"Found class '{cls['name']}' in {file_hint} at line {cls['line']}\n{self.context_manager.get_context_around_line(file_hint, cls['line'])}"
                
                # Check functions
                for func in analysis['functions']:
                    if symbol_name.lower() in func['name'].lower():
                        return f"Found function '{func['name']}' in {file_hint} at line {func['line']}\n{self.context_manager.get_context_around_line(file_hint, func['line'])}"
        
        # Search across all Python files
        python_files = self.context_manager.find_files_by_pattern("**/*.py")
        
        for file_path in python_files:
            analysis = self.context_manager.analyze_python_file(file_path)
            if "error" in analysis:
                continue
            
            # Check classes
            for cls in analysis['classes']:
                if symbol_name.lower() in cls['name'].lower():
                    return f"Found class '{cls['name']}' in {file_path} at line {cls['line']}\n{self.context_manager.get_context_around_line(file_path, cls['line'])}"
            
            # Check functions
            for func in analysis['functions']:
                if symbol_name.lower() in func['name'].lower():
                    return f"Found function '{func['name']}' in {file_path} at line {func['line']}\n{self.context_manager.get_context_around_line(file_path, func['line'])}"
        
        return f"Symbol '{symbol_name}' not found in the codebase"
    
    def get_code_flow(self, entry_point: str) -> str:
        """
        Analyze the code flow starting from an entry point.
        
        Args:
            entry_point: Starting file or function
        """
        if entry_point.endswith('.py'):
            # Analyze file
            analysis = self.context_manager.analyze_python_file(entry_point)
            if "error" in analysis:
                return f"Error analyzing {entry_point}: {analysis['error']}"
            
            result = f"Code flow analysis for {entry_point}:\n\n"
            
            # Show main functions and classes
            if analysis['classes']:
                result += "Classes and their methods:\n"
                for cls in analysis['classes']:
                    result += f"  📦 {cls['name']}\n"
                    for method in cls['methods']:
                        result += f"    🔧 {method}\n"
                result += "\n"
            
            if analysis['functions']:
                result += "Functions:\n"
                for func in analysis['functions']:
                    result += f"  🔧 {func['name']}({', '.join(func['args'])})\n"
                result += "\n"
            
            # Show dependencies
            dependencies = self.context_manager.get_file_dependencies(entry_point)
            if dependencies:
                result += "Dependencies:\n"
                for dep in dependencies:
                    result += f"  📄 {dep}\n"
            
            return result
        else:
            # Search for function or class
            return self.navigate_to_symbol(entry_point)
    
    def suggest_improvements(self, file_path: str) -> str:
        """Suggest improvements for a file based on code analysis."""
        analysis = self.context_manager.analyze_python_file(file_path)
        
        if "error" in analysis:
            return f"Error analyzing {file_path}: {analysis['error']}"
        
        suggestions = []
        
        # Check for missing docstrings
        functions_without_docs = [f for f in analysis['functions'] if not f['docstring']]
        if functions_without_docs:
            suggestions.append(f"Consider adding docstrings to {len(functions_without_docs)} functions")
        
        classes_without_docs = [c for c in analysis['classes'] if not c['docstring']]
        if classes_without_docs:
            suggestions.append(f"Consider adding docstrings to {len(classes_without_docs)} classes")
        
        # Check for long files
        if analysis['lines'] > 200:
            suggestions.append("Consider breaking this file into smaller modules (over 200 lines)")
        
        # Check for many imports
        if len(analysis['imports']) > 20:
            suggestions.append("Consider organizing imports or splitting into smaller modules")
        
        if not suggestions:
            return f"No specific improvements suggested for {file_path}. The code looks well-structured!"
        
        result = f"Improvement suggestions for {file_path}:\n\n"
        for i, suggestion in enumerate(suggestions, 1):
            result += f"{i}. {suggestion}\n"
        
        return result
    
    def get_project_health(self) -> str:
        """Get an overall health assessment of the project."""
        if not self.context_manager.project_structure:
            return "Unable to analyze project structure"
        
        ps = self.context_manager.project_structure
        health_report = "Project Health Report\n"
        health_report += "===================\n\n"
        
        # File count analysis
        total_files = len(ps.files)
        python_files = len([f for f in ps.files if f.endswith('.py')])
        
        health_report += f"📊 File Statistics:\n"
        health_report += f"  Total files: {total_files}\n"
        health_report += f"  Python files: {python_files}\n"
        health_report += f"  Other files: {total_files - python_files}\n\n"
        
        # Language distribution
        health_report += f"📈 Language Distribution:\n"
        for lang, count in sorted(ps.language_stats.items(), key=lambda x: x[1], reverse=True):
            health_report += f"  {lang}: {count} files\n"
        health_report += "\n"
        
        # Entry points
        health_report += f"🚪 Entry Points:\n"
        for ep in ps.entry_points:
            health_report += f"  📄 {ep}\n"
        health_report += "\n"
        
        # Git status
        if ps.git_info.get('is_git_repo'):
            health_report += f"🌿 Git Repository:\n"
            health_report += f"  Branch: {ps.git_info.get('branch', 'unknown')}\n"
            health_report += f"  Root: {ps.git_info.get('root', 'unknown')}\n"
        else:
            health_report += "⚠️  Not a Git repository\n"
        
        return health_report
    
    def execute_with_context(self, command: str, working_dir: str = None) -> str:
        """
        Execute a command with proper context and error handling.
        
        Args:
            command: Command to execute
            working_dir: Directory to execute in (defaults to current)
        """
        if working_dir is None:
            working_dir = str(self.current_working_dir)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"Command: {command}\n"
            output += f"Working Directory: {working_dir}\n"
            output += f"Exit Code: {result.returncode}\n\n"
            
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Command timed out after 30 seconds: {command}"
        except Exception as e:
            return f"Error executing command '{command}': {e}"
