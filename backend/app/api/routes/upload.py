"""
File upload endpoint
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from processing.document_processor import processor
from app.core.database import get_db
from app.core.cache import set_cache
from app.core.exceptions import DocumentProcessingError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        processor.validate_file(file.filename, len(content))
        
        document_id = str(uuid.uuid4())
        file_path = await processor.save_upload(content, f"{document_id}_{file.filename}")
        
        text = processor.extract_text(file_path)
        cleaned_text = processor.clean_text(text)
        chunks = processor.chunk_text(cleaned_text)
        
        db = get_db()
        document = {
            "document_id": document_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "upload_date": datetime.utcnow(),
            "text_preview": cleaned_text[:500],
            "chunks": chunks,
            "status": "uploaded"
        }
        
        await db.documents.insert_one(document)
        await set_cache(f"doc:{document_id}", {"id": document_id, "filename": file.filename}, ttl=3600)
        
        logger.info(f"Document uploaded: {document_id} - {file.filename}")
        
        return JSONResponse(
            status_code=201,
            content={
                "document_id": document_id,
                "filename": file.filename,
                "file_size": len(content),
                "chunks": len(chunks),
                "status": "uploaded",
                "message": "Document uploaded successfully"
            }
        )
        
    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {e}")
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.exception(f"Unexpected error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
