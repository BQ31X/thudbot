from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class LangGraphState(TypedDict):
    """
    Represents the state of our LangGraph.

    Attributes:
        chat_history: A list of messages that represents the conversation history.
        hint_level: An integer to track the current hint level (1 for subtle, 2 for moderate, etc.).
        last_question_id: A unique identifier for the last question asked.
        user_input: The current user input
        current_hint: The hint being processed
        formatted_output: The final formatted response
    """
    chat_history: List[BaseMessage]
    hint_level: int
    last_question_id: str
    user_input: str
    current_hint: str
    formatted_output: str
