"""
Database models for compliance system
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Document(BaseModel):
    """Document model"""
    document_id: str
    filename: str
    file_path: str
    file_size: int
    upload_date: datetime
    text_preview: str
    chunks: List[str]
    status: str  # uploaded, processing, analyzed, failed
    analysis_id: Optional[str] = None
    risk_score: Optional[float] = None
    confidence_score: Optional[float] = None

class AnalysisResult(BaseModel):
    """Analysis result model"""
    analysis_id: str
    document_id: str
    risk_score: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    risks: List[Dict[str, Any]]
    explanation: str
    recommended_actions: List[str]
    created_at: datetime
    status: str  # completed, processing, failed

class ChatMessage(BaseModel):
    """Chat message model"""
    session_id: str
    message: str
    response: str
    timestamp: datetime
    context_used: List[str]
