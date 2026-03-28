\"\"\"
Health check endpoint
\"\"\"
from fastapi import APIRouter
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Compliance & Risk Copilot",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": {"status": "up", "message": "API is operational"},
            "database": {"status": "pending", "message": "Requires MongoDB"},
            "redis": {"status": "pending", "message": "Requires Redis"},
            "vector_store": {"status": "pending", "message": "Initialized on first upload"}
        }
    }
