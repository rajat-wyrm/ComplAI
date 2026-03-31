from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Issue(BaseModel):
    title: str
    severity: str  # Low, Medium, High
    category: str
    description: str
    recommendation: str

class ComplianceReport(BaseModel):
    company_name: str
    document_type: str
    risk_score: int = Field(ge=0, le=100)
    compliance_score: int = Field(ge=0, le=100)
    issues: List[Issue]
    summary: str
    next_actions: List[str]
    confidence_score: int = Field(ge=0, le=100)
    analysis_timestamp: Optional[str] = None
    document_name: Optional[str] = None

class DocumentMetadata(BaseModel):
    word_count: int
    character_count: int
    dates_found: List[str]
    clauses_count: int
    headings_count: int

class Document(BaseModel):
    company_name: str
    filename: str
    file_path: str
    upload_date: datetime
    document_metadata: DocumentMetadata
    analysis_report: ComplianceReport
    chunks_count: int

class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    document_id: str
    message: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    success: bool
    response: str
    timestamp: str

class UploadResponse(BaseModel):
    success: bool
    document_id: str
    company_name: str
    report: ComplianceReport
    document_stats: DocumentMetadata

class InsightSummary(BaseModel):
    total_documents: int
    average_risk_score: float
    average_compliance_score: float
    average_confidence_score: float
    risk_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    recent_trends: List[Dict[str, Any]]
    top_issues: List[Dict[str, Any]]
