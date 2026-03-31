# check_health.ps1
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
    Write-Host "System Health: $($health.status)" -ForegroundColor Green
    Write-Host "MongoDB: $($health.services.mongodb)" -ForegroundColor Green
    Write-Host "Redis: $($health.services.redis)" -ForegroundColor Green
    Write-Host "Version: $($health.version)" -ForegroundColor Green
} catch {
    Write-Host "System is not responding. Make sure backend is running." -ForegroundColor Red
    Write-Host "Run: .\start_simple.ps1" -ForegroundColor Yellow
}
