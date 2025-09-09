import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Maximum number of concurrent sessions allowed
# Session limits to prevent memory exhaustion DoS; can override in .env
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "500"))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REQUESTS_PER_MINUTE_IP = int(os.getenv("RATE_LIMIT_IP", "20")) # Requests per minute per IP address (10)
REQUESTS_PER_MINUTE_GLOBAL = int(os.getenv("RATE_LIMIT_GLOBAL", "1000")) # Requests per minute per global (1000)
