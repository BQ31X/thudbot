"""
FastAPI application for Retrieval Service.

Provides HTTP endpoints for vector retrieval operations.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging

from .retriever import RetrieverClient
from .config import QDRANT_URL, QDRANT_COLLECTION, EMBEDDING_PROVIDER, EMBEDDING_MODEL, DEFAULT_K

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Thudbot Retrieval Service",
    description="Stateless API for vector retrieval from Qdrant",
    version="0.1.0"
)

# Initialize retriever (singleton)
retriever_client = None


@app.on_event("startup")
async def startup_event():
    """Initialize retriever on startup."""
    global retriever_client
    try:
        logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
        retriever_client = RetrieverClient()
        logger.info(f"Successfully connected to collection '{QDRANT_COLLECTION}'")
    except Exception as e:
        logger.error(f"Failed to initialize retriever: {e}")
        raise


# Request/Response models
class RetrieveRequest(BaseModel):
    """Request model for /retrieve endpoint."""
    query: str = Field(..., description="User's query text")
    k: int = Field(DEFAULT_K, description="Number of results to return", ge=1, le=20)


class RetrieveResult(BaseModel):
    """Single retrieval result."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk content")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    score: float = Field(..., description="Similarity score")


class RetrieveResponse(BaseModel):
    """Response model for /retrieve endpoint."""
    query: str = Field(..., description="Original query")
    k: int = Field(..., description="Number of results requested")
    results: List[RetrieveResult] = Field(..., description="Retrieved documents")


# Endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status.
    This endpoint is intentionally minimal (liveness only).
    Embedding config and Qdrant wiring were removed on purpose.
    If needed later:
      - add provider/model to /meta (human introspection)
      - keep topology (URLs) out of /health
    """
    if retriever_client is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized")
    
    return {
        "status": "ok",
        "service": "retrieval",
        "version": "0.1.0"
    }


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    """
    Retrieve top-k documents for a query.
    
    Embeds the query and searches Qdrant collection.
    Returns documents with text, metadata, and similarity scores.
    """
    if retriever_client is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized")
    
    # Validate query is not empty or whitespace-only
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty or whitespace-only"
        )
    
    try:
        logger.info(f"Retrieving k={request.k} documents")
        
        results = retriever_client.retrieve(
            query=request.query,
            k=request.k
        )
        
        logger.info(f"Retrieved {len(results)} documents")
        
        return RetrieveResponse(
            query=request.query,
            k=request.k,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(e)}"
        )


@app.get("/meta")
async def get_metadata():
    """
    Get collection metadata.
    
    Returns collection information for debugging and validation.
    """
    if retriever_client is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized")
    
    try:
        info = retriever_client.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Failed to get collection metadata: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metadata: {str(e)}"
        )

