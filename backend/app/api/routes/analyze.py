from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
import logging

from app.services.document_processor import DocumentProcessor
from app.services.rag.pipeline import RAGPipeline
from app.services.ai_service import AIService
from app.core.database import get_database
from app.core.cache import get_redis
from app.core.websocket import manager

router = APIRouter()
logger = logging.getLogger(__name__)

document_processor = DocumentProcessor()
rag_pipeline = RAGPipeline()
ai_service = AIService()

@router.post("/upload")
async def upload_and_analyze(
    file: UploadFile = File(...),
    db = Depends(get_database),
    redis_client = Depends(get_redis)
):
    try:
        logger.info(f"Received file: {file.filename}")
        os.makedirs("uploads", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = f"uploads/{safe_filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # WebSocket: processing started
        await manager.broadcast({"type": "upload_started", "filename": file.filename})

        # Extract text and metadata
        doc_analysis = document_processor.analyze_document(file_path)
        company_name = doc_analysis['company_name']
        full_text = doc_analysis['full_text']

        await manager.broadcast({"type": "processing", "stage": "text_extracted"})

        # Process through RAG (chunk and embed)
        chunks = rag_pipeline.process_document(full_text, {'company': company_name, 'filename': file.filename})
        await manager.broadcast({"type": "processing", "stage": "chunked", "chunks": len(chunks)})

        # Retrieve relevant context (optional, but can help AI)
        context = rag_pipeline.retrieve_context("compliance risks regulations requirements", k=5)

        await manager.broadcast({"type": "processing", "stage": "ai_analysis"})

        # Get AI analysis
        report = await ai_service.analyze_document(full_text, context)
        report['analysis_timestamp'] = datetime.utcnow().isoformat()
        report['document_name'] = file.filename

        # Add metadata from document processor
        report['company_name'] = company_name
        report['document_metadata'] = {
            'word_count': doc_analysis['word_count'],
            'character_count': doc_analysis['character_count'],
            'dates_found': doc_analysis['dates'],
            'clauses_count': len(doc_analysis['clauses']),
            'headings_count': len(doc_analysis['headings'])
        }

        # Save to database
        document_data = {
            'company_name': company_name,
            'filename': file.filename,
            'file_path': file_path,
            'upload_date': datetime.utcnow(),
            'user_id': 'default_user',  # TODO: add authentication
            'role': 'user',
            'document_metadata': doc_analysis,
            'analysis_report': report,
            'chunks_count': len(chunks)
        }
        result = await db.documents.insert_one(document_data)
        document_id = str(result.inserted_id)

        # Clean up temp file
        os.remove(file_path)

        # WebSocket: completion
        await manager.broadcast({
            "type": "analysis_complete",
            "document_id": document_id,
            "company_name": company_name,
            "report": report
        })

        return JSONResponse(content={
            'success': True,
            'document_id': document_id,
            'company_name': company_name,
            'report': report,
            'redirect_url': f'/dashboard?docId={document_id}'
        })

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        await manager.broadcast({"type": "error", "message": str(e)})
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': str(e)}
        )
