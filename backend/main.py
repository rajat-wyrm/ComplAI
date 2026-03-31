from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Compliance & Risk Copilot", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import analyze, insights, chat, history, health
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.cache import connect_to_redis, close_redis_connection

app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(insights.router, prefix="/api", tags=["Insights"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(health.router, prefix="/api", tags=["Health"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Compliance Copilot...")
    await connect_to_mongo()
    await connect_to_redis()
    logger.info("All services initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await close_mongo_connection()
    await close_redis_connection()

@app.get("/")
async def root():
    return {
        "message": "AI Compliance & Risk Copilot API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": ["/api/upload", "/api/insights", "/api/chat", "/api/history", "/health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
