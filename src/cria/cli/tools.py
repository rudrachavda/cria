"""
Tools for the cria AI agent.
"""

import os
import subprocess
from pathlib import Path
from typing import List

def list_files(path: str = ".") -> str:
    """
    Lists files and directories in a given path.

    Args:
        path (str): The path to the directory. Defaults to the current directory.

    Returns:
        str: A list of files and directories, or an error message.
    """
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: Directory '{path}' does not exist"
        
        files = []
        for item in p.iterdir():
            if item.is_file():
                files.append(f"📄 {item.name}")
            elif item.is_dir():
                files.append(f"📁 {item.name}/")
        
        if not files:
            return f"No files found in '{path}'"
        
        return "\n".join(sorted(files))
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
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
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
