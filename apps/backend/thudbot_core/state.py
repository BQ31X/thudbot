from typing import TypedDict, List, Set
from langchain_core.messages import BaseMessage

class LangGraphState(TypedDict):
    """
    Represents the state of our LangGraph.

    Attributes:
        chat_history: A list of messages that represents the conversation history.
        hint_level: An integer to track the current hint level (1 for subtle, 2 for moderate, etc.).
        last_question_id: A unique identifier for the last question asked.
        last_question_keywords: A set of keywords from the last question for semantic matching.
        user_input: The current user input
        current_hint: The hint being processed
        formatted_output: The final formatted response
        verification_passed: Boolean indicating if hint verification passed
        verification_reason: Reason for verification failure (if any)
        retry_count: Number of retries attempted for failed verifications
        retrieved_context: The original context documents from RAG retrieval
        intent_classification: The classifier output (GAME_RELATED or OFF_TOPIC) - signal only, not used for routing
    """
    chat_history: List[BaseMessage]
    hint_level: int
    last_question_id: str
    last_question_keywords: Set[str]
    user_input: str
    current_hint: str
    formatted_output: str
    verification_passed: bool
    verification_reason: str
    retry_count: int
    retrieved_context: str
    intent_classification: str
