from fastapi import APIRouter
from app.core.database import get_db

router = APIRouter()

@router.get("")
async def get_insights():
    db = get_db()
    docs = await db.documents.find().to_list(100)

    if not docs:
        return {
            "total_documents": 0,
            "average_risk_score": 0,
            "average_compliance_score": 0,
            "average_confidence_score": 0
        }

    total = len(docs)

    risk = sum(d.get("analysis_report", {}).get("risk_score", 0) for d in docs) / total
    comp = sum(d.get("analysis_report", {}).get("compliance_score", 0) for d in docs) / total

    return {
        "total_documents": total,
        "average_risk_score": round(risk, 2),
        "average_compliance_score": round(comp, 2),
        "average_confidence_score": 85
    }