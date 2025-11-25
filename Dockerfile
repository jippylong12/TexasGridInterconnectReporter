# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY web/frontend/package.json web/frontend/package-lock.json* ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source code
COPY web/frontend ./

# Build the application
RUN npm run build

# Stage 2: Setup Python Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for matplotlib)
# matplotlib might need some libraries, but usually wheels are fine.
# If needed: RUN apt-get update && apt-get install -y ...

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY src ./src
COPY web/backend ./web/backend
COPY inputs ./inputs
# Create outputs directory
RUN mkdir outputs

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./web/frontend/dist

# Expose port
EXPOSE 8080

# Command to run the application
# We run uvicorn on 0.0.0.0:8080
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
