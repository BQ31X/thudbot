# src/rate_limiter.py

import sys
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from redis import Redis, ConnectionError, TimeoutError
from config import REDIS_HOST, REDIS_PORT, REQUESTS_PER_MINUTE_IP, REQUESTS_PER_MINUTE_GLOBAL

logger = logging.getLogger(__name__)

def test_redis_startup():
    """Test Redis connection at startup - fail fast if unavailable"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=5)
            redis_client.ping()
            print(f"✅ Redis connection successful at {REDIS_HOST}:{REDIS_PORT}")
            logger.info(f"✅ Redis connection successful at {REDIS_HOST}:{REDIS_PORT}")
            return True
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Redis connection attempt {attempt + 1} failed, retrying...")
                logger.warning(f"⚠️  Redis connection attempt {attempt + 1} failed, retrying...")
                import time
                time.sleep(1)
            else:
                logger.error(f"🚨 Redis is not available at {REDIS_HOST}:{REDIS_PORT} after {max_retries} attempts")
                print(f"🚨 Redis is not available — exiting.")
                sys.exit(1)
        except Exception as e:
            logger.error(f"🚨 Unexpected Redis error: {e}")
            print(f"🚨 Redis connection failed — exiting.")
            sys.exit(1)

# Test Redis connection on import (fail fast)
test_redis_startup()

# Rate limiter instance (Redis is confirmed working)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}"
)

# Rate limit strings for use with decorators
IP_RATE_LIMIT = f"{REQUESTS_PER_MINUTE_IP}/minute"
GLOBAL_RATE_LIMIT = f"{REQUESTS_PER_MINUTE_GLOBAL}/minute"
