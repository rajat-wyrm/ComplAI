from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.database import get_database

router = APIRouter()

@router.get("/insights")
async def get_insights(db = Depends(get_database)):
    return JSONResponse(content={"message": "Insights endpoint"})
