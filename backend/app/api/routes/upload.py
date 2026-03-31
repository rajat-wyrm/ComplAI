from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from datetime import datetime
import logging

from app.services.document_processor import processor
from app.services.vector_store import vector_store
from app.services.ai_service import AIService
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

ai_service = AIService()

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()

        doc_id = str(uuid.uuid4())

        file_path = await processor.save_upload(content, f"{doc_id}_{file.filename}")
        text = processor.extract_text(file_path)
        chunks = processor.chunk_text(text)

        # 🔥 AI CALL
        analysis = await ai_service.analyze_document(text)

        db = get_db()

        await db.documents.insert_one({
            "document_id": doc_id,
            "filename": file.filename,
            "upload_date": datetime.utcnow(),
            "analysis_report": analysis["report"]
        })

        vector_store.add_document(doc_id, chunks)

        return {
            "success": True,
            "document_id": doc_id,
            "report": analysis["report"]
        }

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Upload failed")