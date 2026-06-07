import os
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment")

# Remove sslmode query param for asyncpg compatibility
ASYNC_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).split("?")[0]

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)
    company_name = Column(String, index=True)
    filename = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, default="default_user")
    role = Column(String, default="user")
    document_metadata = Column(JSON)
    analysis_report = Column(JSON)
    chunks_count = Column(Integer, default=0)

engine = create_async_engine(ASYNC_URL, connect_args={"ssl": True}, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
