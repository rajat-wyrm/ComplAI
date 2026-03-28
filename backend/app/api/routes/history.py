"""
History endpoint
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def get_document_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    days: Optional[int] = None
):
    try:
        db = get_db()
        
        query = {}
        if status:
            query["status"] = status
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query["upload_date"] = {"$gte": cutoff_date}
        
        total = await db.documents.count_documents(query)
        
        cursor = db.documents.find(query).sort("upload_date", -1).skip(offset).limit(limit)
        
        documents = []
        async for doc in cursor:
            documents.append({
                "document_id": doc["document_id"],
                "filename": doc["filename"],
                "file_size": doc["file_size"],
                "upload_date": doc["upload_date"].isoformat(),
                "status": doc["status"],
                "risk_score": doc.get("risk_score"),
                "confidence_score": doc.get("confidence_score")
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
