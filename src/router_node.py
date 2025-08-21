from state import LangGraphState
from langsmith import traceable
from langgraph_flow import classify_intent, OFF_TOPIC_RESPONSES, is_vague_escalation_request, extract_question_keywords

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
        
        # Keep the existing last_question_id (don't update it)
        # Just escalate the hint level
        state["hint_level"] = state.get("hint_level", 1) + 1
        print(f"🔄 Escalating hint level to {state['hint_level']} for previous question")
        print(f"🔍 ROUTER OUTPUT: VAGUE_ESCALATION -> continuing to hint flow (level {state['hint_level']})")
        return state
    
    # Use LLM to classify intent for non-escalation requests
    intent = classify_intent(user_input)
    print(f"🔍 ROUTER CLASSIFICATION: {intent}")
    
    if intent == "OFF_TOPIC":
        # Use a canned response instead of calling character maintenance
        import random
        canned_response = random.choice(OFF_TOPIC_RESPONSES)
        state["formatted_output"] = canned_response
        print(f"🚫 Off-topic question detected, using canned response")
        print(f"🔍 ROUTER OUTPUT: OFF_TOPIC -> '{canned_response[:50]}...'")
        return state
    
    # This is a game-related question, proceed with hint logic
    print(f"✅ Game-related question detected")
    
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
