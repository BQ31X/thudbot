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


def create_cached_openai_embeddings(
    model_name: str = "text-embedding-3-small",
    cache_dir: str = "./cache/embeddings"
):
    """
    Create cached OpenAI embeddings with a safe fallback to direct embeddings 
    if caching is unavailable.

    This implementation is intentionally stable and should not be modified
    without careful consideration, as it defines the canonical OpenAI
    embedding behavior for the project.
    
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


def get_embedding_function(
    provider: str,
    execution_mode: str,
    model_name: Optional[str] = None
):
    """
    Create embeddings with support for multiple providers.
    
    Args:
        provider: Embedding provider ("openai" or "local")
        execution_mode: Execution context - REQUIRED, must be "runtime" or "eval"
                        Controls whether local embeddings are allowed.
        model_name: Model name (if None, uses provider default)
        
    Returns:
        Configured embeddings object
        
    Provider Defaults:
        - openai: text-embedding-3-small (with caching at ./cache/embeddings)
        - local: BAAI/bge-small-en-v1.5 (handles own caching internally)
    
    Raises:
        RuntimeError: If provider="local" and execution_mode="runtime"
        ValueError: If execution_mode is not "runtime" or "eval"
    
    Notes:
        Local embeddings (provider="local") are ONLY supported in evaluation mode.
        This is an architectural invariant, not a missing dependency.
        
        If TEF shows local embeddings are viable for production, they must be
        accessed via a separate embedding service (e.g., provider="embedding-service"),
        not by loading models in-process.
    """
    # Validate execution_mode
    if execution_mode not in ["runtime", "eval"]:
        raise ValueError(
            f"execution_mode must be 'runtime' or 'eval', got: {execution_mode}"
        )
    if provider == "openai":
        model_name = model_name or "text-embedding-3-small"
        # Cache directory is OpenAI implementation detail
        cache_dir = "./cache/embeddings"
        return create_cached_openai_embeddings(
            model_name=model_name, 
            cache_dir=cache_dir
        )
        
    elif provider == "local":
        # Architectural guardrail: local embeddings are evaluation-only
        if execution_mode == "runtime":
            raise RuntimeError(
                "Local embeddings (provider='local') are not supported in backend runtime.\n"
                "\n"
                "This is an architectural invariant:\n"
                "  - Backend runtime must remain lightweight (no ML models in-process)\n"
                "  - Local embeddings are for evaluation only (TEF, build scripts)\n"
                "\n"
                "If TEF shows local embeddings are viable for production:\n"
                "  1. Deploy a separate embedding service container\n"
                "  2. Add a new provider (e.g., 'embedding-service')\n"
                "  3. Backend calls the service over HTTP\n"
                "\n"
                "The backend will never load models in-process."
            )
        
        # Evaluation mode: allow local embeddings
        model_name = model_name or "BAAI/bge-small-en-v1.5"
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError as e:
            raise RuntimeError(
                "Local embeddings require optional dependencies.\n"
                "Install with: uv sync --extra local-embeddings\n"
                "\n"
                "Note: This is only for evaluation/development (TEF, build scripts).\n"
                "Production backend uses OpenAI embeddings."
            ) from e
        return HuggingFaceEmbeddings(model_name=model_name)
        
    else:
        raise ValueError(f"Unknown provider: {provider}. Must be 'openai' or 'local'")


def embed_text(
    text: str,
    execution_mode: str,
    model_name: str = "text-embedding-3-small"
) -> List[float]:
    """
    Embed a single text string.
    
    Args:
        text: Text to embed
        execution_mode: Execution context ("runtime" or "eval") - REQUIRED
        model_name: OpenAI embedding model name
        
    Returns:
        Embedding vector as list of floats
    """
    embeddings = get_embedding_function(
        provider="openai",
        execution_mode=execution_mode,
        model_name=model_name
    )
    return embeddings.embed_query(text)


def embed_batch(
    texts: List[str],
    execution_mode: str,
    model_name: str = "text-embedding-3-small"
) -> List[List[float]]:
    """
    Embed a batch of text strings.
    
    Args:
        texts: List of texts to embed
        execution_mode: Execution context ("runtime" or "eval") - REQUIRED
        model_name: OpenAI embedding model name
        
    Returns:
        List of embedding vectors
    """
    embeddings = get_embedding_function(
        provider="openai",
        execution_mode=execution_mode,
        model_name=model_name
    )
    return embeddings.embed_documents(texts)
