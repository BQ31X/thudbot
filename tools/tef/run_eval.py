#!/usr/bin/env python3
"""
TEF CLI Entry Point

Run retrieval evaluation on Thudbot benchmark.

Usage:
    python tools/tef/run_eval.py
    python tools/tef/run_eval.py --embedding-provider local
    python tools/tef/run_eval.py --qdrant-path ./apps/backend/qdrant_db_eval
"""
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path (needed before we can import from tools/)
script_dir = Path(__file__).resolve().parent
PROJECT_ROOT = script_dir.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.tef.config import TEFConfig
from tools.tef.evaluator import TEFEvaluator
from tools.tef.metrics import compute_recall_at_k, compute_latency_stats


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Thudbot Evaluation Framework - Retrieval Performance Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings (OpenAI embeddings, dedicated eval collection)
  python tools/tef/run_eval.py

  # Use local embeddings with default model
  python tools/tef/run_eval.py --embedding-provider local

  # Use local embeddings with custom model
  python tools/tef/run_eval.py --embedding-provider local --embedding-model BAAI/bge-base-en-v1.5

  # Point to different collection
  python tools/tef/run_eval.py --qdrant-path ./apps/backend/qdrant_db

  # Custom benchmark file
  python tools/tef/run_eval.py --benchmark ./tools/tef/benchmark/test_benchmark.csv
        """
    )
    
    parser.add_argument(
        '--qdrant-path',
        default=str(PROJECT_ROOT / "apps/backend/qdrant_db_eval"),
        help='Path to Qdrant collection (default: apps/backend/qdrant_db_eval)'
    )
    
    parser.add_argument(
        '--collection',
        default='Thudbot_Hints',
        help='Collection name (default: Thudbot_Hints)'
    )
    
    parser.add_argument(
        '--benchmark',
        default=str(PROJECT_ROOT / "tools/tef/benchmark/benchmark_tef.csv"),
        help='Path to benchmark CSV (default: tools/tef/benchmark/benchmark_tef.csv)'
    )
    
    parser.add_argument(
        '--embedding-provider',
        choices=['openai', 'local'],
        default='openai',
        help='Embedding provider (default: openai)'
    )
    
    parser.add_argument(
        '--embedding-model',
        help='Override default embedding model'
    )
    
    parser.add_argument(
        '--output-dir',
        default=str(PROJECT_ROOT / "tools/tef/results"),
        help='Results output directory (default: tools/tef/results)'
    )
    
    parser.add_argument(
        '--k-values',
        type=int,
        nargs='+',
        default=[1, 3, 5, 10],
        help='K values for recall@k (default: 1 3 5 10)'
    )
    
    return parser.parse_args()


def save_results(
    results,
    config: TEFConfig,
    collection_metadata: dict,
    output_dir: str
):
    """
    Save evaluation results to CSV and JSON.
    
    Creates timestamped subdirectory with:
    - per_question.csv: Detailed per-question results
    - summary.json: Aggregate metrics
    
    Args:
        results: List of QuestionResult objects
        config: TEFConfig instance
        collection_metadata: Collection metadata dict
        output_dir: Output directory path
    """
    # Create timestamped output directory
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = Path(output_dir) / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 Saving results to {run_dir}/")
    
    # Save per-question results to CSV
    per_question_path = run_dir / "per_question.csv"
    with open(per_question_path, 'w', newline='') as f:
        if results:
            fieldnames = list(results[0].to_dict(config.k_values).keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result.to_dict(config.k_values))
    
    print(f"  ✅ Saved per-question results: {per_question_path.name}")
    
    # Compute aggregate metrics
    recall_metrics = {}
    for k in config.k_values:
        recall_metrics[f"recall@{k}"] = round(compute_recall_at_k(results, k), 4)
    
    latency_metrics = compute_latency_stats(results)
    
    # Count errors
    error_count = sum(1 for r in results if r.error)
    
    # Build summary
    summary = {
        "config": {
            "qdrant_path": config.qdrant_path,
            "collection_name": config.collection_name,
            "embedding_provider": config.embedding_provider,
            "embedding_model": config.embedding_model or collection_metadata["embedding_model"],
            "k_values": config.k_values,
            "benchmark_path": config.benchmark_path,
        },
        "collection_metadata": collection_metadata,
        "recall": recall_metrics,
        "latency": latency_metrics,
        "total_questions": len(results),
        "error_count": error_count,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save summary to JSON
    summary_path = run_dir / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✅ Saved summary: {summary_path.name}\n")
    
    return run_dir


def print_summary(results, config: TEFConfig):
    """
    Print summary to console.
    
    Args:
        results: List of QuestionResult objects
        config: TEFConfig instance
    """
    print("=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)
    
    # Recall metrics
    print("\n🎯 Recall@k:")
    for k in config.k_values:
        recall = compute_recall_at_k(results, k)
        print(f"  recall@{k:2d}: {recall:.2%}")
    
    # Latency metrics
    latency = compute_latency_stats(results)
    print("\n⏱️  Latency (ms):")
    print(f"  retrieval - p50: {latency['search_ms_p50']:6.1f}  p95: {latency['search_ms_p95']:6.1f}  p99: {latency['search_ms_p99']:6.1f}")
    print("  (includes embedding + vector search)")
    
    # Error summary
    error_count = sum(1 for r in results if r.error)
    if error_count > 0:
        print(f"\n⚠️  Errors: {error_count}/{len(results)} questions failed")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    args = parse_args()
    
    # Build configuration from CLI args
    config = TEFConfig(
        qdrant_path=args.qdrant_path,
        collection_name=args.collection,
        benchmark_path=args.benchmark,
        embedding_provider=args.embedding_provider,
        embedding_model=args.embedding_model,
        k_values=args.k_values,
        output_dir=args.output_dir
    )
    
    print("=" * 60)
    print("🚀 THUDBOT EVALUATION FRAMEWORK")
    print("=" * 60)
    print()
    
    try:
        # Initialize evaluator
        evaluator = TEFEvaluator(config)
        
        # Run evaluation
        results = evaluator.evaluate()
        
        # Print summary to console
        print_summary(results, config)
        
        # Save results to disk
        run_dir = save_results(
            results,
            config,
            evaluator.collection_metadata,
            args.output_dir
        )
        
        print(f"✅ Evaluation complete! Results saved to:")
        print(f"   {run_dir}/")
        print()
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}\n")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

