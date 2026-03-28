# Run the backend server
Write-Host "🚀 Starting AI Compliance & Risk Copilot..." -ForegroundColor Green
Set-Location "C:\Users\rajat\ai-compliance-copilot"

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
Set-Location backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run the server
Write-Host "`n🚀 Starting server..." -ForegroundColor Green
Write-Host "📍 API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📍 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
