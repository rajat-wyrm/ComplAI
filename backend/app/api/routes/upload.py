"""
File upload endpoint
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
import logging

from app.services.document_processor import processor
from app.services.vector_store import vector_store
from app.core.database import get_db
from app.models import UploadResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a document for analysis"""
    try:
        content = await file.read()
        processor.validate_file(file.filename, len(content))
        
        doc_id = str(uuid.uuid4())
        file_path = await processor.save_upload(content, f"{doc_id}_{file.filename}")
        
        text = processor.extract_text(file_path)
        chunks = processor.chunk_text(text)
        
        db = get_db()
        document = {
            "document_id": doc_id,
            "filename": file.filename,
            "file_size": len(content),
            "upload_date": datetime.utcnow(),
            "content": text[:5000],
            "chunks": chunks,
            "status": "uploaded"
        }
        
        await db.documents.insert_one(document)
        
        # Add to vector store
        vector_store.add_document(doc_id, chunks)
        
        logger.info(f"Uploaded: {doc_id} - {file.filename}")
        
        return UploadResponse(
            document_id=doc_id,
            filename=file.filename,
            status="uploaded",
            chunks=len(chunks)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
