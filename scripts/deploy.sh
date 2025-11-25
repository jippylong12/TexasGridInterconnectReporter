#!/bin/bash

# Exit on error
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Load configuration
if [ -f "config.yaml" ]; then
    # Simple parser for yaml (assumes simple key: value format)
    eval $(grep -E "^(project_id|region|service_name|image_name):" config.yaml | sed 's/: /=/' | sed 's/ //g' | sed 's/"//g')
else
    echo "Error: config.yaml not found."
    exit 1
fi

if [ "$project_id" == "your-project-id" ]; then
    echo "Error: Please update project_id in config.yaml"
    exit 1
fi

echo "Deploying to Project: $project_id"
echo "Region: $region"
echo "Service: $service_name"

# Build Docker image
echo "Building Docker image..."
# Use Google Cloud Build for building (optional, but easier for pushing)
# Or build locally and push
# Let's assume local build + push for simplicity if docker is available, 
# but gcloud builds submit is more robust for cloud deployment.

# Method 1: gcloud builds submit
echo "Submitting build to Cloud Build..."
gcloud builds submit --tag "gcr.io/$project_id/$image_name" .

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$service_name" \
  --image "gcr.io/$project_id/$image_name" \
  --platform managed \
  --region "$region" \
  --allow-unauthenticated \
  --port 8080

echo "Deployment complete!"
