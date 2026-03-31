"""
Redis Cache Layer (ULTIMATE VERSION)

✔ Async safe
✔ Singleton connection
✔ Auto fallback (never breaks system)
✔ Production-ready pooling
✔ Compatible with chat + RAG
✔ Safe get/set wrappers
"""

import os
import logging
from typing import Optional

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class RedisManager:
    client: Optional[redis.Redis] = None
    enabled: bool = True

    # =========================
    # CONNECT
    # =========================
    @classmethod
    async def connect(cls):
        try:
            if cls.client:
                return cls.client

            redis_url = os.getenv("REDIS_URL")

            if not redis_url:
                logger.warning("⚠️ REDIS_URL not found → disabling cache")
                cls.enabled = False
                return None

            cls.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                max_connections=20,
            )

            await cls.client.ping()

            logger.info("✅ Redis connected")
            return cls.client

        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable → fallback mode: {e}")
            cls.enabled = False
            cls.client = None
            return None

    # =========================
    # CLOSE
    # =========================
    @classmethod
    async def close(cls):
        try:
            if cls.client:
                await cls.client.close()
                cls.client = None
                logger.info("🔌 Redis closed")
        except Exception as e:
            logger.warning(f"Redis close error: {e}")

    # =========================
    # SAFE GET
    # =========================
    @classmethod
    async def get(cls, key: str):
        if not cls.enabled or not cls.client:
            return None
        try:
            return await cls.client.get(key)
        except Exception:
            return None

    # =========================
    # SAFE SET
    # =========================
    @classmethod
    async def set(cls, key: str, value: str, ex: int = 1800):
        if not cls.enabled or not cls.client:
            return
        try:
            await cls.client.set(key, value, ex=ex)
        except Exception:
            pass

    # =========================
    # SAFE LIST PUSH
    # =========================
    @classmethod
    async def lpush(cls, key: str, value: str):
        if not cls.enabled or not cls.client:
            return
        try:
            await cls.client.lpush(key, value)
        except Exception:
            pass

    # =========================
    # SAFE LIST RANGE
    # =========================
    @classmethod
    async def lrange(cls, key: str, start: int, end: int):
        if not cls.enabled or not cls.client:
            return []
        try:
            return await cls.client.lrange(key, start, end)
        except Exception:
            return []


# =========================
# GLOBAL ACCESS
# =========================
def get_redis():
    """
    Always returns usable object (even if Redis disabled)
    """
    return RedisManager


# =========================
# FASTAPI LIFECYCLE
# =========================
async def init_redis():
    return await RedisManager.connect()


async def close_redis():
    await RedisManager.close()