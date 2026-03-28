# Verify installation
Write-Host "🔍 Verifying AI Compliance & Risk Copilot Installation..." -ForegroundColor Green
Set-Location "C:\Users\rajat\ai-compliance-copilot"

Write-Host "`n📋 Checking project structure..." -ForegroundColor Yellow
$requiredDirs = @(
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/models",
    "data/uploads",
    "data/vectors",
    "rag",
    "processing",
    "inference"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir (missing)" -ForegroundColor Red
    }
}

Write-Host "`n📋 Checking key files..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend/app/main.py",
    "backend/app/core/config.py",
    "backend/requirements.txt",
    "docker-compose.yml",
    "Dockerfile.backend",
    "rag/vector_store.py",
    "inference/decision_engine.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (missing)" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Installation verification complete!" -ForegroundColor Green

Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Add your DeepSeek API key to .env file" -ForegroundColor White
Write-Host "2. Run: .\run.ps1 (local development)" -ForegroundColor White
Write-Host "3. Or run: .\docker-run.ps1 (Docker containers)" -ForegroundColor White
Write-Host "4. Open: http://localhost:8000/docs" -ForegroundColor White
