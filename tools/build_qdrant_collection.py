#!/usr/bin/env python3
"""
Simplest possible script to build persistent Qdrant collection from CSV.

Can be run from any directory - paths are resolved relative to script location.

Usage:
    python tools/build_qdrant_collection.py [--csv-path PATH] [--txt-dir PATH] [--qdrant-path PATH]
    
Examples:
    # Use defaults (run from project root or anywhere)
    python tools/build_qdrant_collection.py
    
    # Custom CSV path
    python tools/build_qdrant_collection.py --csv-path /path/to/data.csv
    
    # Include sequential text documents
    python tools/build_qdrant_collection.py --txt-dir apps/backend/data/walkthroughs
"""

import sys
import os
import warnings
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path for rag_utils imports
# Minimal path bootstrap for standalone execution.
# This script is an offline build tool, not runtime code,
# so a small sys.path adjustment is going to havea to suffice here.
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Suppress verbose library output
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Suppress tokenizer warnings
warnings.filterwarnings("ignore")  # Suppress all warnings

# Suppress all library logging except critical errors
logging.basicConfig(level=logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)

from qdrant_client import QdrantClient

# Import from shared rag_utils
from rag_utils.embedding_utils import get_embedding_function
from rag_utils.build_utils import load_csv_documents, load_csv_with_chunk_id, upsert_documents_to_collection, chunk_text_by_lines


def get_default_model_for_provider(provider: str) -> str:
    """Get default model for provider (must match embedding_utils.py defaults)"""
    if provider == "openai":
        return "text-embedding-3-small"
    elif provider == "local":
        return "BAAI/bge-small-en-v1.5"
    else:
        raise ValueError(f"Unknown provider: {provider}")


def load_dotenv_from_path():
    """Load the nearest .env file by walking up the directory tree."""
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            return
    # Silently continue if no .env found - may be using environment variables


def main():
    # Load environment variables (including OPENAI_API_KEY)
    load_dotenv_from_path()
    
    # Resolve default CSV path relative to script location (allows running from any directory)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    default_csv_path = project_root / "apps" / "backend" / "data" / "Thudbot_Hint_Data_1.csv"
    
    parser = argparse.ArgumentParser(
        description="Build Qdrant vectorstore from CSV data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults (can run from any directory)
  python tools/build_qdrant_collection.py
  
  # Custom paths
  python tools/build_qdrant_collection.py --csv-path ./data/hints.csv --qdrant-path /tmp/my_qdrant/
  
  # Include sequential text documents
  python tools/build_qdrant_collection.py --txt-dir apps/backend/data/walkthroughs
        """
    )
    parser.add_argument(
        "--csv-path",
        default=str(default_csv_path),
        help=f"Path to the input CSV file (default: {default_csv_path})"
    )
    parser.add_argument(
        "--txt-dir",
        default=None,
        help="Optional: Directory containing .txt sequential text files to ingest"
    )
    parser.add_argument(
        "--qdrant-path",
        default="/tmp/thudbot_qdrant_build/",
        help="Path to store the Qdrant collection (default: /tmp/thudbot_qdrant_build/)"
    )
    parser.add_argument(
        "--collection-name",
        default="Thudbot_Hints",
        help="Name of the Qdrant collection (default: Thudbot_Hints)"
    )
    parser.add_argument(
        "--embedding-provider",
        default="openai",
        choices=["openai", "local"],
        help="Embedding provider: 'openai' for OpenAI API, 'local' for HuggingFace models (default: openai)"
    )
    parser.add_argument(
        "--embedding-model",
        default=None,
        help="Override default embedding model. If not specified, uses provider default: "
             "OpenAI='text-embedding-3-small', Local='BAAI/bge-small-en-v1.5'"
    )
    
    args = parser.parse_args()
    csv_path = args.csv_path
    txt_dir = args.txt_dir
    qdrant_path = args.qdrant_path
    
    print(f"📦 Building Qdrant Collection")
    print(f"   CSV: {csv_path}")
    if txt_dir:
        print(f"   TXT: {txt_dir}")
    print(f"   DB:  {qdrant_path}")
    print()
    
    # Make sure directory exists
    Path(qdrant_path).mkdir(parents=True, exist_ok=True)
    
    # Check if Qdrant database already exists (without opening client to avoid locks)
    # Qdrant creates a meta.json file when initialized
    meta_file = Path(qdrant_path) / "meta.json"
    if meta_file.exists():
        print(f"⚠️  Qdrant database already exists at {qdrant_path}")
        print(f"   To rebuild, delete the directory first:")
        print(f"   rm -rf {qdrant_path}")
        return
    
    # Load CSV using rag_utils with chunk_id generation
    hint_data = load_csv_with_chunk_id(
        csv_path=csv_path,
        source_id="HINTS",
        metadata_columns=[
            "question_id",  # Required for chunk_id generation
            "question", "hint_level", "character", "speaker",
            "narrative_context", "planet", "location", "category",
            "puzzle_id", "response_must_mention", "response_must_not_mention"
        ]
    )
    print(f"✅ Loaded {len(hint_data)} CSV documents")
    
    # Load and chunk sequential text files if txt_dir provided
    sequential_docs = []
    if txt_dir:
        txt_path = Path(txt_dir)
        if not txt_path.exists():
            print(f"⚠️  Warning: Text directory not found: {txt_dir}")
        else:
            for file in txt_path.glob("*.txt"):
                raw_text = file.read_text(encoding="utf-8", errors="ignore")
                docs = chunk_text_by_lines(raw_text, file.name)
                sequential_docs.extend(docs)
                print(f"✅ Loaded {file.name}: {len(docs)} chunks")
            
            if sequential_docs:
                print(f"✅ Total sequential text chunks: {len(sequential_docs)}")
    
    # Merge all documents
    all_docs = hint_data + sequential_docs
    print(f"✅ Total documents for ingestion: {len(all_docs)}")
    
    # Determine actual model used (CLI arg or provider default)
    actual_model = args.embedding_model or get_default_model_for_provider(args.embedding_provider)
    print(f"🔧 Using embedding provider: {args.embedding_provider}")
    print(f"🔧 Using embedding model: {actual_model}")
    
    # Create embeddings using rag_utils
    embeddings = get_embedding_function(
        provider=args.embedding_provider,
        model_name=actual_model if args.embedding_model else None
    )
    
    # Create persistent vectorstore using rag_utils
    print(f"🔨 Creating collection...")
    vectorstore = upsert_documents_to_collection(
        qdrant_path=qdrant_path,
        collection_name=args.collection_name,
        documents=all_docs,
        embeddings=embeddings
    )
    
    # Write collection metadata
    import json
    from datetime import datetime
    
    metadata = {
        "schema_version": "1.0",
        "embedding_provider": args.embedding_provider,
        "embedding_model": actual_model,
        "chunk_strategy": "line_based",
        "chunk_size": 10,
        "chunk_overlap": 4,
        "collection_name": args.collection_name,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    metadata_path = Path(qdrant_path) / "collection_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))
    print(f"✅ Wrote collection metadata: {metadata_path}")
    
    # Show where files are
    resolved_path = Path(qdrant_path).resolve()
    print()
    print(f"✅ Done! Collection created")
    print(f"   Location: {resolved_path}")
    print(f"   To open:  open {qdrant_path}")


if __name__ == "__main__":
    main()
