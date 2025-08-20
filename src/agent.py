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

# Caching imports
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
import hashlib
import logging

# Global components for RAG-only system
_multi_query_retrieval_chain = None

def create_cached_embeddings(model="text-embedding-3-small", cache_dir="./cache/embeddings"):
    """Create cached embeddings with fallback to non-cached if caching fails.
    
    Based on HW16 pattern with production-ready fallback strategy.
    """
    try:
        # Create base embeddings
        base_embeddings = OpenAIEmbeddings(model=model)
        
        # Create safe namespace from model name
        safe_namespace = hashlib.md5(model.encode()).hexdigest()
        
        # Set up file store and cached embeddings
        store = LocalFileStore(cache_dir)
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
            base_embeddings, 
            store, 
            namespace=safe_namespace,
            key_encoder="sha256"
        )
        
        print(f"✅ Cached embeddings initialized with cache dir: {cache_dir}")
        return cached_embeddings
        
    except (PermissionError, OSError, IOError) as e:
        logging.warning(f"Cache unavailable, falling back to direct embeddings: {e}")
        print(f"⚠️  Cache failed, using direct embeddings: {e}")
        return OpenAIEmbeddings(model=model)
    except Exception as e:
        logging.warning(f"Unexpected caching error, falling back to direct embeddings: {e}")
        print(f"⚠️  Unexpected cache error, using direct embeddings: {e}")
        return OpenAIEmbeddings(model=model)

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
    
    # Create vector store with cached embeddings
    embeddings = create_cached_embeddings(model="text-embedding-3-small")
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
    
    # Fact-only RAG template (personality added downstream by maintain_character_node)
    RAG_TEMPLATE = """\
You are a knowledge retrieval system for The Space Bar adventure game. Your job is to extract and return only factual information from the provided context.

CRITICAL INSTRUCTIONS:
- Use ONLY the information provided in the context below
- Do NOT add creative suggestions, general advice, or made-up details  
- Do NOT inject personality, character voice, or creative interpretations
- Answer the question using the provided facts, even if terminology differs slightly (e.g., "token" vs "bus token")
- Look for semantically relevant information that addresses the player's intent
- For location questions ("where is X"), look for any mention of X's location or placement in the context
- For very general questions like "I'm stuck on this puzzle" without specific context, respond with: "Please provide more specific details about which puzzle or location you're having trouble with."
- If the context truly contains no relevant information, respond with: "The provided information doesn't contain enough details to answer this question."
- Return the relevant fact(s) from the context as directly as possible

Player's question:
{question}

Context from game data:
{context}

Factual response:"""
    
    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
    
    # Create RAG chain
    multi_query_retrieval_chain = (
        {"context": itemgetter("question") | multi_query_retriever, "question": itemgetter("question")}
        | RunnablePassthrough.assign(context=itemgetter("context"))
        | {"response": rag_prompt | chat_model, "context": itemgetter("context")}
    ).with_config({"run_name": "multi_query_chain"})
    
    return multi_query_retrieval_chain



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

def get_direct_hint_with_context(question: str) -> dict:
    """Get hint with context from RAG chain for verification purposes"""
    global _multi_query_retrieval_chain
    
    # Initialize if needed
    if _multi_query_retrieval_chain is None:
        _multi_query_retrieval_chain = initialize_rag_only()  # Clean RAG-only init
    
    print(f"\n🎮 DIRECT_HINT_WITH_CONTEXT called with: '{question}'")
    result = _multi_query_retrieval_chain.invoke({"question": question})
    
    # Extract response and context
    response = result["response"].content
    context = result["context"]  # This contains the retrieved documents
    
    # Format context for verification
    if isinstance(context, list):
        # Convert document objects to text
        context_text = "\n\n".join([
            f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(context)
        ])
    else:
        context_text = str(context)
    
    print(f"📝 RAG Response: {response[:100]}{'...' if len(response) > 100 else ''}")
    print(f"📄 Context docs: {len(context) if isinstance(context, list) else '1'}")
    
    return {
        "response": response,
        "context": context_text
    }