\"\"\"
Redis cache management
\"\"\"
import redis.asyncio as redis
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

redis_client = None

async def init_redis():
    global redis_client
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info(f"Connected to Redis: {settings.REDIS_URL}")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

async def close_redis():
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

async def get_cache(key: str):
    if redis_client:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
    return None

async def set_cache(key: str, value: dict, ttl: int = 3600):
    if redis_client:
        await redis_client.setex(key, ttl, json.dumps(value))

async def delete_cache(key: str):
    if redis_client:
        await redis_client.delete(key)

async def invalidate_pattern(pattern: str):
    if redis_client:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
