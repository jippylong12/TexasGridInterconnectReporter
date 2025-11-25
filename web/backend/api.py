import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
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
    generate_technology_type_report,
    generate_county_fuel_report
)
from src.constants import normalize_fuel_type, normalize_technology_type, FUEL_COLORS

router = APIRouter()

# Define paths
# We need to be careful with paths. 
# main.py adds project root to sys.path.
# So we can find 'inputs' relative to project root.
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

import json
from typing import Optional, List
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    report_type: str = "all"
    quarters: Optional[List[str]] = None
    force_regenerate: bool = False

@router.get("/quarters")
async def get_quarters():
    """
    Returns a list of available quarters from the dataset.
    """
    try:
        # Find input file (reuse logic from generate_reports or extract to helper)
        input_file = INPUTS_DIR / "10" / "file.xlsx"
        if not input_file.exists():
             for p in INPUTS_DIR.glob("*/*.xlsx"):
                input_file = p
                break
        
        if not input_file.exists():
             raise HTTPException(status_code=404, detail="No input Excel file found")

        import pandas as pd
        df = extract_large_gen_data(input_file)
        
        # Extract quarters
        df['Projected COD'] = pd.to_datetime(df['Projected COD'], errors='coerce')
        df = df[df['Projected COD'].notna()]
        quarters = sorted(df['Projected COD'].dt.to_period('Q').astype(str).unique())
        
        return {"quarters": quarters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_reports(request: GenerateRequest = None):
    """
    Triggers report generation using the default input file.
    Accepts an optional report_type to generate a specific report.
    """
    try:
        # Handle default if no body provided
        report_type = request.report_type if request else "all"
        quarters = request.quarters if request else None
        force_regenerate = request.force_regenerate if request else False
        
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
            "technology": {
                "filename": "technology_type_breakdown.png",
                "func": generate_technology_type_report,
                "name": "Technology Type Breakdown"
            },
            "county_fuel": {
                "filename": "county_fuel_breakdown.png",
                "func": generate_county_fuel_report,
                "name": "County + Fuel Type Breakdown"
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
            
            # Cache check logic
            should_generate = True
            
            if file_path.exists() and filename in cache and not force_regenerate:
                cached_info = cache[filename]
                # Check if parameters match
                cached_quarters = cached_info.get("quarters")
                # If quarters are provided, they must match. If not provided, cached should be None/Empty
                # Normalize for comparison (sort lists)
                req_q = sorted(quarters) if quarters else None
                cached_q = sorted(cached_info.get("quarters")) if cached_info.get("quarters") else None
                
                if req_q == cached_q:
                    print(f"Using cached report: {filename}")
                    should_generate = False
            
            if should_generate:
                print(f"Generating report: {r_type}")
                if df is None:
                    df = extract_large_gen_data(input_file)
                
                if r_type == 'county_fuel':
                    info["func"](df, OUTPUTS_DIR, quarters=quarters)
                else:
                    info["func"](df, OUTPUTS_DIR)
                
                # Update cache
                cache[filename] = {
                    "generated_at": str(input_file.stat().st_mtime),
                    "source": str(input_file.name),
                    "quarters": quarters
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


@router.get("/quarter-data")
async def get_quarter_data(quarters: List[str] = Query(None)):
    """
    Returns aggregated data for the Quarter Report dashboard.
    """
    try:
        # Find input file
        input_file = INPUTS_DIR / "10" / "file.xlsx"
        if not input_file.exists():
             for p in INPUTS_DIR.glob("*/*.xlsx"):
                input_file = p
                break
        
        if not input_file.exists():
             raise HTTPException(status_code=404, detail="No input Excel file found")

        import pandas as pd
        df = extract_large_gen_data(input_file)
        
        # Filter by quarters
        df['Projected COD'] = pd.to_datetime(df['Projected COD'], errors='coerce')
        df['Quarter'] = df['Projected COD'].dt.to_period('Q').astype(str)
        
        if quarters:
            df_filtered = df[df['Quarter'].isin(quarters)].copy()
        else:
            df_filtered = df.copy()
        
        if len(df_filtered) == 0:
            return {
                "summary": {"total_mw": 0, "total_projects": 0, "top_counties": []},
                "fuel_chart": {"labels": [], "data": [], "colors": []},
                "county_data": []
            }

        # Summary Stats
        total_mw = df_filtered['Capacity (MW)'].sum()
        total_projects = len(df_filtered)
        
        # Top Counties by MW
        top_counties = df_filtered.groupby('County')['Capacity (MW)'].sum().sort_values(ascending=False).head(5)
        top_counties_list = [{"county": c, "mw": mw} for c, mw in top_counties.items()]
        
        # Fuel Chart Data
        # Refine Fuel Type: If 'Other' or 'Unknown', try Technology
        def refine_fuel(row):
            fuel = normalize_fuel_type(row['Fuel'])
            if fuel in ['Other', 'Unknown']:
                tech = normalize_technology_type(row['Technology'])
                if tech != 'Unknown':
                    return tech
            return fuel

        df_filtered['Fuel_Normalized'] = df_filtered.apply(refine_fuel, axis=1)
        fuel_mw = df_filtered.groupby('Fuel_Normalized')['Capacity (MW)'].sum().sort_values(ascending=False)
        
        fuel_chart = {
            "labels": fuel_mw.index.tolist(),
            "data": fuel_mw.values.tolist(),
            "colors": [FUEL_COLORS.get(f, '#D3D3D3') for f in fuel_mw.index]
        }
        
        # Main Table Data (All Counties)
        # We want: County, Total MW, Fuel Breakdown (string or object)
        county_groups = df_filtered.groupby('County')
        county_data = []
        
        for county, group in county_groups:
            c_total_mw = group['Capacity (MW)'].sum()
            # Fuel breakdown for this county
            c_fuel_mw = group.groupby('Fuel_Normalized')['Capacity (MW)'].sum().sort_values(ascending=False)
            c_fuel_str = ", ".join([f"{f}: {mw:.1f} MW" for f, mw in c_fuel_mw.items()])
            
            county_data.append({
                "county": county,
                "total_mw": c_total_mw,
                "project_count": len(group),
                "fuel_breakdown": c_fuel_str
            })
            
        # Sort by Total MW desc
        county_data.sort(key=lambda x: x['total_mw'], reverse=True)
        
        return {
            "summary": {
                "total_mw": total_mw,
                "total_projects": total_projects,
                "top_counties": top_counties_list
            },
            "fuel_chart": fuel_chart,
            "county_data": county_data
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/county-details")
async def get_county_details(county: str, quarters: List[str] = Query(None)):
    """
    Returns detailed data for a specific county and quarters.
    """
    try:
        # Find input file
        input_file = INPUTS_DIR / "10" / "file.xlsx"
        if not input_file.exists():
             for p in INPUTS_DIR.glob("*/*.xlsx"):
                input_file = p
                break
        
        if not input_file.exists():
             raise HTTPException(status_code=404, detail="No input Excel file found")

        import pandas as pd
        df = extract_large_gen_data(input_file)
        
        # Filter by quarters and county
        df['Projected COD'] = pd.to_datetime(df['Projected COD'], errors='coerce')
        df['Quarter'] = df['Projected COD'].dt.to_period('Q').astype(str)
        
        # Refine Fuel Type logic (same as above)
        def refine_fuel(row):
            fuel = normalize_fuel_type(row['Fuel'])
            if fuel in ['Other', 'Unknown']:
                tech = normalize_technology_type(row['Technology'])
                if tech != 'Unknown':
                    return tech
            return fuel

        df['Fuel_Normalized'] = df.apply(refine_fuel, axis=1)
        
        if quarters:
            df_filtered = df[(df['Quarter'].isin(quarters)) & (df['County'] == county)].copy()
        else:
            df_filtered = df[df['County'] == county].copy()
        
        if len(df_filtered) == 0:
             raise HTTPException(status_code=404, detail="No data found for this county and quarter")

        # Summary Cards Logic
        # Sum of Solar, Wind, Storage (Battery)
        # We need to check normalized fuel types
        solar_mw = df_filtered[df_filtered['Fuel_Normalized'] == 'Solar']['Capacity (MW)'].sum()
        wind_mw = df_filtered[df_filtered['Fuel_Normalized'] == 'Wind']['Capacity (MW)'].sum()
        
        # Storage is tricky, it might be 'Other' or have specific tech. 
        # Let's check Technology column for 'Battery' or 'Storage'
        # Or use Fuel='Storage' if it exists? 
        # Looking at constants.py, 'BA' is Battery Energy Storage, 'EN' is Energy Storage.
        # Let's use Technology column for storage check.
        # Let's use Technology column for storage check.
        df_filtered['Technology_Normalized'] = df_filtered['Technology'].apply(normalize_technology_type)
        
        storage_mw = df_filtered[
            df_filtered['Technology_Normalized'].str.contains('Storage', case=False, na=False) |
            df_filtered['Technology_Normalized'].str.contains('Battery', case=False, na=False)
        ]['Capacity (MW)'].sum()
        
        summary_cards = {
            "solar_mw": solar_mw,
            "wind_mw": wind_mw,
            "storage_mw": storage_mw,
            "total_mw": df_filtered['Capacity (MW)'].sum(),
            "project_count": len(df_filtered)
        }
        
        # Detailed Project List
        # Convert NaN to None for JSON serialization
        projects = df_filtered.where(pd.notnull(df_filtered), None).to_dict(orient='records')
        
        return {
            "county": county,
            "quarters": quarters,
            "summary": summary_cards,
            "projects": projects
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
