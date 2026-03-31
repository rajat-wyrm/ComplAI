"""
Document History API (FINAL - FIXED & OPTIMIZED)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

from app.core.database import get_database

router = APIRouter()


# =========================
# GET ALL DOCUMENTS
# =========================
@router.get("/history")
async def get_history(
    company_name: Optional[str] = None,
    limit: int = 50,
    db=Depends(get_database)
):
    try:
        query = {}

        if company_name:
            query["company_name"] = company_name

        documents = await db.documents.find(query).sort("upload_date", -1).to_list(length=limit)

        # get unique companies
        companies = await db.documents.distinct("company_name")

        history_list = []

        for doc in documents:
            report = doc.get("analysis", {})  # ✅ FIXED

            history_list.append({
                "document_id": doc.get("document_id"),  # ✅ FIXED
                "company_name": doc.get("company_name", "Unknown"),
                "filename": doc.get("filename", "unknown"),
                "upload_date": (
                    doc.get("upload_date").isoformat()
                    if doc.get("upload_date")
                    else datetime.utcnow().isoformat()
                ),
                "risk_score": report.get("risk_score", 0),
                "compliance_score": report.get("compliance_score", 0),
                "confidence_score": report.get("confidence_score", 0),
                "issues_count": len(report.get("issues", [])),
                "summary": report.get("summary", ""),
                "status": doc.get("status", "processed")
            })

        return JSONResponse(content={
            "success": True,
            "total": len(history_list),
            "documents": history_list,
            "companies": companies
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# GET SINGLE DOCUMENT FULL DATA
# =========================
@router.get("/history/{document_id}")
async def get_document(document_id: str, db=Depends(get_database)):
    try:
        doc = await db.documents.find_one({"document_id": document_id})

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return JSONResponse(content={
            "success": True,
            "document": {
                "document_id": doc.get("document_id"),
                "company_name": doc.get("company_name", "Unknown"),
                "filename": doc.get("filename"),
                "upload_date": (
                    doc.get("upload_date").isoformat()
                    if doc.get("upload_date")
                    else datetime.utcnow().isoformat()
                ),
                "analysis": doc.get("analysis", {})
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# GET COMPANY HISTORY
# =========================
@router.get("/history/company/{company_name}")
async def get_company_history(
    company_name: str,
    limit: int = 100,
    db=Depends(get_database)
):
    try:
        documents = await db.documents.find(
            {"company_name": company_name}
        ).sort("upload_date", -1).to_list(length=limit)

        history_list = []

        for doc in documents:
            report = doc.get("analysis", {})  # ✅ FIXED

            history_list.append({
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
                "upload_date": (
                    doc.get("upload_date").isoformat()
                    if doc.get("upload_date")
                    else datetime.utcnow().isoformat()
                ),
                "risk_score": report.get("risk_score", 0),
                "compliance_score": report.get("compliance_score", 0),
                "summary": report.get("summary", "")
            })

        return JSONResponse(content={
            "success": True,
            "company_name": company_name,
            "total": len(history_list),
            "documents": history_list
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))