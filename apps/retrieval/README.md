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
| `EMBEDDING_PROVIDER` | `openai` | Embedding provider (`openai`, `huggingface`) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model name |
| `OPENAI_API_KEY` | (required) | OpenAI API key (if using `openai` provider) |
| `SERVICE_PORT` | `8001` | Service port |

**Production:** Secrets managed by Docker Swarm secrets model.  
**Development:** Secrets loaded from `.env` file.

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

**Multi-VM Architecture:**
- **VM 1:** Thudbot Backend (calls retrieval API via HTTP)
- **VM 2:** Qdrant + Retrieval Service (colocated for performance)

**Why colocate Qdrant and Retrieval?**
- Minimize network latency
- Single point of failure isolation
- Simplified deployment

**Network boundary:**
```
Internet → Thudbot Backend (VM1) → Retrieval API (VM2) → Qdrant (VM2)
```

## Design Principles

1. **Stateless**: No session state, fully RESTful
2. **Fail-fast**: Clear errors, no silent fallbacks
3. **Single responsibility**: Only embedding + retrieval
4. **Production-safe**: All config via environment
5. **Thin wrapper**: Delegates to rag_utils for Qdrant logic

