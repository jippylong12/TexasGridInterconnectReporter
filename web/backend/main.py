import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path to allow importing from src
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from web.backend.api import router

app = FastAPI(title="Texas Grid Interconnect Reporter")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated images
# We'll serve the 'outputs' directory
outputs_dir = project_root / "outputs"
outputs_dir.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

# Include API router
app.include_router(router, prefix="/api")

# Serve React Frontend
# We assume the frontend is built to web/frontend/dist
frontend_dir = project_root / "web" / "frontend" / "dist"

if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # If it's an API call that wasn't matched, let it 404 (handled by FastAPI default)
        # But wait, include_router is above, so if it matched /api it would have been handled.
        # If it starts with /api and didn't match, it falls through here.
        if full_path.startswith("api/"):
             raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve index.html for any other path (SPA routing)
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend not found. Please build the React app."}
else:
    @app.get("/")
    async def root():
        return {"message": "Backend running. Frontend not found (dist directory missing)."}
