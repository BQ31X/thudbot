"""
Thin wrapper around rag_utils for vector retrieval.

This module provides a simple interface for query retrieval,
delegating all Qdrant interaction to rag_utils.loader.
"""
from typing import List, Dict, Any

# Import from shared rag_utils (copied into container during build)
from rag_utils.loader import load_qdrant_client
from rag_utils.embedding_utils import get_embedding_function

from .config import QDRANT_URL, QDRANT_COLLECTION, EMBEDDING_PROVIDER, EMBEDDING_MODEL


class RetrieverClient:
    """Thin wrapper for Qdrant retrieval operations."""
    
    def __init__(self):
        """Initialize client and verify collection exists."""
        self.qdrant_url = QDRANT_URL
        self.collection_name = QDRANT_COLLECTION
        
        # Use rag_utils to load client
        self.client = load_qdrant_client(self.qdrant_url)
        
        # Verify collection exists (fail fast)
        if not self.client.collection_exists(self.collection_name):
            raise RuntimeError(
                f"Collection '{self.collection_name}' not found at {self.qdrant_url}"
            )
        
        # Initialize embeddings function (for query embedding only)
        self.embeddings = get_embedding_function(
            provider=EMBEDDING_PROVIDER,
            execution_mode="retrieval-service",
            model_name=EMBEDDING_MODEL
        )
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k documents for a query.
        
        Args:
            query: User's query text
            k: Number of results to return
            
        Returns:
            List of documents with text, metadata, and scores
        """
        # Embed the query
        query_vector = self.embeddings.embed_query(query)
        
        # Search Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k
        )
        
        # Format results
        results = []
        for hit in search_results:
            results.append({
                "chunk_id": hit.id,
                "text": hit.payload.get("page_content", ""),
                "metadata": hit.payload.get("metadata", {}),
                "score": hit.score
            })
        
        return results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection metadata for introspection."""
        collection_info = self.client.get_collection(self.collection_name)
        
        return {
            "collection_name": self.collection_name,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status,
            "config": {
                "vector_size": collection_info.config.params.vectors.size
            }
        }

