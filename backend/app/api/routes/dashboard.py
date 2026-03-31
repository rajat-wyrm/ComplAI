from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from datetime import datetime
from app.core.database import get_database

router = APIRouter()

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
            # Also get trends for that company
            company = doc.get('company_name')
            if company:
                other_docs = await db.documents.find({'company_name': company}).sort('upload_date', -1).to_list(length=10)
                trend = []
                for d in other_docs:
                    report = d.get('analysis_report', {})
                    trend.append({
                        'date': d['upload_date'].isoformat(),
                        'risk': report.get('risk_score', 0),
                        'compliance': report.get('compliance_score', 0)
                    })
                doc['risk_trend'] = trend
            return JSONResponse(content={'success': True, 'current_document': doc})
    # No specific doc, return all docs with analytics
    docs = await db.documents.find({}).sort('upload_date', -1).to_list(length=100)
    total_risk = 0
    total_compliance = 0
    risk_dist = {'Low': 0, 'Medium': 0, 'High': 0}
    for d in docs:
        report = d.get('analysis_report', {})
        risk = report.get('risk_score', 0)
        total_risk += risk
        total_compliance += report.get('compliance_score', 0)
        if risk < 30:
            risk_dist['Low'] += 1
        elif risk < 70:
            risk_dist['Medium'] += 1
        else:
            risk_dist['High'] += 1
        d['_id'] = str(d['_id'])
        d['upload_date'] = d['upload_date'].isoformat()
    avg_risk = total_risk / len(docs) if docs else 0
    avg_compliance = total_compliance / len(docs) if docs else 0
    analytics = {
        'total_documents': len(docs),
        'average_risk_score': avg_risk,
        'average_compliance_score': avg_compliance,
        'risk_distribution': risk_dist,
        'latest_risk_score': docs[0].get('analysis_report', {}).get('risk_score', 0) if docs else 0,
        'latest_compliance_score': docs[0].get('analysis_report', {}).get('compliance_score', 0) if docs else 0
    }
    return JSONResponse(content={'success': True, 'documents': docs, 'analytics': analytics})
