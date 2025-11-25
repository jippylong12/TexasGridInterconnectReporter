#!/bin/bash

# Texas Grid Interconnect Reporter - Startup Script

# Function to kill processes on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "=================================================="
echo "   Texas Grid Interconnect Reporter - Web App"
echo "=================================================="

# Check if virtual environment is active or requirements are installed
# For simplicity, we assume the user has set up the environment as per README

# 1. Start Backend
echo "[1/2] Starting Backend Server (FastAPI)..."
# Navigate to project root just in case
cd "$(dirname "$0")"
uvicorn web.backend.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "      Backend running on http://localhost:8000"

# 2. Start Frontend
echo "[2/2] Starting Frontend Server (Vite)..."
cd web/frontend
npm run dev -- --host &
FRONTEND_PID=$!
echo "      Frontend running on http://localhost:5173"

echo "=================================================="
echo "   App is ready! Open: http://localhost:5173"
echo "=================================================="
echo "Press Ctrl+C to stop."

# Wait for processes
wait
