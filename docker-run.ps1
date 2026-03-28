# Run with Docker Compose
Write-Host "🐳 Starting AI Compliance & Risk Copilot with Docker..." -ForegroundColor Green
Set-Location "C:\Users\rajat\ai-compliance-copilot"

# Check Docker
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "❌ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "`n🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`n✅ Services started!" -ForegroundColor Green
Write-Host "📍 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📍 MongoDB: localhost:27017" -ForegroundColor Cyan
Write-Host "📍 Redis: localhost:6379" -ForegroundColor Cyan

Write-Host "`nTo view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f" -ForegroundColor White

Write-Host "`nTo stop services:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor White
