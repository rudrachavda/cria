"""
Main entry point for the cria CLI application.
"""

import sys
import os

# Add the current directory to the Python path so we can import cli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import agent, tui

def run_agent_loop(initial_goal):
    """
    Runs the main agentic loop with a given goal.
    """
    # Use the existing agent logic but with our new TUI functions
    messages = agent.get_initial_messages(initial_goal)
    
    for i in range(agent.MAX_ITERATIONS):
        tui.console.rule(f"[bold yellow]Iteration {i+1}")

        # 1. THINK
        action = agent.get_next_action(messages)
        if not action:
            break
        
        tool_name = action.get("tool")
        tool_args = action.get("args", {})
        tui.display_agent_thought(tool_name, tool_args)
        
        # Add agent's thought to history
        messages.append({"role": "assistant", "content": agent.format_action_to_json(action)})

        # 2. ACT & OBSERVE
        if tool_name == "finish":
            tui.display_final_response(tool_args.get("response", "Task completed."))
            break

        observation = agent.execute_tool(tool_name, tool_args)
        tui.display_observation(observation)
        
        # Add observation to history
        messages.append({"role": "system", "content": f"Tool Output: {observation}"})

    else:
        tui.console.print("[bold red]⚠️ Agent reached maximum iterations without finishing.[/bold red]")


def main():
    """The main entry point for the cria CLI application."""
    tui.display_header()
    
    # Check if a goal was passed as a command-line argument
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
        tui.console.print(f"[bold]Goal:[/bold] {goal}\n")
        run_agent_loop(goal)
    else:
        # Interactive mode
        while True:
            try:
                goal = tui.get_user_input()
                if goal.lower() in ["exit", "quit"]:
                    break
                run_agent_loop(goal)
            except (KeyboardInterrupt, EOFError):
                break
    
    tui.console.print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
