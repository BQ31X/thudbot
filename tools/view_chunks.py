#!/usr/bin/env python3
"""
View and export chunks from Qdrant collection to CSV.

This tool enumerates all chunks in the collection and exports them to CSV
for manual inspection and benchmark labeling.

Usage:
    python tools/view_chunks.py --qdrant-path ./apps/backend/qdrant_db
    python tools/view_chunks.py --output ./my_chunks.csv
    python tools/view_chunks.py --include-full-content
"""

import sys
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from qdrant_client import QdrantClient


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max_length, adding ellipsis if truncated.
    Also replaces newlines with spaces for CSV readability.
    """
    # Replace newlines and multiple spaces with single space
    text = " ".join(text.split())
    
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def export_chunks_to_csv(
    qdrant_path: str,
    collection_name: str,
    output_path: str,
    include_full_content: bool = False,
    preview_length: int = 100
):
    """
    Export all chunks from Qdrant collection to CSV.
    
    Args:
        qdrant_path: Path to Qdrant storage directory
        collection_name: Name of the collection
        output_path: Path to output CSV file
        include_full_content: If True, include full page_content in CSV
        preview_length: Length of preview text (default: 100 chars)
    """
    # Connect to Qdrant
    print(f"📂 Loading collection from: {qdrant_path}")
    client = QdrantClient(path=qdrant_path)
    
    # Verify collection exists
    if not client.collection_exists(collection_name):
        print(f"❌ Error: Collection '{collection_name}' not found at {qdrant_path}")
        sys.exit(1)
    
    # Get collection info
    collection_info = client.get_collection(collection_name)
    total_points = collection_info.points_count
    print(f"✅ Found collection: {collection_name}")
    print(f"   Total chunks: {total_points}")
    print()
    
    # Prepare CSV columns
    columns = ["chunk_id", "source", "document_type", "preview"]
    if include_full_content:
        columns.append("full_content")
    
    # Collect all chunks
    chunks_data: List[Dict[str, Any]] = []
    offset = None
    batch_size = 100
    processed = 0
    
    print("🔄 Retrieving chunks...")
    while True:
        # Scroll through collection
        points, next_offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )
        
        if not points:
            break
        
        # Extract metadata and content from each point
        for point in points:
            payload = point.payload or {}
            metadata = payload.get("metadata", {})
            page_content = payload.get("page_content", "")
            
            # Build row data
            row = {
                "chunk_id": metadata.get("chunk_id", "MISSING"),
                "source": metadata.get("source", "MISSING"),
                "document_type": metadata.get("document_type", "MISSING"),
                "preview": truncate_text(page_content, preview_length)
            }
            
            if include_full_content:
                row["full_content"] = page_content
            
            chunks_data.append(row)
        
        processed += len(points)
        print(f"   Retrieved {processed}/{total_points} chunks...")
        
        # Check if we're done
        if next_offset is None:
            break
        offset = next_offset
    
    print(f"✅ Retrieved {len(chunks_data)} chunks")
    print()
    
    # Write to CSV
    print(f"💾 Writing to: {output_path}")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(chunks_data)
    
    print(f"✅ Exported {len(chunks_data)} chunks to CSV")
    print(f"   Location: {output_file.resolve()}")
    print()
    print("📊 Summary by document type:")
    
    # Print summary stats
    type_counts: Dict[str, int] = {}
    for chunk in chunks_data:
        doc_type = chunk["document_type"]
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    for doc_type, count in sorted(type_counts.items()):
        print(f"   {doc_type}: {count} chunks")


def main():
    parser = argparse.ArgumentParser(
        description="Export Qdrant collection chunks to CSV for inspection and labeling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export with default settings
  python tools/view_chunks.py
  
  # Custom output location
  python tools/view_chunks.py --output ./my_export.csv
  
  # Include full content (for detailed inspection)
  python tools/view_chunks.py --include-full-content
  
  # Different collection
  python tools/view_chunks.py --collection MyCollection
        """
    )
    
    parser.add_argument(
        "--qdrant-path",
        default="./apps/backend/qdrant_db",
        help="Path to Qdrant storage directory (default: ./apps/backend/qdrant_db)"
    )
    parser.add_argument(
        "--collection",
        default="Thudbot_Hints",
        help="Collection name (default: Thudbot_Hints)"
    )
    parser.add_argument(
        "--output",
        default="./tools/tef/benchmark/chunks_export.csv",
        help="Output CSV file path (default: ./tools/tef/benchmark/chunks_export.csv)"
    )
    parser.add_argument(
        "--include-full-content",
        action="store_true",
        help="Include full page_content in CSV (default: preview only)"
    )
    parser.add_argument(
        "--preview-length",
        type=int,
        default=100,
        help="Length of preview text in characters (default: 100)"
    )
    
    args = parser.parse_args()
    
    export_chunks_to_csv(
        qdrant_path=args.qdrant_path,
        collection_name=args.collection,
        output_path=args.output,
        include_full_content=args.include_full_content,
        preview_length=args.preview_length
    )


if __name__ == "__main__":
    main()

