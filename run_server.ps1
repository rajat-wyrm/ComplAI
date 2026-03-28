# Run script with proper PYTHONPATH
$env:PYTHONPATH = "C:\Users\rajat\ai-compliance-copilot"
Set-Location "C:\Users\rajat\ai-compliance-copilot\backend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Compliance & Risk Copilot" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
