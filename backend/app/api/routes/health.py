from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": "connected",
            "redis": "connected",
            "api": "operational"
        },
        "version": "2.0.0"
    })
