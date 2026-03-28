"""
Insights and dashboard endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import logging

from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard")
async def get_dashboard(days: int = Query(30, ge=1, le=365)):
    """Get dashboard metrics"""
    try:
        db = get_db()
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        total_docs = await db.documents.count_documents({"upload_date": {"$gte": cutoff}})
        analyzed_docs = await db.documents.count_documents({
            "upload_date": {"$gte": cutoff},
            "status": "analyzed"
        })
        
        analyses = await db.analyses.find({"created_at": {"$gte": cutoff}}).to_list(1000)
        
        risk_scores = [a.get("risk_score", 0) for a in analyses if a.get("risk_score")]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            "total_documents": total_docs,
            "analyzed_documents": analyzed_docs,
            "average_risk_score": round(avg_risk, 1),
            "period_days": days
        }
        
    except Exception as e:
        logger.exception(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_insights(document_id: str):
    """Get insights for a document"""
    try:
        db = get_db()
        
        document = await db.documents.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        analysis = await db.analyses.find_one({"document_id": document_id})
        
        if not analysis:
            return {
                "document_id": document_id,
                "filename": document["filename"],
                "status": document["status"],
                "message": "Analysis pending"
            }
        
        return {
            "document_id": document_id,
            "filename": document["filename"],
            "upload_date": document["upload_date"].isoformat(),
            "status": analysis["status"],
            "risk_score": analysis.get("risk_score"),
            "confidence_score": analysis.get("confidence_score"),
            "risks": analysis.get("risks", []),
            "explanation": analysis.get("explanation", ""),
            "recommended_actions": analysis.get("recommended_actions", []),
            "compliance_gaps": analysis.get("compliance_gaps", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
