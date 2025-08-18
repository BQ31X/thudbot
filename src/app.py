# src/app.py - LangGraph Implementation

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from state import LangGraphState
from langgraph_flow import (
    router_node, 
    find_hint_node, 
    verify_correctness_node, 
    maintain_character_node, 
    format_output_node
)

# Load environment variables
load_dotenv()

def should_continue(state: LangGraphState) -> str:
    """Conditional edge function to determine next step"""
    # If we already have a formatted output (off-topic response), end here
    if state.get("formatted_output"):
        return "end"
    return "continue"

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
    
    # Sequential flow for hint processing
    graph.add_edge("find_hint", "verify_correctness")
    graph.add_edge("verify_correctness", "maintain_character")
    graph.add_edge("maintain_character", "format_output")
    graph.add_edge("format_output", END)
    
    # Compile the graph
    return graph.compile()

# Create the compiled graph
compiled_graph = create_thud_graph()

def run_hint_request(user_input: str) -> str:
    """Run a hint request through the graph"""
    
    initial_state = LangGraphState(
        chat_history=[],
        hint_level=1,
        last_question_id="",
        user_input=user_input,
        current_hint="",
        formatted_output=""
    )
    
    print(f"🚀 Running LangGraph with input: '{user_input}'")
    print("=" * 50)
    
    # Run the graph
    result = compiled_graph.invoke(initial_state)
    
    print("=" * 50)
    print(f"🎉 Final result: {result['formatted_output']}")
    
    return result["formatted_output"]

if __name__ == "__main__":
    # Test the graph
    test_input = "I need a hint to find the bus token"
    run_hint_request(test_input)