"""
Runtime utilities for loading existing Qdrant collections.

Provides collection loading for runtime retrieval.
Used ONLY by runtime code, never embeds documents.

DO NOT import from apps.backend, thudbot_core, or tools.
"""
from typing import Optional, Dict, Any

from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant


def load_qdrant_client(qdrant_url: str) -> QdrantClient:
    """
    Load Qdrant client connected to server.
    
    Args:
        qdrant_url: Qdrant server URL (e.g., "http://localhost:6333")
        
    Returns:
        QdrantClient instance
    """
    return QdrantClient(url=qdrant_url)


def load_retriever(
    qdrant_url: str,
    collection_name: str,
    embeddings,
    search_kwargs: Optional[Dict[str, Any]] = None
):
    """
    Load a retriever from an existing Qdrant collection.
    
    Args:
        qdrant_url: Qdrant server URL (e.g., "http://localhost:6333")
        collection_name: Name of the collection to load
        embeddings: Embeddings function (for query embedding only)
        search_kwargs: Optional search parameters (e.g., {"k": 4})
        
    Returns:
        Retriever instance
    """
    if search_kwargs is None:
        search_kwargs = {"k": 4}
    
    # Load client and verify collection exists
    client = load_qdrant_client(qdrant_url)
    
    if not client.collection_exists(collection_name):
        raise RuntimeError(
            f"Collection '{collection_name}' not found at {qdrant_url}"
        )
    
    # Load vectorstore
    vectorstore = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings
    )
    
    # Return retriever
    return vectorstore.as_retriever(search_kwargs=search_kwargs)
