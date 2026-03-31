from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

mongodb_client = None
database = None

async def connect_to_mongo():
    global mongodb_client, database
    try:
        mongodb_url = os.getenv('MONGODB_URL')
        mongodb_client = AsyncIOMotorClient(mongodb_url)
        database = mongodb_client.compliance_copilot
        await mongodb_client.admin.command('ping')
        logger.info("Connected to MongoDB Atlas")
        return database
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")

def get_database():
    return database
