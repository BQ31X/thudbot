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
from langchain_community.vectorstores import Qdrant
from langchain_openai import ChatOpenAI
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from operator import itemgetter
import requests
import logging

# Import from shared rag_utils
from rag_utils.embedding_utils import get_embedding_function
from rag_utils.loader import load_qdrant_client

# Global components for RAG-only system
_multi_query_retrieval_chain = None

def initialize_rag_only(api_key=None):
    """Load existing Qdrant collection - fail fast if missing"""
    
    # Use provided API key or fall back to environment
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    
    # Verify API key is available
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OpenAI API key required - provide via parameter or environment variable")
    
    # Get Qdrant URL from config
    from thudbot_core.config import QDRANT_URL, QDRANT_COLLECTION
    
    print(f"🌐 Connecting to Qdrant at: {QDRANT_URL}")
    
    # Create client and check collection exists using rag_utils
    client = load_qdrant_client(QDRANT_URL)
    collection_name = QDRANT_COLLECTION
    
    # Fail fast if collection doesn't exist
    if not client.collection_exists(collection_name):
        raise RuntimeError(
            f"❌ Qdrant collection '{collection_name}' not found at {QDRANT_URL}\n"
            f"   Build the collection before starting:\n"
            f"   python tools/build_qdrant_collection.py --qdrant-url {QDRANT_URL} --collection-name {collection_name}"
        )
    
    print(f"✅ Found collection '{collection_name}' with existing data")
    
    # Load embeddings (used for query embedding only, not document embedding)
    embeddings = get_embedding_function(
        provider="openai",
        execution_mode="runtime",  # Backend runtime - only OpenAI allowed
        model_name="text-embedding-3-small"
    )
    
    # Load existing collection (NO CSV, NO document embedding)
    vectorstore = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings
    )
    
    print(f"✅ Vectorstore loaded successfully")
    
    # Create retrievers
    # increased from 4 to 5 to improve recall based on TEF evaluation Dec 19, 2025
    naive_retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) 
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

def get_direct_hint_with_context(question: str, hint_level: int = 1) -> dict:
    """Get hint with context from RAG chain for verification purposes
    
    Args:
        question: The user's question
        hint_level: Maximum hint level to retrieve (1=subtle, 2=moderate, 3=explicit)
                   Retrieves all hints from level 1 up to hint_level (cumulative)
    """
    global _multi_query_retrieval_chain
    
    # Initialize if needed
    if _multi_query_retrieval_chain is None:
        _multi_query_retrieval_chain = initialize_rag_only()  # Clean RAG-only init
    
    print(f"\n🎮 DIRECT_HINT_WITH_CONTEXT called with: '{question}' (max_level: {hint_level})")
    
    # PROGRESSIVE HINTS: Filter by hint level if possible
    # Get the underlying vectorstore for level-filtered retrieval
    try:
        # Create a level-filtered retriever that gets hints up to the specified level
        # This implements cumulative hint retrieval (levels 1 through hint_level)
        vectorstore = _multi_query_retrieval_chain.steps[0].steps[0].vectorstore if hasattr(_multi_query_retrieval_chain.steps[0].steps[0], 'vectorstore') else None
        
        if vectorstore and hasattr(vectorstore, 'as_retriever'):
            # Create retriever with hint level filter (graceful fallback if metadata missing)
            # increased from 4 to 5 to improve recall based on TEF evaluation Dec 19, 2025
            level_filter = {"hint_level": {"$lte": hint_level}}
            level_filtered_retriever = vectorstore.as_retriever(
                search_kwargs={"k": 5, "filter": level_filter} 
            )
            
            # Test if level filtering works by doing a quick search
            test_docs = level_filtered_retriever.get_relevant_documents(question)
            
            if test_docs:
                # Level filtering succeeded - use filtered retriever
                print(f"🎯 Using level-filtered retrieval (levels 1-{hint_level})")
                result = _multi_query_retrieval_chain.invoke({"question": question})
                # Note: For now, we'll use the standard chain but this sets up the architecture
                # TODO: Replace the retriever in the chain with level_filtered_retriever
            else:
                # No results with level filter - fall back to unfiltered search
                print(f"⚠️  No results with level filter, falling back to unfiltered search")
                result = _multi_query_retrieval_chain.invoke({"question": question})
        else:
            # Vectorstore not accessible - use standard retrieval
            print(f"ℹ️  Vectorstore not accessible, using standard retrieval")
            result = _multi_query_retrieval_chain.invoke({"question": question})
            
    except Exception as e:
        # Graceful fallback: if level filtering fails, use standard retrieval
        print(f"⚠️  Level filtering failed ({e}), falling back to standard retrieval")
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
    
    # Enhanced logging: show which documents were retrieved
    if isinstance(context, list):
        for i, doc in enumerate(context):
            source = doc.metadata.get('source', 'unknown')
            doc_type = doc.metadata.get('document_type', 'csv')
            chunk_idx = doc.metadata.get('chunk_index', '')
            
            if doc_type == 'sequential':
                print(f"   [{i+1}] {source} (chunk {chunk_idx})")
            else:
                # CSV hints - show first 50 chars of content for context
                preview = doc.page_content[:50].replace('\n', ' ')
                print(f"   [{i+1}] CSV: \"{preview}...\"")
    
    return {
        "response": response,
        "context": context_text
    }