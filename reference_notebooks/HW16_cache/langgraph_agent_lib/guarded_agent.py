"""
Implementation of an agent with input and output guardrails.
"""

from typing import Dict, Any, List, Optional, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.language_models import BaseChatModel

from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

# Temporary: Define AgentState here instead of importing
class AgentState(TypedDict):
    """Type definition for agent state."""
    messages: List[BaseMessage]
    next: Optional[str]
    needs_refinement: Optional[bool]
    refinement_feedback: Optional[str]
    used_rag: Optional[bool]

from .rag import ProductionRAGChain
from .guardrails import check_message, GuardrailResult
from .agents import get_default_tools

def guardrail_node(state: AgentState) -> Dict[str, Any]:
    """
    Node that validates messages against guardrails.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with validation results
    """
    messages = state["messages"]
    if not messages:
        return {"messages": messages}
    
    latest_message = messages[-1]
    
    # Build context for validation
    context = {
        "requires_aid_info": any(
            keyword in latest_message.content.lower()
            for keyword in ["loan", "grant", "aid", "fafsa", "student"]
        ) if isinstance(latest_message, HumanMessage) else False
    }
    
    # Run guardrail checks
    result = check_message(latest_message, context)
    
    if not result.passed:
        # For both failed pre-checks (user input) and post-checks (agent output),
        # end the conversation with an error message
        error_message = result.message
        if isinstance(latest_message, AIMessage):
            # For failed post-checks, provide a more specific error
            error_message = "I apologize, but I cannot provide a response that meets our guidelines. Please try rephrasing your question about student financial aid."
        
        messages.append(AIMessage(content=error_message))
        return {"messages": messages, "next": END}
    
    return state



def call_model(state: AgentState) -> Dict[str, Any]:
    """Invoke the model with the accumulated messages and append its response."""
    model = state.get("model")  # Get model from state
    if not model:
        raise ValueError("Model not found in state")
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": messages + [response]}

def should_continue_after_pre_guard(state: AgentState) -> str:
    """Route after pre-guard: continue to agent or end if guardrail failed."""
    if state.get("next") == END:
        return "end"
    return "agent"

def should_use_tools(state: AgentState) -> str:
    """Route to 'action' if the last message includes tool calls; else continue."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "action"
    return "post_guard"

def create_guarded_agent(
    model: BaseChatModel,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None
) -> StateGraph:
    """
    Create a LangGraph agent with guardrail validation.
    
    Args:
        model: The language model to use
        tools: Optional list of tools available to the agent
        rag_chain: Optional RAG chain for retrieving context
        
    Returns:
        A StateGraph configured with guardrails
    """
    
    # Use default tools with RAG chain if no tools provided
    if tools is None:
        tools = get_default_tools(rag_chain)
    # Create a closure to capture the model
    def call_model_with_model(state: AgentState) -> Dict[str, Any]:
        """Call model with the captured model instance."""
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": messages + [response]}
    
    # Initialize the graph
    graph = StateGraph(AgentState)
    
    # Create nodes
    graph.add_node("pre_guard", guardrail_node)
    graph.add_node("agent", call_model_with_model)  # Use the closure that has access to model
    graph.add_node("action", ToolNode(tools or []))  # For handling tool calls
    graph.add_node("post_guard", guardrail_node)
    
    # Add edges with conditional routing
    graph.add_conditional_edges(
        "pre_guard",
        should_continue_after_pre_guard,
        {
            "agent": "agent",
            "end": END
        }
    )
    graph.add_conditional_edges(
        "agent",
        should_use_tools,
        {
            "action": "action",
            "post_guard": "post_guard"
        }
    )
    graph.add_edge("action", "agent")
    
    # Add simple edge for post-guard - always end after post-check
    graph.add_edge("post_guard", END)
    
    # Set entry point
    graph.set_entry_point("pre_guard")
    
    return graph.compile()
