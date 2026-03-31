from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
import shutil
from datetime import datetime
from bson import ObjectId
import logging

from app.services.document_processor import DocumentProcessor
from app.services.rag.pipeline import RAGPipeline
from app.services.ai_service import AIService
from app.core.database import get_database
from app.core.cache import get_redis

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
        
        # Create uploads directory if not exists
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = f"uploads/{safe_filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved to {file_path}")
        
        # Extract text and analyze document
        doc_analysis = document_processor.analyze_document(file_path)
        company_name = doc_analysis['company_name']
        full_text = doc_analysis['full_text']
        
        logger.info(f"Document analyzed. Company: {company_name}, Text length: {len(full_text)}")
        
        # Process through RAG pipeline
        chunks = rag_pipeline.process_document(full_text, {'company': company_name, 'filename': file.filename})
        logger.info(f"Document chunked into {len(chunks)} chunks")
        
        # Retrieve relevant context
        context = rag_pipeline.retrieve_context("compliance risks regulations requirements legal", k=5)
        
        # Run AI analysis
        try:
            logger.info("Starting AI analysis...")
            report = await ai_service.analyze_document(full_text, context)
            logger.info("AI analysis completed successfully")
        except Exception as ai_error:
            logger.warning(f"AI analysis failed, using mock: {ai_error}")
            report = await ai_service.generate_mock_analysis(full_text, company_name)
        
        # Add metadata to report
        report['analysis_timestamp'] = datetime.utcnow().isoformat()
        report['document_name'] = file.filename
        report['file_type'] = file.filename.split('.')[-1]
        
        # Prepare document for database
        document_data = {
            'company_name': company_name,
            'filename': file.filename,
            'file_path': file_path,
            'upload_date': datetime.utcnow(),
            'user_id': 'default_user',  # Will be replaced with actual user ID when auth is added
            'role': 'user',
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
        
        # Save to MongoDB
        result = await db.documents.insert_one(document_data)
        document_id = str(result.inserted_id)
        logger.info(f"Document saved to MongoDB with ID: {document_id}")
        
        # Cache the latest report for this company
        cache_key = f"company:{company_name}:latest"
        await redis_client.setex(cache_key, 3600, document_id)
        
        # Add to company history
        history_key = f"company:{company_name}:history"
        await redis_client.lpush(history_key, document_id)
        await redis_client.ltrim(history_key, 0, 99)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
            logger.info(f"Temporary file removed: {file_path}")
        except:
            pass
        
        # Return success response
        response_data = {
            'success': True,
            'document_id': document_id,
            'company_name': company_name,
            'report': report,
            'redirect_url': f'/dashboard?docId={document_id}',
            'document_stats': document_data['document_metadata']
        }
        
        logger.info(f"Upload successful. Returning document ID: {document_id}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'error': str(e),
                'message': 'Failed to process document'
            }
        )
