import ollama
import json
from cli import tools

MODEL = 'llama2:7b'
MAX_ITERATIONS = 10

AVAILABLE_TOOLS = {
    "list_files": tools.list_files,
    "read_file": tools.read_file,
    "write_file": tools.write_file,
    "execute_command": tools.execute_command,
}

def get_tool_definitions():
    """Returns the tool definitions for the AI agent."""
    return """
You have access to the following tools:
- list_files: List files in a directory
- read_file: Read the contents of a file
- write_file: Write content to a file
- execute_command: Execute a shell command

You must respond with ONLY a JSON object in this exact format:
{
  "tool": "tool_name",
  "args": {
    "param1": "value1",
    "param2": "value2"
  }
}

If you want to finish and provide a final answer, use:
{
  "tool": "finish",
  "args": {
    "response": "Your final answer here"
  }
}

Always respond with valid JSON. Do not include any other text.
"""

def get_initial_messages(goal):
    """Creates the initial message list with the system prompt and user goal."""
    return [
        {"role": "system", "content": f"You are an expert AI programming assistant. You can help with coding tasks by using the available tools. {get_tool_definitions()}"},
        {"role": "user", "content": goal}
    ]

def get_next_action(messages):
    """Gets the next action from the LLM."""
    try:
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            options={"temperature": 0.1},
            format='json'
        )
        return json.loads(response['message']['content'])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing model response: {e}")
        return None

def execute_tool(tool_name, tool_args):
    """Executes a tool and returns the observation."""
    if tool_name in AVAILABLE_TOOLS:
        tool_function = AVAILABLE_TOOLS[tool_name]
        try:
            return tool_function(**tool_args)
        except TypeError as e:
            return f"Error: Invalid arguments for tool '{tool_name}': {e}"
    else:
        return f"Error: Unknown tool '{tool_name}'"

def format_action_to_json(action):
    """Utility to format the action dict into a JSON string."""
    return json.dumps(action, indent=2)