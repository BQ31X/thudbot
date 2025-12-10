"""
Build-time utilities for RAG document processing.

Provides CSV loading and Qdrant collection creation.
Used ONLY by build scripts, never by runtime code.

DO NOT import from apps.backend, thudbot_core, or tools.
"""
from typing import List
from pathlib import Path

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Qdrant


def load_csv_documents(
    csv_path: str,
    metadata_columns: List[str]
):
    """
    Load documents from CSV file with metadata columns.
    
    Args:
        csv_path: Path to CSV file
        metadata_columns: List of column names to extract as metadata
        
    Returns:
        List of Document objects
    """
    loader = CSVLoader(
        file_path=csv_path,
        metadata_columns=metadata_columns
    )
    return loader.load()


def upsert_documents_to_collection(
    qdrant_path: str,
    collection_name: str,
    documents: List,
    embeddings
):
    """
    Create or update Qdrant collection with documents.
    
    Args:
        qdrant_path: Path to Qdrant storage directory
        collection_name: Name of the collection
        documents: List of Document objects to add
        embeddings: Embeddings function to use
        
    Returns:
        Qdrant vectorstore instance
    """
    # Ensure directory exists
    Path(qdrant_path).mkdir(parents=True, exist_ok=True)
    
    # Create persistent vectorstore
    vectorstore = Qdrant.from_documents(
        documents=documents,
        embedding=embeddings,
        path=qdrant_path,
        collection_name=collection_name
    )
    
    return vectorstore
