import redis
import hashlib
import logging

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

def get_cache_key(prompt: str, model: str) -> str:
    return hashlib.md5(f"{prompt}{model}".encode()).hexdigest()

def get_cached_response(prompt: str, model: str):
    try:
        cache_key = get_cache_key(prompt, model)
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Cache hit!")
            return cached
    except Exception:
        logger.warning("Redis unavailable, skipping cache")
    return None

def set_cached_response(prompt: str, model: str, response: str, ttl: int = 300):
    try:
        cache_key = get_cache_key(prompt, model)
        redis_client.setex(cache_key, ttl, response)
        logger.info("Response cached")
    except Exception:
        logger.warning("Redis unavailable, response not cached")