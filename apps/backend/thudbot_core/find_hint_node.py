from langsmith import traceable
from thudbot_core.agent import get_direct_hint_with_context
from thudbot_core.state import LangGraphState

@traceable(run_type="chain", name="find_hint_node")  
def find_hint_node(state: LangGraphState) -> LangGraphState:
    """Find hint using direct RAG chain (no Agent Executor)"""
    user_input = state["user_input"]
    hint_level = state.get("hint_level", 1)
    
    print(f"🔍 FIND_HINT INPUT: '{user_input}' (level {hint_level})")
    print(f"🎮 Finding hint for: {user_input}")
    
    # Get both hint and context in one RAG call with progressive hint level filtering
    rag_result = get_direct_hint_with_context(user_input, hint_level)
    hint = rag_result["response"]
    context = rag_result["context"]
    
    # Store both in state
    state["current_hint"] = hint
    state["retrieved_context"] = context
    
    print(f"📝 Retrieved hint: {hint[:100]}{'...' if len(hint) > 100 else ''}")
    print(f"📄 Stored context: {len(context)} chars")
    print(f"🔍 FIND_HINT OUTPUT: '{hint[:50]}...' -> current_hint and retrieved_context updated")
    return state