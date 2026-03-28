\"\"\"
Document analysis endpoint
\"\"\"
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.cache import set_cache
from inference.decision_engine import decision_engine
from rag.vector_store import vector_store

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalyzeRequest(BaseModel):
    document_id: str

@router.post("")
async def analyze_document(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    try:
        db = get_db()
        document = await db.documents.find_one({"document_id": request.document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        await db.documents.update_one(
            {"document_id": request.document_id},
            {"": {"status": "processing"}}
        )
        
        analysis_id = str(uuid.uuid4())
        
        if not any(m.get("document_id") == request.document_id for m in vector_store.metadata):
            vector_store.add_document(
                request.document_id,
                document["chunks"],
                {"filename": document["filename"]}
            )
        
        async def process_analysis():
            try:
                analysis = await decision_engine.analyze_document(
                    request.document_id,
                    document["text_preview"]
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
                    {"": {
                        "status": "analyzed",
                        "analysis_id": analysis_id,
                        "risk_score": analysis.get("risk_score"),
                        "confidence_score": analysis.get("confidence_score")
                    }}
                )
                
                await set_cache(f"analysis:{analysis_id}", analysis, ttl=3600)
                logger.info(f"Analysis completed for {request.document_id}")
                
            except Exception as e:
                logger.error(f"Background analysis failed: {e}")
                await db.documents.update_one(
                    {"document_id": request.document_id},
                    {"": {"status": "failed"}}
                )
        
        background_tasks.add_task(process_analysis)
        
        return {
            "analysis_id": analysis_id,
            "document_id": request.document_id,
            "status": "processing",
            "message": "Analysis started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
