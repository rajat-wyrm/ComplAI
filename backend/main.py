import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Compliance & Risk Copilot",
    version="2.0.0",
    description="Production-grade AI compliance analysis platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import analyze, insights, chat, history, health, dashboard, websocket
from app.api.routes import auth as auth_router

app.include_router(auth_router.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(analyze.router,          prefix="/api",           tags=["Analysis"])
app.include_router(insights.router,         prefix="/api",           tags=["Insights"])
app.include_router(chat.router,             prefix="/api",           tags=["Chat"])
app.include_router(history.router,          prefix="/api",           tags=["History"])
app.include_router(health.router,           prefix="/api",           tags=["Health"])
app.include_router(dashboard.router,        prefix="/api",           tags=["Dashboard"])
app.include_router(websocket.router,        prefix="",               tags=["WebSocket"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Compliance Copilot...")
    from app.core.database import connect_to_postgres
    from app.core.cache import connect_to_redis
    await connect_to_postgres()
    await connect_to_redis()
    logger.info("All services initialized")

@app.on_event("shutdown")
async def shutdown_event():
    from app.core.database import close_postgres_connection
    from app.core.cache import close_redis_connection
    await close_postgres_connection()
    await close_redis_connection()

@app.get("/")
async def root():
    return {
        "message": "AI Compliance & Risk Copilot API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
