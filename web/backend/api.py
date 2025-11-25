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

@router.post("/generate")
async def generate_reports():
    """
    Triggers report generation using the default input file.
    In a real app, we might accept a file upload here.
    """
    try:
        # Ensure output directory exists
        OUTPUTS_DIR.mkdir(exist_ok=True)
        
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

        # Extract data
        df = extract_large_gen_data(input_file)
        
        # Generate all reports
        generate_county_report(df, OUTPUTS_DIR)
        generate_cod_quarterly_report(df, OUTPUTS_DIR)
        generate_fuel_type_report(df, OUTPUTS_DIR)
        generate_technology_type_report(df, OUTPUTS_DIR)
        
        # Return list of generated images
        # We assume the filenames are constant as per reports.py
        images = [
            "/outputs/county_mw_breakdown.png",
            "/outputs/cod_quarterly_buckets.png",
            "/outputs/fuel_type_breakdown.png",
            "/outputs/technology_type_breakdown.png"
        ]
        
        return {
            "status": "success",
            "message": "Reports generated successfully",
            "images": images,
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
