import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import zipfile
import os

# Import report generation logic
# Assuming src is in path (handled in main.py)
from src.extract_large_gen import extract_large_gen_data
from src.reports import (
    generate_county_report,
    generate_cod_quarterly_report,
    generate_fuel_type_report,
    generate_technology_type_report
)

router = APIRouter()

# Define paths
# We need to be careful with paths. 
# main.py adds project root to sys.path.
# So we can find 'inputs' relative to project root.
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

import json
from typing import Optional
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    report_type: str = "all"

@router.post("/generate")
async def generate_reports(request: GenerateRequest = None):
    """
    Triggers report generation using the default input file.
    Accepts an optional report_type to generate a specific report.
    """
    try:
        # Handle default if no body provided
        report_type = request.report_type if request else "all"
        
        # Ensure output directory exists
        OUTPUTS_DIR.mkdir(exist_ok=True)
        
        # Load generated reports cache
        cache_file = OUTPUTS_DIR / "generated_reports.json"
        cache = {}
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            except json.JSONDecodeError:
                pass # Start fresh if corrupt

        # Find the input file. For now, hardcoded to 10/file.xlsx as per original script default
        # or we could look for the latest one.
        # Let's try to find the file used in the original script default: inputs/10/file.xlsx
        input_file = INPUTS_DIR / "10" / "file.xlsx"
        
        if not input_file.exists():
            # Fallback: try to find ANY xlsx file in inputs/*
            found = False
            for p in INPUTS_DIR.glob("*/*.xlsx"):
                input_file = p
                found = True
                break
            
            if not found:
                raise HTTPException(status_code=404, detail="No input Excel file found in inputs/ directory")

        # Map report types to filenames and generation functions
        report_map = {
            "county": {
                "filename": "county_mw_breakdown.png",
                "func": generate_county_report,
                "name": "County MW Breakdown"
            },
            "cod": {
                "filename": "cod_quarterly_buckets.png",
                "func": generate_cod_quarterly_report,
                "name": "COD Quarterly Buckets"
            },
            "fuel": {
                "filename": "fuel_type_breakdown.png",
                "func": generate_fuel_type_report,
                "name": "Fuel Type Breakdown"
            },
            "technology": {
                "filename": "technology_type_breakdown.png",
                "func": generate_technology_type_report,
                "name": "Technology Type Breakdown"
            }
        }

        reports_to_generate = []
        if report_type == "all":
            reports_to_generate = list(report_map.keys())
        elif report_type in report_map:
            reports_to_generate = [report_type]
        else:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")

        # Check if we actually need to generate anything
        # For now, we'll assume if it's in the cache and file exists, it's good.
        # In a real app, we'd check timestamps against input file.
        
        # Extract data ONLY if we need to generate something
        df = None
        
        generated_images = []
        
        for r_type in reports_to_generate:
            info = report_map[r_type]
            filename = info["filename"]
            file_path = OUTPUTS_DIR / filename
            
            # Simple cache check: if file exists and is in cache, skip generation
            # NOTE: This doesn't account for updated input data. 
            # For this task, "archive" implies we don't regenerate if we have it.
            # But usually user wants to regenerate if they click generate.
            # The user said: "archive the image generations so we don't have to keep remaking them."
            # Let's assume if it exists, we return it. 
            # BUT, if the user explicitly requests generation, maybe they want a refresh?
            # Let's implement a "force" flag later if needed. For now, check existence.
            
            if file_path.exists() and filename in cache:
                print(f"Using cached report: {filename}")
            else:
                print(f"Generating report: {r_type}")
                if df is None:
                    df = extract_large_gen_data(input_file)
                
                info["func"](df, OUTPUTS_DIR)
                
                # Update cache
                cache[filename] = {
                    "generated_at": str(input_file.stat().st_mtime), # Using input file mtime as version proxy? Or current time?
                    "source": str(input_file.name)
                }
            
            generated_images.append(f"/outputs/{filename}")

        # Save cache
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        
        return {
            "status": "success",
            "message": "Reports generated/retrieved successfully",
            "images": generated_images,
            "source_file": str(input_file.relative_to(PROJECT_ROOT))
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
async def download_reports(background_tasks: BackgroundTasks):
    """
    Zips the generated reports and returns them.
    """
    try:
        zip_filename = "ercot_reports.zip"
        zip_path = OUTPUTS_DIR / zip_filename
        
        # Create zip file
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for image_name in [
                "county_mw_breakdown.png",
                "cod_quarterly_buckets.png",
                "fuel_type_breakdown.png",
                "technology_type_breakdown.png"
            ]:
                file_path = OUTPUTS_DIR / image_name
                if file_path.exists():
                    zipf.write(file_path, arcname=image_name)
        
        if not zip_path.exists():
             raise HTTPException(status_code=404, detail="No reports found to download. Please generate them first.")

        return FileResponse(
            path=zip_path, 
            filename=zip_filename, 
            media_type='application/zip'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
