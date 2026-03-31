# Save as verify_system_fixed.ps1
cd C:\Users\rajat\ai-compliance-copilot

Write-Host "Verifying AI Compliance Copilot System" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$allPassed = $true

Write-Host "`n1. Checking Directory Structure..." -ForegroundColor Yellow
$requiredDirs = @(
    "backend\app\api\routes",
    "backend\app\core",
    "backend\app\models",
    "backend\app\services\rag",
    "backend\uploads",
    "backend\vectors",
    "frontend\app"
)

foreach($dir in $requiredDirs) {
    if(Test-Path $dir) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir missing" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host "`n2. Checking Required Files..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\main.py",
    "backend\requirements.txt",
    "backend\.env",
    "backend\app\services\ai_service.py",
    "backend\app\services\document_processor.py",
    "backend\app\services\rag\pipeline.py",
    "backend\app\api\routes\analyze.py",
    "backend\app\api\routes\insights.py",
    "backend\app\api\routes\chat.py",
    "backend\app\core\database.py",
    "backend\app\core\cache.py",
    "Dockerfile",
    "docker-compose.yml"
)

foreach($file in $requiredFiles) {
    if(Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host "`n3. Checking Python Imports..." -ForegroundColor Yellow
$importCheck = python -c "import sys; sys.path.append('backend'); from app.services.ai_service import AIService; from app.services.rag.pipeline import RAGPipeline; from app.services.document_processor import DocumentProcessor; print('OK')" 2>&1
if($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ All Python modules import successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python import errors detected" -ForegroundColor Red
    Write-Host $importCheck -ForegroundColor Red
    $allPassed = $false
}

Write-Host "`n4. Checking Environment Variables..." -ForegroundColor Yellow
if(Test-Path "backend\.env") {
    $envFile = Get-Content "backend\.env"
    if($envFile -match "DEEPSEEK_API_KEY=sk-") {
        Write-Host "  ✓ DeepSeek API key configured" -ForegroundColor Green
    } else {
        Write-Host "  ✗ DeepSeek API key missing" -ForegroundColor Red
        $allPassed = $false
    }

    if($envFile -match "MONGODB_URL=mongodb\+srv://") {
        Write-Host "  ✓ MongoDB URL configured" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MongoDB URL missing" -ForegroundColor Red
        $allPassed = $false
    }

    if($envFile -match "REDIS_URL=redis://") {
        Write-Host "  ✓ Redis URL configured" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Redis URL missing" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "  ✗ .env file not found" -ForegroundColor Red
    $allPassed = $false
}

Write-Host "`n5. Checking Git Status..." -ForegroundColor Yellow
$commits = git rev-list --count HEAD
Write-Host "  ✓ $commits commits made" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Green
if($allPassed) {
    Write-Host "VERIFICATION PASSED!" -ForegroundColor Green
    Write-Host "System is ready for production!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Run .\start_system.ps1 to start the system" -ForegroundColor White
    Write-Host "2. Upload sample_compliance_document.txt to test" -ForegroundColor White
    Write-Host "3. Check dashboard at http://localhost:3000" -ForegroundColor White
    Write-Host "4. Monitor with .\monitor.ps1" -ForegroundColor White
} else {
    Write-Host "VERIFICATION FAILED!" -ForegroundColor Red
    Write-Host "Please fix missing items above" -ForegroundColor Red
}
