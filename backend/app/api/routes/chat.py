"""
Chat endpoint for conversational AI
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.cache import set_cache, get_cache
from inference.decision_engine import decision_engine

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    document_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    context_used: List[str]
    confidence: float
    timestamp: datetime

@router.post("")
async def chat(request: ChatRequest):
    try:
        db = get_db()
        document = await db.documents.find_one({"document_id": request.document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        session_id = request.session_id or str(uuid.uuid4())
        
        cache_key = f"chat:{session_id}:{hash(request.message)}"
        cached_response = await get_cache(cache_key)
        
        if cached_response:
            return ChatResponse(**cached_response)
        
        result = await decision_engine.chat_query(
            query=request.message,
            document_id=request.document_id
        )
        
        chat_message = {
            "session_id": session_id,
            "document_id": request.document_id,
            "message": request.message,
            "response": result["response"],
            "context_used": result["context_used"],
            "confidence": result["confidence"],
            "timestamp": datetime.utcnow()
        }
        
        await db.chat_history.insert_one(chat_message)
        
        response_data = {
            "session_id": session_id,
            "response": result["response"],
            "context_used": result["context_used"],
            "confidence": result["confidence"],
            "timestamp": datetime.utcnow()
        }
        await set_cache(cache_key, response_data, ttl=300)
        
        return ChatResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    try:
        db = get_db()
        cursor = db.chat_history.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
        
        history = []
        async for msg in cursor:
            history.append({
                "message": msg["message"],
                "response": msg["response"],
                "timestamp": msg["timestamp"].isoformat(),
                "confidence": msg.get("confidence", 0)
            })
        
        return {
            "session_id": session_id,
            "history": list(reversed(history)),
            "total": len(history)
        }
        
    except Exception as e:
        logger.exception(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
