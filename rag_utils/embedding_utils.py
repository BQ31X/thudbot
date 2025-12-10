"""
Shared embedding utilities for Thudbot RAG system.

Provides cached OpenAI embeddings with fallback strategy.
Used by both build scripts and runtime code.

DO NOT import from apps.backend, thudbot_core, or tools.
"""
import logging
import hashlib
from typing import List, Optional

from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore


def get_embedding_function(
    model_name: str = "text-embedding-3-small",
    cache_dir: str = "./cache/embeddings"
):
    """
    Create cached embeddings with fallback to non-cached if caching fails.
    
    Based on HW16 pattern with production-ready fallback strategy.
    
    Args:
        model_name: OpenAI embedding model name
        cache_dir: Directory for embedding cache
        
    Returns:
        Configured embeddings object (cached or direct)
    """
    try:
        # Create base embeddings
        base_embeddings = OpenAIEmbeddings(model=model_name)
        
        # Create safe namespace from model name
        safe_namespace = hashlib.md5(model_name.encode()).hexdigest()
        
        # Set up file store and cached embeddings
        store = LocalFileStore(cache_dir)
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
            base_embeddings, 
            store, 
            namespace=safe_namespace,
            key_encoder="sha256"
        )
        
        logging.info(f"✅ Cached embeddings initialized with cache dir: {cache_dir}")
        return cached_embeddings
        
    except (PermissionError, OSError, IOError) as e:
        logging.warning(f"Cache unavailable, falling back to direct embeddings: {e}")
        return OpenAIEmbeddings(model=model_name)
    except Exception as e:
        logging.warning(f"Unexpected caching error, falling back to direct embeddings: {e}")
        return OpenAIEmbeddings(model=model_name)


def embed_text(text: str, model_name: str = "text-embedding-3-small") -> List[float]:
    """
    Embed a single text string.
    
    Args:
        text: Text to embed
        model_name: OpenAI embedding model name
        
    Returns:
        Embedding vector as list of floats
    """
    embeddings = get_embedding_function(model_name)
    return embeddings.embed_query(text)


def embed_batch(
    texts: List[str],
    model_name: str = "text-embedding-3-small"
) -> List[List[float]]:
    """
    Embed a batch of text strings.
    
    Args:
        texts: List of texts to embed
        model_name: OpenAI embedding model name
        
    Returns:
        List of embedding vectors
    """
    embeddings = get_embedding_function(model_name)
    return embeddings.embed_documents(texts)
