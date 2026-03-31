# test_upload.ps1 - Test the upload endpoint
$filePath = "C:\Users\rajat\ai-compliance-copilot\sample_compliance_document.txt"

if (Test-Path $filePath) {
    Write-Host "Uploading sample document..." -ForegroundColor Yellow
    
    $uri = "http://localhost:8000/api/upload"
    
    $multipartContent = [System.Net.Http.MultipartFormDataContent]::new()
    $fileStream = [System.IO.FileStream]::new($filePath, [System.IO.FileMode]::Open)
    $fileContent = [System.Net.Http.StreamContent]::new($fileStream)
    $multipartContent.Add($fileContent, "file", "sample_compliance_document.txt")
    
    try {
        $response = Invoke-WebRequest -Uri $uri -Method Post -Body $multipartContent -ContentType $multipartContent.Headers.ContentType
        $result = $response.Content | ConvertFrom-Json
        Write-Host "Upload successful!" -ForegroundColor Green
        Write-Host "Document ID: $($result.document_id)" -ForegroundColor Cyan
        Write-Host "Company: $($result.company_name)" -ForegroundColor Cyan
        Write-Host "Risk Score: $($result.report.risk_score)" -ForegroundColor Yellow
        Write-Host "Compliance Score: $($result.report.compliance_score)%" -ForegroundColor Green
    } catch {
        Write-Host "Upload failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Sample file not found at: $filePath" -ForegroundColor Red
}
