"""
Health check endpoint
"""
from fastapi import APIRouter
from datetime import datetime
from app.models import HealthResponse

router = APIRouter()

@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="AI Compliance & Risk Copilot",
        version="1.0.0"
    )
