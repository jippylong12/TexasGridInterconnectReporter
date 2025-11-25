import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path to allow importing from src
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

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

@app.get("/")
async def root():
    return {"message": "Texas Grid Interconnect Reporter API is running"}
