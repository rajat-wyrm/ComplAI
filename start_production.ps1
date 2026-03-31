# Save as start_production.ps1
param(
    [switch],
    [switch]
)

cd C:\Users\rajat\ai-compliance-copilot

Write-Host "AI Compliance Copilot - Production System" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

if () {
    Write-Host "Starting with Docker Compose..." -ForegroundColor Yellow
    docker-compose up --build
}
elseif () {
    Write-Host "Starting in Development Mode..." -ForegroundColor Yellow
    
    Write-Host "
Installing backend dependencies..." -ForegroundColor Green
    pip install -r backend/requirements.txt
    
    Write-Host "
Starting Backend Server..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\rajat\ai-compliance-copilot\backend'; python main.py"
    
    Start-Sleep -Seconds 3
    
    Write-Host "
Installing frontend dependencies..." -ForegroundColor Green
    cd frontend
    npm install
    
    Write-Host "
Starting Frontend Server..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\rajat\ai-compliance-copilot'; npm run dev"
    
    cd ..
    
    Write-Host "
System Started!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
}
else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start_production.ps1 -Dev     # Start in development mode" -ForegroundColor White
    Write-Host "  .\start_production.ps1 -Docker  # Start with Docker" -ForegroundColor White
}
