from state import LangGraphState

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
