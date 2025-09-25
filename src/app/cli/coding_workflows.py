"""
Coding-specific workflows and optimizations for the cria AI agent.
Provides specialized tools for common development tasks.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .context import ContextManager

class CodingWorkflows:
    """Specialized workflows for coding tasks."""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.common_patterns = {
            "python": {
                "imports": r"^(import|from)\s+\w+",
                "functions": r"^def\s+(\w+)\s*\(",
                "classes": r"^class\s+(\w+)\s*[\(:]",
                "docstrings": r'""".*?"""',
                "comments": r"#.*$"
            },
            "javascript": {
                "imports": r"^(import|require)\s+",
                "functions": r"^(function\s+(\w+)|(\w+)\s*:\s*function|(\w+)\s*=>)",
                "classes": r"^class\s+(\w+)",
                "comments": r"//.*$|/\*.*?\*/"
            },
            "typescript": {
                "imports": r"^(import|export)\s+",
                "functions": r"^(function\s+(\w+)|(\w+)\s*:\s*function|(\w+)\s*=>)",
                "classes": r"^class\s+(\w+)",
                "interfaces": r"^interface\s+(\w+)",
                "comments": r"//.*$|/\*.*?\*/"
            }
        }
    
    def detect_language(self, file_path: str) -> str:
        """Detect the programming language of a file."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        return language_map.get(ext, 'unknown')
    
    def find_code_smells(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Find potential code smells and issues in a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            List of code smell objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            return []
        
        language = self.detect_language(file_path)
        smells = []
        
        # Long functions (more than 50 lines)
        current_function = None
        function_start = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if language == 'python':
                if re.match(r'^def\s+\w+', stripped):
                    if current_function and (i - function_start) > 50:
                        smells.append({
                            "type": "long_function",
                            "line": function_start,
                            "message": f"Function '{current_function}' is {i - function_start} lines long",
                            "severity": "warning"
                        })
                    current_function = re.match(r'^def\s+(\w+)', stripped).group(1)
                    function_start = i
                elif stripped and not stripped.startswith('#') and current_function:
                    # Check for deeply nested code
                    indent_level = len(line) - len(line.lstrip())
                    if indent_level > 20:  # More than 5 levels of indentation
                        smells.append({
                            "type": "deep_nesting",
                            "line": i,
                            "message": f"Deep nesting detected (level {indent_level // 4})",
                            "severity": "warning"
                        })
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if re.search(r'(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                smells.append({
                    "type": "todo_comment",
                    "line": i,
                    "message": f"TODO/FIXME comment: {line.strip()}",
                    "severity": "info"
                })
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                smells.append({
                    "type": "long_line",
                    "line": i,
                    "message": f"Line is {len(line)} characters long",
                    "severity": "warning"
                })
        
        # Check for duplicate code patterns
        function_patterns = {}
        for i, line in enumerate(lines, 1):
            if language == 'python' and re.match(r'^def\s+(\w+)', line.strip()):
                func_name = re.match(r'^def\s+(\w+)', line.strip()).group(1)
                if func_name in function_patterns:
                    smells.append({
                        "type": "duplicate_function",
                        "line": i,
                        "message": f"Function '{func_name}' appears to be duplicated",
                        "severity": "error"
                    })
                function_patterns[func_name] = i
        
        return smells
    
    def suggest_refactoring(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Suggest refactoring opportunities for a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            List of refactoring suggestions
        """
        analysis = self.context_manager.analyze_python_file(file_path)
        if "error" in analysis:
            return []
        
        suggestions = []
        
        # Suggest extracting long functions
        for func in analysis.get('functions', []):
            if not func.get('docstring'):
                suggestions.append({
                    "type": "add_docstring",
                    "target": func['name'],
                    "line": func['line'],
                    "message": f"Add docstring to function '{func['name']}'",
                    "priority": "medium"
                })
        
        # Suggest breaking down large classes
        for cls in analysis.get('classes', []):
            if len(cls.get('methods', [])) > 10:
                suggestions.append({
                    "type": "split_class",
                    "target": cls['name'],
                    "line": cls['line'],
                    "message": f"Class '{cls['name']}' has {len(cls['methods'])} methods, consider splitting",
                    "priority": "high"
                })
        
        # Suggest organizing imports
        if len(analysis.get('imports', [])) > 15:
            suggestions.append({
                "type": "organize_imports",
                "target": "imports",
                "line": 1,
                "message": f"File has {len(analysis['imports'])} imports, consider organizing them",
                "priority": "low"
            })
        
        return suggestions
    
    def generate_test_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Generate test suggestions for a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            List of test suggestions
        """
        analysis = self.context_manager.analyze_python_file(file_path)
        if "error" in analysis:
            return []
        
        suggestions = []
        
        # Suggest tests for functions without obvious test patterns
        for func in analysis.get('functions', []):
            if not func['name'].startswith('_') and not func['name'].startswith('test'):
                suggestions.append({
                    "type": "unit_test",
                    "target": func['name'],
                    "message": f"Create unit test for function '{func['name']}'",
                    "priority": "high",
                    "suggestion": f"def test_{func['name']}():\n    # Test {func['name']}\n    pass"
                })
        
        # Suggest integration tests for classes
        for cls in analysis.get('classes', []):
            if not cls['name'].startswith('_'):
                suggestions.append({
                    "type": "integration_test",
                    "target": cls['name'],
                    "message": f"Create integration test for class '{cls['name']}'",
                    "priority": "medium",
                    "suggestion": f"def test_{cls['name'].lower()}_integration():\n    # Test {cls['name']} integration\n    pass"
                })
        
        return suggestions
    
    def find_security_issues(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Find potential security issues in a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            List of security issues
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            return []
        
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "hardcoded_secret",
                        "line": i,
                        "message": "Potential hardcoded secret detected",
                        "severity": "high",
                        "suggestion": "Use environment variables or secure configuration"
                    })
        
        # Check for SQL injection vulnerabilities
        sql_patterns = [
            r'execute\s*\(\s*["\'].*%s.*["\']',
            r'query\s*=\s*["\'].*\+.*["\']',
            r'cursor\.execute\s*\(\s*f["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "sql_injection",
                        "line": i,
                        "message": "Potential SQL injection vulnerability",
                        "severity": "high",
                        "suggestion": "Use parameterized queries"
                    })
        
        # Check for eval usage
        for i, line in enumerate(lines, 1):
            if re.search(r'\beval\s*\(', line):
                issues.append({
                    "type": "eval_usage",
                    "line": i,
                    "message": "eval() usage detected - potential security risk",
                    "severity": "high",
                    "suggestion": "Avoid eval() - use safer alternatives"
                })
        
        return issues
    
    def get_code_metrics(self, file_path: str) -> Dict[str, Any]:
        """
        Get code metrics for a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary of code metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            return {}
        
        analysis = self.context_manager.analyze_python_file(file_path)
        
        metrics = {
            "lines_of_code": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "total_lines": len(lines),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "functions": len(analysis.get('functions', [])),
            "classes": len(analysis.get('classes', [])),
            "imports": len(analysis.get('imports', [])),
            "complexity": "low"  # Simplified complexity assessment
        }
        
        # Calculate complexity based on function count and lines
        if metrics["functions"] > 10 or metrics["lines_of_code"] > 200:
            metrics["complexity"] = "high"
        elif metrics["functions"] > 5 or metrics["lines_of_code"] > 100:
            metrics["complexity"] = "medium"
        
        return metrics
    
    def generate_documentation_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Generate documentation suggestions for a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            List of documentation suggestions
        """
        analysis = self.context_manager.analyze_python_file(file_path)
        if "error" in analysis:
            return []
        
        suggestions = []
        
        # Check for missing module docstring
        if not any(line.strip().startswith('"""') for line in analysis.get('content', '').splitlines()[:5]):
            suggestions.append({
                "type": "module_docstring",
                "message": "Add module docstring at the top of the file",
                "priority": "medium"
            })
        
        # Check for missing function docstrings
        for func in analysis.get('functions', []):
            if not func.get('docstring') and not func['name'].startswith('_'):
                suggestions.append({
                    "type": "function_docstring",
                    "target": func['name'],
                    "line": func['line'],
                    "message": f"Add docstring to function '{func['name']}'",
                    "priority": "high"
                })
        
        # Check for missing class docstrings
        for cls in analysis.get('classes', []):
            if not cls.get('docstring'):
                suggestions.append({
                    "type": "class_docstring",
                    "target": cls['name'],
                    "line": cls['line'],
                    "message": f"Add docstring to class '{cls['name']}'",
                    "priority": "high"
                })
        
        return suggestions
