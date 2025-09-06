import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Maximum number of concurrent sessions allowed
# Session limits to prevent memory exhaustion DoS; can override in .env
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "500"))
