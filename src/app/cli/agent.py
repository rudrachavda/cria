import ollama
import json
from . import tools
from .tui import display_agent_thought, display_observation, get_user_input
from .memory import Memory
from .intelligence import AgentIntelligence
import inspect

MODEL = 'llama3.1:latest'
MAX_ITERATIONS = 10

def get_available_tools():
    """
    Returns a dictionary of available tools, mapping tool names to their functions.
    """
    return {
        # Basic file operations
        "list_files": tools.list_files,
        "read_file": tools.read_file,
        "read_multiple_files": tools.read_multiple_files,
        "write_file": tools.write_file,
        "execute_command": tools.execute_command,
        
        # Enhanced MCP-like tools
        "get_project_overview": tools.get_project_overview,
        "explore_codebase": tools.explore_codebase,
        "analyze_file": tools.analyze_file,
        "find_code_patterns": tools.find_code_patterns,
        "get_file_dependencies": tools.get_file_dependencies,
        "navigate_to_symbol": tools.navigate_to_symbol,
        "get_code_flow": tools.get_code_flow,
        "suggest_improvements": tools.suggest_improvements,
        "get_project_health": tools.get_project_health,
        "execute_with_context": tools.execute_with_context,
        
        # Coding-specific tools
        "find_code_smells": tools.find_code_smells,
        "suggest_refactoring": tools.suggest_refactoring,
        "generate_test_suggestions": tools.generate_test_suggestions,
        "find_security_issues": tools.find_security_issues,
        "get_code_metrics": tools.get_code_metrics,
        "generate_documentation_suggestions": tools.generate_documentation_suggestions,
        "read_and_summarize_project": tools.read_and_summarize_project,
    }

def get_system_prompt():
    """
    Generates the system prompt for the AI agent, including tool definitions.
    """
    tool_definitions = ""
    for name, func in get_available_tools().items():
        tool_definitions += f"""- {name}:
"""
        tool_definitions += f"""  - Description: {inspect.getdoc(func)}
"""
        tool_definitions += f"""  - Arguments: {inspect.signature(func)}

"""

    return f"""
You are an expert AI programming assistant with advanced codebase understanding capabilities. You have access to powerful tools that allow you to navigate, analyze, and understand codebases like a professional developer.

## Your Capabilities

You can:
- Navigate and explore codebases intelligently
- Analyze code structure, dependencies, and patterns
- Find symbols, functions, and classes across the project
- Understand code flow and relationships
- Suggest improvements and identify issues
- Execute commands with proper context
- Read and write files efficiently

## Response Format

You must respond with a single JSON object in this exact format:
{{
  "thought": {{
    "goal": "What is the user's goal?",
    "current_state": "What is the current state of the project?",
    "analysis": "What have I learned from previous observations?",
    "next_action": "What is the next logical step to take?",
    "tool": "Which tool is best suited for this step?",
    "reasoning": "Why is this the best approach?"
  }},
  "plan": "Your step-by-step plan to achieve the user's goal. Mark completed steps with [x].",
  "progress": "A summary of the progress you have made so far.",
  "tool": "tool_name",
  "args": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}

## Strategic Approach

1. **Start with context**: Use `get_project_overview` to understand the project structure
2. **Explore intelligently**: Use `explore_codebase` to find relevant files
3. **Read and analyze**: Use `read_and_summarize_project` to read all files and create comprehensive analysis
4. **Write results**: Use `write_file` to save the analysis to the requested file
5. **Navigate efficiently**: Use `navigate_to_symbol` to find specific functions/classes
6. **Understand relationships**: Use `get_file_dependencies` to see how files connect
7. **Search patterns**: Use `find_code_patterns` to locate specific code patterns
8. **Execute with context**: Use `execute_with_context` for commands with proper working directory

## Tool Selection Strategy

- **For exploration**: `get_project_overview`, `explore_codebase`
- **For analysis**: `analyze_file`, `get_code_flow`, `get_file_dependencies`
- **For navigation**: `navigate_to_symbol`, `find_code_patterns`
- **For execution**: `execute_with_context` (preferred over `execute_command`)
- **For improvement**: `suggest_improvements`, `get_project_health`

## Important Rules

1. **Always respond with valid JSON** - No other text or explanations
2. **Always provide a tool** - Even if it's just `finish`
3. **Complete the full task** - Don't stop until you've done everything the user asked for
4. **Stay focused on the original goal** - Do not deviate from the user's specific request
5. **Think strategically** - Plan your approach before acting
6. **Use context effectively** - Leverage the enhanced tools for better understanding
7. **Be efficient** - Choose the most appropriate tool for each task
8. **Learn from observations** - Analyze results to inform next steps
9. **Handle errors gracefully** - If a tool fails, analyze and try a different approach
10. **Track progress** - Update your plan and progress with each step
11. **Remember the goal** - Always reference the original goal in your thought process

## Available Tools

{tool_definitions}

## Intelligence Guidelines

- **Think step by step** - Break down complex tasks into logical steps
- **Use appropriate tools** - Choose the best tool for each specific task
- **Provide correct arguments** - Always include required parameters for tools
- **Stay focused** - Always reference the original goal in your reasoning
- **Be thorough** - Complete all parts of the user's request
- **Learn from context** - Use observations to inform next steps

## Tool Usage Examples

- read_file requires: {{"path": "filename.py"}}
- write_file requires: {{"path": "filename.py", "content": "file content"}}
- read_multiple_files requires: {{"paths": ["file1.py", "file2.py"]}}
- explore_codebase can use: {{"pattern": "**/*.py", "max_files": 20}}

Let's begin!
"""

def get_next_action(memory: Memory):
    """
    Gets the next action from the LLM, ensuring it's a valid JSON object.
    """
    while True:
        try:
            response = ollama.chat(
                model=MODEL,
                messages=memory.get_history(),
                options={"temperature": 0.1},
                format='json'
            )
            action = json.loads(response['message']['content'])
            return action
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing model response: {e}. Retrying...")
            # Optionally, add the error to the messages to inform the model
            memory.add_message("assistant", "Invalid JSON response. Please provide a valid JSON object.")

def criticize_tool_call(action):
    """
    Criticizes the tool call generated by the model.
    Returns a string with criticism if the tool call is invalid, otherwise returns None.
    """
    tool_name = action.get("tool")
    tool_args = action.get("args", {})

    if not tool_name:
        return "The 'tool' field is missing in your response."

    if tool_name == "finish":
        if "response" not in tool_args:
            return "The 'response' field is missing in the 'finish' tool."
        return None

    available_tools = get_available_tools()
    if tool_name not in available_tools:
        return f"Unknown tool '{tool_name}'. Please choose from the available tools: {list(available_tools.keys())}"

    tool_function = available_tools[tool_name]
    try:
        # Check if all required arguments are present
        sig = inspect.signature(tool_function)
        for param in sig.parameters.values():
            if param.default == inspect.Parameter.empty and param.name not in tool_args:
                return f"Missing required argument '{param.name}' for tool '{tool_name}'."
        
        # Check for unexpected arguments
        unexpected_args = [arg_name for arg_name in tool_args if arg_name not in sig.parameters]
        if unexpected_args:
            return f"Unexpected argument '{unexpected_args[0]}' for tool '{tool_name}'."

        return None
    except Exception as e:
        return f"An unexpected error occurred during criticism: {e}"


def execute_tool(tool_name, tool_args):
    """
    Executes a tool and returns the observation.
    """
    available_tools = get_available_tools()
    tool_function = available_tools[tool_name]
    try:
        return tool_function(**tool_args)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {e}"

def run_agent(goal):
    """
    The main agent loop with enhanced intelligence.
    """
    memory = Memory()
    intelligence = AgentIntelligence()
    
    # Generate smart plan
    smart_plan = intelligence.generate_smart_plan(goal)
    print(f"🧠 Generated smart plan with {len(smart_plan)} steps")
    
    # Enhanced system prompt with goal focus
    system_prompt = get_system_prompt() + f"\n\n**CURRENT GOAL**: {goal}\n**IMPORTANT**: Stay focused on this specific goal throughout the conversation. Do not deviate from the user's request."
    
    memory.add_message("system", system_prompt)
    memory.add_message("user", goal)
    
    actions_taken = []
    
    for i in range(MAX_ITERATIONS):
        print(f"\n🔄 Iteration {i + 1}")
        
        # Get next action with intelligence
        action = get_next_action(memory)
        if not action:
            print("Could not get a valid action from the model. Aborting.")
            break

        # Ensure the action includes the original goal in thought
        if "thought" in action and isinstance(action["thought"], dict):
            action["thought"]["original_goal"] = goal
            action["thought"]["current_iteration"] = i + 1

        display_agent_thought(action.get("thought"))

        criticism = criticize_tool_call(action)
        if criticism:
            display_observation(f"Criticism: {criticism}")
            memory.add_message("assistant", json.dumps(action))
            memory.add_message("user", f"Your last tool call was invalid. {criticism}. Please try again with the correct arguments.")
            continue

        if action["tool"] == "finish":
            display_observation(action["args"]["response"])
            # Learn from successful interaction
            intelligence.learn_from_interaction(goal, actions_taken, action["args"]["response"], True)
            break

        # Auto-execute for exploration and analysis tools (MCP-like behavior)
        auto_execute_tools = {
            "get_project_overview", "explore_codebase", "analyze_file", 
            "find_code_patterns", "get_file_dependencies", "navigate_to_symbol",
            "get_code_flow", "suggest_improvements", "get_project_health",
            "list_files", "read_file", "read_multiple_files", "write_file",
            "find_code_smells", "suggest_refactoring", "generate_test_suggestions",
            "find_security_issues", "get_code_metrics", "generate_documentation_suggestions",
            "read_and_summarize_project"
        }
        
        if action["tool"] in auto_execute_tools:
            print("🤖 Auto-executing exploration/analysis tool...")
        else:
            # User confirmation for potentially destructive actions
            user_response = get_user_input("Execute this action? (y/n): ").lower()
            if user_response != 'y':
                print("Action cancelled by user.")
                break

        observation = execute_tool(action["tool"], action["args"])
        actions_taken.append(action)
        
        # Intelligent error handling
        if "Error: File" in observation and "not found" in observation:
            display_observation(observation)
            suggestions = intelligence.get_contextual_suggestions(observation)
            if suggestions:
                print(f"💡 Suggestions: {'; '.join(suggestions[:2])}")
            
            memory.add_message("assistant", json.dumps(action))
            memory.add_message("user", f"Observation: {observation}\n\nI got a 'file not found' error. I will now run `pwd` to find out my current working directory.")
            
            action = {"tool": "execute_command", "args": {"command": "pwd"}}
            display_agent_thought(action)
            observation = execute_tool(action["tool"], action["args"])
        
        display_observation(observation)
        
        # Check if we should continue
        should_continue, reason = intelligence.should_continue(observation, i, MAX_ITERATIONS)
        if not should_continue:
            print(f"🛑 Stopping: {reason}")
            break
        
        memory.add_message("assistant", json.dumps(action))
        memory.add_message("user", f"Observation: {observation}")

    else:
        print("Maximum iterations reached. Aborting.")
        # Learn from incomplete interaction
        intelligence.learn_from_interaction(goal, actions_taken, "Maximum iterations reached", False)
