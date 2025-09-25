"""
Memory for the cria AI agent.
"""

from typing import List, Dict

class Memory:
    """
    A class to store the conversation history.
    """

    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """
        Adds a message to the conversation history.

        Args:
            role (str): The role of the message sender (e.g., "user", "assistant").
            content (str): The content of the message.
        """
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        """
        Returns the conversation history.

        Returns:
            List[Dict[str, str]]: The conversation history.
        """
        return self.history
