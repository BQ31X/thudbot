from state import LangGraphState
from agent import get_thud_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable

# Canned responses for off-topic questions
OFF_TOPIC_RESPONSES = [
    "Listen sweetie, I'm Zelda - your personal digital assistant for *The Space Bar*. I only help with puzzles, locations, and characters from our little corner of the galaxy. Try asking about the game!",
    "Sorry hon, but I'm programmed specifically for *The Space Bar* mysteries. Ask me about the Thirsty Tentacle, alien suspects, or any puzzles you're stuck on.",
    "I appreciate the chat, but my circuits are dedicated to *The Space Bar* only. Need help finding something in the game? That's my specialty!"
]

def classify_intent(user_input: str) -> str:
    """Use LLM to classify if input is about The Space Bar game or off-topic"""
    
    chat_model = ChatOpenAI(model="gpt-4o-mini")  # Using mini instead of nano for now
    
    template = ChatPromptTemplate.from_template("""
    You are a classifier for The Space Bar adventure game. Determine if the user's input is:
    1. GAME_RELATED: About The Space Bar game (puzzles, characters, locations, mechanics, story, walkthrough help)
    2. OFF_TOPIC: About anything else (weather, general conversation, other games, etc.)

    Examples of GAME_RELATED:
    - "How do I find the token?"
    - "Where is the bus?" 
    - "I'm stuck on this puzzle"
    - "Who is Zelda?"
    - "How do I save the game?"
    - "What do I do in the Thirsty Tentacle?"
    - "How do I interact with objects?"
    - "I need help with the alien suspects"

    Examples of OFF_TOPIC:
    - "What's the weather like?"
    - "Tell me a joke"
    - "How do I play Minecraft?"
    - "What's 2+2?"
    - "Hello, how are you?"

    User input: "{user_input}"
    
    Respond with exactly: GAME_RELATED or OFF_TOPIC
    """)
    
    response = chat_model.invoke(template.format(user_input=user_input))
    classification = response.content.strip()
    
    print(f"🤖 Intent classification: {classification}")
    return classification

# Node functions for LangGraph
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

@traceable(run_type="chain", name="find_hint_node")  
def find_hint_node(state: LangGraphState) -> LangGraphState:
    """Find hint using the existing thud agent"""
    user_input = state["user_input"]
    hint_level = state.get("hint_level", 1)
    
    print(f"🔍 FIND_HINT INPUT: '{user_input}' (level {hint_level})")
    print(f"🎮 Finding hint for: {user_input}")
    agent = get_thud_agent()
    hint = agent.run(user_input)
    
    state["current_hint"] = hint
    print(f"📝 Retrieved hint: {hint[:100]}{'...' if len(hint) > 100 else ''}")
    print(f"🔍 FIND_HINT OUTPUT: '{hint[:50]}...' -> current_hint updated")
    return state

def verify_correctness_node(state: LangGraphState) -> LangGraphState:
    """Stub verification - just pass through for now"""
    hint = state["current_hint"]
    print(f"✅ Verifying hint (stub - passing through)")
    # For now, just pass through
    return state

@traceable(run_type="chain", name="maintain_character_node")
def maintain_character_node(state: LangGraphState) -> LangGraphState:
    """Rewrite hint in Zelda's voice with guardrails"""
    hint = state["current_hint"]
    
    print(f"🔍 MAINTAIN_CHARACTER INPUT: '{hint[:50]}...'")
    print(f"🎭 Rewriting in Zelda's voice...")
    chat_model = ChatOpenAI(model="gpt-4o-mini")
    template = ChatPromptTemplate.from_template("""
    You are Zelda, the Personal Digital Assistant (PDA) in The Space Bar adventure game by Boffo Games. 
    You are NOT the princess from Legend of Zelda - you are a sassy AI assistant helping detective Alias Node.
    
    CRITICAL GUARDRAILS:
    - NEVER mention "Legend of Zelda", "Link", "Hyrule", "princess", or any Nintendo references
    - You are an AI assistant in a sci-fi detective game, NOT royalty
    - Stay focused on The Space Bar game world: aliens, space stations, detective work
    - Your personality: smart, helpful, but with attitude and sass
    
    Context: You're helping with puzzles in The Space Bar, a cult classic sci-fi adventure game.
    
    Original hint: {hint}
    
    Rewrite this in YOUR voice as Zelda the PDA assistant (be helpful but sassy):""")
    
    response = chat_model.invoke(template.format(hint=hint))
    
    # Guardrail check - scan for forbidden content
    forbidden_terms = ["legend of zelda", "hyrule", "princess", "nintendo", "triforce"]
    response_lower = response.content.lower()
    
    if any(term in response_lower for term in forbidden_terms):
        print(f"🚨 Guardrail triggered! Regenerating response...")
        # Use a fallback response that's safe
        fallback_response = f"Listen up, space detective! {hint.split('.')[0]}. Now quit bothering me and get back to solving this mystery!"
        state["current_hint"] = fallback_response
        print(f"🛡️ Using guardrail fallback response")
    else:
        state["current_hint"] = response.content
        print(f"✅ Guardrail passed - response is clean")
    
    print(f"✨ Zelda's version: {state['current_hint'][:100]}{'...' if len(state['current_hint']) > 100 else ''}")
    print(f"🔍 MAINTAIN_CHARACTER OUTPUT: '{state['current_hint'][:50]}...' -> current_hint updated")
    return state

def format_output_node(state: LangGraphState) -> LangGraphState:
    """Format the final output"""
    hint = state["current_hint"]
    hint_level = state.get("hint_level", 1)
    
    print(f"🔍 FORMAT_OUTPUT INPUT: hint='{hint[:50]}...', level={hint_level}")
    formatted = f"🎯 Hint (Level {hint_level}): {hint}"
    state["formatted_output"] = formatted
    print(f"📋 Formatted output ready")
    print(f"🔍 FORMAT_OUTPUT OUTPUT: '{formatted[:50]}...' -> formatted_output set")
    return state
