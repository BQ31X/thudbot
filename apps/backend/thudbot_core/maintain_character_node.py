from thudbot_core.state import LangGraphState
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable
import openai

@traceable(run_type="chain", name="maintain_character_node")
def maintain_character_node(state: LangGraphState) -> LangGraphState:
    """Rewrite hint in Zelda's voice with guardrails"""
    hint = state["current_hint"]
    
    print(f"🔍 MAINTAIN_CHARACTER INPUT: '{hint[:50]}...'")
    print(f"🎭 Rewriting in Zelda's voice...")
    
    try:
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
            
    except (openai.AuthenticationError, openai.APIError) as e:
        print(f"🚨 OpenAI API error in character maintenance: {type(e).__name__}")
        # Use the original hint with minimal Zelda flair as fallback
        fallback_response = f"Listen up, space detective! {hint} Now get back to solving this mystery!"
        state["current_hint"] = fallback_response
        print(f"🛡️ Using API error fallback for character maintenance")
        
    except Exception as e:
        print(f"🚨 Unexpected error in character maintenance: {type(e).__name__}")
        # Use the original hint as ultimate fallback
        state["current_hint"] = hint
        print(f"🛡️ Using original hint as ultimate fallback")
    
    print(f"✨ Zelda's version: {state['current_hint'][:100]}{'...' if len(state['current_hint']) > 100 else ''}")
    print(f"🔍 MAINTAIN_CHARACTER OUTPUT: '{state['current_hint'][:50]}...' -> current_hint updated")
    return state
