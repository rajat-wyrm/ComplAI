import redis.asyncio as redis
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

redis_client = None

async def connect_to_redis():
    global redis_client
    try:
        redis_url = os.getenv('REDIS_URL')
        redis_client = await redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis Cloud")
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

async def close_redis_connection():
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

def get_redis():
    return redis_client
