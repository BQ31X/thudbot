# Thudbot Retrieval Service

Stateless FastAPI service providing HTTP boundary between Thudbot backend and Qdrant vector database.

## Architecture

```
Thudbot Backend → HTTP → Retrieval Service → Qdrant Server
                           ↓
                      rag_utils/loader.py
```

## Responsibilities

- Embed user queries using OpenAI
- Query Qdrant vector database
- Return top-k chunks with scores
- Fail fast with clear errors

## Non-Responsibilities

❌ Multi-query logic (handled by Thudbot)  
❌ Collection building (handled by build tools)  
❌ Retries or circuit breakers (caller's responsibility)  
❌ Session management (stateless service)

## 🎯 Embedding Options

The retrieval service supports two embedding providers:

### OpenAI Embeddings (Default)
```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small  # 1536 dimensions
```

### Local BGE Embeddings (CPU-only)
```bash
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5  # 768 dimensions
```

**Why Local Embeddings?**
- ✅ No API costs
- ✅ No external dependencies
- ✅ Privacy (no data leaves your server)
- ✅ CPU-only (no GPU required)

**Performance:** BGE embeddings are comparable to OpenAI for retrieval quality (validated via TEF framework).

## Endpoints

### `GET /health`
Health check with service metadata.

**Response:**
```json
{
  "status": "ok",
  "service": "retrieval",
  "version": "0.1.0",
  "config": {
    "qdrant_url": "http://qdrant:6333",
    "collection": "Thudbot_Hints",
    "embedding_model": "text-embedding-3-small"
  }
}
```

### `POST /retrieve`
Retrieve top-k documents for a query.

**Request:**
```json
{
  "query": "how do I get the bus token",
  "k": 5
}
```

**Response:**
```json
{
  "query": "how do I get the bus token",
  "k": 5,
  "results": [
    {
      "chunk_id": "WEBHINTS:123",
      "text": "The bus token is in the phone booth...",
      "metadata": {
        "source": "WEBHINTS.txt",
        "hint_level": 2
      },
      "score": 0.892
    }
  ]
}
```

### `GET /meta`
Get collection metadata (for debugging).

**Response:**
```json
{
  "collection_name": "Thudbot_Hints",
  "vectors_count": 138,
  "points_count": 138,
  "status": "green",
  "config": {
    "vector_size": 1536
  }
}
```

## Configuration

All configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `QDRANT_COLLECTION` | `Thudbot_Hints` | Collection name |
| `EMBEDDING_PROVIDER` | `openai` | Embedding provider (`openai`, `local`) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Model name for embeddings |
| `OPENAI_API_KEY` | (required if using OpenAI) | OpenAI API key |
| `SERVICE_PORT` | `8001` | Service port |

**Production:** Secrets managed by Docker Swarm secrets model (app node only).  
**Development:** Secrets loaded from `.env` file.

### Local Embeddings Setup

The retrieval service includes CPU-only PyTorch + sentence-transformers for local BGE embeddings.

**Dependencies** (already in `pyproject.toml`):
```toml
dependencies = [
    ...
    "langchain-huggingface>=0.1.0",
    "sentence-transformers>=5.2.0",
]

[tool.uv.sources]
# Force CPU-only PyTorch (~500MB vs ~2GB GPU version)
torch = { index = "pytorch-cpu" }

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

**First run:** Downloads BGE model (~438MB, takes 60-90 seconds). Cached afterwards.

## Local Development

```bash
# Build image
docker build -t retrieval-service .

# Run standalone (requires Qdrant running)
docker run -p 8001:8001 \
  -e QDRANT_URL=http://localhost:6333 \
  -e OPENAI_API_KEY=sk-... \
  retrieval-service

# Test health
curl http://localhost:8001/health

# Test retrieval
curl -X POST http://localhost:8001/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "how do I solve the first puzzle", "k": 5}'
```

## Docker Compose Integration

Service is defined in `infra/compose.yml`:

```yaml
services:
  retrieval:
    build: ../apps/retrieval
    ports:
      - "8001:8001"
    environment:
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant
    networks:
      - thudbot-network
```

## Dependencies

- **FastAPI**: HTTP API framework
- **qdrant-client**: Vector database client
- **langchain**: Embedding abstractions
- **openai**: Query embedding
- **rag_utils**: Shared Qdrant loader (from repo root)

## Error Handling

**Philosophy:** Fail fast with clear errors. No retries, no circuit breakers.

**Common errors:**
- `503`: Service not initialized (Qdrant unreachable or collection missing)
- `500`: Retrieval failed (embedding error, Qdrant error)

**Client responsibility:** Handle retries and fallbacks.

## Testing

```bash
# Run unit tests (TODO)
pytest tests/

# Integration test (requires running Qdrant)
curl http://localhost:8001/meta
```

## Production Deployment

### Two-Node Architecture

**Node 1 (App):** Backend + Frontend + Redis  
**Node 2 (Retrieval):** Qdrant + Retrieval Service

**Why separate nodes?**
- ✅ Isolate compute (app) from retrieval workloads
- ✅ No secrets needed on retrieval node (local embeddings only)
- ✅ Independent scaling and deployment
- ✅ Simpler failure isolation

**Network flow:**
```
Internet → Backend (Node 1) → HTTP → Retrieval API (Node 2) → Qdrant (Node 2)
```

### Multi-Arch Build

```bash
# Build for both amd64 (Linode) and arm64 (Mac)
make build-retrieval

# Or manually
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t bq31/thudbot-retrieval:latest \
  -f apps/retrieval/Dockerfile \
  --push \
  .
```

**Note:** Build context is project root (`.`) because it needs access to `rag_utils/`.

### Deploy to Retrieval Node

```bash
# Deploy qdrant + retrieval service
make deploy-retrieval

# Check logs
make logs-retrieval
make logs-qdrant

# Restart if needed
make restart-retrieval
```

### Building Collections

Build Qdrant collections locally, then rsync to retrieval node:

```bash
# 1. Start local Qdrant server
docker compose -f infra/compose.yml up -d qdrant

# 2. Build BGE collection locally
python tools/build_qdrant_collection.py \
  --qdrant-url http://localhost:6333 \
  --collection-name Thudbot_Hints_BGE_base \
  --embedding-provider local \
  --embedding-model BAAI/bge-base-en-v1.5 \
  --force

# 3. Extract from Docker volume
docker run --rm \
  -v infra_qdrant_storage:/source:ro \
  -v ~/thudbot_build_artifacts:/dest \
  alpine \
  cp -r /source/collections/Thudbot_Hints_BGE_base /dest/

# 4. Rsync to retrieval node
rsync -avz --progress \
  ~/thudbot_build_artifacts/Thudbot_Hints_BGE_base/ \
  bq@<retrieval-node-ip>:/opt/thud-retrieval/qdrant_data/collections/Thudbot_Hints_BGE_base/

# 5. Restart qdrant on retrieval node
ssh bq@<retrieval-node-ip> 'cd ~/thudbot && docker compose -f compose.prod.retrieval.yml restart qdrant'
```

**Verification:**
```bash
# Check collection exists
curl http://<retrieval-node-ip>:6333/collections/Thudbot_Hints_BGE_base | jq

# Should show no storage.sqlite (server-mode, not embedded)
ssh bq@<retrieval-node-ip> 'find /opt/thud-retrieval/qdrant_data -name "*.sqlite"'
```

## Design Principles

1. **Stateless**: No session state, fully RESTful
2. **Fail-fast**: Clear errors, no silent fallbacks
3. **Single responsibility**: Only embedding + retrieval
4. **Production-safe**: All config via environment
5. **Thin wrapper**: Delegates to rag_utils for Qdrant logic

