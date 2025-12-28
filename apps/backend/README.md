# 🔧 Thudbot Backend (thudbot_core)

  

The **FastAPI backend** for Thudbot - providing the AI-powered hint API for The Space Bar adventure game.

  

## 🚀 Quick Start

  

### Development (Local)

```bash

# Install dependencies (includes dev tools)

uv sync --frozen --extra dev

# Make sure Redis is running

# Option A: Run Redis via Docker (recommended for local dev)
docker run -p 6379:6379 --name thudbot-redis -d redis:7-alpine

# Option B: If Redis is installed on your system
redis-server

# Run the backend server

python -m thudbot_core

  

# Or with auto-reload

uvicorn thudbot_core.api:app --reload --host 0.0.0.0 --port 8000

```


## 🌐 Retrieval API Integration

**As of Dec 2024**, the backend no longer accesses Qdrant directly. Instead, it communicates with a separate **Retrieval Service** via HTTP.

### Architecture

```
Backend → HTTP (RETRIEVAL_API_URL) → Retrieval Service → Qdrant
```

### Configuration

Set the retrieval API URL via environment variable:

```bash
# Development (.env file)
RETRIEVAL_API_URL=http://localhost:8001

# Or point to remote retrieval node
RETRIEVAL_API_URL=http://<retrieval-node-ip>:8001

# Production (set in compose.prod.app.yml)
RETRIEVAL_API_URL=http://<retrieval-node-ip>:8001
```

### Local Development Options

**Option 1: Point to remote retrieval node (recommended)**
```bash
# In .env
RETRIEVAL_API_URL=http://<retrieval-node-ip>:8001

# Start backend only
python -m thudbot_core
```

**Option 2: Run retrieval service locally**
```bash
# Start qdrant + retrieval service
cd infra
docker compose --profile local-retrieval up

# In .env
RETRIEVAL_API_URL=http://localhost:8001

# Start backend
python -m thudbot_core
```

### Collection Management

Collection building is handled **offline** (on your local machine), then deployed as a derived artifact to the retrieval node:

1. **Build locally:** Run `tools/build_qdrant_collection.py` to create a server-mode Qdrant collection
2. **Extract artifact:** Export the collection from the Docker volume to `~/thudbot_build_artifacts/`
3. **Deploy artifact:** `rsync` the collection directory to the retrieval node at `/opt/thud-retrieval/qdrant_data/collections/`

See `apps/retrieval/README.md` for detailed collection building and deployment steps.

**Note:** The backend will fail fast if `RETRIEVAL_API_URL` is unreachable (by design).  

### Production (Docker)

```bash

# Build the optimized container

docker build -t thudbot-backend .

  

# Run with environment file

docker run -p 8000:8000 --env-file .env thudbot-backend

```

  

## 📊 API Documentation

  

**Interactive docs available when running:**

- **Swagger UI**: http://localhost:8000/docs

- **ReDoc**: http://localhost:8000/redoc

- **OpenAPI Schema**: http://localhost:8000/openapi.json

  

## 🏗️ Architecture

  

```

FastAPI ── LangGraph ── RAG Pipeline
│ │ │
│ │ ├── OpenAI GPT-4
│ │ ├── Qdrant Vector Store (persistent)
│ │ └── Multi-query Retrieval
│ │
│ └── Workflow Nodes:
│ ├── Router (intent classification)
│ ├── Find Hint (RAG retrieval)
│ ├── Verify Correctness
│ ├── Maintain Character
│ └── Format Output
│
└── Features:
├── Rate Limiting (Redis)
├── Session Management
├── CORS Protection
└── Error Handling

```

  

## 🛠️ Key Components

  

- **`api.py`**: FastAPI application with CORS, rate limiting, error handling

- **`app.py`**: LangGraph workflow orchestration and session management

- **`agent.py`**: Multi-query RAG retrieval system with Qdrant

- **`*_node.py`**: Individual LangGraph workflow nodes

- **`config.py`**: Environment configuration and Redis setup

- **`state.py`**: Shared state management for LangGraph

  

## 🧪 Testing

  

```bash

# Run regression tests

python -m tests.regression.run_quick_regression

  

# Run security tests

python -m tests.security.run_security_tests

  

# Run all checks

./run_checks.sh

```

  

## 🐳 Docker & Docker Compose

### **🚀 Quick Start with Docker Compose**

**From project root:**
```bash
# Start the full stack (Redis + Backend)
cd infra
docker compose up --build

# Backend available at: http://localhost:8000
# Redis available at: localhost:6379
```

**Environment Configuration:**
- Automatically uses `COMPOSE_MODE=true` for service discovery
- Backend connects to Redis via service name `redis`
- Mounts your root `.env` file for API keys

**Useful Commands:**
```bash
# View logs
docker compose logs -f backend
docker compose logs -f redis

# Stop services
docker compose down

# Rebuild and restart
docker compose up --build --force-recreate
```

### **🐳 Standalone Docker (Advanced)**

**Production image optimizations:**

- Multi-stage build pattern

- UV package manager for fast dependency resolution

- Production vs development dependency separation

- Optimized image size: **561MB** (reduced from 2.7GB)

  

## 🔧 Environment Variables

  

Required in `.env` file:

```bash

OPENAI_API_KEY=your_key_here

LANGCHAIN_API_KEY=your_key_here

REDIS_HOST=localhost # Auto-configured for Docker

REDIS_PORT=6379

RATE_LIMIT_IP=20 # Requests per minute per IP

RATE_LIMIT_GLOBAL=1000 # Global requests per minute

```

  ### **🚀 Production Deployment**

For production deployment with Docker Swarm, secure secrets management, and production best practices:

**👉 See the main project README: [Production Deployment Guide](../../README.md#-production-deployment-docker-swarm)**

Key production differences:
- Uses Docker Swarm for orchestration
- Secure API key management via Docker secrets
- Pre-built Docker Hub images for consistency
- Overlay networking for multi-host deployments
- Production-grade restart policies and health checks

---

## 📈 Performance

  

- **Redis**: Session storage and rate limiting

- **Multi-query retrieval**: Enhanced context precision for game hints

- **LangSmith tracing**: Full observability and debugging

- **Async FastAPI**: High-performance concurrent request handling

  

## 🔗 Related

  

- **Main Project**: [../../README.md](../../README.md)

- **Frontend**: [../frontend/](../frontend/)

- **Documentation**: [../../docs/](../../docs/)

  

---

  

Part of the **Thudbot** project - an AI assistant for The Space Bar adventure game.