from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from bson import ObjectId
import logging
from app.services.rag.pipeline import RAGPipeline
from app.services.ai_service import AIService
from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)
rag_pipeline = RAGPipeline()
ai_service = AIService()

class ChatRequest(BaseModel):
    document_id: str
    message: str
    history: List[Dict[str, str]] = []

@router.post("/chat")
async def chat_with_document(
    request: ChatRequest,
    db = Depends(get_database),
    redis_client = Depends(get_redis)
):
    try:
        doc = await db.documents.find_one({'_id': ObjectId(request.document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Retrieve context using RAG
        context = rag_pipeline.retrieve_context(request.message, k=5)

        # Build prompt
        full_text = doc.get('analysis_report', {}).get('full_text', '') or doc.get('document_metadata', {}).get('full_text', '')
        if not full_text:
            full_text = "Document content not available"
        prompt = f"""Based on the document, answer the following question.

Document content (excerpt):
{full_text[:2000]}

Relevant context from vector search:
{context}

User question: {request.message}

Provide a concise, helpful answer focusing on compliance and risk aspects.
"""
        # Use AI service to generate answer
        try:
            if ai_service.deepseek_client:
                response = await ai_service.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a compliance expert assistant. Answer questions based on the provided document."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                answer = response.choices[0].message.content
            elif ai_service.openai_client:
                response = await ai_service.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a compliance expert assistant. Answer questions based on the provided document."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                answer = response.choices[0].message.content
            else:
                # Simple fallback
                answer = f"Based on the document, I found: {context[:500]}. For more detailed guidance, please consult a compliance officer."
        except Exception as e:
            logger.error(f"Chat AI failed: {e}")
            answer = "I'm sorry, I couldn't generate a response at the moment. Please try again later."

        # Store chat history in Redis (optional)
        await redis_client.lpush(f"chat:{request.document_id}", f"{request.message}|{answer}")
        await redis_client.ltrim(f"chat:{request.document_id}", 0, 99)

        return JSONResponse(content={'success': True, 'response': answer})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{document_id}")
async def get_chat_history(document_id: str, redis_client = Depends(get_redis)):
    try:
        raw = await redis_client.lrange(f"chat:{document_id}", 0, 49)
        history = []
        for item in raw:
            parts = item.split('|', 1)
            if len(parts) == 2:
                history.append({'question': parts[0], 'answer': parts[1]})
        return JSONResponse(content={'success': True, 'history': history})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
