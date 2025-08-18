"""LangGraph Agent Library

A library for LangGraph agents with caching, monitoring, and agent integration.
"""

from .models import get_openai_model
from .models import AgentState as _AgentState  # Import explicitly
from .agents import create_langgraph_agent
from .caching import CacheBackedEmbeddings, setup_llm_cache
from .rag import ProductionRAGChain

# Re-export AgentState
AgentState = _AgentState

__version__ = "0.1.0"
__all__ = [
    "create_langgraph_agent",
    "CacheBackedEmbeddings",
    "setup_llm_cache",
    "ProductionRAGChain",
    "get_openai_model",
    "AgentState",
]

