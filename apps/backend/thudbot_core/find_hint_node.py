"""
Retrieve candidate hint content for the current player query using retrieval-augmented generation.

Responsibilities:
- Acts as the sole entry point for hint retrieval within the LangGraph.
- Translates the current player query and hint level into multiple retrieval queries.
- Invokes the external retrieval service and assembles candidate hint material.
- Applies progressive hint filtering based on the current hint level, with defined fallbacks.
- Produces fact-only hint content for downstream selection and presentation.
- Does not decide whether a hint should be shown or how it is phrased to the player.

Reads from state:

user_input
hint_level
Writes to state:

current_hint (RAG response)
retrieved_context (formatted document text for verification)

Notes:
Calls external HTTP retrieval API via HTTPRetriever (URL from config)
Uses MultiQueryRetriever to generate alternative queries
Progressive hint filtering: Attempts level-based filtering (hint_level: {$lte: hint_level}) with fallback to unfiltered
Level filtering implementation incomplete (TODO comment in code)
RAG template explicitly removes personality (fact-only extraction)
Retrieves k=5 documents (increased from 4 per Dec 2025 TEF evaluation)
External dependency: Requires retrieval service running (fails fast if unavailable)
"""
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