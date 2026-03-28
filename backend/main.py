"""
AI Compliance & Risk Copilot - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import init_db, close_db
from app.services.vector_store import vector_store
from app.api.routes import health, upload, analyze, insights, chat, history

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("Starting AI Compliance & Risk Copilot...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database connected")
    except Exception as e:
        logger.warning(f"Database init skipped: {e}")
    
    # Load vector store
    try:
        vector_store.load()
        logger.info("Vector store loaded")
    except Exception as e:
        logger.warning(f"Vector store load skipped: {e}")
    
    yield
    
    # Cleanup
    try:
        await close_db()
        logger.info("Database closed")
    except Exception as e:
        logger.warning(f"Database close error: {e}")

app = FastAPI(
    title="AI Compliance & Risk Copilot",
    description="RegTech AI for compliance document analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(history.router, prefix="/history", tags=["History"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Compliance & Risk Copilot",
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
