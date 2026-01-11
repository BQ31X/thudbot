"""
Route an incoming player query to the appropriate next node in the LangGraph.

Responsibilities:
- Acts as the single, authoritative decision point for high-level control flow.
- Classifies the player's current input using classification-focused signals
  (intent, keyword overlap, prior state).
- Chooses the *next node* to execute, not the final response.
- Does not perform retrieval, hint generation, or narrative synthesis itself.

Reads from state:
- user_input
- chat_history
- hint_level
- last_question_id
- last_question_keywords

Writes to state:
- user_input (may replace with previous question)
- hint_level (escalates or resets to 1)
- last_question_id (stores current question)
- last_question_keywords (stores extracted keywords)
- intent_classification (signal only, not used for routing)
- formatted_output (only for smalltalk pattern match)

Notes:
- Spans multiple phases: intent classification, progressive hint detection,
  keyword extraction, session state management, and early exit for smalltalk.
- Uses LLM (gpt-4.1-nano) for intent classification; OFF_TOPIC is advisory only.
- Pattern matching for vague escalation (is_vague_escalation_request)
  and smalltalk (is_smalltalk_question).
- Keyword overlap detection (2+ matches) triggers hint level escalation.
- Side effect: replaces vague user input with previous question when escalating.
- Early termination: sets formatted_output for smalltalk, triggering END via should_continue.
- Imports utility functions from langgraph_flow.py.
"""

from thudbot_core.state import LangGraphState
from langsmith import traceable
from thudbot_core.langgraph_flow import classify_intent, OFF_TOPIC_RESPONSES, is_vague_escalation_request, extract_question_keywords, is_smalltalk_question

@traceable(run_type="chain", name="router_node")
def router_node(state: LangGraphState) -> LangGraphState:
    """Router node to determine if this is a Space Bar game question and if it's a repeat"""
    user_input = state["user_input"]
    chat_history = state.get("chat_history", [])
    
    print(f"🔍 ROUTER INPUT: '{user_input}'")
    print(f"🗣️ Chat history length: {len(chat_history)}")
    
    # PROGRESSIVE HINTS: Context-aware escalation detection
    # If user says something vague like "I'm still stuck" AND we have chat history,
    # treat it as a request for more help on the previous question (skip LLM classification)
    # This allows natural follow-up phrases that would normally be rejected as OFF_TOPIC
    if is_vague_escalation_request(user_input) and chat_history:
        # This is a vague request ("I'm still stuck") but we have chat history
        # Treat as GAME_RELATED and escalate hint level for the last question
        print(f"🔄 Vague escalation detected with chat history - treating as GAME_RELATED")
        
        # KEY FIX: Replace vague phrase with previous question for downstream nodes
        previous_question = state.get("last_question_id", "")
        if previous_question:
            print(f"🔄 Replacing vague input '{user_input}' with previous question '{previous_question}'")
            state["user_input"] = previous_question
        else:
            print(f"⚠️ No previous question found, keeping vague input")
        
        # Keep the existing last_question_id (don't update it)
        # Just escalate the hint level
        state["hint_level"] = state.get("hint_level", 1) + 1
        print(f"🔄 Escalating hint level to {state['hint_level']} for previous question")
        print(f"🔍 ROUTER OUTPUT: VAGUE_ESCALATION -> continuing to hint flow (level {state['hint_level']})")
        return state
    
    # Check for smalltalk questions first (demo-day allowlist)
    if is_smalltalk_question(user_input):
        # Direct response for smalltalk about Zelda's capabilities
        smalltalk_response = "I'm Zelda, your personal digital assistant here in *The Space Bar*! I help players navigate puzzles, find objects, and understand game mechanics. Ask me about specific locations, characters, or what to do when you're stuck!"
        state["formatted_output"] = smalltalk_response
        print(f"💬 Smalltalk question detected, using direct response")
        print(f"🔍 ROUTER OUTPUT: SMALLTALK -> '{smalltalk_response[:50]}...'")
        return state
    
    # Use LLM to classify intent for non-escalation requests
    intent = classify_intent(user_input)
    state["intent_classification"] = intent
    print(f"🔍 ROUTER CLASSIFICATION (signal): {intent}")
    
    # Classification is now advisory only - do not block on OFF_TOPIC
    # Let flow continue regardless of classification
    print(f"➡️ ROUTER NEXT: find_hint")
    
    # Extract keywords from current question
    current_keywords = extract_question_keywords(user_input)
    print(f"🔤 Current question keywords: {current_keywords}")
    
    # Check if it's a repeat/similar question using keyword matching with fallback
    last_keywords = state.get("last_question_keywords", set())
    last_question_id = state.get("last_question_id", "")
    
    # Count overlapping keywords
    keyword_overlap = len(current_keywords.intersection(last_keywords))
    print(f"🔤 Last question keywords: {last_keywords}")
    print(f"🔗 Keyword overlap: {keyword_overlap} words")
    
    # Escalate if: 2+ keywords match OR exact string match (fallback)
    if (keyword_overlap >= 2) or (user_input == last_question_id):
        state["hint_level"] = state.get("hint_level", 1) + 1
        if keyword_overlap >= 2:
            print(f"🔄 Escalating hint level to {state['hint_level']} (keyword similarity)")
        else:
            print(f"🔄 Escalating hint level to {state['hint_level']} (exact match fallback)")
    else:
        # New question - store both ID and keywords
        state["last_question_id"] = user_input
        state["last_question_keywords"] = current_keywords
        state["hint_level"] = 1
        print(f"🆕 New query, starting at hint level 1")
    
    print(f"🔍 ROUTER OUTPUT: GAME_RELATED -> continuing to hint flow (level {state['hint_level']})")
    return state
