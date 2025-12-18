"""
TEF Metrics Computation

Recall@k and latency statistics for retrieval evaluation.
"""
from typing import List, Dict, Any, Optional
import statistics


class QuestionResult:
    """
    Result for a single evaluation question.
    
    Note: embed_ms is kept for schema compatibility but set to 0.0.
    search_ms includes the full retrieval cost (embedding + vector search).
    total_ms = embed_ms + search_ms = search_ms (since embed_ms = 0.0).
    """
    
    def __init__(
        self,
        qid: str,
        question: str,
        expected_primary: str,
        expected_secondary: Optional[str],
        retrieved_chunks: List[str],
        embed_ms: float,
        search_ms: float,
        error: Optional[str] = None
    ):
        self.qid = qid
        self.question = question
        self.expected_primary = expected_primary
        self.expected_secondary = expected_secondary
        self.retrieved_chunks = retrieved_chunks
        self.embed_ms = embed_ms
        self.search_ms = search_ms
        self.total_ms = embed_ms + search_ms
        self.error = error
    
    def is_hit_at_k(self, k: int) -> bool:
        """
        Check if any expected chunk appears in top-k results.
        
        A hit occurs if either expected_primary OR expected_secondary
        appears in the top-k retrieved chunks.
        """
        if self.error:
            return False
        
        top_k = self.retrieved_chunks[:k]
        
        # Check primary expected chunk
        if self.expected_primary and self.expected_primary in top_k:
            return True
        
        # Check secondary expected chunk (if present)
        if self.expected_secondary and self.expected_secondary in top_k:
            return True
        
        return False
    
    def to_dict(self, k_values: List[int]) -> Dict[str, Any]:
        """
        Convert to dictionary for CSV export.
        
        Args:
            k_values: List of k values for which to compute hit@k
            
        Returns:
            Dictionary with all result fields and computed hit@k values
        """
        result = {
            "qid": self.qid,
            "question": self.question,
            "expected_primary": self.expected_primary,
            "expected_secondary": self.expected_secondary or "",
            "embed_ms": round(self.embed_ms, 2),
            "search_ms": round(self.search_ms, 2),
            "total_ms": round(self.total_ms, 2),
        }
        
        # Compute hit@k on demand (stateless - single source of truth)
        for k in sorted(k_values):
            result[f"hit@{k}"] = 1 if self.is_hit_at_k(k) else 0
        
        # Add top-10 retrieved chunks
        for i in range(10):
            if i < len(self.retrieved_chunks):
                result[f"retrieved_{i+1}"] = self.retrieved_chunks[i]
            else:
                result[f"retrieved_{i+1}"] = ""
        
        # Add error if present
        result["error"] = self.error or ""
        
        return result


def compute_recall_at_k(results: List[QuestionResult], k: int) -> float:
    """
    Compute recall@k across all questions.
    
    Recall@k = (number of questions with hit@k) / (total questions)
    
    Questions with errors are counted as misses (hit = 0).
    
    Args:
        results: List of QuestionResult objects
        k: The k value for top-k retrieval
        
    Returns:
        Recall@k as a float between 0.0 and 1.0
    """
    if not results:
        return 0.0
    
    hits = sum(1 for r in results if r.is_hit_at_k(k))
    return hits / len(results)


def compute_latency_stats(results: List[QuestionResult]) -> Dict[str, float]:
    """
    Compute latency statistics across all questions.
    
    Computes p50, p95, p99 for:
    - embed_ms: Always 0.0 (embedding included in search_ms)
    - search_ms: Full retrieval time (embedding + vector search)
    - total_ms: Same as search_ms (since embed_ms = 0.0)
    
    Note: embed_ms stats are kept for schema compatibility but will be 0.
    
    Questions with errors are excluded from latency stats.
    
    Args:
        results: List of QuestionResult objects
        
    Returns:
        Dictionary with latency percentiles
    """
    # Filter out results with errors
    valid_results = [r for r in results if not r.error]
    
    if not valid_results:
        return {
            "embed_ms_p50": 0.0,
            "embed_ms_p95": 0.0,
            "embed_ms_p99": 0.0,
            "search_ms_p50": 0.0,
            "search_ms_p95": 0.0,
            "search_ms_p99": 0.0,
            "total_ms_p50": 0.0,
            "total_ms_p95": 0.0,
            "total_ms_p99": 0.0,
        }
    
    embed_times = [r.embed_ms for r in valid_results]
    search_times = [r.search_ms for r in valid_results]
    total_times = [r.total_ms for r in valid_results]
    
    def percentile(data: List[float], p: float) -> float:
        """
        Compute percentile using linear interpolation.
        
        Uses statistics.quantiles() which provides smooth percentile estimates
        via linear interpolation between data points.
        """
        if not data:
            return 0.0
        sorted_data = sorted(data)
        return statistics.quantiles(sorted_data, n=100)[int(p) - 1] if len(sorted_data) > 1 else sorted_data[0]
    
    return {
        "embed_ms_p50": round(percentile(embed_times, 50), 2),
        "embed_ms_p95": round(percentile(embed_times, 95), 2),
        "embed_ms_p99": round(percentile(embed_times, 99), 2),
        "search_ms_p50": round(percentile(search_times, 50), 2),
        "search_ms_p95": round(percentile(search_times, 95), 2),
        "search_ms_p99": round(percentile(search_times, 99), 2),
        "total_ms_p50": round(percentile(total_times, 50), 2),
        "total_ms_p95": round(percentile(total_times, 95), 2),
        "total_ms_p99": round(percentile(total_times, 99), 2),
    }

