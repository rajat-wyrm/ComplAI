# Save as start_system.ps1
param(
    [switch]$Docker,
    [switch]$Dev
)

cd C:\Users\rajat\ai-compliance-copilot

Write-Host "AI Compliance Copilot - Production System" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

if ($Docker) {
    Write-Host "Starting with Docker Compose..." -ForegroundColor Yellow
    docker-compose up --build
}
elseif ($Dev) {
    Write-Host "Starting in Development Mode..." -ForegroundColor Yellow

    Write-Host "`nInstalling backend dependencies..." -ForegroundColor Green
    pip install -r backend\requirements.txt

    Write-Host "`nStarting Backend Server..." -ForegroundColor Green
    $backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python main.py" -PassThru

    Start-Sleep -Seconds 5

    Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Green
    cd frontend
    npm install
    
    Write-Host "`nStarting Frontend Server..." -ForegroundColor Green
    $frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev" -PassThru

    cd ..

    Write-Host "`nSystem Started!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Health Check: http://localhost:8000/api/health" -ForegroundColor Cyan
    
    Write-Host "`nPress any key to stop all services..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    Stop-Process -Id $backendJob.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendJob.Id -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start_system.ps1 -Dev     # Start in development mode" -ForegroundColor White
    Write-Host "  .\start_system.ps1 -Docker  # Start with Docker" -ForegroundColor White
}
