\"\"\"
Insights and analytics endpoints
\"\"\"
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.cache import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{document_id}")
async def get_document_insights(document_id: str):
    \"\"\"Get insights for a specific document\"\"\"
    try:
        # Check cache
        cache_key = f"insights:{document_id}"
        cached = await get_cache(cache_key)
        if cached:
            return cached
        
        db = get_db()
        
        # Get document
        document = await db.documents.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get analysis results
        analysis = await db.analyses.find_one({"document_id": document_id})
        
        if not analysis:
            return {
                "document_id": document_id,
                "filename": document["filename"],
                "status": document["status"],
                "message": "Analysis not yet completed"
            }
        
        # Get chat count for this document
        chat_count = await db.chat_history.count_documents({"document_id": document_id})
        
        # Prepare insights
        insights = {
            "document_id": document_id,
            "filename": document["filename"],
            "upload_date": document["upload_date"].isoformat(),
            "status": analysis["status"],
            "risk_score": analysis.get("risk_score", 0),
            "confidence_score": analysis.get("confidence_score", 0),
            "risks": analysis.get("risks", [])[:10],  # Top 10 risks
            "explanation": analysis.get("explanation", ""),
            "recommended_actions": analysis.get("recommended_actions", []),
            "compliance_gaps": analysis.get("compliance_gaps", []),
            "chat_interactions": chat_count,
            "risk_level": _get_risk_level(analysis.get("risk_score", 0)),
            "summary": _generate_summary(analysis)
        }
        
        # Cache for 1 hour
        await set_cache(cache_key, insights, ttl=3600)
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    days: int = Query(30, ge=1, le=365)
):
    \"\"\"Get dashboard summary statistics\"\"\"
    try:
        db = get_db()
        
        # Date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get statistics
        total_documents = await db.documents.count_documents({"upload_date": {"": cutoff_date}})
        analyzed_documents = await db.documents.count_documents({
            "status": "analyzed",
            "upload_date": {"": cutoff_date}
        })
        
        # Get all analyses
        analyses = await db.analyses.find({"created_at": {"": cutoff_date}}).to_list(length=1000)
        
        # Calculate averages
        risk_scores = [a.get("risk_score", 0) for a in analyses if a.get("risk_score")]
        confidence_scores = [a.get("confidence_score", 0) for a in analyses if a.get("confidence_score")]
        
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Risk distribution
        risk_distribution = {
            "critical": len([s for s in risk_scores if s >= 80]),
            "high": len([s for s in risk_scores if 60 <= s < 80]),
            "medium": len([s for s in risk_scores if 40 <= s < 60]),
            "low": len([s for s in risk_scores if 20 <= s < 40]),
            "minimal": len([s for s in risk_scores if s < 20])
        }
        
        # Recent activity
        recent_docs = await db.documents.find(
            {"upload_date": {"": cutoff_date}}
        ).sort("upload_date", -1).limit(10).to_list(length=10)
        
        recent_activity = []
        for doc in recent_docs:
            recent_activity.append({
                "document_id": doc["document_id"],
                "filename": doc["filename"],
                "upload_date": doc["upload_date"].isoformat(),
                "status": doc["status"],
                "risk_score": doc.get("risk_score")
            })
        
        # Chat statistics
        chat_count = await db.chat_history.count_documents({"timestamp": {"": cutoff_date}})
        
        return {
            "period_days": days,
            "total_documents": total_documents,
            "analyzed_documents": analyzed_documents,
            "analysis_rate": round(analyzed_documents / total_documents * 100, 1) if total_documents > 0 else 0,
            "average_risk_score": round(avg_risk, 1),
            "average_confidence_score": round(avg_confidence, 1),
            "risk_distribution": risk_distribution,
            "total_chat_interactions": chat_count,
            "recent_activity": recent_activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/risk")
async def get_risk_trends(
    days: int = Query(90, ge=7, le=365)
):
    \"\"\"Get risk score trends over time\"\"\"
    try:
        db = get_db()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get analyses grouped by day
        pipeline = [
            {"": {"created_at": {"": cutoff_date}}},
            {"": {
                "_id": {
                    "": {"format": "%Y-%m-%d", "date": ""}
                },
                "avg_risk": {"": ""},
                "avg_confidence": {"": ""},
                "count": {"": 1}
            }},
            {"": {"_id": 1}}
        ]
        
        cursor = db.analyses.aggregate(pipeline)
        trends = []
        async for doc in cursor:
            trends.append({
                "date": doc["_id"],
                "average_risk": round(doc["avg_risk"], 1),
                "average_confidence": round(doc["avg_confidence"], 1),
                "documents_analyzed": doc["count"]
            })
        
        return {
            "trends": trends,
            "period_days": days
        }
        
    except Exception as e:
        logger.exception(f"Failed to get risk trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_risk_level(score: float) -> str:
    \"\"\"Get risk level based on score\"\"\"
    if score >= 80:
        return "Critical"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Medium"
    elif score >= 20:
        return "Low"
    else:
        return "Minimal"

def _generate_summary(analysis: dict) -> str:
    \"\"\"Generate a brief summary of analysis\"\"\"
    risk_score = analysis.get("risk_score", 0)
    risk_level = _get_risk_level(risk_score)
    
    summary = f"Risk Assessment: {risk_level} risk level detected (Score: {risk_score:.1f}/100). "
    summary += f"Confidence: {analysis.get('confidence_score', 0):.1f}%. "
    
    risks = analysis.get("risks", [])
    if risks:
        summary += f"Key risks: {', '.join([r.get('description', '')[:50] for r in risks[:3]])}"
    
    return summary
