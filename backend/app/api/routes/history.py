from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from datetime import datetime

from app.core.database import get_database

router = APIRouter()

@router.get("/history")
async def get_history(
    user_id: str = "default_user",
    limit: int = 50,
    db = Depends(get_database)
):
    try:
        documents = await db.documents.find({'user_id': user_id}).sort('upload_date', -1).to_list(length=limit)
        history_list = []
        for doc in documents:
            history_list.append({
                'document_id': str(doc['_id']),
                'company_name': doc.get('company_name', 'Unknown'),
                'filename': doc.get('filename'),
                'upload_date': doc.get('upload_date').isoformat(),
                'risk_score': doc.get('analysis_report', {}).get('risk_score', 0),
                'compliance_score': doc.get('analysis_report', {}).get('compliance_score', 0)
            })
        return JSONResponse(content={'success': True, 'documents': history_list})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{document_id}")
async def get_document_detail(document_id: str, db = Depends(get_database)):
    try:
        doc = await db.documents.find_one({'_id': ObjectId(document_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc['_id'] = str(doc['_id'])
        doc['upload_date'] = doc['upload_date'].isoformat()
        return JSONResponse(content={'success': True, 'document': doc})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
