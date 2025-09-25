"""
Context management system for the cria AI agent.
Implements MCP-like capabilities for codebase understanding and navigation.
"""

import os
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import fnmatch
import subprocess

@dataclass
class CodeContext:
    """Represents a code context with metadata."""
    file_path: str
    line_start: int
    line_end: int
    content: str
    context_type: str  # 'function', 'class', 'import', 'variable', 'comment'
    name: Optional[str] = None
    parent: Optional[str] = None
    docstring: Optional[str] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ProjectStructure:
    """Represents the overall project structure."""
    root_path: str
    files: List[str]
    directories: List[str]
    entry_points: List[str]
    dependencies: Dict[str, List[str]]
    language_stats: Dict[str, int]
    git_info: Dict[str, Any]

class ContextManager:
    """Manages codebase context and provides MCP-like navigation capabilities."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.ignore_patterns = self._load_ignore_patterns()
        self.context_cache: Dict[str, Any] = {}
        self.project_structure: Optional[ProjectStructure] = None
        self._build_project_structure()
    
    def _load_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from .criaignore and common patterns."""
        patterns = [
            '.git', '__pycache__', '*.pyc', '*.pyo', '*.pyd', 
            '*.egg-info', '.pytest_cache', '.coverage', 'node_modules',
            '.venv', 'venv', 'env', '.env', '*.log', '.DS_Store'
        ]
        
        try:
            with open(self.root_path / '.criaignore', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except FileNotFoundError:
            pass
        
        return patterns
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
        return False
    
    def _build_project_structure(self):
        """Build a comprehensive project structure."""
        files = []
        directories = []
        entry_points = []
        dependencies = {}
        language_stats = {}
        
        for item in self.root_path.rglob("*"):
            if self._should_ignore(item):
                continue
                
            if item.is_file():
                files.append(str(item.relative_to(self.root_path)))
                ext = item.suffix.lower()
                language_stats[ext] = language_stats.get(ext, 0) + 1
                
                # Identify entry points
                if item.name in ['__main__.py', 'main.py', 'app.py', 'index.py']:
                    entry_points.append(str(item.relative_to(self.root_path)))
                elif item.name == 'pyproject.toml' or item.name == 'setup.py':
                    entry_points.append(str(item.relative_to(self.root_path)))
                    
            elif item.is_dir():
                directories.append(str(item.relative_to(self.root_path)))
        
        # Get git information
        git_info = self._get_git_info()
        
        self.project_structure = ProjectStructure(
            root_path=str(self.root_path),
            files=sorted(files),
            directories=sorted(directories),
            entry_points=entry_points,
            dependencies=dependencies,
            language_stats=language_stats,
            git_info=git_info
        )
    
    def _get_git_info(self) -> Dict[str, Any]:
        """Get git repository information."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_root = result.stdout.strip()
                branch_result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=self.root_path,
                    capture_output=True,
                    text=True
                )
                branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
                
                return {
                    "is_git_repo": True,
                    "root": git_root,
                    "branch": branch,
                    "current_dir": str(self.root_path)
                }
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return {"is_git_repo": False, "current_dir": str(self.root_path)}
    
    def get_project_overview(self) -> str:
        """Get a comprehensive project overview."""
        if not self.project_structure:
            return "No project structure available."
        
        ps = self.project_structure
        overview = f"""
Project Overview:
================
Root: {ps.root_path}
Files: {len(ps.files)} files
Directories: {len(ps.directories)} directories

Language Distribution:
{json.dumps(ps.language_stats, indent=2)}

Entry Points:
{chr(10).join(f"  - {ep}" for ep in ps.entry_points)}

Git Info:
  Repository: {'Yes' if ps.git_info.get('is_git_repo') else 'No'}
  Branch: {ps.git_info.get('branch', 'N/A')}
  Current Dir: {ps.git_info.get('current_dir', 'N/A')}

Top-level Structure:
{chr(10).join(f"  📁 {d}/" for d in ps.directories[:10])}
{chr(10).join(f"  📄 {f}" for f in ps.files[:10])}
"""
        return overview.strip()
    
    def find_files_by_pattern(self, pattern: str, file_type: str = None) -> List[str]:
        """Find files matching a pattern."""
        matches = []
        for file_path in self.project_structure.files:
            if fnmatch.fnmatch(file_path, pattern):
                if file_type is None or file_path.endswith(f".{file_type}"):
                    matches.append(file_path)
        return matches
    
    def find_files_by_content(self, search_term: str, file_types: List[str] = None) -> List[Tuple[str, int, str]]:
        """Find files containing specific content."""
        results = []
        file_types = file_types or ['.py', '.js', '.ts', '.md', '.txt']
        
        for file_path in self.project_structure.files:
            if not any(file_path.endswith(ft) for ft in file_types):
                continue
                
            try:
                full_path = self.root_path / file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            results.append((file_path, line_num, line.strip()))
            except Exception:
                continue
        
        return results
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and extract context."""
        full_path = self.root_path / file_path
        if not full_path.exists():
            return {"error": f"File {file_path} not found"}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            analysis = {
                "file_path": file_path,
                "lines": len(content.splitlines()),
                "classes": [],
                "functions": [],
                "imports": [],
                "variables": [],
                "docstrings": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        analysis["imports"].extend([alias.name for alias in node.names])
                    else:
                        module = node.module or ""
                        analysis["imports"].extend([f"{module}.{alias.name}" for alias in node.names])
            
            return analysis
            
        except SyntaxError as e:
            return {"error": f"Syntax error in {file_path}: {e}"}
        except Exception as e:
            return {"error": f"Error analyzing {file_path}: {e}"}
    
    def get_file_dependencies(self, file_path: str) -> List[str]:
        """Get dependencies of a file (imports, references)."""
        analysis = self.analyze_python_file(file_path)
        if "error" in analysis:
            return []
        
        dependencies = []
        for import_name in analysis.get("imports", []):
            # Try to find the actual file
            if "." in import_name:
                parts = import_name.split(".")
                potential_paths = [
                    f"{'/'.join(parts)}.py",
                    f"{'/'.join(parts[:-1])}/__init__.py"
                ]
                for path in potential_paths:
                    if path in self.project_structure.files:
                        dependencies.append(path)
                        break
            else:
                # Look for files with this name
                matches = self.find_files_by_pattern(f"**/{import_name}.py")
                dependencies.extend(matches)
        
        return list(set(dependencies))
    
    def get_context_around_line(self, file_path: str, line_num: int, context_lines: int = 5) -> str:
        """Get context around a specific line in a file."""
        full_path = self.root_path / file_path
        if not full_path.exists():
            return f"File {file_path} not found"
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)
            
            context = []
            for i in range(start, end):
                marker = ">>> " if i == line_num - 1 else "    "
                context.append(f"{marker}{i+1:4d}: {lines[i].rstrip()}")
            
            return f"Context around line {line_num} in {file_path}:\n" + "\n".join(context)
            
        except Exception as e:
            return f"Error reading context from {file_path}: {e}"
    
    def suggest_next_actions(self, current_context: str) -> List[str]:
        """Suggest next actions based on current context."""
        suggestions = []
        
        if "error" in current_context.lower():
            suggestions.extend([
                "Check the file exists and is readable",
                "Look for similar files in the project",
                "Check the project structure for clues"
            ])
        elif "import" in current_context.lower():
            suggestions.extend([
                "Find the imported module in the project",
                "Check if dependencies are installed",
                "Look for similar import patterns"
            ])
        elif "function" in current_context.lower() or "class" in current_context.lower():
            suggestions.extend([
                "Read the full file to understand the context",
                "Look for usage examples of this function/class",
                "Check the docstring for more information"
            ])
        
        return suggestions
