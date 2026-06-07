from app.models.database import get_db, init_db, engine, Base
from app.models import user, token  # ensure tables registered

async def connect_to_postgres():
    await init_db()

async def close_postgres_connection():
    await engine.dispose()

async def get_database():
    async for session in get_db():
        return session
