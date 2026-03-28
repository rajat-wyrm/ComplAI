#!/bin/bash
# Google Cloud Run Deployment Script

echo "Deploying AI Compliance & Risk Copilot to Google Cloud Run..."

# Set variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="compliance-copilot"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Authenticate with Google Cloud
echo "Authenticating with Google Cloud..."
gcloud auth configure-docker

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Push to Google Container Registry
echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --set-env-vars "DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}" \
    --set-env-vars "SECRET_KEY=${SECRET_KEY}" \
    --set-env-vars "MONGODB_URL=${MONGODB_URL}" \
    --set-env-vars "REDIS_URL=${REDIS_URL}" \
    --set-env-vars "ENVIRONMENT=production"

# Get the deployed URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')
echo "Deployment complete!"
echo "Service URL: ${SERVICE_URL}"
echo "Health Check: ${SERVICE_URL}/health"
echo "API Docs: ${SERVICE_URL}/docs"
