import redis
import logging
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.core.config import API_KEY

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key")

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

async def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        logger.warning("Invalid API key attempt")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key

async def check_rate_limit(key: str = Security(api_key_header)):
    rate_limit_key = f"rate_limit:{key}"
    try:
        requests = redis_client.incr(rate_limit_key)
        if requests == 1:
            redis_client.expire(rate_limit_key, 60)
        if requests > 10:
            logger.warning(f"Rate limit exceeded for key: {key}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 10 requests per minute.")
    except HTTPException:
        raise
    except Exception:
        logger.warning("Redis unavailable, skipping rate limit check")
    return key