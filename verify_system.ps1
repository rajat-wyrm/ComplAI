# Save as verify_system.ps1
cd C:\Users\rajat\ai-compliance-copilot

Write-Host "Verifying AI Compliance Copilot System" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

 = @()
 = True

Write-Host "
1. Checking Directory Structure..." -ForegroundColor Yellow
 = @(
    "backend\app\api\routes",
    "backend\app\core",
    "backend\app\models",
    "backend\app\services\rag",
    "backend\uploads",
    "backend\vectors",
    "frontend\app"
)

foreach( in ) {
    if(Test-Path ) {
        Write-Host "  ✓ " -ForegroundColor Green
    } else {
        Write-Host "  ✗  missing" -ForegroundColor Red
         = False
    }
}

Write-Host "
2. Checking Required Files..." -ForegroundColor Yellow
 = @(
    "backend\main.py",
    "backend\requirements.txt",
    "backend\.env",
    "backend\app\services\ai_service.py",
    "backend\app\services\document_processor.py",
    "backend\app\services\rag\pipeline.py",
    "backend\app\api\routes\upload.py",
    "backend\app\api\routes\analyze.py",
    "backend\app\api\routes\insights.py",
    "backend\app\api\routes\chat.py",
    "backend\app\core\database.py",
    "backend\app\core\cache.py",
    "Dockerfile",
    "docker-compose.yml"
)

foreach( in ) {
    if(Test-Path ) {
        Write-Host "  ✓ " -ForegroundColor Green
    } else {
        Write-Host "  ✗  missing" -ForegroundColor Red
         = False
    }
}

Write-Host "
3. Checking Python Imports..." -ForegroundColor Yellow
python -c "import sys; sys.path.append('backend'); from app.services.ai_service import AIService; from app.services.rag.pipeline import RAGPipeline; from app.services.document_processor import DocumentProcessor" 2>
if(0 -eq 0) {
    Write-Host "  ✓ All Python modules import successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python import errors detected" -ForegroundColor Red
     = False
}

Write-Host "
4. Checking Environment Variables..." -ForegroundColor Yellow
 = Get-Content backend\.env
if( -match "DEEPSEEK_API_KEY=sk-") {
    Write-Host "  ✓ DeepSeek API key configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ DeepSeek API key missing" -ForegroundColor Red
     = False
}

if( -match "MONGODB_URL=mongodb\+srv://") {
    Write-Host "  ✓ MongoDB URL configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ MongoDB URL missing" -ForegroundColor Red
     = False
}

if( -match "REDIS_URL=redis://") {
    Write-Host "  ✓ Redis URL configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ Redis URL missing" -ForegroundColor Red
     = False
}

Write-Host "
5. Checking Git Status..." -ForegroundColor Yellow
 = git rev-list --count HEAD
Write-Host "  ✓  commits made" -ForegroundColor Green

Write-Host "
=====================================" -ForegroundColor Green
if() {
    Write-Host "VERIFICATION PASSED!" -ForegroundColor Green
    Write-Host "System is ready for production!" -ForegroundColor Green
    Write-Host "
Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run .\start_production.ps1 -Dev to start the system" -ForegroundColor White
    Write-Host "2. Upload sample_compliance_document.txt to test" -ForegroundColor White
    Write-Host "3. Check dashboard at http://localhost:3000" -ForegroundColor White
    Write-Host "4. Monitor with .\monitor.ps1" -ForegroundColor White
} else {
    Write-Host "VERIFICATION FAILED!" -ForegroundColor Red
    Write-Host "Please fix missing items above" -ForegroundColor Red
}
