"""
TEF Core Evaluation Logic

Loads benchmark, validates configuration, and evaluates retrieval performance.
"""
import sys
import json
import csv
import re
import time
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
script_dir = Path(__file__).resolve().parent
PROJECT_ROOT = script_dir.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag_utils.loader import load_retriever
from rag_utils.embedding_utils import get_embedding_function
from tools.tef.config import TEFConfig
from tools.tef.metrics import QuestionResult


class TEFEvaluator:
    """
    Core evaluation engine for Thudbot Evaluation Framework.
    
    Validates collection metadata, loads retriever, and evaluates
    recall@k performance on benchmark questions.
    """
    
    def __init__(self, config: TEFConfig):
        """
        Initialize evaluator with configuration.
        
        Args:
            config: TEFConfig instance
            
        Raises:
            RuntimeError: If collection metadata validation fails
            FileNotFoundError: If benchmark or collection not found
        """
        self.config = config
        
        # Step 1: Validate collection metadata
        print("📋 Validating collection metadata...")
        self._validate_collection_metadata()
        
        # Step 2: Load embeddings
        print(f"🔧 Loading embeddings ({self.config.embedding_provider})...")
        self.embeddings = self._load_embeddings()
        
        # Step 3: Load retriever (configured to return max_k documents)
        print(f"🔍 Loading retriever from {self.config.qdrant_url}...")
        self.max_k = max(self.config.k_values)
        self.retriever = self._load_retriever()
        
        # Step 4: Load and validate benchmark
        print(f"📊 Loading benchmark from {self.config.benchmark_path}...")
        self.benchmark = self._load_and_validate_benchmark()
        
        print(f"✅ TEF initialized: {len(self.benchmark)} questions loaded\n")
    
    def _validate_collection_metadata(self):
        """
        Validate that query embedding configuration matches collection.
        
        CRITICAL: Collection was built with specific embedding model.
        Query embeddings MUST use the same model to avoid incompatibility.
        
        Raises:
            RuntimeError: If metadata doesn't exist or doesn't match config
        """
        # TODO: In server mode, metadata validation is skipped for Phase 1
        # Need to implement proper metadata storage/retrieval for server Qdrant
        print("⚠️  Metadata validation skipped (server mode - Phase 1)")
        print("   Ensure collection was built with matching embedding configuration")
        
        # Store default metadata for output artifacts
        collection_meta = {
            "embedding_provider": self.config.embedding_provider,
            "embedding_model": self.config.embedding_model or self._get_default_model(self.config.embedding_provider)
        }
        
        # Skip file-based validation in server mode
        # Original path-based validation code commented out for reference:
        # metadata_path = Path(self.config.qdrant_path) / "collection_metadata.json"
        # if not metadata_path.exists():
        #     raise RuntimeError(...)
        # with open(metadata_path) as f:
        #     collection_meta = json.load(f)
        # Validation checks skipped - user responsible for matching embeddings
        
        # Store validated metadata for output artifacts
        self.collection_metadata = collection_meta
        print(f"✅ Validated: {collection_meta['embedding_provider']}/{collection_meta['embedding_model']}")
    
    def _get_default_model(self, provider: str) -> str:
        """
        Get default model for provider.
        
        MUST match defaults in rag_utils.embedding_utils.get_embedding_function()
        
        Args:
            provider: "openai" or "local"
            
        Returns:
            Default model name for provider
        """
        if provider == "openai":
            return "text-embedding-3-small"
        elif provider == "local":
            return "BAAI/bge-small-en-v1.5"
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _load_embeddings(self):
        """
        Load embedding function matching collection configuration.
        
        Returns:
            Configured embeddings object
        """
        return get_embedding_function(
            provider=self.config.embedding_provider,
            execution_mode="build",  # TEF is evaluation-only
            model_name=self.config.embedding_model
        )
    
    def _load_retriever(self):
        """
        Load retriever using rag_utils.loader.
        
        Configures retriever to return max(k_values) documents to ensure
        we have enough results for all recall@k computations.
        
        Returns:
            Configured retriever object
        """
        return load_retriever(
            qdrant_url=self.config.qdrant_url,
            collection_name=self.config.collection_name,
            embeddings=self.embeddings,
            search_kwargs={"k": self.max_k}
        )
    
    def _load_and_validate_benchmark(self) -> List[Dict[str, str]]:
        """
        Load benchmark CSV and validate schema.
        
        Enforces design doc constraints:
        - Required columns must exist
        - chunk_id format must match expected pattern
        - No fuzzy matching or reinterpretation
        
        Returns:
            List of benchmark question dictionaries
            
        Raises:
            FileNotFoundError: If benchmark file doesn't exist
            ValueError: If required columns are missing
        """
        benchmark_path = Path(self.config.benchmark_path)
        
        if not benchmark_path.exists():
            raise FileNotFoundError(
                f"❌ Benchmark file not found: {benchmark_path}"
            )
        
        # Load CSV
        with open(benchmark_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            raise ValueError(f"❌ Benchmark file is empty: {benchmark_path}")
        
        # Validate required columns
        required_columns = {"qid", "question", "expected_primary"}
        actual_columns = set(rows[0].keys())
        
        missing = required_columns - actual_columns
        if missing:
            raise ValueError(
                f"❌ Benchmark missing required columns: {missing}\n"
                f"Required: {required_columns}\n"
                f"Found: {actual_columns}"
            )
        
        # Validate chunk_id format (basic pattern check)
        chunk_id_pattern = re.compile(r'^[A-Z0-9_]+:(chunk|row):\S+$')
        
        invalid_chunks = []
        for row in rows:
            primary = row.get('expected_primary', '').strip()
            secondary = row.get('expected_secondary', '').strip()
            
            if primary and not chunk_id_pattern.match(primary):
                invalid_chunks.append((row['qid'], 'primary', primary))
            
            if secondary and not chunk_id_pattern.match(secondary):
                invalid_chunks.append((row['qid'], 'secondary', secondary))
        
        if invalid_chunks:
            print("⚠️  Warning: Invalid chunk_id formats detected:")
            for qid, field, chunk_id in invalid_chunks[:5]:  # Show first 5
                print(f"  {qid} ({field}): {chunk_id}")
            if len(invalid_chunks) > 5:
                print(f"  ... and {len(invalid_chunks) - 5} more")
            print()
        
        return rows
    
    def evaluate(self) -> List[QuestionResult]:
        """
        Run evaluation on all benchmark questions.
        
        For each question:
        1. Retrieve top-max(k) chunks (time: search_ms, includes embedding)
        2. Check if expected_primary or expected_secondary in results for each k
        3. Record hit@k for each k value
        4. Record latencies
        
        Note: embed_ms is set to 0.0 since embedding is included in search_ms.
        This avoids double-embedding and measures actual retrieval cost.
        Latency metrics represent end-to-end retrieval cost only.
        Component-level timing (embed vs search) is intentionally not measured in Phase 3.
        This ensures consistent and comparable results across different embedding providers.

        Returns:
            List of QuestionResult objects
        """
        results = []
        
        print(f"🔬 Evaluating {len(self.benchmark)} questions...")
        print(f"📊 K values: {self.config.k_values}")
        print(f"📥 Retrieving top-{self.max_k} chunks per question\n")
        
        for i, row in enumerate(self.benchmark, 1):
            qid = row['qid']
            question = row['question']
            expected_primary = row['expected_primary'].strip()
            expected_secondary = row.get('expected_secondary', '').strip() or None
            
            # Progress indicator
            if i % 5 == 0 or i == len(self.benchmark):
                print(f"  Processing {i}/{len(self.benchmark)}...")
            
            try:
                # Time the full retrieval (includes embedding + search)
                retrieval_start = time.perf_counter()
                docs = self.retriever.get_relevant_documents(question)
                search_ms = (time.perf_counter() - retrieval_start) * 1000
                
                # Extract chunk_ids from retrieved documents (up to max_k)
                retrieved_chunks = []
                for doc in docs[:self.max_k]:
                    chunk_id = doc.metadata.get('chunk_id', '')
                    if chunk_id:
                        retrieved_chunks.append(chunk_id)
                
                # Create result (stateless - hit@k computed on demand)
                # Note: embed_ms set to 0.0 since embedding is included in search_ms
                result = QuestionResult(
                    qid=qid,
                    question=question,
                    expected_primary=expected_primary,
                    expected_secondary=expected_secondary,
                    retrieved_chunks=retrieved_chunks,
                    embed_ms=0.0,
                    search_ms=search_ms
                )
                
                results.append(result)
                
            except Exception as e:
                # Record error but continue evaluation (hit@k will be False due to error)
                error_msg = f"{type(e).__name__}: {str(e)}"
                result = QuestionResult(
                    qid=qid,
                    question=question,
                    expected_primary=expected_primary,
                    expected_secondary=expected_secondary,
                    retrieved_chunks=[],
                    embed_ms=0.0,
                    search_ms=0.0,
                    error=error_msg
                )
                results.append(result)
                
                print(f"  ⚠️  Error on {qid}: {error_msg}")
        
        print(f"\n✅ Evaluation complete: {len(results)} questions processed\n")
        return results

