from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from bson import ObjectId
from datetime import datetime, timedelta
import logging

from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard")
async def get_dashboard_data(
    doc_id: Optional[str] = Query(None, description="Specific document ID to view"),
    user_id: str = "default_user",  # Will be replaced with actual auth
    db = Depends(get_database),
    redis_client = Depends(get_redis)
):
    try:
        logger.info(f"Fetching dashboard data for user: {user_id}, doc_id: {doc_id}")
        
        # If specific document requested
        if doc_id:
            try:
                document = await db.documents.find_one({'_id': ObjectId(doc_id)})
                if not document:
                    return JSONResponse(
                        status_code=404,
                        content={'success': False, 'error': 'Document not found'}
                    )
                
                # Check access rights
                if document.get('user_id') != user_id and document.get('role') != 'admin':
                    # For now, allow access to all documents (will implement proper auth later)
                    pass
                
                document['_id'] = str(document['_id'])
                document['upload_date'] = document['upload_date'].isoformat()
                
                return JSONResponse(content={
                    'success': True,
                    'current_document': document,
                    'report': document.get('analysis_report', {})
                })
            except Exception as e:
                logger.error(f"Error fetching document {doc_id}: {e}")
                return JSONResponse(
                    status_code=404,
                    content={'success': False, 'error': 'Invalid document ID'}
                )
        
        # Get all documents for the user
        query = {'user_id': user_id}
        documents = await db.documents.find(query).sort('upload_date', -1).to_list(length=100)
        
        if not documents:
            return JSONResponse(content={
                'success': True,
                'documents': [],
                'analytics': {
                    'total_documents': 0,
                    'average_risk_score': 0,
                    'average_compliance_score': 0,
                    'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0}
                }
            })
        
        # Calculate analytics
        total_risk = 0
        total_compliance = 0
        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0}
        recent_docs = []
        
        for doc in documents[:10]:  # Last 10 documents
            report = doc.get('analysis_report', {})
            risk_score = report.get('risk_score', 50)
            total_risk += risk_score
            total_compliance += report.get('compliance_score', 50)
            
            if risk_score < 30:
                risk_distribution['Low'] += 1
            elif risk_score < 70:
                risk_distribution['Medium'] += 1
            else:
                risk_distribution['High'] += 1
            
            recent_docs.append({
                'id': str(doc['_id']),
                'company_name': doc.get('company_name', 'Unknown'),
                'filename': doc.get('filename', 'Unknown'),
                'upload_date': doc.get('upload_date', datetime.now()).isoformat(),
                'risk_score': risk_score,
                'compliance_score': report.get('compliance_score', 50)
            })
        
        doc_count = len(documents)
        
        response_data = {
            'success': True,
            'documents': recent_docs,
            'analytics': {
                'total_documents': doc_count,
                'average_risk_score': round(total_risk / doc_count, 2) if doc_count > 0 else 0,
                'average_compliance_score': round(total_compliance / doc_count, 2) if doc_count > 0 else 0,
                'risk_distribution': risk_distribution,
                'latest_risk_score': recent_docs[0]['risk_score'] if recent_docs else 0,
                'latest_compliance_score': recent_docs[0]['compliance_score'] if recent_docs else 0
            }
        }
        
        # Cache dashboard data for 30 seconds
        await redis_client.setex(f"dashboard:{user_id}", 30, str(response_data))
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Dashboard API error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': str(e)}
        )

@router.get("/dashboard/analytics")
async def get_global_analytics(
    user_id: str = "default_user",
    db = Depends(get_database)
):
    """Get global analytics for admin users"""
    try:
        # Check if user is admin (simplified for now)
        # In production, check user role from auth token
        
        # Get all documents (admin view)
        documents = await db.documents.find({}).sort('upload_date', -1).to_list(length=500)
        
        # Group by company
        company_stats = {}
        for doc in documents:
            company = doc.get('company_name', 'Unknown')
            report = doc.get('analysis_report', {})
            
            if company not in company_stats:
                company_stats[company] = {
                    'documents': [],
                    'risk_scores': [],
                    'compliance_scores': []
                }
            
            company_stats[company]['documents'].append(doc)
            company_stats[company]['risk_scores'].append(report.get('risk_score', 50))
            company_stats[company]['compliance_scores'].append(report.get('compliance_score', 50))
        
        # Calculate company averages
        company_summary = []
        for company, stats in company_stats.items():
            company_summary.append({
                'company_name': company,
                'document_count': len(stats['documents']),
                'average_risk': sum(stats['risk_scores']) / len(stats['risk_scores']) if stats['risk_scores'] else 0,
                'average_compliance': sum(stats['compliance_scores']) / len(stats['compliance_scores']) if stats['compliance_scores'] else 0,
                'latest_document': str(stats['documents'][0]['_id']) if stats['documents'] else None
            })
        
        return JSONResponse(content={
            'success': True,
            'total_documents': len(documents),
            'total_companies': len(company_stats),
            'companies': company_summary,
            'all_documents': [
                {
                    'id': str(doc['_id']),
                    'company_name': doc.get('company_name'),
                    'filename': doc.get('filename'),
                    'upload_date': doc.get('upload_date').isoformat(),
                    'risk_score': doc.get('analysis_report', {}).get('risk_score', 50)
                }
                for doc in documents[:50]
            ]
        })
        
    except Exception as e:
        logger.error(f"Global analytics error: {e}")
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': str(e)}
        )
