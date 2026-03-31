# Save as monitor.ps1
while(True) {
    Clear-Host
    Write-Host "AI Compliance Copilot - System Monitor" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit
" -ForegroundColor Yellow
    
    try {
         = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -ErrorAction Stop
        Write-Host "System Status: " -ForegroundColor Green
        Write-Host "MongoDB: " -ForegroundColor Green
        Write-Host "Redis: " -ForegroundColor Green
        Write-Host "Version: 
" -ForegroundColor Green
    }
    catch {
        Write-Host "System Status: OFFLINE" -ForegroundColor Red
    }
    
    try {
         = Invoke-RestMethod -Uri "http://localhost:8000/api/insights" -Method Get -ErrorAction Stop
        Write-Host "System Analytics:" -ForegroundColor Cyan
        Write-Host "  Total Documents: " -ForegroundColor White
        Write-Host "  Avg Risk Score: " -ForegroundColor White
        Write-Host "  Avg Compliance: %" -ForegroundColor White
        Write-Host "  Risk Distribution:" -ForegroundColor White
        Write-Host "    Low: " -ForegroundColor Green
        Write-Host "    Medium: " -ForegroundColor Yellow
        Write-Host "    High: " -ForegroundColor Red
    }
    catch {
        Write-Host "Analytics: Not available" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 5
}
