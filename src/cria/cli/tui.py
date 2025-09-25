from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
import os
import subprocess

# Initialize Rich Console for beautiful printing
console = Console()

def get_git_branch():
    """Gets the current git branch of the working directory."""
    try:
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).strip().decode('utf-8')
        return f"🌿 {branch}"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

def display_header():
    """Displays the ASCII art header and intro tips."""
    ascii_art = """
██████╗██████╗ ██╗ █████╗ 
██╔═══╝██╔══██╗██║██╔══██╗
██║    ██████╔╝██║███████║
██║    ██╔══██╗██║██╔══██║
██████╗██║  ██║██║██║  ██║
╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
    """
    console.print(Text(ascii_art, style="bold cyan"), justify="center")
    
    tips = """
[bold]Tips for getting started:[/bold]
1. Ask questions, edit files, or run commands.
2. Be specific for the best results.
3. Use `@path/to/file` to add file context to your message.
    """
    console.print(Panel(tips, title="Welcome to CoderIA!", border_style="dim", expand=False))

def display_agent_thought(tool_name, tool_args):
    """Displays the agent's thought process in a formatted panel."""
    thought = f"[bold]Tool:[/bold] {tool_name}\n[bold]Args:[/bold] {tool_args}"
    console.print(Panel(thought, title="🧠 Thought", border_style="yellow", expand=False))

def display_observation(result):
    """Displays the result of a tool execution."""
    # Use a simple print for observations to avoid excessive boxing
    console.print(f"[bold dim yellow]🛠️ Observation:[/bold dim yellow]\n{result}")

def display_final_response(response):
    """Displays the agent's final response."""
    console.print(Panel(response, title="✅ Final Answer", border_style="green", expand=False))

def get_user_input():
    """Gets user input using prompt_toolkit with a status bar."""
    
    # Define the bottom toolbar content
    toolbar_text = f" CWD: {os.getcwd()}  {get_git_branch()} | Model: {os.getenv('CRIA_MODEL', 'llama3')} "
    
    return prompt(
        "› ",
        bottom_toolbar=toolbar_text,
        prompt_continuation="  "
    )