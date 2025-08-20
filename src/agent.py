"""
Thudbot Agent - Converted from notebook
"""
import os

# Load environment variables (optional - for local development)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env", override=True)
except ImportError:
    # python-dotenv not installed - that's fine, use system environment
    pass

# Core imports
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from operator import itemgetter
import requests

# Initialize global components
def initialize_thudbot(api_key=None):
    """Initialize the Thudbot agent with RAG and tools"""
    
    # Use provided API key or fall back to environment
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    
    # Verify API key is available
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OpenAI API key required - provide via parameter or environment variable")
    
    # Load hint data
    loader = CSVLoader(
        file_path="./data/Thudbot_Hint_Data_1.csv",
            metadata_columns=[
        "question", "hint_level", "character", "speaker",
        "narrative_context", "planet", "location", "category",
        "puzzle_id", "response_must_mention", "response_must_not_mention"
    ]
    )
    hint_data = loader.load()
    
    # Create vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Qdrant.from_documents(
        documents=hint_data,
        embedding=embeddings,
        location=":memory:",
        collection_name="Thudbot_Hints"
    )
    
    # Create retrievers
    naive_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    chat_model = ChatOpenAI(model="gpt-4.1-nano")
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=naive_retriever, llm=chat_model
    )
    
    # Thud prompt template
    THUD_TEMPLATE = """\
You are Thud, a friendly and somewhat simple-minded patron at The Thirsty Tentacle. 

You're trying your best to help the player navigate the game "The Space Bar."

Use the clues and context provided below to offer a gentle hint — not a full solution.

If you're not sure what to say, admit it honestly or say something silly — like talk about the weather or suggest looking around more.

If the player's question is clearly outside the game's scope (e.g., about real-world topics), 
you may consult the get_weather tool to offer a friendly distraction.

Player's question:
{question}

Context:
{context}

Your hint:"""
    
    rag_prompt = ChatPromptTemplate.from_template(THUD_TEMPLATE)
    
    # Create RAG chain
    multi_query_retrieval_chain = (
        {"context": itemgetter("question") | multi_query_retriever, "question": itemgetter("question")}
        | RunnablePassthrough.assign(context=itemgetter("context"))
        | {"response": rag_prompt | chat_model, "context": itemgetter("context")}
    ).with_config({"run_name": "multi_query_chain"})
    
    # Define tools
    @tool
    def hint_lookup(question: str) -> str:
        """Get Thud's advice about game puzzles and locations."""
        print(f"\n🎮 HINT_LOOKUP called with: '{question}'")
        result = multi_query_retrieval_chain.invoke({"question": question})
        response = result["response"].content
        print(f"📝 RAG Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        print(f"✅ Returning RAG response directly")
        return response
    
    @tool
    def get_weather(city: str) -> str:
        """Gets the current weather for a given city using the OpenWeatherMap API."""
        print(f"\n🌤️ GET_WEATHER called with: '{city}'")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            response = f"🌤️ I'd love to tell you about the weather in {city}, but I need a weather API key! Ask your developer to add OPENWEATHER_API_KEY to the .env file, or just enjoy the game hints instead! 🎮"
            print(f"❌ No API key - returning: {response[:50]}...")
            return response

        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&units=imperial&appid={api_key}"
            )
            response = requests.get(url)
            data = response.json()

            if response.status_code != 200 or "weather" not in data:
                return f"Couldn't get weather for {city} right now."

            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            response = f"It's currently {weather}, around {temp:.0f}°F in {city}."
            print(f"✅ Weather API success: {response}")
            return response
        
        except Exception as e:
            error_msg = f"Weather system error: {e}"
            print(f"❌ Weather API error: {error_msg}")
            return error_msg
    
    # Create agent
    tools = [hint_lookup, get_weather]
    thud_agent = initialize_agent(
        tools=tools,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        llm=chat_model,
        verbose=True,
        handle_parsing_errors=True  # Gracefully handle LLM output parsing errors
    )
    
    # Store components globally for direct access
    global _multi_query_retrieval_chain
    _multi_query_retrieval_chain = multi_query_retrieval_chain
    
    return thud_agent

# Global components
_thud_agent = None
_multi_query_retrieval_chain = None

def initialize_rag_only(api_key=None):
    """Initialize only the RAG components without AgentExecutor"""
    
    # Use provided API key or fall back to environment
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    
    # Verify API key is available
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OpenAI API key required - provide via parameter or environment variable")
    
    # Load hint data
    loader = CSVLoader(
        file_path="./data/Thudbot_Hint_Data_1.csv",
        metadata_columns=[
            "question", "hint_level", "character", "speaker",
            "narrative_context", "planet", "location", "category",
            "puzzle_id", "response_must_mention", "response_must_not_mention"
        ]
    )
    hint_data = loader.load()
    
    # Create vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Qdrant.from_documents(
        documents=hint_data,
        embedding=embeddings,
        location=":memory:",
        collection_name="Thudbot_Hints"
    )
    
    # Create retrievers
    naive_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    chat_model = ChatOpenAI(model="gpt-4.1-nano")
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=naive_retriever, llm=chat_model
    )
    
    # Thud prompt template (still used in RAG chain for now)
    THUD_TEMPLATE = """\
You are Thud, a friendly and somewhat simple-minded patron at The Thirsty Tentacle. 

You're trying your best to help the player navigate the game "The Space Bar."

Use the clues and context provided below to offer a gentle hint — not a full solution.

If you're not sure what to say, admit it honestly or say something silly — like talk about the weather or suggest looking around more.

If the player's question is clearly outside the game's scope (e.g., about real-world topics), 
you may consult the get_weather tool to offer a friendly distraction.

Player's question:
{question}

Context:
{context}

Your hint:"""
    
    rag_prompt = ChatPromptTemplate.from_template(THUD_TEMPLATE)
    
    # Create RAG chain
    multi_query_retrieval_chain = (
        {"context": itemgetter("question") | multi_query_retriever, "question": itemgetter("question")}
        | RunnablePassthrough.assign(context=itemgetter("context"))
        | {"response": rag_prompt | chat_model, "context": itemgetter("context")}
    ).with_config({"run_name": "multi_query_chain"})
    
    return multi_query_retrieval_chain

def get_thud_agent(api_key=None):
    """Get or create the Thudbot agent with optional API key"""
    global _thud_agent
    
    # If no agent exists, create one with provided API key
    if _thud_agent is None:
        if api_key or os.getenv('OPENAI_API_KEY'):
            _thud_agent = initialize_thudbot(api_key)
        else:
            raise ValueError("OpenAI API key required for first-time agent initialization")
    
    return _thud_agent

def get_direct_hint(question: str) -> str:
    """Get hint directly from RAG chain without Agent Executor wrapper"""
    global _multi_query_retrieval_chain
    
    # Initialize if needed
    if _multi_query_retrieval_chain is None:
        _multi_query_retrieval_chain = initialize_rag_only()  # Clean RAG-only init
    
    print(f"\n🎮 DIRECT_HINT called with: '{question}'")
    result = _multi_query_retrieval_chain.invoke({"question": question})
    response = result["response"].content
    print(f"📝 RAG Response: {response[:100]}{'...' if len(response) > 100 else ''}")
    print(f"✅ Returning RAG response directly (no Agent Executor)")
    return response