#!/usr/bin/env python3
"""
Simplest possible script to build persistent Qdrant collection from CSV.

Can be run from any directory - paths are resolved relative to script location.

Usage:
    python tools/build_qdrant_collection.py [--csv-path PATH] [--qdrant-path PATH]
    
Examples:
    # Use defaults (run from project root or anywhere)
    python tools/build_qdrant_collection.py
    
    # Custom CSV path
    python tools/build_qdrant_collection.py --csv-path /path/to/data.csv
"""

import sys
import os
import warnings
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Suppress verbose library output
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Suppress tokenizer warnings
warnings.filterwarnings("ignore")  # Suppress all warnings

# Suppress all library logging except critical errors
logging.basicConfig(level=logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from qdrant_client import QdrantClient
import hashlib


def load_dotenv_from_path():
    """Load the nearest .env file by walking up the directory tree."""
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            return
    # Silently continue if no .env found - may be using environment variables


def create_cached_embeddings(model="text-embedding-3-small", cache_dir="./cache/embeddings"):
    """Create cached embeddings (copied from agent.py to avoid loading entire package)"""
    try:
        base_embeddings = OpenAIEmbeddings(model=model)
        safe_namespace = hashlib.md5(model.encode()).hexdigest()
        store = LocalFileStore(cache_dir)
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
            base_embeddings, 
            store, 
            namespace=safe_namespace,
            key_encoder="sha256"
        )
        return cached_embeddings
    except Exception:
        # Fallback to direct embeddings if caching fails
        return OpenAIEmbeddings(model=model)


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
        """
    )
    parser.add_argument(
        "--csv-path",
        default=str(default_csv_path),
        help=f"Path to the input CSV file (default: {default_csv_path})"
    )
    parser.add_argument(
        "--qdrant-path",
        default="/tmp/thudbot_qdrant_build/",
        help="Path to store the Qdrant collection (default: /tmp/thudbot_qdrant_build/)"
    )
    
    args = parser.parse_args()
    csv_path = args.csv_path
    qdrant_path = args.qdrant_path
    
    print(f"📦 Building Qdrant Collection")
    print(f"   CSV: {csv_path}")
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
    
    # Load CSV (exactly like agent.py does)
    loader = CSVLoader(
        file_path=csv_path,
        metadata_columns=[
            "question", "hint_level", "character", "speaker",
            "narrative_context", "planet", "location", "category",
            "puzzle_id", "response_must_mention", "response_must_not_mention"
        ]
    )
    hint_data = loader.load()
    print(f"✅ Loaded {len(hint_data)} documents")
    
    # Create embeddings (exactly like agent.py does)
    embeddings = create_cached_embeddings(model="text-embedding-3-small")
    
    # Create persistent vectorstore (only difference: path instead of :memory:)
    print(f"🔨 Creating collection...")
    vectorstore = Qdrant.from_documents(
        documents=hint_data,
        embedding=embeddings,
        path=qdrant_path,  # <-- This is the only change from agent.py!
        collection_name="Thudbot_Hints"
    )
    
    # Show where files are
    resolved_path = Path(qdrant_path).resolve()
    print()
    print(f"✅ Done! Collection created")
    print(f"   Location: {resolved_path}")
    print(f"   To open:  open {qdrant_path}")


if __name__ == "__main__":
    main()
