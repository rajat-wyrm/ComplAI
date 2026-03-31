# Save as deploy.ps1
cd C:\Users\rajat\ai-compliance-copilot

Write-Host "Deploying AI Compliance Copilot to Google Cloud Run" -ForegroundColor Green

Write-Host "
1. Building Docker image..." -ForegroundColor Yellow
docker build -t gcr.io/your-project-id/compliance-copilot:latest .

Write-Host "
2. Pushing to Google Container Registry..." -ForegroundColor Yellow
docker push gcr.io/your-project-id/compliance-copilot:latest

Write-Host "
3. Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy compliance-copilot 
    --image gcr.io/your-project-id/compliance-copilot:latest 
    --platform managed 
    --region us-central1 
    --allow-unauthenticated 
    --memory 2Gi 
    --cpu 2 
    --set-env-vars "MONGODB_URL=,REDIS_URL=,DEEPSEEK_API_KEY="

Write-Host "
Deployment Complete!" -ForegroundColor Green
