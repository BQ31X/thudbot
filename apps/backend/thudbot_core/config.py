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
    print("🔧 _set_redis_host() called!")

    # Manual override always wins
    redis_host_env = os.getenv("REDIS_HOST")
    compose_mode = os.getenv("COMPOSE_MODE", "false").lower() == "true"

    if redis_host_env:
        REDIS_HOST = redis_host_env
    elif compose_mode:
        REDIS_HOST = "redis"
    elif is_in_docker():
        REDIS_HOST = "host.docker.internal"
    else:
        REDIS_HOST = "localhost"

    print(f"🔧 DEBUG: is_in_docker()={is_in_docker()}, COMPOSE_MODE={compose_mode}, REDIS_HOST={REDIS_HOST}")

# Load .env variables before accessing any of them
load_env()

# Maximum number of concurrent sessions allowed
# Session limits to prevent memory exhaustion DoS; can override in .env
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "500"))

# Redis port (simple fallback)
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REQUESTS_PER_MINUTE_IP = int(os.getenv("RATE_LIMIT_IP", "20")) # Requests per minute per IP address (10)
REQUESTS_PER_MINUTE_GLOBAL = int(os.getenv("RATE_LIMIT_GLOBAL", "1000")) # Requests per minute per global (1000)
