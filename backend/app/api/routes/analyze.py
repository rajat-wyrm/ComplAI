from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
import shutil
from datetime import datetime
from bson import ObjectId

from app.services.document_processor import DocumentProcessor
from app.services.rag.pipeline import RAGPipeline
from app.services.ai_service import AIService
from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()

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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"backend/uploads/{timestamp}_{file.filename}"
        
        os.makedirs("backend/uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        doc_analysis = document_processor.analyze_document(file_path)
        
        company_name = doc_analysis['company_name']
        full_text = doc_analysis['full_text']
        
        chunks = rag_pipeline.process_document(full_text, {'company': company_name})
        
        context = rag_pipeline.retrieve_context("compliance risks regulations requirements", k=5)
        
        try:
            report = await ai_service.analyze_document(full_text, context)
        except Exception as e:
            logger.warning(f"AI analysis failed, using mock: {e}")
            report = await ai_service.generate_mock_analysis(full_text, company_name)
        
        report['analysis_timestamp'] = datetime.utcnow().isoformat()
        report['document_name'] = file.filename
        
        document_data = {
            'company_name': company_name,
            'filename': file.filename,
            'file_path': file_path,
            'upload_date': datetime.utcnow(),
            'document_metadata': {
                'word_count': doc_analysis['word_count'],
                'character_count': doc_analysis['character_count'],
                'dates_found': doc_analysis['dates'],
                'clauses_count': len(doc_analysis['clauses']),
                'headings_count': len(doc_analysis['headings'])
            },
            'analysis_report': report,
            'chunks_count': len(chunks)
        }
        
        result = await db.documents.insert_one(document_data)
        document_id = str(result.inserted_id)
        
        cache_key = f"company:{company_name}:latest"
        await redis_client.setex(cache_key, 3600, document_id)
        
        history_key = f"company:{company_name}:history"
        await redis_client.lpush(history_key, document_id)
        await redis_client.ltrim(history_key, 0, 99)
        
        os.remove(file_path)
        
        return JSONResponse(content={
            'success': True,
            'document_id': document_id,
            'company_name': company_name,
            'report': report,
            'document_stats': document_data['document_metadata']
        })
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{document_id}")
async def get_analysis(document_id: str, db = Depends(get_database)):
    try:
        document = await db.documents.find_one({'_id': ObjectId(document_id)})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document['_id'] = str(document['_id'])
        document['upload_date'] = document['upload_date'].isoformat()
        
        return JSONResponse(content=document)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
