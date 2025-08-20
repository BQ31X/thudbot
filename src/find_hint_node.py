from langsmith import traceable
from agent import get_direct_hint
from state import LangGraphState

@traceable(run_type="chain", name="find_hint_node")  
def find_hint_node(state: LangGraphState) -> LangGraphState:
    """Find hint using direct RAG chain (no Agent Executor)"""
    user_input = state["user_input"]
    hint_level = state.get("hint_level", 1)
    
    print(f"🔍 FIND_HINT INPUT: '{user_input}' (level {hint_level})")
    print(f"🎮 Finding hint for: {user_input}")
    hint = get_direct_hint(user_input)
    
    state["current_hint"] = hint
    print(f"📝 Retrieved hint: {hint[:100]}{'...' if len(hint) > 100 else ''}")
    print(f"🔍 FIND_HINT OUTPUT: '{hint[:50]}...' -> current_hint updated")
    return state