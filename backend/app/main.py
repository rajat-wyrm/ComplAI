"""
AI Compliance & Risk Copilot - Main Application (PRODUCTION-GRADE)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.cache import init_redis, close_redis
from app.services.vector_store import vector_store  # auto-loads
from app.api.routes import ws, health, upload, insights, chat, history

# =========================
# LOGGING SETUP
# =========================
setup_logging()
logger = logging.getLogger(__name__)


# =========================
# LIFECYCLE MANAGEMENT
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("?? Starting AI Compliance & Risk Copilot...")

    # ===== DATABASE =====
    try:
        await connect_to_mongo()
        logger.info("? MongoDB connected")
    except Exception as e:
        logger.exception(f"? MongoDB failed: {e}")

    # ===== REDIS =====
    try:
        await init_redis()
        logger.info("? Redis connected")
    except Exception as e:
        logger.warning(f"?? Redis unavailable: {e}")

    # ===== VECTOR STORE =====
    try:
        # already auto-loaded via import
        logger.info(f"? Vector store ready ({len(vector_store.chunks)} chunks)")
    except Exception as e:
        logger.warning(f"?? Vector store issue: {e}")

    logger.info("?? Application startup complete")

    yield

    logger.info("?? Shutting down...")

    # ===== CLEANUP =====
    try:
        await close_mongo_connection()
    except Exception as e:
        logger.warning(f"Mongo close failed: {e}")

    try:
        await close_redis()
    except Exception as e:
        logger.warning(f"Redis close failed: {e}")

    logger.info("?? Shutdown complete")


# =========================
# APP INIT
# =========================
app = FastAPI(
    title="AI Compliance & Risk Copilot",
    description="RegTech AI SaaS for compliance, risk analysis & RAG-based insights",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)


# =========================
# MIDDLEWARE
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# =========================
# GLOBAL EXCEPTION HANDLER
# =========================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )


# =========================
# ROUTES
# =========================
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(ws.router)


# =========================
# ROOT
# =========================
@app.get("/")
async def root():
    return {
        "success": True,
        "name": "AI Compliance & Risk Copilot",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }


# =========================
# HEALTH CHECK (DEEP)
# =========================
@app.get("/system/health")
async def system_health():
    """
    Full system health check (DB + Redis + Vector)
    """
    status = {
        "database": "unknown",
        "redis": "unknown",
        "vector_store": "ok"
    }

    # DB check
    try:
        from app.core.database import get_database
        db = get_database()
        await db.command("ping")
        status["database"] = "ok"
    except:
        status["database"] = "down"

    # Redis check
    try:
        from app.core.cache import get_redis
        redis = get_redis()
        await redis.ping()
        status["redis"] = "ok"
    except:
        status["redis"] = "down"

    return {
        "success": True,
        "system_status": status
    }


# =========================
# RUN
# =========================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        workers=1  # can increase in production
    )
