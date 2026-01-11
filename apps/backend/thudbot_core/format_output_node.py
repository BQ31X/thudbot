"""
Format the final player-facing response and update conversational session state.

Responsibilities:
- Produces the final, player-visible response string from the prepared hint content.
- Applies simple, consistent formatting that reflects the current hint level.
- Updates conversational history to persist the completed exchange.
- Acts as the terminal node in the LangGraph, always leading to END.
- Does not perform retrieval, verification, or content transformation beyond formatting.

Reads from state:
- current_hint
- hint_level
- user_input
- chat_history

Writes to state:
- formatted_output (final response string)
- chat_history (appends HumanMessage and AIMessage entries)

Notes:
- Uses simple string formatting (e.g., "🎯 Hint (Level {hint_level}): {hint}").
- Appends the current turn to chat history for session continuity.
- Truncates chat history to the most recent 20 messages (10 exchanges).
- This node represents the final side-effectful step before returning control to the caller.
"""
from thudbot_core.state import LangGraphState
from langchain_core.messages import HumanMessage, AIMessage

def format_output_node(state: LangGraphState) -> LangGraphState:
    """Format the final output and update chat history for session persistence"""
    hint = state["current_hint"]
    hint_level = state.get("hint_level", 1)
    user_input = state["user_input"]
    
    print(f"🔍 FORMAT_OUTPUT INPUT: hint='{hint[:50]}...', level={hint_level}")
    formatted = f"🎯 Hint (Level {hint_level}): {hint}"
    state["formatted_output"] = formatted
    
    # PROGRESSIVE HINTS: Update chat history for session persistence
    chat_history = state.get("chat_history", [])
    
    # Add user message and bot response to chat history
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=formatted))
    
    # Keep chat history manageable (last 10 exchanges = 20 messages)
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
    
    state["chat_history"] = chat_history
    
    print(f"📋 Formatted output ready")
    print(f"💬 Chat history updated: {len(chat_history)} messages")
    print(f"🔍 FORMAT_OUTPUT OUTPUT: '{formatted[:50]}...' -> formatted_output set, chat_history updated")
    return state
