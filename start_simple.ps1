# Simple working start script - start_simple.ps1
Write-Host "Starting AI Compliance Copilot System" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Kill any existing processes on ports 8000 and 3000
Write-Host "Cleaning ports..." -ForegroundColor Yellow
net stop winnat 2>$null
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force

# Install backend dependencies
Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn python-multipart pymongo redis faiss-cpu sentence-transformers openai python-dotenv pypdf python-docx numpy pydantic pydantic-settings tenacity

# Start backend
Write-Host "`nStarting backend server..." -ForegroundColor Yellow
$backendDir = "C:\Users\rajat\ai-compliance-copilot\backend"
$backendWindow = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; Write-Host 'Backend running at http://localhost:8000' -ForegroundColor Cyan; python main.py" -PassThru

Start-Sleep -Seconds 8

# Check if backend is running
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -ErrorAction Stop
    Write-Host "Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Warning: Backend not responding yet, continuing..." -ForegroundColor Yellow
}

# Install frontend dependencies
Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Yellow
$frontendDir = "C:\Users\rajat\ai-compliance-copilot\frontend"
cd $frontendDir
npm install --silent

# Start frontend
Write-Host "`nStarting frontend server..." -ForegroundColor Yellow
$frontendWindow = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; Write-Host 'Frontend running at http://localhost:3000' -ForegroundColor Cyan; npm run dev" -PassThru

cd C:\Users\rajat\ai-compliance-copilot

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "SYSTEM STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Green

Write-Host "`nTest Commands:" -ForegroundColor Yellow
Write-Host "  Test Health: curl http://localhost:8000/api/health" -ForegroundColor White
Write-Host "  Get Insights: curl http://localhost:8000/api/insights" -ForegroundColor White
Write-Host "`nPress Enter to stop all services..." -ForegroundColor Red
Read-Host

# Cleanup on exit
Stop-Process -Id $backendWindow.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $frontendWindow.Id -Force -ErrorAction SilentlyContinue
Write-Host "Services stopped" -ForegroundColor Red
