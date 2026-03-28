\"\"\"
Document analysis endpoint
\"\"\"
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.cache import set_cache, get_cache
from inference.decision_engine import decision_engine
from rag.vector_store import vector_store

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalyzeRequest(BaseModel):
    document_id: str
    session_id: Optional[str] = None

@router.post("")
async def analyze_document(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    \"\"\"Analyze a document for compliance risks\"\"\"
    try:
        # Get document from database
        db = get_db()
        document = await db.documents.find_one({"document_id": request.document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update status
        await db.documents.update_one(
            {"document_id": request.document_id},
            {"": {"status": "processing"}}
        )
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Add to vector store if not already there
        if not any(m.get("document_id") == request.document_id for m in vector_store.metadata):
            vector_store.add_document(
                request.document_id,
                document["chunks"],
                {"filename": document["filename"]}
            )
        
        # Run analysis in background
        background_tasks.add_task(
            process_analysis,
            request.document_id,
            document["text_preview"],
            analysis_id
        )
        
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

async def process_analysis(document_id: str, text: str, analysis_id: str):
    \"\"\"Background task for document analysis\"\"\"
    try:
        # Run decision engine
        analysis = await decision_engine.analyze_document(document_id, text)
        
        # Save results
        db = get_db()
        await db.analyses.insert_one({
            "analysis_id": analysis_id,
            "document_id": document_id,
            "risk_score": analysis.get("risk_score"),
            "confidence_score": analysis.get("confidence_score"),
            "risks": analysis.get("risks", []),
            "explanation": analysis.get("explanation", ""),
            "recommended_actions": analysis.get("recommended_actions", []),
            "compliance_gaps": analysis.get("compliance_gaps", []),
            "created_at": datetime.utcnow(),
            "status": "completed"
        })
        
        # Update document
        await db.documents.update_one(
            {"document_id": document_id},
            {"": {
                "status": "analyzed",
                "analysis_id": analysis_id,
                "risk_score": analysis.get("risk_score"),
                "confidence_score": analysis.get("confidence_score")
            }}
        )
        
        # Cache results
        await set_cache(f"analysis:{analysis_id}", analysis, ttl=3600)
        
        logger.info(f"Analysis completed for {document_id}")
        
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")
        await db.documents.update_one(
            {"document_id": document_id},
            {"": {"status": "failed"}}
        )
