from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_database
from app.models.database import Document

router = APIRouter()

@router.get("/insights")
async def get_insights():
    stmt = select(Document).order_by(Document.upload_date.desc())
    result = await db.execute(stmt)
    docs = result.scalars().all()
    total = len(docs)
    avg_risk = sum(d.analysis_report.get('risk_score', 0) for d in docs if d.analysis_report) / total if total else 0
    return JSONResponse(content={'total_documents': total, 'average_risk_score': round(avg_risk, 2)})
