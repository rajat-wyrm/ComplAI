# Save as test_upgrade.ps1
cd C:\Users\rajat\ai-compliance-copilot

Write-Host "Testing AI Compliance Copilot Upgrade" -ForegroundColor Green

Write-Host "
1. Installing dependencies..." -ForegroundColor Yellow
pip install -r backend/requirements.txt

Write-Host "
2. Starting backend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\rajat\ai-compliance-copilot\backend; python main.py"

Start-Sleep -Seconds 5

Write-Host "
3. Testing health endpoint..." -ForegroundColor Yellow
try {
     = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "Health check: " -ForegroundColor Green
} catch {
    Write-Host "Health check failed" -ForegroundColor Red
}

Write-Host "
4. Testing insights endpoint..." -ForegroundColor Yellow
try {
     = Invoke-RestMethod -Uri "http://localhost:8000/api/insights" -Method Get
    Write-Host "Insights retrieved:  documents" -ForegroundColor Green
} catch {
    Write-Host "Insights retrieval failed" -ForegroundColor Red
}

Write-Host "
5. Starting frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\rajat\ai-compliance-copilot\frontend; npm run dev"

Write-Host "
System Upgrade Complete!" -ForegroundColor Green
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor White
