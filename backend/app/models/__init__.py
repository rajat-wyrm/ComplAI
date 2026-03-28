"""
Pydantic models for API requests and responses
All models use Pydantic v2 syntax with model_config
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ Request Models ============

class AnalyzeRequest(BaseModel):
    """Request model for document analysis"""
    document_id: str = Field(..., description="Document ID to analyze")


class ChatRequest(BaseModel):
    """Request model for chat with document"""
    document_id: str = Field(..., description="Document ID to chat about")
    message: str = Field(..., description="User message/question")
    session_id: Optional[str] = Field(None, description="Chat session ID for continuity")


# ============ Response Models ============

class UploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    chunks: int = Field(..., description="Number of text chunks created")
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "abc-123",
                "filename": "contract.pdf",
                "file_size": 1024000,
                "chunks": 15,
                "status": "uploaded",
                "message": "Document uploaded successfully"
            }
        }
    )


class AnalysisResponse(BaseModel):
    """Response for document analysis"""
    analysis_id: str = Field(..., description="Analysis identifier")
    document_id: str = Field(..., description="Associated document ID")
    status: str = Field(..., description="Analysis status: processing, completed, failed")
    risk_score: Optional[float] = Field(None, description="Risk score (0-100)", ge=0, le=100)
    confidence_score: Optional[float] = Field(None, description="Confidence level (0-100)", ge=0, le=100)
    risks: Optional[List[Dict[str, Any]]] = Field(None, description="List of identified risks")
    explanation: Optional[str] = Field(None, description="Detailed analysis explanation")
    recommended_actions: Optional[List[str]] = Field(None, description="Actionable recommendations")
    compliance_gaps: Optional[List[str]] = Field(None, description="Identified compliance gaps")
    
    model_config = ConfigDict(from_attributes=True)


class InsightResponse(BaseModel):
    """Response for document insights"""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Document filename")
    upload_date: Optional[str] = Field(None, description="Upload timestamp")
    status: str = Field(..., description="Document status")
    risk_score: Optional[float] = Field(None, description="Risk score (0-100)")
    confidence_score: Optional[float] = Field(None, description="Confidence level")
    risks: Optional[List[Dict[str, Any]]] = Field(None, description="Identified risks")
    explanation: Optional[str] = Field(None, description="Analysis explanation")
    recommended_actions: Optional[List[str]] = Field(None, description="Recommended actions")
    compliance_gaps: Optional[List[str]] = Field(None, description="Compliance gaps")
    message: Optional[str] = Field(None, description="Status message for pending analysis")
    
    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """Response for chat interaction"""
    session_id: str = Field(..., description="Chat session ID")
    response: str = Field(..., description="AI response message")
    context_used: List[str] = Field(default_factory=list, description="Document context used for response")
    confidence: float = Field(default=0.0, description="Response confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    """Response for chat history"""
    session_id: str = Field(..., description="Chat session ID")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Chat message history")
    total: int = Field(..., description="Total number of messages")


class DocumentHistoryItem(BaseModel):
    """Individual document in history list"""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Document filename")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: str = Field(..., description="Upload timestamp")
    status: str = Field(..., description="Document status")
    risk_score: Optional[float] = Field(None, description="Risk score if analyzed")
    
    model_config = ConfigDict(from_attributes=True)


class DocumentHistoryResponse(BaseModel):
    """Response for document history endpoint"""
    documents: List[DocumentHistoryItem] = Field(default_factory=list, description="List of documents")
    total: int = Field(..., description="Total number of documents")
    limit: int = Field(..., description="Items per page limit")
    offset: int = Field(..., description="Current offset")
    has_more: bool = Field(..., description="Whether more items exist")


class DashboardResponse(BaseModel):
    """Response for dashboard metrics"""
    total_documents: int = Field(..., description="Total documents in period")
    analyzed_documents: int = Field(..., description="Documents with completed analysis")
    average_risk_score: float = Field(..., description="Average risk score across analyzed documents")
    period_days: int = Field(..., description="Time period in days")
    
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")


# ============ Internal Models ============

class Document(BaseModel):
    """Internal document model (matches MongoDB structure)"""
    document_id: str
    filename: str
    file_size: int
    upload_date: datetime
    content: str
    chunks: List[str]
    status: str
    risk_score: Optional[float] = None
    analysis_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class Analysis(BaseModel):
    """Internal analysis model (matches MongoDB structure)"""
    analysis_id: str
    document_id: str
    risk_score: float
    confidence_score: float
    risks: List[Dict[str, Any]]
    explanation: str
    recommended_actions: List[str]
    compliance_gaps: List[str]
    created_at: datetime
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class ChatMessage(BaseModel):
    """Internal chat message model"""
    session_id: str
    document_id: str
    message: str
    response: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
