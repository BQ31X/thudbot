# Shared utilities for LangGraph nodes
# This file contains shared constants and utility functions used by multiple nodes

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

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
