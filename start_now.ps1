# Save as start_now.ps1 - Simple direct start
cd C:\Users\rajat\ai-compliance-copilot

Write-Host "Starting AI Compliance Copilot System" -ForegroundColor Green

Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
pip install -q -r backend\requirements.txt

Write-Host "Starting backend server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host 'Backend starting at http://localhost:8000' -ForegroundColor Cyan; python main.py"

Start-Sleep -Seconds 5

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
cd frontend
npm install -q

Write-Host "Starting frontend server on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Frontend starting at http://localhost:3000' -ForegroundColor Cyan; npm run dev"

cd ..

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "SYSTEM STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Green
Write-Host "`nTo test the system:" -ForegroundColor Yellow
Write-Host "1. Open browser to http://localhost:3000" -ForegroundColor White
Write-Host "2. Upload sample_compliance_document.txt" -ForegroundColor White
Write-Host "3. View the compliance report" -ForegroundColor White
Write-Host "4. Chat with the document" -ForegroundColor White
Write-Host "`nTo stop: Close the PowerShell windows" -ForegroundColor Red
