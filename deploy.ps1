# Windows Deployment Script for Google Cloud Run
Write-Host "Deploying AI Compliance & Risk Copilot to Google Cloud Run..." -ForegroundColor Green

# Check if gcloud is installed
$gcloudCheck = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudCheck) {
    Write-Host "Google Cloud SDK not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Set variables
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "your-project-id" }
$REGION = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$SERVICE_NAME = "compliance-copilot"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Authenticate
Write-Host "Authenticating with Google Cloud..." -ForegroundColor Yellow
gcloud auth configure-docker

# Build image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t $IMAGE_NAME .

# Push to GCR
Write-Host "Pushing to Google Container Registry..." -ForegroundColor Yellow
docker push $IMAGE_NAME

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300

# Get URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)"
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host "Health Check: $SERVICE_URL/health" -ForegroundColor Cyan
Write-Host "API Docs: $SERVICE_URL/docs" -ForegroundColor Cyan
