#!/bin/bash

# Exit on error
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

CONTAINER_NAME="texas-grid-reporter"
IMAGE_NAME="texas-grid-reporter"
PORT=8080

echo "=================================================="
echo "   Restarting Docker Container: $CONTAINER_NAME"
echo "=================================================="

# 1. Stop and remove existing container
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping and removing existing container..."
    docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
    docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
else
    echo "No existing container found."
fi

# 2. Build Docker Image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# 3. Run Container
echo "Starting container on port $PORT..."
docker run -d -p $PORT:8080 --name $CONTAINER_NAME $IMAGE_NAME

echo "=================================================="
echo "   Container is running!"
echo "   URL: http://localhost:$PORT"
echo "   Logs: docker logs -f $CONTAINER_NAME"
echo "=================================================="
