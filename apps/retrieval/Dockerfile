# Dockerfile for Retrieval Service
# Multi-stage build using Python 3.13 + UV package manager
# Follows Astral UV best practices for Docker containerization

# --------------------------------------
# Stage 1: Builder - installs UV and dependencies
# --------------------------------------
FROM python:3.13-slim-bookworm AS builder

# Install UV using pip (cache-friendly)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv

# Set UV environment variables for optimal performance
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Copy dependency management files first (for layer caching)
COPY apps/retrieval/pyproject.toml ./
COPY apps/retrieval/uv.lock ./

# Copy shared rag_utils (required by retriever)
COPY rag_utils/ ./rag_utils/

# Copy retrieval service code
COPY apps/retrieval/retrieval_service/ ./retrieval_service/

# Install dependencies into a virtual environment
# --frozen uses uv.lock for reproducible builds
# --no-dev excludes dev dependencies to keep image lean
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --------------------------------------
# Stage 2: Production - minimal runtime image
# --------------------------------------
FROM python:3.13-slim-bookworm

# Set Python environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create app directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY --from=builder /app/retrieval_service/ /app/retrieval_service/
COPY --from=builder /app/rag_utils/ /app/rag_utils/

# Copy and set up entrypoint script
COPY apps/retrieval/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose service port
EXPOSE 8001

# Health check
# Generous timing for local embedding model download/loading (can take 60-120s on first run)
HEALTHCHECK --interval=30s --timeout=20s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"

# Set the entrypoint (runs before CMD)
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


# Run FastAPI with uvicorn
CMD ["uvicorn", "retrieval_service.api:app", "--host", "0.0.0.0", "--port", "8001"]
