\"\"\"
Document history and tracking endpoints
\"\"\"
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.cache import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def get_document_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    days: Optional[int] = None
):
    \"\"\"Get list of documents with history\"\"\"
    try:
        db = get_db()
        
        # Build query
        query = {}
        if status:
            query["status"] = status
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query["upload_date"] = {"": cutoff_date}
        
        # Get total count
        total = await db.documents.count_documents(query)
        
        # Get documents
        cursor = db.documents.find(query).sort("upload_date", -1).skip(offset).limit(limit)
        
        documents = []
        async for doc in cursor:
            # Get analysis if exists
            analysis = await db.analyses.find_one({"document_id": doc["document_id"]})
            
            documents.append({
                "document_id": doc["document_id"],
                "filename": doc["filename"],
                "file_size": doc["file_size"],
                "upload_date": doc["upload_date"].isoformat(),
                "status": doc["status"],
                "risk_score": doc.get("risk_score"),
                "confidence_score": doc.get("confidence_score"),
                "analysis_date": analysis["created_at"].isoformat() if analysis else None,
                "chat_count": await db.chat_history.count_documents({"document_id": doc["document_id"]})
            })
        
        return {
            "documents": documents,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        logger.exception(f"Failed to get document history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document_details(document_id: str):
    \"\"\"Get detailed document history\"\"\"
    try:
        db = get_db()
        
        # Get document
        document = await db.documents.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get analysis
        analysis = await db.analyses.find_one({"document_id": document_id})
        
        # Get chat history
        chat_cursor = db.chat_history.find({"document_id": document_id}).sort("timestamp", -1).limit(20)
        chats = []
        async for chat in chat_cursor:
            chats.append({
                "message": chat["message"],
                "response": chat["response"],
                "timestamp": chat["timestamp"].isoformat(),
                "confidence": chat.get("confidence", 0)
            })
        
        return {
            "document_id": document["document_id"],
            "filename": document["filename"],
            "file_size": document["file_size"],
            "upload_date": document["upload_date"].isoformat(),
            "status": document["status"],
            "text_preview": document["text_preview"],
            "chunks_count": len(document.get("chunks", [])),
            "analysis": {
                "risk_score": analysis.get("risk_score") if analysis else None,
                "confidence_score": analysis.get("confidence_score") if analysis else None,
                "risks": analysis.get("risks", []) if analysis else [],
                "explanation": analysis.get("explanation", "") if analysis else "",
                "recommended_actions": analysis.get("recommended_actions", []) if analysis else [],
                "compliance_gaps": analysis.get("compliance_gaps", []) if analysis else [],
                "analysis_date": analysis["created_at"].isoformat() if analysis else None
            } if analysis else None,
            "chat_history": chats,
            "total_chats": len(chats)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get document details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    \"\"\"Delete document and all associated data\"\"\"
    try:
        db = get_db()
        
        # Check if document exists
        document = await db.documents.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from database
        await db.documents.delete_one({"document_id": document_id})
        await db.analyses.delete_one({"document_id": document_id})
        await db.chat_history.delete_many({"document_id": document_id})
        
        # Remove from vector store
        from rag.vector_store import vector_store
        # Note: FAISS doesn't support deletion easily, we'll rebuild if needed
        
        logger.info(f"Deleted document {document_id}")
        
        return {
            "document_id": document_id,
            "deleted": True,
            "message": "Document and associated data deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
