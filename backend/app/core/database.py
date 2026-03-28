\"\"\"
Database connection management
\"\"\"
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def init_db():
    \"\"\"Initialize database connection\"\"\"
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.db = db.client[settings.MONGO_DB_NAME]
        
        await db.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_URL}")
        
        await db.db.documents.create_index("document_id", unique=True)
        await db.db.analyses.create_index("document_id")
        await db.db.chat_history.create_index("session_id")
        
        return db.db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_db():
    \"\"\"Close database connection\"\"\"
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")

def get_db():
    \"\"\"Get database instance\"\"\"
    return db.db
