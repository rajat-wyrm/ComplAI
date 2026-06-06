from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from app.core.database import get_database
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard")
async def get_dashboard_data(
    doc_id: Optional[str] = Query(None),
    db = Depends(get_database)
):
    if doc_id:
        doc = await db.documents.find_one({'_id': ObjectId(doc_id)})
        if doc:
            doc['_id'] = str(doc['_id'])
            doc['upload_date'] = doc['upload_date'].isoformat()
            return JSONResponse(content={'success': True, 'current_document': doc})

    docs = await db.documents.find({}).sort('upload_date', -1).to_list(length=100)
    total_risk = 0
    total_compliance = 0
    risk_dist = {'Low': 0, 'Medium': 0, 'High': 0}
    category_counts = {}  # For issue categories
    for d in docs:
        report = d.get('analysis_report', {})
        risk = report.get('risk_score', 50)
        total_risk += risk
        total_compliance += report.get('compliance_score', 50)
        if risk < 30: risk_dist['Low'] += 1
        elif risk < 70: risk_dist['Medium'] += 1
        else: risk_dist['High'] += 1
        # Count issue categories
        for issue in report.get('issues', []):
            cat = issue.get('category', 'Other')
            category_counts[cat] = category_counts.get(cat, 0) + 1

    doc_count = len(docs)
    avg_risk = total_risk / doc_count if doc_count else 0
    avg_compliance = total_compliance / doc_count if doc_count else 0
    top_issues = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    analytics = {
        'total_documents': doc_count,
        'average_risk_score': round(avg_risk, 2),
        'average_compliance_score': round(avg_compliance, 2),
        'risk_distribution': risk_dist,
        'latest_risk_score': docs[0].get('analysis_report', {}).get('risk_score', 0) if docs else 0,
        'latest_compliance_score': docs[0].get('analysis_report', {}).get('compliance_score', 0) if docs else 0,
        'top_issue_categories': [{'category': k, 'count': v} for k, v in top_issues]
    }

    for d in docs:
        d['_id'] = str(d['_id'])
        d['upload_date'] = d['upload_date'].isoformat()

    return JSONResponse(content={'success': True, 'documents': docs, 'analytics': analytics})
