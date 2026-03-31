# QUICK TEST - Verify API
Write-Host "Testing API endpoints..." -ForegroundColor Yellow
Write-Host ""

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "  ✅ Health Check: $($health.status)" -ForegroundColor Green
    Write-Host "     Version: $($health.version)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Backend not running. Start with .\start.ps1 first" -ForegroundColor Red
}

try {
    $root = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get -ErrorAction Stop
    Write-Host "  ✅ Root Endpoint: $($root.name)" -ForegroundColor Green
    Write-Host "     Status: $($root.status)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Root endpoint failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Frontend URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Backend URL: http://localhost:8000/docs" -ForegroundColor Cyan
