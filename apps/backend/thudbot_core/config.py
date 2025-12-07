import os
import logging
from pathlib import Path
from dotenv import load_dotenv

def is_in_docker():
    """Detects if we're running in a Docker container."""
    return os.path.exists("/.dockerenv")

"""
Search upward from this file for the first .env file and load it.
Assumes there is only one .env file located near project root.
"""

# Load environment variables first
def load_env(verbose: bool = False):
    """
    Load the nearest .env file by walking up the directory tree from this file.
    In Docker containers, environment variables may already be loaded via --env-file,
    so gracefully handle missing .env files if key variables are present.
    """
    global REDIS_HOST  # Need to declare global since we're setting it
    
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        env_path = parent / ".env"
        print(f"🔧 DEBUG: Checking .env file at: {env_path}")
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            if verbose:
                logging.info(f".env loaded from: {env_path}")
            # Set Redis host after loading .env
            _set_redis_host(verbose)
            return
    
    # Docker-friendly: If no .env file found, check if essential env vars are already present
    if os.getenv("OPENAI_API_KEY"):  # Check for a critical env var
        if verbose:
            print("⚠️ .env file not found; relying on Docker environment variables")
        # Set Redis host for Docker scenario
        _set_redis_host(verbose)
        return
    
    raise FileNotFoundError("No .env file found and essential environment variables missing.")

def _set_redis_host(verbose: bool = False):
    """Helper function to set Redis host based on environment"""
    global REDIS_HOST
    REDIS_HOST = None # to clear any cached value?
    print("🔧 _set_redis_host() called!")

    compose_mode = os.getenv("COMPOSE_MODE", "false").lower() == "true"
    print(f"🔧 COMPOSE_MODE env var: '{os.getenv('COMPOSE_MODE')}', compose_mode bool: {compose_mode}")

    if compose_mode:
        print("🔧 Taking COMPOSE branch -> redis")
        REDIS_HOST = "redis"
    elif is_in_docker():
        print("🔧 Taking DOCKER branch -> host.docker.internal") 
        REDIS_HOST = "host.docker.internal"
    else:
        print("🔧 Taking LOCAL branch -> localhost")
        REDIS_HOST = "localhost"

    print(f"🔧 DEBUG: is_in_docker()={is_in_docker()}, COMPOSE_MODE={compose_mode}, REDIS_HOST={REDIS_HOST}")

def _set_qdrant_path(verbose: bool = False):
    """Set Qdrant database path - always absolute"""
    global QDRANT_DB_PATH
    
    raw_path = os.getenv("QDRANT_DB_PATH", None)
    
    if raw_path:
        QDRANT_DB_PATH = str(Path(raw_path).resolve())
        if verbose:
            print(f"🗄️  Qdrant DB (from env): {QDRANT_DB_PATH}")
    else:
        # Default: qdrant_db relative to backend directory
        current_file = Path(__file__).resolve()
        backend_dir = current_file.parent.parent
        default_path = backend_dir / "qdrant_db"
        QDRANT_DB_PATH = str(default_path.resolve())
        if verbose:
            print(f"🗄️  Qdrant DB (default): {QDRANT_DB_PATH}")

# Load .env variables before accessing any of them but skip in CI
if os.getenv("CI") != "true":
    load_env(verbose=True)
    _set_qdrant_path(verbose=True)
else:
    print("🧪 CI detected — skipping load_env() in config.py")
    # Still set Redis host for CI
    _set_redis_host(verbose=True)
    # Set default Qdrant path for CI
    QDRANT_DB_PATH = "/tmp/qdrant_db"

# Maximum number of concurrent sessions allowed
# Session limits to prevent memory exhaustion DoS; can override in .env
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "500"))

# Redis port (simple fallback)
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REQUESTS_PER_MINUTE_IP = int(os.getenv("RATE_LIMIT_IP", "20")) # Requests per minute per IP address (10)
REQUESTS_PER_MINUTE_GLOBAL = int(os.getenv("RATE_LIMIT_GLOBAL", "1000")) # Requests per minute per global (1000)
