# Thudbot*NarrativeHints*20260106

## Purpose

Expand RAG coverage using narrative hint text files that provide in-universe, prose-oriented guidance rather than procedural walkthroughs.

Built on: 2026-01-06

Built by:

```
python tools/build_qdrant_collection.py \
  --qdrant-url http://localhost:6333 \
  --collection-name Thudbot_NarrativeHints_bge-base_20260106 \
  --csv-path apps/backend/data/Thudbot_Hint_Data_1.csv \
  --txt-dir apps/backend/data/walkthroughs \
  --embedding-provider local \
  --embedding-model BAAI/bge-base-en-v1.5
```

Qdrant collection:  Thudbot_NarrativeHints_bge-base_20260106

## Source Files

* VILWIN.txt
* WEBHINT2.txt
* WEBHINT3.txt
* WEBHINT4.txt
* WEBHINTS.txt
* AUDWIN.txt
* BACKER.txt
* BARWIN.txt
* FPUZZLES.txt
* GAMEWIN.txt
* KERWIN.txt
* NEBWIN.txt
* SALWIN.txt
* SRAWIN.txt
* TRISECKS.txt
* VEDJWIN.txt
* ZZAWIN.txt
* Thudbot_*Hint_*Data_1.csv

**Source location:**

* `data/walkthroughs/` (legacy directory name only; treated conceptually as Narrative Hint Texts)

## Embedding

* Provider: Hugging Face
* Model: bge-base-en-v1.5
* Build mode: Offline (build-time only)

## Chunking Strategy

Chunking is source-type specific. Two ingestion strategies are used within this collection.

### Narrative Text Files (`.txt`)

* Line-based chunking (split only on `
  `)
* Fixed-size sliding window
* Default window: 10 lines per chunk
* Overlap: 4 lines between consecutive chunks
* Order preserved
* No sentence- or paragraph-aware logic
* No semantic rewriting or normalization
* Text content is not modified in any way

**Characteristics:**

* Deterministic, line-count based
* Window advances by `(chunk_size - chunk_overlap)` lines
* Significant overlap to preserve local sequential context
* Suitable for sequential or quasi-sequential narrative text

### Structured Hint Data (`.csv`)

* One logical hint record per chunk
* Chunk boundaries defined by CSV row structure
* No overlap between chunks
* Text content taken directly from the hint text field
* Associated metadata preserved per row

**Characteristics:**

* Semantically atomic chunks
* No cross-row context blending
* Optimized for precise hint retrieval rather than sequential context

## Collection Scope

* Narrative hint prose only
* No procedural walkthrough logic
* No design commentary or internal notes

## Notes

* This collection is immutable once built
* Runtime behavior is unchanged
* Intended for coverage expansion only
