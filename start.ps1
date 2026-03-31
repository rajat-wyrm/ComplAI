# START ALL SERVICES
Write-Host "Starting AI Compliance & Risk Copilot..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\rajat\ai-compliance-copilot\backend'; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'BACKEND SERVER' -ForegroundColor Green; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'URL: http://localhost:8000' -ForegroundColor White; Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor White; Write-Host 'Health: http://localhost:8000/health' -ForegroundColor White; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\rajat\ai-compliance-copilot\frontend'; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'FRONTEND SERVER' -ForegroundColor Green; Write-Host '========================================' -ForegroundColor Cyan; Write-Host 'URL: http://localhost:5000' -ForegroundColor White; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ SERVERS ARE STARTING!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application:" -ForegroundColor Yellow
Write-Host "  🚀 Frontend: http://localhost:5000" -ForegroundColor White
Write-Host "  📚 Backend API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  💚 Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Features:" -ForegroundColor Green
Write-Host "  ✓ Upload documents (PDF/DOCX/TXT)" -ForegroundColor White
Write-Host "  ✓ AI risk analysis with DeepSeek" -ForegroundColor White
Write-Host "  ✓ Conversational AI chat" -ForegroundColor White
Write-Host "  ✓ Dashboard with analytics" -ForegroundColor White
Write-Host "  ✓ Document history tracking" -ForegroundColor White
Write-Host "  ✓ Detailed risk analysis page" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close the terminal windows" -ForegroundColor Red
Write-Host ""
Read-Host "Press Enter to exit this window"
