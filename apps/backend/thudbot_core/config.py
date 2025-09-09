import os
import logging
from pathlib import Path
from dotenv import load_dotenv

"""
Search upward from this file for the first .env file and load it.
Assumes there is only one .env file located near project root.
"""

# Load environment variables first
def load_env(verbose: bool = False):
    """
    Load the nearest .env file by walking up the directory tree from this file.
    Raises a clear error if not found.
    """
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            if verbose:
                logging.info(f".env loaded from: {env_path}")
            return
    raise FileNotFoundError("No .env file found in current or parent directories.")

# Load .env variables before accessing any of them
load_env()

# Maximum number of concurrent sessions allowed
# Session limits to prevent memory exhaustion DoS; can override in .env
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "500"))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REQUESTS_PER_MINUTE_IP = int(os.getenv("RATE_LIMIT_IP", "20")) # Requests per minute per IP address (10)
REQUESTS_PER_MINUTE_GLOBAL = int(os.getenv("RATE_LIMIT_GLOBAL", "1000")) # Requests per minute per global (1000)
