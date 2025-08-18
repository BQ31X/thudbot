from state import LangGraphState
from agent import get_thud_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Node functions for LangGraph
def router_node(state: LangGraphState) -> LangGraphState:
    """Router node to determine if this is a hint request and if it's a repeat"""
    user_input = state["user_input"]
    
    # Simple logic to determine if the input is a hint request
    is_hint_request = 'hint' in user_input.lower()
    
    if not is_hint_request:
        state["formatted_output"] = "I can only help with game hints. Try asking for a hint!"
        return state
    
    # Check if it's a repeat of the last question
    if user_input == state.get("last_question_id", ""):
        state["hint_level"] = state.get("hint_level", 1) + 1
        print(f"🔄 Escalating hint level to {state['hint_level']}")
    else:
        state["last_question_id"] = user_input
        state["hint_level"] = 1
        print(f"🆕 New query, starting at hint level 1")
    
    return state

def find_hint_node(state: LangGraphState) -> LangGraphState:
    """Find hint using the existing thud agent"""
    user_input = state["user_input"]
    
    print(f"🎮 Finding hint for: {user_input}")
    agent = get_thud_agent()
    hint = agent.run(user_input)
    
    state["current_hint"] = hint
    print(f"📝 Retrieved hint: {hint[:100]}{'...' if len(hint) > 100 else ''}")
    return state

def verify_correctness_node(state: LangGraphState) -> LangGraphState:
    """Stub verification - just pass through for now"""
    hint = state["current_hint"]
    print(f"✅ Verifying hint (stub - passing through)")
    # For now, just pass through
    return state

def maintain_character_node(state: LangGraphState) -> LangGraphState:
    """Rewrite hint in Zelda's voice"""
    hint = state["current_hint"]
    
    print(f"🎭 Rewriting in Zelda's voice...")
    chat_model = ChatOpenAI(model="gpt-4o-mini")
    template = ChatPromptTemplate.from_template("""
    You are Zelda, a smart but irreverent secretary in The Space Bar game. 
    Rewrite this hint in your characteristic voice - be helpful but with a bit of sass.
    
    Original hint: {hint}
    
    Zelda's version:""")
    
    response = chat_model.invoke(template.format(hint=hint))
    state["current_hint"] = response.content
    print(f"✨ Zelda's version: {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
    return state

def format_output_node(state: LangGraphState) -> LangGraphState:
    """Format the final output"""
    hint = state["current_hint"]
    hint_level = state.get("hint_level", 1)
    
    formatted = f"🎯 Hint (Level {hint_level}): {hint}"
    state["formatted_output"] = formatted
    print(f"📋 Formatted output ready")
    return state
