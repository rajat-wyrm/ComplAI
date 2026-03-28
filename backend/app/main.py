"""
AI Compliance & Risk Copilot - Main Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.api.routes import health, upload, analyze, insights, chat, history
from app.core.exceptions import ComplianceException

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Starting AI Compliance & Risk Copilot...")
    
    try:
        from app.core.database import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    
    try:
        from app.core.cache import init_redis
        await init_redis()
        logger.info("Redis initialized")
    except Exception as e:
        logger.warning(f"Redis initialization skipped: {e}")
    
    try:
        from rag.vector_store import init_vector_store
        await init_vector_store()
        logger.info("Vector store initialized")
    except Exception as e:
        logger.warning(f"Vector store initialization skipped: {e}")
    
    logger.info("Application startup complete")
    yield
    
    logger.info("Shutting down...")
    try:
        from app.core.database import close_db
        await close_db()
    except:
        pass
    
    try:
        from app.core.cache import close_redis
        await close_redis()
    except:
        pass

app = FastAPI(
    title="AI Compliance & Risk Copilot",
    description="RegTech AI system for legal and compliance document analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ComplianceException)
async def compliance_exception_handler(request: Request, exc: ComplianceException):
    logger.error(f"Compliance exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(history.router, prefix="/history", tags=["History"])

@app.get("/")
async def root():
    return {
        "name": "AI Compliance & Risk Copilot",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
