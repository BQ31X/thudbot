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
from langchain.schema import Document


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


def chunk_text_by_lines(
    raw_text: str,
    source_name: str,
    chunk_size: int = 10,
    chunk_overlap: int = 4,
    document_type: str = "sequential"
) -> list[Document]:
    """
    Chunk text into overlapping line-based chunks.
    
    Strategy: Split on newlines, group into fixed-size windows with overlap.
    Suitable for sequential content like step-by-step instructions.
    
    Args:
        raw_text: Raw text content (unmodified)
        source_name: Source filename for metadata
        chunk_size: Number of lines per chunk
        chunk_overlap: Number of overlapping lines between chunks
        document_type: Document structure type (e.g., "sequential", "prose")
    
    Returns:
        List of LangChain Document objects with metadata
    
    Rules:
        - Do NOT modify text. No normalization, stripping, or filtering.
        - Split only on '\n'.
        - Return a list of LangChain Document objects with metadata.
        - This function is for build-time ingestion ONLY.
    """
    # Split into lines (no modification)
    lines = raw_text.split("\n")
    
    # Calculate source_id (uppercase stem without extension)
    file_stem = source_name.rsplit(".", 1)[0]
    source_id = file_stem.upper()
    
    # Generate chunks with overlap
    chunks = []
    chunk_index = 0
    
    start = 0
    while start < len(lines):
        # Get chunk_size lines starting from start position
        end = start + chunk_size
        chunk_lines = lines[start:end]
        
        # Join lines with newline (no modification)
        page_content = "\n".join(chunk_lines)
        
        # Create Document with metadata
        doc = Document(
            page_content=page_content,
            metadata={
                "source": source_name,
                "document_type": document_type,
                "source_id": source_id,
                "chunk_index": chunk_index
            }
        )
        chunks.append(doc)
        
        # Move to next chunk with overlap
        chunk_index += 1
        start += (chunk_size - chunk_overlap)
    
    return chunks
