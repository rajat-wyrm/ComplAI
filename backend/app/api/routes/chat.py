"""
Chat endpoint for conversational AI
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import logging

from app.services.decision_engine import decision_engine
from app.core.database import get_db

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

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with a document"""
    try:
        db = get_db()
        document = await db.documents.find_one({"document_id": request.document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        session_id = request.session_id or str(uuid.uuid4())
        
        result = await decision_engine.chat(request.document_id, request.message)
        
        # Save chat history
        await db.chat_history.insert_one({
            "session_id": session_id,
            "document_id": request.document_id,
            "message": request.message,
            "response": result["response"],
            "timestamp": datetime.utcnow()
        })
        
        return ChatResponse(
            session_id=session_id,
            response=result["response"],
            context_used=result["context_used"],
            confidence=result["confidence"],
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        db = get_db()
        cursor = db.chat_history.find({"session_id": session_id}).sort("timestamp", -1).limit(50)
        
        history = []
        async for msg in cursor:
            history.append({
                "message": msg["message"],
                "response": msg["response"],
                "timestamp": msg["timestamp"].isoformat()
            })
        
        return {
            "session_id": session_id,
            "history": list(reversed(history)),
            "total": len(history)
        }
        
    except Exception as e:
        logger.exception(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
