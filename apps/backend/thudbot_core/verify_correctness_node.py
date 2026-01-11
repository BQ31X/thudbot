"""
Verify that the retrieved hint content is correct, relevant, and supported by the retrieved context.

Responsibilities:
- Evaluates the candidate hint against retrieved source context for correctness and relevance.
- Performs verification across multiple dimensions (answer appropriateness, factual accuracy, contextual support).
- Produces a structured verification outcome and reason code for downstream routing.
- Acts as a routing gate between successful hint delivery and error or fallback paths.
- Does not modify the hint content itself.
- Does not perform retrieval or generate new hint material.

Reads from state:
- current_hint
- user_input
- retrieved_context

Writes to state:
- verification_passed (Boolean)
- verification_reason (String: VERIFIED, TOO_SPECIFIC, HALLUCINATED,
  INSUFFICIENT_CONTEXT, API_ERROR, VERIFICATION_ERROR)

Notes:
- Uses LLM (gpt-4o-mini) to verify hint content against retrieved context.
- Verification considers multiple dimensions: question-answer appropriateness,
  factual accuracy, and contextual relevance.
- On API or verification errors, sets verification_passed=False and continues
  execution (graceful degradation).
- This node is a critical control-flow point that determines success vs. error routing.
"""

from thudbot_core.state import LangGraphState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
import openai

@traceable(run_type="chain", name="verify_correctness_node")
def verify_correctness_node(state: LangGraphState) -> LangGraphState:
    """Verify if the hint is based on RAG data or hallucinated"""
    hint = state["current_hint"]
    user_input = state["user_input"]
    retrieved_context = state["retrieved_context"]
    
    print(f"🔍 VERIFY_CORRECTNESS INPUT: '{hint[:50]}...'")
    print(f"🔬 Checking if hint is factual vs hallucinated...")
    print(f"📄 Using cached context: {len(retrieved_context)} chars")
    
    try:
        # Use LLM to verify if the current hint aligns with retrieved context
        chat_model = ChatOpenAI(model="gpt-4o-mini")
        
        verification_template = ChatPromptTemplate.from_template("""
        You are a fact-checking system for a game hint system. Your job is to determine if a generated hint appropriately matches the user's question specificity and is based on reliable game data.

        USER QUESTION: {user_question}
        
        RETRIEVED GAME DATA:
        {context}
        
        GENERATED HINT TO VERIFY:
        {hint}
        
        CRITICAL VERIFICATION CHECKS:
        1. QUESTION-ANSWER APPROPRIATENESS:
           - If the user question is VAGUE (like "I'm stuck on this puzzle", "help me", "what should I do"), the hint should NOT provide specific puzzle solutions
           - Vague questions should get clarification requests, not specific answers about clocks, crystals, buttons, etc.
           - If user asks specifically about something (like "bus token", "Zelda", "save game"), specific answers are appropriate
        
        2. CONTENT ACCURACY:
           - Check if the hint's factual claims are supported by the retrieved context
           - Look for hallucinated details not present in the game data
        
        3. RELEVANCE:
           - Does the hint actually address what the user asked about?
           - Are there multiple different puzzles in the context but the hint assumes one specific puzzle?
        
        RESPOND WITH ONLY:
        - "VERIFIED" if the hint appropriately matches the question's specificity AND is factually supported by context
        - "TOO_SPECIFIC" if the user question was vague but the hint provides specific puzzle solutions
        - "HALLUCINATED" if the hint contains information not found in the context
        - "INSUFFICIENT_CONTEXT" if there isn't enough context data to answer the user's specific question
        
        Response:""")
        
        verification_prompt = verification_template.format(
            user_question=user_input,
            context=retrieved_context,
            hint=hint
        )
        
        verification_result = chat_model.invoke(verification_prompt)
        verdict = verification_result.content.strip().upper()
        
        print(f"🔬 Verification verdict: {verdict}")
        
        if verdict == "VERIFIED":
            print(f"✅ Hint verified as appropriate and factual")
            state["verification_passed"] = True
            return state
        else:
            print(f"❌ Hint failed verification: {verdict}")
            if verdict == "TOO_SPECIFIC":
                print(f"📋 Reason: User question was too vague for specific puzzle solution")
            elif verdict == "HALLUCINATED":
                print(f"📋 Reason: Hint contains information not in game data")
            elif verdict == "INSUFFICIENT_CONTEXT":
                print(f"📋 Reason: Not enough context to answer user's specific question")
            
            state["verification_passed"] = False
            state["verification_reason"] = verdict
            return state
            
    except (openai.AuthenticationError, openai.APIError) as e:
        print(f"⚠️  OpenAI API error during verification: {type(e).__name__}")
        # On API error, fail verification gracefully and continue to error generation
        state["verification_passed"] = False
        state["verification_reason"] = "API_ERROR"
        return state
        
    except Exception as e:
        print(f"⚠️  Verification failed due to unexpected error: {type(e).__name__}")
        # On other errors, assume verification failed for safety
        state["verification_passed"] = False
        state["verification_reason"] = "VERIFICATION_ERROR"
        return state
