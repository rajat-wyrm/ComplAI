from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from datetime import datetime

from app.core.database import get_database

router = APIRouter()

@router.get("/history")
async def get_history(company_name: Optional[str] = None, limit: int = 50, db = Depends(get_database)):
    try:
        query = {}
        if company_name:
            query['company_name'] = company_name
        
        documents = await db.documents.find(query).sort('upload_date', -1).to_list(length=limit)
        
        companies = await db.documents.distinct('company_name')
        
        history_list = []
        for doc in documents:
            report = doc.get('analysis_report', {})
            history_list.append({
                'document_id': str(doc['_id']),
                'company_name': doc.get('company_name', 'Unknown'),
                'filename': doc.get('filename', 'unknown'),
                'upload_date': doc.get('upload_date', datetime.now()).isoformat(),
                'risk_score': report.get('risk_score', 0),
                'compliance_score': report.get('compliance_score', 0),
                'confidence_score': report.get('confidence_score', 0),
                'issues_count': len(report.get('issues', [])),
                'document_type': report.get('document_type', 'Unknown')
            })
        
        return JSONResponse(content={
            'success': True,
            'documents': history_list,
            'companies': companies,
            'total': len(history_list)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/company/{company_name}")
async def get_company_history(company_name: str, limit: int = 100, db = Depends(get_database)):
    try:
        documents = await db.documents.find({'company_name': company_name}).sort('upload_date', -1).to_list(length=limit)
        
        history_list = []
        for doc in documents:
            report = doc.get('analysis_report', {})
            history_list.append({
                'document_id': str(doc['_id']),
                'filename': doc.get('filename', 'unknown'),
                'upload_date': doc.get('upload_date', datetime.now()).isoformat(),
                'risk_score': report.get('risk_score', 0),
                'compliance_score': report.get('compliance_score', 0)
            })
        
        return JSONResponse(content={
            'success': True,
            'company_name': company_name,
            'documents': history_list,
            'total': len(history_list)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
