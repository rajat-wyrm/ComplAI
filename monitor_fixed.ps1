# Save as monitor_fixed.ps1
while($true) {
    Clear-Host
    Write-Host "AI Compliance Copilot - System Monitor" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit`n" -ForegroundColor Yellow
    
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -ErrorAction Stop
        Write-Host "System Status: $($health.status)" -ForegroundColor Green
        Write-Host "MongoDB: $($health.services.mongodb)" -ForegroundColor Green
        Write-Host "Redis: $($health.services.redis)" -ForegroundColor Green
        Write-Host "Version: $($health.version)`n" -ForegroundColor Green
    }
    catch {
        Write-Host "System Status: OFFLINE" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
    }
    
    try {
        $insights = Invoke-RestMethod -Uri "http://localhost:8000/api/insights" -Method Get -ErrorAction Stop
        Write-Host "System Analytics:" -ForegroundColor Cyan
        Write-Host "  Total Documents: $($insights.total_documents)" -ForegroundColor White
        Write-Host "  Avg Risk Score: $($insights.average_risk_score)" -ForegroundColor White
        Write-Host "  Avg Compliance: $($insights.average_compliance_score)%" -ForegroundColor White
        Write-Host "  Risk Distribution:" -ForegroundColor White
        Write-Host "    Low: $($insights.risk_distribution.Low)" -ForegroundColor Green
        Write-Host "    Medium: $($insights.risk_distribution.Medium)" -ForegroundColor Yellow
        Write-Host "    High: $($insights.risk_distribution.High)" -ForegroundColor Red
    }
    catch {
        Write-Host "Analytics: Not available yet" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 5
}
