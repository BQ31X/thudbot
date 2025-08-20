from state import LangGraphState
from langsmith import traceable
from langgraph_flow import classify_intent, OFF_TOPIC_RESPONSES

@traceable(run_type="chain", name="router_node")
def router_node(state: LangGraphState) -> LangGraphState:
    """Router node to determine if this is a Space Bar game question and if it's a repeat"""
    user_input = state["user_input"]
    print(f"🔍 ROUTER INPUT: '{user_input}'")
    
    # Use LLM to classify intent
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
    
    # Check if it's a repeat of the last question
    if user_input == state.get("last_question_id", ""):
        state["hint_level"] = state.get("hint_level", 1) + 1
        print(f"🔄 Escalating hint level to {state['hint_level']}")
    else:
        state["last_question_id"] = user_input
        state["hint_level"] = 1
        print(f"🆕 New query, starting at hint level 1")
    
    print(f"🔍 ROUTER OUTPUT: GAME_RELATED -> continuing to hint flow (level {state['hint_level']})")
    return state
