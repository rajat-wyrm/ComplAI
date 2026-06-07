import os, logging
from typing import Optional
from cachetools import TTLCache

logger = logging.getLogger(__name__)
_mem = TTLCache(maxsize=2000, ttl=3600)
redis_client = None

async def connect_to_redis():
    global redis_client
    url = os.environ.get("REDIS_URL", "")
    if not url:
        logger.warning("REDIS_URL not set - in-memory cache only")
        return
    try:
        import redis.asyncio as redis
        c = redis.from_url(url, encoding="utf-8", decode_responses=True,
                           socket_connect_timeout=3, socket_timeout=3)
        await c.ping()
        redis_client = c
        logger.info("Redis connected - two-tier cache active")
    except Exception as e:
        logger.warning(f"Redis unavailable (non-fatal): {e}")
        redis_client = None

async def close_redis_connection():
    global redis_client
    if redis_client:
        try: await redis_client.close()
        except: pass
        redis_client = None

async def cache_get(key: str) -> Optional[str]:
    if key in _mem: return _mem[key]
    if redis_client:
        try:
            v = await redis_client.get(key)
            if v: _mem[key] = v
            return v
        except: pass
    return None

async def cache_set(key: str, value: str, ttl: int = 3600):
    _mem[key] = value
    if redis_client:
        try: await redis_client.setex(key, ttl, value)
        except: pass

async def cache_delete(key: str):
    _mem.pop(key, None)
    if redis_client:
        try: await redis_client.delete(key)
        except: pass

async def cache_clear_prefix(prefix: str):
    keys = [k for k in list(_mem.keys()) if str(k).startswith(prefix)]
    for k in keys: _mem.pop(k, None)
    if redis_client:
        try:
            ks = await redis_client.keys(f"{prefix}*")
            if ks: await redis_client.delete(*ks)
        except: pass

def get_cache_stats() -> dict:
    return {
        "memory_size": len(_mem),
        "memory_maxsize": _mem.maxsize,
        "redis": redis_client is not None,
    }

async def get_redis():
    return redis_client

