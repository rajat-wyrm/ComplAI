"""
Chat API (PRODUCTION-GRADE - RAG + CACHE + STABLE AI)

- Uses vector_store for RAG
- Uses OpenAI via ai_service (NO DeepSeek dependency)
- Redis caching (context + history)
- Safe fallbacks (never breaks UI)
- Optimized + async-safe
"""

import logging
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.vector_store import vector_store
from app.services.ai_service import ai_service
from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)


# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    document_id: str
    message: str
    history: List[Dict[str, str]] = []


# =========================
# BUILD CONTEXT (RAG)
# =========================
def build_context(query: str, top_k: int = 5) -> str:
    results = vector_store.search(query, top_k=top_k)

    if not results:
        return "No relevant context found."

    context_chunks = [chunk for chunk, _, _ in results]

    return "\n\n".join(context_chunks[:top_k])


# =========================
# MAIN CHAT ENDPOINT
# =========================
@router.post("")
async def chat_with_document(
    request: ChatRequest,
    db=Depends(get_database),
    redis_client=Depends(get_redis)
):
    try:
        # =========================
        # 1. FETCH DOCUMENT
        # =========================
        document = await db.documents.find_one(
            {"document_id": request.document_id}
        )

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # =========================
        # 2. CACHE CONTEXT
        # =========================
        cache_key = f"chat:{request.document_id}:context:{hash(request.message)}"

        cached_context = await redis_client.get(cache_key)

        if cached_context:
            context = cached_context.decode() if isinstance(cached_context, bytes) else cached_context
        else:
            context = build_context(request.message, top_k=5)

            await redis_client.setex(cache_key, 1800, context)  # 30 min cache

        # =========================
        # 3. BUILD CHAT HISTORY
        # =========================
        chat_history = ""
        for msg in request.history[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            chat_history += f"{role}: {content}\n"

        # =========================
        # 4. PROMPT
        # =========================
        prompt = f"""
You are an AI Compliance Assistant.

Context:
{context}

Chat History:
{chat_history}

User Question:
{request.message}

Instructions:
- Answer strictly based on context
- Be precise and actionable
- Highlight risks, compliance gaps, recommendations
- If unsure, say "Not found in document"
"""

        # =========================
        # 5. AI CALL (OPENAI)
        # =========================
        try:
            response = await ai_service._call_openai(prompt)
            answer = response.strip()
        except Exception as e:
            logger.warning(f"AI chat failed: {e}")
            answer = self_fallback_answer(context)

        # =========================
        # 6. STORE CHAT HISTORY (REDIS)
        # =========================
        history_key = f"chat:{request.document_id}:history"

        entry = f"{datetime.utcnow().isoformat()}|{request.message}|{answer}"

        await redis_client.lpush(history_key, entry)
        await redis_client.ltrim(history_key, 0, 99)

        # =========================
        # 7. RESPONSE
        # =========================
        return JSONResponse(content={
            "success": True,
            "response": answer,
            "timestamp": datetime.utcnow().isoformat()
        })

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Chat failed: {str(e)}")

        return JSONResponse(content={
            "success": True,
            "response": "AI service temporarily unavailable. Please try again.",
            "timestamp": datetime.utcnow().isoformat()
        })


# =========================
# HISTORY ENDPOINT
# =========================
@router.get("/history/{document_id}")
async def get_chat_history(
    document_id: str,
    redis_client=Depends(get_redis)
):
    try:
        history_key = f"chat:{document_id}:history"

        history = await redis_client.lrange(history_key, 0, 49)

        chat_history = []

        for item in history:
            if isinstance(item, bytes):
                item = item.decode()

            parts = item.split("|")

            if len(parts) == 3:
                chat_history.append({
                    "timestamp": parts[0],
                    "question": parts[1],
                    "answer": parts[2]
                })

        return JSONResponse(content={
            "success": True,
            "history": chat_history
        })

    except Exception as e:
        logger.exception(f"Chat history failed: {str(e)}")

        return JSONResponse(content={
            "success": True,
            "history": []
        })


# =========================
# FALLBACK
# =========================
def self_fallback_answer(context: str) -> str:
    return (
        "Based on available document context:\n\n"
        + context[:500]
        + "\n\nRecommendation: Review highlighted clauses and ensure compliance controls are implemented."
    )
