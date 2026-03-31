"""
Document History API (PRODUCTION-GRADE - OPTIMIZED & CONSISTENT)
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.database import get_database

router = APIRouter()
logger = logging.getLogger(__name__)


# =========================
# HELPERS
# =========================
def _serialize_date(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return datetime.utcnow().isoformat()


def _extract_report(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure backward compatibility:
    supports both 'report' and old 'analysis'
    """
    return doc.get("report") or doc.get("analysis") or {}


def _format_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    report = _extract_report(doc)

    return {
        "document_id": doc.get("document_id"),
        "company_name": doc.get("company_name", "Unknown"),
        "filename": doc.get("filename", "unknown"),
        "upload_date": _serialize_date(doc.get("upload_date")),
        "risk_score": report.get("risk_score", 0),
        "compliance_score": report.get("compliance_score", 0),
        "confidence_score": report.get("confidence_score", 0),
        "issues_count": len(report.get("issues", [])),
        "summary": report.get("summary", ""),
        "document_type": report.get("document_type", "Unknown"),
        "status": doc.get("status", "processed")
    }


# =========================
# GET ALL DOCUMENTS (PAGINATED)
# =========================
@router.get("")
async def get_history(
    company_name: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db=Depends(get_database)
):
    """
    Returns paginated document history
    """

    try:
        query = {}

        if company_name:
            query["company_name"] = company_name

        # Fetch documents
        cursor = db.documents.find(query).sort("upload_date", -1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)

        # Total count (for pagination UI)
        total_count = await db.documents.count_documents(query)

        # Unique companies
        companies = await db.documents.distinct("company_name")

        history_list = [_format_document(doc) for doc in documents]

        return JSONResponse(content={
            "success": True,
            "total": total_count,
            "count": len(history_list),
            "documents": history_list,
            "companies": companies,
            "pagination": {
                "limit": limit,
                "skip": skip,
                "has_more": (skip + limit) < total_count
            }
        })

    except Exception as e:
        logger.exception(f"History fetch failed: {str(e)}")

        return JSONResponse(content={
            "success": True,
            "total": 0,
            "count": 0,
            "documents": [],
            "companies": [],
            "pagination": {
                "limit": limit,
                "skip": skip,
                "has_more": False
            }
        })


# =========================
# GET SINGLE DOCUMENT (FULL DATA)
# =========================
@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db=Depends(get_database)
):
    """
    Returns full document + report
    """

    try:
        doc = await db.documents.find_one({"document_id": document_id})

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        report = _extract_report(doc)

        return JSONResponse(content={
            "success": True,
            "document": {
                "document_id": doc.get("document_id"),
                "company_name": doc.get("company_name", "Unknown"),
                "filename": doc.get("filename"),
                "upload_date": _serialize_date(doc.get("upload_date")),
                "report": report,  #  standardized (frontend safe)
                "status": doc.get("status", "processed")
            }
        })

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Get document failed: {str(e)}")

        raise HTTPException(status_code=500, detail="Failed to fetch document")


# =========================
# GET COMPANY HISTORY
# =========================
@router.get("/company/{company_name}")
async def get_company_history(
    company_name: str,
    limit: int = Query(100, ge=1, le=500),
    db=Depends(get_database)
):
    """
    Returns history for a specific company
    """

    try:
        cursor = db.documents.find(
            {"company_name": company_name}
        ).sort("upload_date", -1).limit(limit)

        documents = await cursor.to_list(length=limit)

        history_list = []

        for doc in documents:
            report = _extract_report(doc)

            history_list.append({
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
                "upload_date": _serialize_date(doc.get("upload_date")),
                "risk_score": report.get("risk_score", 0),
                "compliance_score": report.get("compliance_score", 0),
                "confidence_score": report.get("confidence_score", 0),
                "summary": report.get("summary", ""),
                "document_type": report.get("document_type", "Unknown")
            })

        return JSONResponse(content={
            "success": True,
            "company_name": company_name,
            "total": len(history_list),
            "documents": history_list
        })

    except Exception as e:
        logger.exception(f"Company history failed: {str(e)}")

        return JSONResponse(content={
            "success": True,
            "company_name": company_name,
            "total": 0,
            "documents": []
        })
