"""
Configuration for Retrieval Service.

All configuration is environment-variable driven.
NO SECRETS stored in this file - secrets managed by Docker Swarm in production.
"""
import os

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "Thudbot_Hints")

# OpenAI Configuration (API key from environment only)
# Dev: Read from .env file
# Prod: Managed by Docker Swarm secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Embedding Configuration
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")  # Options: "openai", "huggingface"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Service Configuration
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")

# Default retrieval parameters
DEFAULT_K = 5

