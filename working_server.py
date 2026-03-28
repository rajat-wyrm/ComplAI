"""
Minimal Working Server for AI Compliance Copilot
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import os

app = FastAPI(title="AI Compliance Copilot", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for demo
documents = {}
analyses = {}

class AnalyzeRequest(BaseModel):
    document_id: str

class ChatRequest(BaseModel):
    document_id: str
    message: str
    session_id: Optional[str] = None

@app.get("/")
async def root():
    return {
        "name": "AI Compliance Copilot",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "POST /upload",
            "analyze": "POST /analyze",
            "chat": "POST /chat",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Compliance Copilot"
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a document"""
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store document info
    documents[document_id] = {
        "id": document_id,
        "filename": file.filename,
        "size": len(content),
        "path": file_path,
        "upload_date": datetime.utcnow().isoformat(),
        "status": "uploaded"
    }
    
    return {
        "document_id": document_id,
        "filename": file.filename,
        "size": len(content),
        "status": "uploaded",
        "message": "Document uploaded successfully"
    }

@app.post("/analyze")
async def analyze_document(request: AnalyzeRequest):
    """Analyze document for risks"""
    if request.document_id not in documents:
        return {"error": "Document not found"}, 404
    
    analysis_id = str(uuid.uuid4())
    
    # Mock analysis results
    analysis = {
        "analysis_id": analysis_id,
        "document_id": request.document_id,
        "risk_score": 65,
        "confidence_score": 85,
        "risks": [
            {
                "category": "Compliance",
                "description": "Missing required documentation",
                "severity": "high",
                "impact": "Potential regulatory penalty"
            },
            {
                "category": "Data Privacy",
                "description": "Sensitive data exposure risk",
                "severity": "medium",
                "impact": "Data breach potential"
            }
        ],
        "explanation": "Document contains compliance gaps in sections 3.2 and 4.1. Recommended immediate review.",
        "recommended_actions": [
            "Review section 3.2 for missing compliance requirements",
            "Add data protection clauses in section 4",
            "Conduct legal review of terms and conditions"
        ],
        "compliance_gaps": [
            "Missing GDPR compliance statement",
            "Incomplete liability clauses",
            "No data retention policy defined"
        ],
        "created_at": datetime.utcnow().isoformat(),
        "status": "completed"
    }
    
    analyses[analysis_id] = analysis
    
    return analysis

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with document"""
    if request.document_id not in documents:
        return {"error": "Document not found"}, 404
    
    session_id = request.session_id or str(uuid.uuid4())
    
    # Mock responses based on message
    message_lower = request.message.lower()
    
    if "risk" in message_lower:
        response = "Based on my analysis, this document has a risk score of 65/100. The main risks include missing compliance requirements and potential data privacy issues."
    elif "recommend" in message_lower:
        response = "I recommend reviewing section 3.2 for compliance gaps, adding data protection clauses, and conducting a legal review of terms and conditions."
    elif "score" in message_lower:
        response = "The overall risk score is 65/100 with 85% confidence. This indicates moderate compliance risk that requires attention."
    else:
        response = "I've analyzed this document. You can ask me about risks, recommendations, or specific sections. What would you like to know?"
    
    return {
        "session_id": session_id,
        "response": response,
        "context_used": [
            "Document analysis results",
            "Risk assessment data",
            "Compliance recommendations"
        ],
        "confidence": 0.85,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/insights/{document_id}")
async def get_insights(document_id: str):
    """Get document insights"""
    if document_id not in documents:
        return {"error": "Document not found"}, 404
    
    # Find analysis for this document
    doc_analysis = None
    for aid, analysis in analyses.items():
        if analysis["document_id"] == document_id:
            doc_analysis = analysis
            break
    
    if not doc_analysis:
        return {
            "document_id": document_id,
            "filename": documents[document_id]["filename"],
            "status": "pending",
            "message": "Analysis not yet completed"
        }
    
    return doc_analysis

@app.get("/history")
async def get_history():
    """Get document history"""
    history_list = []
    for doc_id, doc in documents.items():
        history_list.append({
            "document_id": doc_id,
            "filename": doc["filename"],
            "upload_date": doc["upload_date"],
            "status": doc["status"],
            "size": doc["size"]
        })
    
    return {
        "documents": history_list,
        "total": len(history_list)
    }

@app.get("/dashboard")
async def get_dashboard():
    """Get dashboard summary"""
    total_docs = len(documents)
    analyzed_docs = len(analyses)
    
    risk_scores = [a["risk_score"] for a in analyses.values() if "risk_score" in a]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    return {
        "total_documents": total_docs,
        "analyzed_documents": analyzed_docs,
        "average_risk_score": round(avg_risk, 1),
        "pending_analysis": total_docs - analyzed_docs,
        "recent_activity": [
            {
                "document_id": doc_id,
                "filename": doc["filename"],
                "action": "uploaded",
                "timestamp": doc["upload_date"]
            }
            for doc_id, doc in list(documents.items())[-5:]
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("AI Compliance Copilot Server Starting...")
    print("="*50)
    print("Access the server at:")
    print("  http://localhost:8000")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/health")
    print("="*50)
    print("\nPress Ctrl+C to stop the server\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
