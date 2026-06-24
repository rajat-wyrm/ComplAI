from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os, shutil, uuid
from datetime import datetime
import logging

from app.services.document_processor import DocumentProcessor
from app.services.rag.pipeline import RAGPipeline
from app.services.ai_service import AIService
from app.services.s3 import s3_service, MAX_FILE_SIZE
from app.core.database import get_database
from app.core.cache import cache_get, cache_set, get_cache_stats
from app.core.websocket import manager
from app.models.database import Document

router = APIRouter()
logger = logging.getLogger(__name__)

document_processor = DocumentProcessor()
rag_pipeline = RAGPipeline()
ai_service = AIService()

@router.post("/upload")
async def upload_and_analyze(
    file: UploadFile = File(...)
):
    try:
        logger.info(f"Received file: {file.filename}")
        # S3: no local directory needed
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_content = await file.read()
        # Validate file
        valid, msg = await s3_service.validate_file(file_content, file.filename)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)

        await manager.broadcast({"type": "upload_started", "filename": file.filename})

        doc_analysis = document_processor.analyze_document(file_path)
        company_name = doc_analysis['company_name']
        full_text = doc_analysis['full_text']

        chunks = rag_pipeline.process_document(full_text, {'company': company_name, 'filename': file.filename})
        context = rag_pipeline.retrieve_context("compliance risks regulations requirements legal", k=5)

        try:
            report = await ai_service.analyze_document(full_text, context)
        except Exception as ai_error:
            logger.warning(f"AI failed, using mock: {ai_error}")
            report = await ai_service.generate_mock_analysis(full_text, company_name)

        report['analysis_timestamp'] = datetime.utcnow().isoformat()
        report['document_name'] = file.filename
        report['file_type'] = file.filename.split('.')[-1]

        doc_id = str(uuid.uuid4())
        new_doc = Document(
            document_id=doc_id,
            company_name=company_name,
            filename=file.filename,
            file_path=file_path,
            upload_date=datetime.utcnow(),
            user_id='default_user',
            role='user',
            document_metadata={
                'word_count': doc_analysis['word_count'],
                'character_count': doc_analysis['character_count'],
                'dates_found': doc_analysis['dates'],
                'clauses_count': len(doc_analysis['clauses']),
                'headings_count': len(doc_analysis['headings'])
            },
            analysis_report=report,
            chunks_count=len(chunks)
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)

        # Cache in Redis
        await redis_client.setex(f"company:{company_name}:latest", 3600, doc_id)
        await redis_client.lpush(f"company:{company_name}:history", doc_id)
        await redis_client.ltrim(f"company:{company_name}:history", 0, 99)

        # S3: file already stored in cloud, no local cleanup needed

        await manager.broadcast({
            "type": "analysis_complete",
            "document_id": doc_id,
            "company_name": company_name,
            "report": report
        })

        return JSONResponse(content={
            'success': True,
            'document_id': doc_id,
            'company_name': company_name,
            'report': report,
            'redirect_url': f'/dashboard?docId={doc_id}'
        })
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        await manager.broadcast({"type": "error", "message": str(e)})
        return JSONResponse(status_code=500, content={'success': False, 'error': str(e)})
