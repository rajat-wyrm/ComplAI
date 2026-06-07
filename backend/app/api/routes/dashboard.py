from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_database
from app.models.database import Document

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    doc_id: Optional[str] = Query(None)):
    if doc_id:
        stmt = select(Document).where(Document.document_id == doc_id)
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        if doc:
            return JSONResponse(content={
                'success': True,
                'current_document': {
                    'id': doc.document_id,
                    'company_name': doc.company_name,
                    'filename': doc.filename,
                    'upload_date': doc.upload_date.isoformat(),
                    'analysis_report': doc.analysis_report
                }
            })
    # Get all docs
    stmt = select(Document).order_by(Document.upload_date.desc()).limit(100)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    docs_list = []
    total_risk = 0
    for d in docs:
        risk = d.analysis_report.get('risk_score', 50) if d.analysis_report else 50
        total_risk += risk
        docs_list.append({
            'document_id': d.document_id,
            'company_name': d.company_name,
            'filename': d.filename,
            'upload_date': d.upload_date.isoformat(),
            'risk_score': risk,
            'compliance_score': d.analysis_report.get('compliance_score', 0) if d.analysis_report else 0
        })
    avg_risk = total_risk / len(docs) if docs else 0
    return JSONResponse(content={
        'success': True,
        'documents': docs_list,
        'analytics': {
            'total_documents': len(docs),
            'average_risk_score': round(avg_risk, 2)
        }
    })
