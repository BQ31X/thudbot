"""Production model utilities for OpenAI integration and agent state types."""

import os
from typing import Optional, TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

class AgentState(TypedDict):
    """Type definition for LangGraph agent state with guardrails support.
    
    This TypedDict defines the structure of the state object that flows through
    our LangGraph nodes. It's particularly important for the guarded agent implementation
    as it tracks both conversation state and guardrail-specific metadata.
    
    Attributes:
        messages: List of conversation messages (both user and assistant).
                 This is the primary conversation history that gets passed to the LLM.
        
        next: Optional string indicating the next node to execute in the graph.
              Used by conditional edges to control flow (e.g., "refine" or "end").
              
        needs_refinement: Boolean flag set by guardrails when a response needs improvement.
                         When True, the graph will route the response back through the
                         agent node for refinement.
        
        refinement_feedback: Specific feedback from the guardrails explaining why
                           refinement is needed (e.g., "Response lacks relevant student
                           aid information" or "Contains PII").
        
        used_rag: Boolean flag indicating whether RAG was used in generating the response.
                 This affects which guardrails are applied (e.g., RAG quality evaluation).
    
    Example:
        {
            "messages": [HumanMessage(content="How do federal loans work?")],
            "next": None,
            "needs_refinement": False,
            "refinement_feedback": None,
            "used_rag": True
        }
    """
    messages: List[BaseMessage]
    next: Optional[str]
    needs_refinement: Optional[bool]
    refinement_feedback: Optional[str]
    used_rag: Optional[bool]


def get_openai_model(
    model_name: Optional[str] = None, 
    temperature: float = 0.1,
    max_tokens: Optional[int] = None
) -> ChatOpenAI:
    """Get a configured OpenAI model instance.
    
    Args:
        model_name: Model name to use. Defaults to env var OPENAI_MODEL or "gpt-4.1-mini"
        temperature: Sampling temperature 
        max_tokens: Maximum tokens to generate
        
    Returns:
        Configured ChatOpenAI instance
    """
    name = model_name or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    
    kwargs = {
        "model": name,
        "temperature": temperature,
    }
    
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
        
    return ChatOpenAI(**kwargs)

# Define exports after all definitions
__all__ = ["get_openai_model", "AgentState"]
