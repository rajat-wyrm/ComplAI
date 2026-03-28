# Run Frontend Development Server
Write-Host "Starting AI Compliance & Risk Copilot Frontend..." -ForegroundColor Green
Set-Location "frontend"

Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Development Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "URL: http://localhost:3000" -ForegroundColor White
Write-Host "API: http://localhost:8000" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev
