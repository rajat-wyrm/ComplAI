"""
Simple test server to verify setup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Compliance Copilot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI Compliance Copilot is running!",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "upload": "/upload",
            "analyze": "/analyze"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AI Compliance Copilot"}

@app.get("/api-info")
async def api_info():
    return {
        "name": "AI Compliance & Risk Copilot",
        "version": "1.0.0",
        "description": "RegTech AI for document compliance analysis"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
