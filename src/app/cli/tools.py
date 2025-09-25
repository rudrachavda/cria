"""
Tools for the cria AI agent with MCP-like capabilities.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import fnmatch
from contextlib import suppress
from .enhanced_tools import EnhancedTools
from .coding_workflows import CodingWorkflows

# Initialize enhanced tools
_enhanced_tools = None

def get_enhanced_tools():
    """Get or create the enhanced tools instance."""
    global _enhanced_tools
    if _enhanced_tools is None:
        _enhanced_tools = EnhancedTools()
    return _enhanced_tools

def get_coding_workflows():
    """Get or create the coding workflows instance."""
    return CodingWorkflows(get_enhanced_tools().context_manager)

def get_ignore_patterns():
    """
    Reads the .criaignore file and returns a list of glob patterns.
    """
    ignore_patterns = []
    with suppress(FileNotFoundError):
        with open('.criaignore', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
    return ignore_patterns

def list_files(path: str = ".", recursive: bool = False) -> str:
    """
    Lists files and directories in a given path, ignoring patterns from .criaignore.

    Args:
        path (str): The path to the directory. Defaults to the current directory.
        recursive (bool): Whether to list files recursively. Defaults to False.

    Returns:
        str: A list of files and directories, or an error message.
    """
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: Directory '{path}' does not exist"

        ignore_patterns = get_ignore_patterns()

        files = []
        if recursive:
            for item in p.rglob("*"):
                if not any(fnmatch.fnmatch(item, pattern) for pattern in ignore_patterns):
                    if item.is_file():
                        files.append(f"📄 {item.relative_to(p)}")
                    elif item.is_dir():
                        files.append(f"📁 {item.relative_to(p)}/")
        else:
            for item in p.iterdir():
                if not any(fnmatch.fnmatch(item, pattern) for pattern in ignore_patterns):
                    if item.is_file():
                        files.append(f"📄 {item.name}")
                    elif item.is_dir():
                        files.append(f"📁 {item.name}/")

        return "\n".join(sorted(files)) if files else f"No files found in '{path}'"
    except Exception as e:
        return f"Error listing files: {e}"


def read_file(path: str) -> str:
    """
    Reads the contents of a file.

    Args:
        path (str): The path to the file.

    Returns:
        str: The contents of the file, or an error message.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Contents of {path}:\n{content}"
    except FileNotFoundError:
        return f"Error: File '{path}' not found"
    except Exception as e:
        return f"Error reading file '{path}': {e}"
        
def read_multiple_files(paths: List[str]) -> str:
    """
    Reads the contents of multiple files.

    Args:
        paths (List[str]): A list of paths to the files.

    Returns:
        str: The contents of the files, or an error message.
    """
    contents = []
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            contents.append(f"--- Contents of {path} ---\n{content}")
        except FileNotFoundError:
            contents.append(f"Error: File '{path}' not found")
        except Exception as e:
            contents.append(f"Error reading file '{path}': {e}")
    return "\n\n".join(contents)


def write_file(path: str, content: str) -> str:
    """
    Writes content to a file.

    Args:
        path (str): The path to the file.
        content (str): The content to write to the file.

    Returns:
        str: A success message, or an error message.
    """
    try:
        # Create directory if it doesn't exist (only if there's a directory)
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{path}'"
    except Exception as e:
        return f"Error writing to file '{path}': {e}"


def execute_command(command: str) -> str:
    """
    Executes a shell command.

    Args:
        command (str): The command to execute.

    Returns:
        str: The output of the command, or an error message.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        
        output += f"Exit code: {result.returncode}"
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {e}"

# Enhanced MCP-like tools
def get_project_overview() -> str:
    """
    Get a comprehensive overview of the current project structure and health.
    
    Returns:
        str: Detailed project overview including files, dependencies, and structure.
    """
    return get_enhanced_tools().get_project_overview()

def explore_codebase(pattern: str = "*", file_type: str = None, max_files: int = 20) -> str:
    """
    Explore the codebase with intelligent filtering and analysis.
    
    Args:
        pattern: Glob pattern to match files (default: "*")
        file_type: File extension to filter by (e.g., 'py', 'js', 'ts')
        max_files: Maximum number of files to return (default: 20)
    
    Returns:
        str: Formatted list of matching files grouped by directory.
    """
    return get_enhanced_tools().explore_codebase(pattern, file_type, max_files)

def analyze_file(file_path: str, include_content: bool = False) -> str:
    """
    Analyze a file and provide detailed information about its structure.
    
    Args:
        file_path: Path to the file to analyze
        include_content: Whether to include file content in the analysis (default: False)
    
    Returns:
        str: Detailed analysis including classes, functions, imports, and structure.
    """
    return get_enhanced_tools().analyze_file(file_path, include_content)

def find_code_patterns(pattern: str, file_types: List[str] = None, context_lines: int = 2) -> str:
    """
    Find specific code patterns across the codebase using regex.
    
    Args:
        pattern: Regex pattern to search for
        file_types: List of file extensions to search in (default: ['.py', '.js', '.ts', '.md'])
        context_lines: Number of context lines to include around matches (default: 2)
    
    Returns:
        str: Formatted results showing matches with context.
    """
    return get_enhanced_tools().find_code_patterns(pattern, file_types, context_lines)

def get_file_dependencies(file_path: str) -> str:
    """
    Get dependencies and references for a specific file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: List of files that this file depends on.
    """
    return get_enhanced_tools().get_file_dependencies(file_path)

def navigate_to_symbol(symbol_name: str, file_hint: str = None) -> str:
    """
    Navigate to a specific symbol (function, class, variable) in the codebase.
    
    Args:
        symbol_name: Name of the symbol to find
        file_hint: Optional file to start searching from
    
    Returns:
        str: Location and context of the found symbol.
    """
    return get_enhanced_tools().navigate_to_symbol(symbol_name, file_hint)

def get_code_flow(entry_point: str) -> str:
    """
    Analyze the code flow starting from an entry point.
    
    Args:
        entry_point: Starting file or function name
    
    Returns:
        str: Analysis of code structure and flow from the entry point.
    """
    return get_enhanced_tools().get_code_flow(entry_point)

def suggest_improvements(file_path: str) -> str:
    """
    Suggest improvements for a file based on code analysis.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: List of suggested improvements for the file.
    """
    return get_enhanced_tools().suggest_improvements(file_path)

def get_project_health() -> str:
    """
    Get an overall health assessment of the project.
    
    Returns:
        str: Comprehensive health report including statistics and recommendations.
    """
    return get_enhanced_tools().get_project_health()

def execute_with_context(command: str, working_dir: str = None) -> str:
    """
    Execute a command with proper context and error handling.
    
    Args:
        command: Command to execute
        working_dir: Directory to execute in (defaults to current)
    
    Returns:
        str: Command output with context information.
    """
    return get_enhanced_tools().execute_with_context(command, working_dir)

# Coding-specific tools
def find_code_smells(file_path: str) -> str:
    """
    Find potential code smells and issues in a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: Formatted list of code smells and issues found.
    """
    workflows = get_coding_workflows()
    smells = workflows.find_code_smells(file_path)
    
    if not smells:
        return f"No code smells found in {file_path}"
    
    result = f"Code smells found in {file_path}:\n\n"
    for smell in smells:
        severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(smell["severity"], "⚪")
        result += f"{severity_icon} Line {smell['line']}: {smell['message']}\n"
        if 'suggestion' in smell:
            result += f"   💡 Suggestion: {smell['suggestion']}\n"
        result += "\n"
    
    return result.strip()

def suggest_refactoring(file_path: str) -> str:
    """
    Suggest refactoring opportunities for a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: Formatted list of refactoring suggestions.
    """
    workflows = get_coding_workflows()
    suggestions = workflows.suggest_refactoring(file_path)
    
    if not suggestions:
        return f"No refactoring suggestions for {file_path}"
    
    result = f"Refactoring suggestions for {file_path}:\n\n"
    for suggestion in suggestions:
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion["priority"], "⚪")
        result += f"{priority_icon} {suggestion['message']}\n"
        if 'suggestion' in suggestion:
            result += f"   💡 Example: {suggestion['suggestion']}\n"
        result += "\n"
    
    return result.strip()

def generate_test_suggestions(file_path: str) -> str:
    """
    Generate test suggestions for a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: Formatted list of test suggestions.
    """
    workflows = get_coding_workflows()
    suggestions = workflows.generate_test_suggestions(file_path)
    
    if not suggestions:
        return f"No test suggestions for {file_path}"
    
    result = f"Test suggestions for {file_path}:\n\n"
    for suggestion in suggestions:
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion["priority"], "⚪")
        result += f"{priority_icon} {suggestion['message']}\n"
        if 'suggestion' in suggestion:
            result += f"   💡 Example:\n{suggestion['suggestion']}\n"
        result += "\n"
    
    return result.strip()

def find_security_issues(file_path: str) -> str:
    """
    Find potential security issues in a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: Formatted list of security issues found.
    """
    workflows = get_coding_workflows()
    issues = workflows.find_security_issues(file_path)
    
    if not issues:
        return f"No security issues found in {file_path}"
    
    result = f"Security issues found in {file_path}:\n\n"
    for issue in issues:
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"], "⚪")
        result += f"{severity_icon} Line {issue['line']}: {issue['message']}\n"
        if 'suggestion' in issue:
            result += f"   💡 Suggestion: {issue['suggestion']}\n"
        result += "\n"
    
    return result.strip()

def get_code_metrics(file_path: str) -> str:
    """
    Get code metrics for a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: Formatted code metrics.
    """
    workflows = get_coding_workflows()
    metrics = workflows.get_code_metrics(file_path)
    
    if not metrics:
        return f"Could not analyze metrics for {file_path}"
    
    result = f"Code metrics for {file_path}:\n\n"
    result += f"📊 Lines of Code: {metrics['lines_of_code']}\n"
    result += f"📄 Total Lines: {metrics['total_lines']}\n"
    result += f"📝 Comment Lines: {metrics['comment_lines']}\n"
    result += f"🔧 Functions: {metrics['functions']}\n"
    result += f"📦 Classes: {metrics['classes']}\n"
    result += f"📥 Imports: {metrics['imports']}\n"
    result += f"🧠 Complexity: {metrics['complexity'].upper()}\n"
    
    return result

def generate_documentation_suggestions(file_path: str) -> str:
    """
    Generate documentation suggestions for a file.
    
    Args:
        file_path: Path to the file to analyze
    
    Returns:
        str: Formatted list of documentation suggestions.
    """
    workflows = get_coding_workflows()
    suggestions = workflows.generate_documentation_suggestions(file_path)
    
    if not suggestions:
        return f"No documentation suggestions for {file_path}"
    
    result = f"Documentation suggestions for {file_path}:\n\n"
    for suggestion in suggestions:
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion["priority"], "⚪")
        result += f"{priority_icon} {suggestion['message']}\n"
        if 'suggestion' in suggestion:
            result += f"   💡 Example: {suggestion['suggestion']}\n"
        result += "\n"
    
    return result.strip()

def read_and_summarize_project() -> str:
    """
    Read all project files and create a comprehensive summary.
    
    Returns:
        str: Comprehensive project summary with file contents and analysis.
    """
    enhanced_tools = get_enhanced_tools()
    
    # Get project overview first
    overview = enhanced_tools.get_project_overview()
    
    # Get all Python files
    python_files = enhanced_tools.context_manager.find_files_by_pattern("**/*.py")
    
    # Filter out __pycache__ and other irrelevant files
    relevant_files = [f for f in python_files if "__pycache__" not in f and ".pyc" not in f]
    
    summary = f"# Project Analysis Summary\n\n"
    summary += f"## Project Overview\n{overview}\n\n"
    
    summary += f"## File Analysis\n\n"
    
    for file_path in relevant_files[:10]:  # Limit to first 10 files for readability
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file analysis
            analysis = enhanced_tools.context_manager.analyze_python_file(file_path)
            
            summary += f"### {file_path}\n\n"
            
            if "error" not in analysis:
                summary += f"**Structure:** {analysis['lines']} lines, {len(analysis['functions'])} functions, {len(analysis['classes'])} classes\n\n"
                
                if analysis['classes']:
                    summary += "**Classes:**\n"
                    for cls in analysis['classes']:
                        summary += f"- `{cls['name']}` (line {cls['line']})\n"
                    summary += "\n"
                
                if analysis['functions']:
                    summary += "**Functions:**\n"
                    for func in analysis['functions']:
                        summary += f"- `{func['name']}({', '.join(func['args'])})` (line {func['line']})\n"
                    summary += "\n"
            
            # Add file content (truncated if too long)
            if len(content) > 1000:
                summary += f"**Content (first 1000 chars):**\n```python\n{content[:1000]}...\n```\n\n"
            else:
                summary += f"**Content:**\n```python\n{content}\n```\n\n"
                
        except Exception as e:
            summary += f"**Error reading {file_path}:** {e}\n\n"
    
    if len(relevant_files) > 10:
        summary += f"\n*... and {len(relevant_files) - 10} more files*\n"
    
    return summary
