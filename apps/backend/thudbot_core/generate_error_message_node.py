"""
Generate a player-facing error or clarification message when hint delivery fails.

Responsibilities:
- Produces a polite, user-facing message explaining why a hint could not be delivered.
- Tailors the message based on the verification outcome or failure reason.
- Applies character-consistent tone while preserving a non-informational response.
- Acts as the terminal node for verification or retrieval failure paths.
- Does not attempt hint retrieval, verification, or correction.

Reads from state:
- user_input
- verification_reason

Writes to state:
- formatted_output (error or clarification message string)

Notes:
- Uses LLM (gpt-4o-mini) to generate a polite clarification or retry prompt.
- Enforces the same character and IP guardrails as maintain_character_node.
- Implements tiered fallback behavior:
  - Guardrail violation → API error → ultimate fallback to a hardcoded message.
- Does not update chat history (unlike format_output_node).
- This node always leads to END.
"""
from thudbot_core.state import LangGraphState
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable
import openai

@traceable(run_type="chain", name="generate_error_message_node")
def generate_error_message_node(state: LangGraphState) -> LangGraphState:
    """Generate a polite error message asking for clarification when verification fails"""
    user_input = state["user_input"]
    verification_reason = state.get("verification_reason", "UNKNOWN")
    
    print(f"🔍 GENERATE_ERROR_MESSAGE INPUT: user='{user_input[:50]}...', reason='{verification_reason}'")
    print(f"❌ Generating error message for verification failure...")
    
    try:
        chat_model = ChatOpenAI(model="gpt-4o-mini")
        
        # Create error message template
        error_template = ChatPromptTemplate.from_template("""
        You are Zelda, the Personal Digital Assistant (PDA) in The Space Bar adventure game. 
        The user asked a question that passed the initial topic filter (it's game-related), 
        but the hint retrieval system couldn't find reliable information to answer it.
        
        CRITICAL GUARDRAILS:
        - NEVER mention "Legend of Zelda", "Link", "Hyrule", "princess", or any Nintendo references
        - You are an AI assistant in a sci-fi detective game, NOT royalty
        - Stay focused on The Space Bar game world: aliens, space stations, detective work
        - Your personality: smart, helpful, but with attitude and sass
        
        User's question: {user_question}
        Issue: The system couldn't find reliable game data to answer this question.
        
        Generate a helpful response that:
        1. Acknowledges their question is about The Space Bar game
        2. Politely explains you need more specific details
        3. Asks them to rephrase or provide more context
        4. Maintains your sassy PDA personality
        5. Suggests they be more specific about location, character, or puzzle
        
        Keep it concise and in character as Zelda the PDA:""")
        
        response = chat_model.invoke(error_template.format(user_question=user_input))
        
        # Guardrail check - scan for forbidden content
        forbidden_terms = ["legend of zelda", "hyrule", "princess", "nintendo", "triforce"]
        response_lower = response.content.lower()
        
        if any(term in response_lower for term in forbidden_terms):
            print(f"🚨 Guardrail triggered in error message! Using fallback...")
            # Use a safe fallback response
            fallback_response = f"Listen up, detective! I need more specific details about what you're trying to do in The Space Bar. Which location are you in? What puzzle are you stuck on? Give me something to work with here!"
            state["formatted_output"] = fallback_response
            print(f"🛡️ Using guardrail fallback for error message")
        else:
            state["formatted_output"] = response.content
            print(f"✅ Error message guardrail passed")
            
    except (openai.AuthenticationError, openai.APIError) as e:
        print(f"🚨 OpenAI API error in error message generation: {type(e).__name__}")
        # Use hardcoded fallback when API is unavailable
        fallback_response = f"Listen up, detective! I'm having some technical difficulties right now, but I still want to help you with The Space Bar. Can you be more specific about what you're trying to do? Which location are you in? What puzzle are you stuck on?"
        state["formatted_output"] = fallback_response
        print(f"🛡️ Using API error fallback for error message")
        
    except Exception as e:
        print(f"🚨 Unexpected error in error message generation: {type(e).__name__}")
        # Ultimate fallback for any other error
        fallback_response = f"I'm having trouble right now, but I want to help you with The Space Bar game. Please try asking about a specific puzzle, location, or character and I'll do my best to assist!"
        state["formatted_output"] = fallback_response
        print(f"🛡️ Using ultimate fallback for error message")
    
    print(f"❌ Error message: {state['formatted_output'][:100]}{'...' if len(state['formatted_output']) > 100 else ''}")
    print(f"🔍 GENERATE_ERROR_MESSAGE OUTPUT: formatted_output set")
    return state
