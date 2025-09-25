"""
Main entry point for the cria CLI application.
"""

import sys
import os

# Add the current directory to the Python path so we can import cli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import agent, tui

def main():
    """The main entry point for the cria CLI application."""
    tui.display_header()
    
    # Check if a goal was passed as a command-line argument
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
        tui.console.print(f"[bold]Goal:[/bold] {goal}\n")
        agent.run_agent(goal)
    else:
        # Interactive mode
        while True:
            try:
                goal = tui.get_user_input()
                if goal is None or goal.lower() in ["exit", "quit"]:
                    break
                agent.run_agent(goal)
            except (KeyboardInterrupt, EOFError):
                break
    
    tui.console.print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()