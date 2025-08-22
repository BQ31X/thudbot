# Shared utilities for LangGraph nodes
# This file contains shared constants and utility functions used by multiple nodes

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import openai

# Canned responses for off-topic questions
OFF_TOPIC_RESPONSES = [
    "Listen sweetie, I'm Zelda - your personal digital assistant for *The Space Bar*. I only help with puzzles, locations, and characters from our little corner of the galaxy. Try asking about the game!",
    "Sorry hon, but I'm programmed specifically for *The Space Bar*. Ask me about the Thirsty Tentacle, alien suspects, or any puzzles you're stuck on.",
    "I appreciate the chat, but my circuits are dedicated to *The Space Bar* only. Need help finding something in the game? That's my specialty!"
]

# Progressive hints: patterns that indicate user wants escalated help
# These should be treated as GAME_RELATED if chat_history exists
VAGUE_ESCALATION_PATTERNS = [
    "i'm still stuck",
    "still stuck", 
    "still need help",
    "more help",
    "another hint",
    "different hint",
    "that didn't work",
    "tried that",
    "i tried that",
    "need more help",
    "can you help more",
    "give me more",
    "tell me more"
]

# Stop words to remove when extracting meaningful keywords for progressive hints
STOP_WORDS = {
    # Question words
    "how", "where", "what", "why", "when", "who", "which",
    # Common verbs and auxiliaries
    "do", "does", "did", "can", "can't", "could", "would", "should",
    "is", "are", "was", "were", "be", "been", "being",
    # Pronouns
    "i", "me", "my", "you", "your", "it", "that", "this", "they", "them",
    # Articles and prepositions
    "a", "an", "the", "in", "on", "at", "to", "from", "with", "of", "for",
    # Common words
    "please", "help", "still", "again", "and", "or", "but"
}

# TODO, maybe. 20250820.
# below template is used to classify if input is about The Space Bar game or off-topic. 
# it is working well but I am not sure if it is the best way to do this. 
# If it needs further refinement, we should consider removing the specific examples to avoid bloating the prompt.
# e.g. a simpler rule like: Simple rule like "GAME_RELATED if asking HOW/WHERE/WHO about specific things, OFF_TOPIC if vague or non-gaming"

def extract_question_keywords(user_input: str) -> set:
    """Extract meaningful keywords from user input, removing stop words
    
    Args:
        user_input: The user's input text
        
    Returns:
        Set of meaningful keywords (lowercase, no punctuation)
    """
    import re
    
    # Normalize text: lowercase, remove punctuation, split into words
    normalized = re.sub(r'[^\w\s]', '', user_input.lower())
    words = normalized.split()
    
    # Remove stop words and empty strings
    keywords = {word for word in words if word and word not in STOP_WORDS}
    
    return keywords

def is_vague_escalation_request(user_input: str) -> bool:
    """Check if user input matches vague escalation patterns (like 'I'm still stuck')
    
    Args:
        user_input: The user's input text
        
    Returns:
        True if input matches escalation patterns, False otherwise
    """
    input_lower = user_input.lower().strip()
    
    # Check if any escalation pattern is found in the input
    for pattern in VAGUE_ESCALATION_PATTERNS:
        if pattern in input_lower:
            return True
    
    return False

def classify_intent(user_input: str) -> str:
    """Use LLM to classify if input is about The Space Bar game or off-topic"""
    
    try:
        chat_model = ChatOpenAI(model="gpt-4.1-nano")  # testing with nano for now
    
        template = ChatPromptTemplate.from_template("""
        You are a classifier for The Space Bar adventure game. Determine if the user's input is:
        1. GAME_RELATED: Appears to be asking about a specific game element, action, or mechanic (give benefit of the doubt)
        2. OFF_TOPIC: Clearly not about gaming, OR too vague to be actionable

        GAME_RELATED (be permissive - let downstream systems handle if it's not actually in the game):
        - Any question asking HOW to do something specific
        - Any question asking WHERE something is
        - Any question asking about a specific item, character, location, or action
        - Game mechanics questions, even if unfamiliar
        - Questions about specific puzzles or challenges

        Examples of GAME_RELATED:
        - "How do I find the token?"
        - "How do I open the locker?" 
        - "How do I do empathy telepathy?"
        - "How do I start a flashback?"
        - "Where is the bus?"
        - "Who is Zelda?"
        - "How do I save the game?"
        - "What do I do in the Thirsty Tentacle?"
        - "How do I interact with objects?"

        Examples of OFF_TOPIC:
        - "What's the weather like?" (not about gaming)
        - "Tell me a joke" (not about gaming)
        - "How do I play Minecraft?" (different game)
        - "I'm stuck on this puzzle" (too vague - no specific element mentioned)
        - "How do I solve a puzzle?" (too vague - no specific element mentioned)  
        - "Help me with this" (too vague)
        - "What should I do?" (too vague)
        - "Hello, how are you?" (social, not gaming)

        User input: "{user_input}"
        
        Respond with exactly: GAME_RELATED or OFF_TOPIC
        """)
        
        response = chat_model.invoke(template.format(user_input=user_input))
        classification = response.content.strip()
        
        print(f"🤖 Intent classification: {classification}")
        return classification
        
    except (openai.AuthenticationError, openai.APIError) as e:
        print(f"🚨 OpenAI API error in intent classification: {type(e).__name__}")
        # Conservative fallback - assume it's game-related to avoid blocking legitimate questions
        print(f"🛡️ Using fallback classification: GAME_RELATED")
        return "GAME_RELATED"
        
    except Exception as e:
        print(f"🚨 Unexpected error in intent classification: {type(e).__name__}")
        # Conservative fallback - assume it's game-related
        print(f"🛡️ Using fallback classification: GAME_RELATED")
        return "GAME_RELATED"
