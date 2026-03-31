from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from bson import ObjectId
from datetime import datetime, timedelta

from app.core.database import get_database
from app.core.cache import get_redis

router = APIRouter()

@router.get("/insights")
async def get_insights(company_name: str = None, db = Depends(get_database), redis_client = Depends(get_redis)):
    try:
        cache_key = f"insights:{company_name or 'all'}"
        cached = await redis_client.get(cache_key)
        
        if cached:
            return JSONResponse(content=eval(cached))
        
        query = {}
        if company_name:
            query['company_name'] = company_name
        
        documents = await db.documents.find(query).to_list(length=100)
        
        if not documents:
            return JSONResponse(content={
                'total_documents': 0,
                'average_risk_score': 0,
                'average_compliance_score': 0,
                'average_confidence_score': 0,
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                'category_distribution': {},
                'recent_trends': [],
                'top_issues': []
            })
        
        total_risk = 0
        total_compliance = 0
        total_confidence = 0
        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0}
        category_distribution = {}
        issue_count = {}
        
        for doc in documents:
            report = doc.get('analysis_report', {})
            
            risk_score = report.get('risk_score', 50)
            total_risk += risk_score
            
            compliance_score = report.get('compliance_score', 50)
            total_compliance += compliance_score
            
            confidence_score = report.get('confidence_score', 50)
            total_confidence += confidence_score
            
            if risk_score < 30:
                risk_distribution['Low'] += 1
            elif risk_score < 70:
                risk_distribution['Medium'] += 1
            else:
                risk_distribution['High'] += 1
            
            issues = report.get('issues', [])
            for issue in issues:
                category = issue.get('category', 'Other')
                category_distribution[category] = category_distribution.get(category, 0) + 1
                
                title = issue.get('title', 'Unknown')
                issue_count[title] = issue_count.get(title, 0) + 1
        
        doc_count = len(documents)
        top_issues = sorted(issue_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        recent_docs = sorted(documents, key=lambda x: x.get('upload_date', datetime.min), reverse=True)[:30]
        recent_trends = []
        for doc in recent_docs:
            recent_trends.append({
                'date': doc.get('upload_date', datetime.now()).isoformat(),
                'risk_score': doc.get('analysis_report', {}).get('risk_score', 50),
                'compliance_score': doc.get('analysis_report', {}).get('compliance_score', 50),
                'company': doc.get('company_name', 'Unknown')
            })
        
        insights = {
            'total_documents': doc_count,
            'average_risk_score': round(total_risk / doc_count, 2) if doc_count > 0 else 0,
            'average_compliance_score': round(total_compliance / doc_count, 2) if doc_count > 0 else 0,
            'average_confidence_score': round(total_confidence / doc_count, 2) if doc_count > 0 else 0,
            'risk_distribution': risk_distribution,
            'category_distribution': category_distribution,
            'recent_trends': recent_trends[:20],
            'top_issues': [{'issue': issue, 'count': count} for issue, count in top_issues]
        }
        
        await redis_client.setex(cache_key, 300, str(insights))
        
        return JSONResponse(content=insights)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_name}/analytics")
async def get_company_analytics(company_name: str, db = Depends(get_database)):
    try:
        documents = await db.documents.find({'company_name': company_name}).sort('upload_date', -1).to_list(length=50)
        
        if not documents:
            raise HTTPException(status_code=404, detail="Company not found")
        
        risk_scores = []
        compliance_scores = []
        dates = []
        
        for doc in documents:
            report = doc.get('analysis_report', {})
            risk_scores.append(report.get('risk_score', 50))
            compliance_scores.append(report.get('compliance_score', 50))
            dates.append(doc.get('upload_date', datetime.now()).isoformat())
        
        analytics = {
            'company_name': company_name,
            'total_documents': len(documents),
            'latest_risk_score': risk_scores[0] if risk_scores else 0,
            'latest_compliance_score': compliance_scores[0] if compliance_scores else 0,
            'risk_trend': risk_scores,
            'compliance_trend': compliance_scores,
            'dates': dates,
            'average_risk': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            'improvement_rate': ((risk_scores[-1] - risk_scores[0]) / risk_scores[0] * 100) if len(risk_scores) > 1 and risk_scores[0] > 0 else 0
        }
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
