"""
Insights endpoint
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.cache import get_cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{document_id}")
async def get_document_insights(document_id: str):
    try:
        cached = await get_cache(f"insights:{document_id}")
        if cached:
            return cached
        
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
                "message": "Analysis not yet completed"
            }
        
        insights = {
            "document_id": document_id,
            "filename": document["filename"],
            "upload_date": document["upload_date"].isoformat(),
            "status": analysis["status"],
            "risk_score": analysis.get("risk_score", 0),
            "confidence_score": analysis.get("confidence_score", 0),
            "risks": analysis.get("risks", [])[:10],
            "explanation": analysis.get("explanation", ""),
            "recommended_actions": analysis.get("recommended_actions", []),
            "compliance_gaps": analysis.get("compliance_gaps", [])
        }
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/summary")
async def get_dashboard_summary(days: int = Query(30, ge=1, le=365)):
    try:
        db = get_db()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_documents = await db.documents.count_documents({"upload_date": {"$gte": cutoff_date}})
        analyzed_documents = await db.documents.count_documents({
            "status": "analyzed",
            "upload_date": {"$gte": cutoff_date}
        })
        
        analyses = await db.analyses.find({"created_at": {"$gte": cutoff_date}}).to_list(length=1000)
        
        risk_scores = [a.get("risk_score", 0) for a in analyses if a.get("risk_score")]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            "period_days": days,
            "total_documents": total_documents,
            "analyzed_documents": analyzed_documents,
            "analysis_rate": round(analyzed_documents / total_documents * 100, 1) if total_documents > 0 else 0,
            "average_risk_score": round(avg_risk, 1),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
