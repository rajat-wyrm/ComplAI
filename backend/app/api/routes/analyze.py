"""
Document analysis endpoint
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid
from datetime import datetime
import logging

from app.services.decision_engine import decision_engine
from app.core.database import get_db
from app.models import AnalyzeRequest, AnalysisResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=AnalysisResponse)
async def analyze_document(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Start document analysis"""
    try:
        db = get_db()
        document = await db.documents.find_one({"document_id": request.document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        analysis_id = str(uuid.uuid4())
        
        # Update status
        await db.documents.update_one(
            {"document_id": request.document_id},
            {"$set": {"status": "processing"}}
        )
        
        # Run analysis in background
        async def run_analysis():
            try:
                analysis = await decision_engine.analyze_document(
                    request.document_id,
                    document["content"]
                )
                
                await db.analyses.insert_one({
                    "analysis_id": analysis_id,
                    "document_id": request.document_id,
                    "risk_score": analysis.get("risk_score"),
                    "confidence_score": analysis.get("confidence_score"),
                    "risks": analysis.get("risks", []),
                    "explanation": analysis.get("explanation", ""),
                    "recommended_actions": analysis.get("recommended_actions", []),
                    "compliance_gaps": analysis.get("compliance_gaps", []),
                    "created_at": datetime.utcnow(),
                    "status": "completed"
                })
                
                await db.documents.update_one(
                    {"document_id": request.document_id},
                    {"$set": {
                        "status": "analyzed",
                        "risk_score": analysis.get("risk_score"),
                        "analysis_id": analysis_id
                    }}
                )
                
                logger.info(f"Analysis completed: {request.document_id}")
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                await db.documents.update_one(
                    {"document_id": request.document_id},
                    {"$set": {"status": "failed"}}
                )
        
        background_tasks.add_task(run_analysis)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            document_id=request.document_id,
            status="processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
