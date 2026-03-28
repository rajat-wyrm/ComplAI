\"\"\"
Health check endpoints
\"\"\"
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Compliance & Risk Copilot",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check():
    \"\"\"Detailed health check with component status\"\"\"
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": {"status": "up", "message": "API is operational"},
            "database": {"status": "pending", "message": "Not initialized yet"},
            "redis": {"status": "pending", "message": "Not initialized yet"},
            "vector_store": {"status": "pending", "message": "Not initialized yet"}
        }
    }
    return health_status
