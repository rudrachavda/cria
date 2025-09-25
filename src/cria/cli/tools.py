"""
Tools for the cria AI agent.
"""

import os
import subprocess
import sys
from pathlib import Path


def list_files(directory="."):
    """List files in a directory."""
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        files = []
        for item in path.iterdir():
            if item.is_file():
                files.append(f"📄 {item.name}")
            elif item.is_dir():
                files.append(f"📁 {item.name}/")
        
        if not files:
            return f"No files found in '{directory}'"
        
        return "\n".join(sorted(files))
    except Exception as e:
        return f"Error listing files: {e}"


def read_file(file_path):
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Contents of {file_path}:\n{content}"
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found"
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"


def write_file(file_path, content):
    """Write content to a file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{file_path}'"
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"


def execute_command(command):
    """Execute a shell command."""
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
