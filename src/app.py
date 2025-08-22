# src/app.py - LangGraph Implementation

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from state import LangGraphState
from langsmith import traceable
from router_node import router_node
from find_hint_node import find_hint_node  
from verify_correctness_node import verify_correctness_node
from maintain_character_node import maintain_character_node
from format_output_node import format_output_node
from generate_error_message_node import generate_error_message_node

# Load environment variables
load_dotenv()

# Session storage for chat history persistence (in-memory for demo)
# In production, this would be replaced with database or Redis storage
_session_storage = {}

def should_continue(state: LangGraphState) -> str:
    """Conditional edge function to determine next step"""
    # If we already have a formatted output (off-topic response), end here
    if state.get("formatted_output"):
        return "end"
    return "continue"

def verification_router(state: LangGraphState) -> str:
    """Route based on verification results"""
    verification_passed = state.get("verification_passed", False)
    
    if verification_passed:
        print("✅ Verification passed - proceeding to character maintenance")
        return "verified"
    else:
        print("❌ Verification failed - generating error message")
        return "failed"

def create_thud_graph():
    """Create and compile the LangGraph"""
    
    # Create the StateGraph
    graph = StateGraph(LangGraphState)
    
    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("find_hint", find_hint_node)
    graph.add_node("verify_correctness", verify_correctness_node)
    graph.add_node("maintain_character", maintain_character_node)
    graph.add_node("format_output", format_output_node)
    graph.add_node("generate_error_message", generate_error_message_node)
    
    # Add edges
    graph.add_edge(START, "router")
    
    # Conditional edge from router
    graph.add_conditional_edges(
        "router",
        should_continue,
        {
            "continue": "find_hint",
            "end": END
        }
    )
    
    # Sequential flow: find_hint -> verify_correctness
    graph.add_edge("find_hint", "verify_correctness")
    
    # Conditional edge from verify_correctness
    graph.add_conditional_edges(
        "verify_correctness",
        verification_router,
        {
            "verified": "maintain_character",
            "failed": "generate_error_message"
        }
    )
    
    # Success path: maintain_character -> format_output -> END
    graph.add_edge("maintain_character", "format_output")
    graph.add_edge("format_output", END)
    
    # Error path: generate_error_message -> END
    graph.add_edge("generate_error_message", END)
    
    # Compile the graph
    return graph.compile()

# Create the compiled graph
compiled_graph = create_thud_graph()

@traceable(
    run_type="chain", 
    name="thudbot_hint_flow",
    metadata={"version": "progressive-hints-v1"}
)
def run_hint_request(user_input: str, session_id: str = "default") -> str:
    """Run a hint request through the graph with session persistence
    
    Args:
        user_input: The user's question or request
        session_id: Session identifier for chat history persistence (default: "default")
    """
    
    # Get or create session state
    if session_id not in _session_storage:
        # New session - initialize with empty state
        _session_storage[session_id] = {
            "chat_history": [],
            "hint_level": 1,
            "last_question_id": "",
            "last_question_keywords": set()
        }
        print(f"🆕 New session created: {session_id}")
    
    session_data = _session_storage[session_id]
    
    # Create state with session persistence
    initial_state = LangGraphState(
        chat_history=session_data["chat_history"],
        hint_level=session_data["hint_level"],
        last_question_id=session_data["last_question_id"],
        last_question_keywords=session_data["last_question_keywords"],
        user_input=user_input,
        current_hint="",
        formatted_output="",
        verification_passed=False,
        verification_reason="",
        retry_count=0,
        retrieved_context=""
    )
    
    print(f"🚀 Running LangGraph with input: '{user_input}' (session: {session_id})")
    print(f"📚 Loaded session: hint_level={session_data['hint_level']}, history_length={len(session_data['chat_history'])}")
    print("=" * 50)
    
    # Run the graph
    result = compiled_graph.invoke(initial_state)
    
    # Update session storage with latest state
    _session_storage[session_id] = {
        "chat_history": result.get("chat_history", []),
        "hint_level": result.get("hint_level", 1),
        "last_question_id": result.get("last_question_id", ""),
        "last_question_keywords": result.get("last_question_keywords", set())
    }
    
    print("=" * 50)
    print(f"🎉 Final result: {result['formatted_output']}")
    print(f"💾 Session updated: hint_level={_session_storage[session_id]['hint_level']}")
    
    return result["formatted_output"]

def clear_session(session_id: str = "default") -> bool:
    """Clear a specific session's chat history and state
    
    Args:
        session_id: Session identifier to clear
        
    Returns:
        True if session was cleared, False if session didn't exist
    """
    if session_id in _session_storage:
        del _session_storage[session_id]
        print(f"🗑️ Session cleared: {session_id}")
        return True
    return False

if __name__ == "__main__":
    # Test the graph
    test_input = "I need a hint to find the bus token"
    run_hint_request(test_input)