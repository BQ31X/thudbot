# Thudbot Evaluation Framework (TEF)

## Purpose

TEF is a **retrieval-only** evaluation tool that measures **recall@k** and **latency** for the Thudbot knowledge base. It does not evaluate LLM generation quality—only the performance of the vector retrieval layer.

## Quick Start

### 1. Build Dedicated Eval Collection

TEF uses a dedicated collection to isolate evaluation from runtime operations:

```bash
# From project root
python tools/build_qdrant_collection.py \
  --qdrant-path ./apps/backend/qdrant_db_eval \
  --csv-path ./apps/backend/data/Thudbot_Hint_Data_1.csv \
  --txt-dir ./apps/backend/data/walkthroughs \
  --embedding-provider openai
```

### 2. Run Evaluation

```bash
python tools/tef/run_eval.py
```

Default behavior:
- Uses `./apps/backend/qdrant_db_eval` collection
- Uses OpenAI embeddings (text-embedding-3-small)
- Loads `./tools/tef/benchmark/benchmark_tef.csv`
- Computes recall@1, recall@3, recall@5, recall@10

## Configuration

### CLI Options

```bash
python tools/tef/run_eval.py \
  --qdrant-path ./apps/backend/qdrant_db_eval \
  --collection Thudbot_Hints \
  --benchmark ./tools/tef/benchmark/benchmark_tef.csv \
  --embedding-provider openai \
  --embedding-model text-embedding-3-small \
  --output-dir ./tools/tef/results \
  --k-values 1 3 5 10
```

**Options:**

- `--qdrant-path`: Path to Qdrant collection (default: `./apps/backend/qdrant_db_eval`)
- `--collection`: Collection name (default: `Thudbot_Hints`)
- `--benchmark`: Path to benchmark CSV (default: `./tools/tef/benchmark/benchmark_tef.csv`)
- `--embedding-provider`: `openai` or `local` (default: `openai`)
- `--embedding-model`: Override default model (optional)
- `--output-dir`: Results directory (default: `./tools/tef/results`)
- `--k-values`: K values for recall@k (default: `1 3 5 10`)

### Embedding Providers

**OpenAI (default):**
```bash
python tools/tef/run_eval.py --embedding-provider openai
```
- Model: `text-embedding-3-small` (default)
- Requires: `OPENAI_API_KEY` in environment

**Local (HuggingFace):**
```bash
python tools/tef/run_eval.py --embedding-provider local
```
- Model: `BAAI/bge-small-en-v1.5` (default)
- No API key required
- First run downloads model (~100MB)

**Custom model:**
```bash
python tools/tef/run_eval.py \
  --embedding-provider local \
  --embedding-model BAAI/bge-base-en-v1.5
```

## Understanding Results

TEF produces two artifacts per run in `tools/tef/results/YYYY-MM-DD_HH-MM-SS/`:

### 1. `per_question.csv`

Detailed per-question results with columns:
- `qid`: Question ID
- `question`: Question text
- `expected_primary`: Primary expected chunk_id
- `expected_secondary`: Secondary expected chunk_id (if any)
- `hit@1`, `hit@3`, `hit@5`, `hit@10`: Binary hit indicators
- `embed_ms`, `search_ms`, `total_ms`: Latency measurements
- `retrieved_1` through `retrieved_10`: Top-10 retrieved chunk_ids
- `error`: Error message (if question failed)

### 2. `summary.json`

Aggregate metrics:
```json
{
  "config": {
    "qdrant_path": "./apps/backend/qdrant_db_eval",
    "embedding_provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "k_values": [1, 3, 5, 10]
  },
  "collection_metadata": {
    "embedding_provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "chunk_strategy": "line_based",
    "created_at": "2025-12-18T10:30:00Z"
  },
  "recall": {
    "recall@1": 0.65,
    "recall@3": 0.82,
    "recall@5": 0.91,
    "recall@10": 0.95
  },
  "latency": {
    "embed_ms_p50": 12.3,
    "search_ms_p50": 8.1,
    "total_ms_p95": 45.2
  },
  "total_questions": 24,
  "error_count": 0,
  "timestamp": "2025-12-18T10:35:00Z"
}
```

## Key Metrics

### Recall@k

**Definition:** Fraction of questions where the correct chunk appears in the top-k results.

**Interpretation:**
- `recall@1 = 0.65` → 65% of questions have correct chunk as #1 result
- `recall@5 = 0.91` → 91% of questions have correct chunk in top 5

**Primary regression gate:** `recall@5`

If recall@5 drops significantly:
1. Check if collection was rebuilt (compare `collection_metadata.created_at`)
2. Check if chunking parameters changed
3. Check if embedding model changed
4. Inspect `per_question.csv` to find which questions regressed
5. Use chunk viewer to inspect affected chunks

### Latency

**Metrics:**
- `embed_ms`: Always 0.0 (embedding is included in search_ms for accurate measurement)
- `search_ms`: Full retrieval time (embedding + vector search)
- `total_ms`: Same as search_ms (since embed_ms = 0.0)

**Percentiles:** p50 (median), p95, p99

**Typical values (search_ms = full retrieval):**
- OpenAI: ~50-220ms (network call for embedding + search)
- Local: ~15-50ms (on-device embedding + search)

Note: embed_ms is always 0.0 for schema compatibility.

## Embedding Model Enforcement

TEF **validates** that query embeddings match collection embeddings. **Mismatch = hard error.**

### Why This Matters

Vector embeddings are model-specific. You cannot query a collection built with `text-embedding-3-small` using queries embedded with `BAAI/bge-small-en-v1.5`. The results would be meaningless.

### Validation Process

On startup, TEF:
1. Reads `{qdrant_path}/collection_metadata.json`
2. Compares collection embedding config to CLI args
3. **Fails loudly** if provider or model mismatch

### Example Error

```
❌ Embedding provider mismatch!
  Collection was built with: openai
  TEF is configured to use: local
You must either:
  1. Rebuild collection with local, OR
  2. Run TEF with --embedding-provider openai
```

### To Rebuild Collection with Different Embeddings

```bash
# Delete old collection
rm -rf apps/backend/qdrant_db_eval

# Rebuild with desired embeddings
python tools/build_qdrant_collection.py \
  --qdrant-path ./apps/backend/qdrant_db_eval \
  --csv-path ./apps/backend/data/Thudbot_Hint_Data_1.csv \
  --txt-dir ./apps/backend/data/walkthroughs \
  --embedding-provider local
```

## Benchmark Schema

Benchmark CSV at `tools/tef/benchmark/benchmark_tef.csv`:

```csv
qid,question,expected_primary,expected_secondary,notes,tags
TEF-001,Who is Zelda,HINTS:row:TSB-007,,,,
TEF-002,What is the time limit,HINTS:row:TSB-039,HINTS:row:TSB-003,,,
TEF-020,What do I do in the Barbershop?,VILWIN:chunk:1,,,,
```

**Required columns:**
- `qid`: Unique question ID (format: `TEF-NNN`)
- `question`: Question text
- `expected_primary`: Primary expected chunk_id

**Optional columns:**
- `expected_secondary`: Secondary expected chunk_id (alternative valid answer)
- `notes`: Human-readable notes
- `tags`: Tags for categorization (use semicolons or spaces to separate multiple tags)

**Chunk ID format:**
- CSV rows: `HINTS:row:{question_id}` (e.g., `HINTS:row:TSB-007`)
- Sequential text: `{source}:chunk:{N}` (e.g., `VILWIN:chunk:1`)

## Workflow

### Initial Setup (One Time)

1. Build dedicated eval collection: `python tools/build_qdrant_collection.py --qdrant-path ./apps/backend/qdrant_db_eval ...`
2. Verify benchmark: `cat tools/tef/benchmark/benchmark_tef.csv`
3. Run baseline eval: `python tools/tef/run_eval.py`
4. Record baseline metrics (especially `recall@5`)

### Regular Use (Regression Testing)

Before making changes to chunking, embeddings, or source data:

1. Run TEF to establish baseline
2. Make your changes
3. Rebuild eval collection (if needed)
4. Run TEF again
5. Compare recall@5 and other metrics
6. Investigate regressions using `per_question.csv`

### Investigating Regressions

If a question regresses (hit → miss):

1. Check `per_question.csv` for the question
2. Note the `expected_primary` chunk_id
3. Check `retrieved_1` through `retrieved_10` columns
4. Use chunk viewer to inspect retrieved chunks:
   ```bash
   python tools/view_chunks.py --output chunks.csv
   grep "VILWIN:chunk:1" chunks.csv
   ```
5. Determine root cause:
   - Chunk text changed?
   - Chunking boundaries shifted?
   - Embedding model changed?
   - Query semantics unclear?

## Design Constraints

TEF is intentionally simple and deterministic:

- **Retrieval-only** (no LLM judging, no generation eval)
- **String equality** for chunk_id matching (no fuzzy matching)
- **Fail loudly** per-question (errors recorded but don't stop eval)
- **No metadata invention** (uses chunk_id as-is from collection)
- **Isolated from runtime** (lives in `tools/`, uses dedicated collection)

## Future Enhancements

**Not in Phase 3, but possible later:**

- Near-miss diagnostics (adjacent chunks in results)
- Multi-collection comparison (A/B testing)
- Synthetic question generation
- Chunk coverage analysis (unused chunks)
- Export to Weights & Biases / MLflow

## Troubleshooting

### "Collection metadata not found"

**Cause:** Collection was built before Phase 0 metadata tracking.

**Fix:** Rebuild collection with updated build script.

### "Embedding provider mismatch"

**Cause:** TEF config doesn't match collection.

**Fix:** Either rebuild collection or change TEF CLI args to match.

### "Benchmark file not found"

**Cause:** Benchmark CSV missing or path incorrect.

**Fix:** Verify `--benchmark` path points to valid CSV file.

### Low recall scores

**Not an error!** This means retrieval isn't performing well. Possible causes:

- Questions are ambiguous or too general
- Expected chunks don't contain relevant keywords
- Chunk size/overlap needs tuning
- Embedding model not suitable for domain
- Source data quality issues

Use `per_question.csv` to identify specific problem questions, then use chunk viewer to inspect retrieved vs. expected chunks.

## Getting Help

If TEF produces unexpected results or errors:

1. Check `per_question.csv` for per-question details
2. Verify collection metadata matches TEF config
3. Use chunk viewer to inspect specific chunks
4. Check if source data or chunking changed recently
5. Compare current `summary.json` to previous runs

