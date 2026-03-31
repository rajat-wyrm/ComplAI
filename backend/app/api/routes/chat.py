from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.services.rag.pipeline import RAGPipeline
from app.services.ai_service import AIService
from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()
rag_pipeline = RAGPipeline()
ai_service = AIService()

class ChatRequest(BaseModel):
    document_id: str
    message: str
    history: List[Dict[str, str]] = []

@router.post("/chat")
async def chat_with_document(request: ChatRequest, db = Depends(get_database), redis_client = Depends(get_redis)):
    try:
        document = await db.documents.find_one({'_id': ObjectId(request.document_id)})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        cache_key = f"chat:{request.document_id}:context"
        cached_context = await redis_client.get(cache_key)
        
        if cached_context:
            context = cached_context
        else:
            full_text = document.get('analysis_report', {}).get('full_text', '')
            if not full_text:
                full_text = "Document content not available"
            
            context = rag_pipeline.retrieve_context(request.message, k=5)
            await redis_client.setex(cache_key, 1800, context)
        
        chat_history = ""
        for msg in request.history[-5:]:
            chat_history += f"{msg['role']}: {msg['content']}\n"
        
        prompt = f"""Document Context:
{context}

Chat History:
{chat_history}

User Question: {request.message}

Provide a helpful, accurate answer based on the document context. Focus on compliance, risks, and recommendations."""

        try:
            response = await ai_service.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a compliance expert assistant. Answer questions based on the provided document context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            answer = response.choices[0].message.content
        except:
            answer = f"Based on the document analysis regarding compliance: {context[:500]}\n\nI recommend reviewing the specific clauses mentioned and implementing the suggested controls. For detailed guidance, please consult with a compliance officer."

        await redis_client.lpush(f"chat:{request.document_id}:history", f"{datetime.now().isoformat()}|{request.message}|{answer}")
        await redis_client.ltrim(f"chat:{request.document_id}:history", 0, 99)

        return JSONResponse(content={
            'success': True,
            'response': answer,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{document_id}")
async def get_chat_history(document_id: str, redis_client = Depends(get_redis)):
    try:
        history = await redis_client.lrange(f"chat:{document_id}:history", 0, 49)
        
        chat_history = []
        for item in history:
            parts = item.split('|')
            if len(parts) == 3:
                chat_history.append({
                    'timestamp': parts[0],
                    'question': parts[1],
                    'answer': parts[2]
                })
        
        return JSONResponse(content={
            'success': True,
            'history': chat_history
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
