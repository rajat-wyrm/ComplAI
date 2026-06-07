from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_database
from app.models.database import Document

router = APIRouter()

@router.get("/history")
async def get_history(
    user_id: str = "default_user",
    limit: int = 50):
    stmt = select(Document).where(Document.user_id == user_id).order_by(Document.upload_date.desc()).limit(limit)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    history = []
    for d in docs:
        history.append({
            'document_id': d.document_id,
            'company_name': d.company_name,
            'filename': d.filename,
            'upload_date': d.upload_date.isoformat(),
            'risk_score': d.analysis_report.get('risk_score', 0) if d.analysis_report else 0,
            'compliance_score': d.analysis_report.get('compliance_score', 0) if d.analysis_report else 0
        })
    return JSONResponse(content={'success': True, 'documents': history})

@router.get("/history/{document_id}")
async def get_document_detail(document_id: str):
    stmt = select(Document).where(Document.document_id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(content={
        'success': True,
        'document': {
            'document_id': doc.document_id,
            'company_name': doc.company_name,
            'filename': doc.filename,
            'upload_date': doc.upload_date.isoformat(),
            'analysis_report': doc.analysis_report
        }
    })
