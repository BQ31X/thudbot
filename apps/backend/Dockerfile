# Dockerfile for Thudbot Backend
# Multi-stage build using Python 3.13 + UV package manager
# Follows Astral UV best practices for Docker containerization

# --------------------------------------
# Stage 1: Builder - installs UV and dependencies
# --------------------------------------
FROM python:3.13-slim-bookworm AS builder

# Install UV using the official installation script (cache-friendly)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv

# Set UV environment variables for optimal performance
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Copy dependency management files first (for layer caching)
COPY pyproject.toml uv.lock README.md ./
COPY thudbot_core/ ./thudbot_core/
COPY data/ ./data/

# Install dependencies into a virtual environment
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
COPY thudbot_core/ /app/thudbot_core/
COPY data/ /app/data/

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Note: Running as root for simplicity in single-service container
# In production, consider using non-root user with proper ownership setup

# Expose FastAPI port
EXPOSE 8000

# Health check to ensure the container is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)" || exit 1

# Entry point using thudbot_core.__main__ module
CMD ["python", "-m", "thudbot_core"]
