"""
Data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Document(BaseModel):
    document_id: str
    filename: str
    file_size: int
    upload_date: datetime
    content: str
    chunks: List[str]
    status: str = "uploaded"

class Analysis(BaseModel):
    analysis_id: str
    document_id: str
    risk_score: float
    confidence_score: float
    risks: List[Dict[str, Any]]
    explanation: str
    recommended_actions: List[str]
    compliance_gaps: List[str]
    created_at: datetime

class ChatMessage(BaseModel):
    session_id: str
    document_id: str
    message: str
    response: str
    timestamp: datetime

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks: int

class AnalysisResponse(BaseModel):
    analysis_id: str
    document_id: str
    status: str
    risk_score: Optional[float] = None
    confidence_score: Optional[float] = None
    risks: Optional[List[Dict]] = None
    explanation: Optional[str] = None
    recommended_actions: Optional[List[str]] = None
