# AI Compliance & Risk Copilot

A production-ready RegTech AI system for analyzing legal, GST, and compliance documents.

## Features
- Document Processing (PDF, DOCX, TXT)
- RAG Pipeline with FAISS Vector Store
- AI Risk Analysis with DeepSeek
- Conversational AI Chat
- Risk Scoring (0-100)
- Dashboard Analytics
- History Tracking

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- DeepSeek API Key

### Run with Docker
1. Copy .env.docker to .env and add your DeepSeek API key
2. Run: docker-compose up -d
3. Access: http://localhost:8000/docs

### Run Locally
1. cd backend
2. pip install -r requirements.txt
3. uvicorn app.main:app --reload
4. Open http://localhost:8000

## API Endpoints
- POST /upload - Upload document
- POST /analyze - Analyze document
- POST /chat - Chat with document
- GET /insights/{id} - Get insights
- GET /history - List documents
- GET /health - Health check

## Environment Variables
Create .env file with:
- DEEPSEEK_API_KEY=your-key
- MONGODB_URL=mongodb://localhost:27017
- REDIS_URL=redis://localhost:6379
- SECRET_KEY=your-secret-key

## Deployment
Run deploy.ps1 (Windows) or deploy.sh (Linux/Mac) to deploy to Google Cloud Run.
