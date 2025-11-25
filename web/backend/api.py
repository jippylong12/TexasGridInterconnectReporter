import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
import zipfile
import os
from fastapi.staticfiles import StaticFiles

# Import report generation logic
# Assuming src is in path (handled in main.py)
from src.extract_large_gen import extract_large_gen_data

from src.constants import normalize_fuel_type, normalize_technology_type, FUEL_COLORS

router = APIRouter()

# Define paths
# We need to be careful with paths. 
# main.py adds project root to sys.path.
# So we can find 'inputs' relative to project root.
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
STATIC_DIR = PROJECT_ROOT / "web" / "frontend" / "dist"

# Mount static files
# We will mount it in main.py usually, but since api.py is a router, we might need to do it in main.py.
# However, the user wants "single Google cloud platform project" and "backend to be serverless".
# Serving static files from FastAPI is a good way to do this.
# Let's check main.py first to see where the app is defined.

import json
from typing import Optional, List
from pydantic import BaseModel




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

@router.get("/county-map-data")
async def get_county_map_data(quarters: List[str] = Query(None)):
    """
    Returns county-level data optimized for map visualization.
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
            return {"counties": []}

        # Refine Fuel Type logic
        def refine_fuel(row):
            fuel = normalize_fuel_type(row['Fuel'])
            if fuel in ['Other', 'Unknown']:
                tech = normalize_technology_type(row['Technology'])
                if tech != 'Unknown':
                    return tech
            return fuel

        df_filtered['Fuel_Normalized'] = df_filtered.apply(refine_fuel, axis=1)
        
        # Aggregate by county
        county_groups = df_filtered.groupby('County')
        county_map_data = []
        
        for county, group in county_groups:
            total_mw = group['Capacity (MW)'].sum()
            project_count = len(group)
            
            # Get top 2 fuel types for brief summary
            fuel_mw = group.groupby('Fuel_Normalized')['Capacity (MW)'].sum().sort_values(ascending=False)
            top_fuels = fuel_mw.head(2)
            fuel_summary = ", ".join([f"{f}: {mw:.0f}MW" for f, mw in top_fuels.items()])
            
            county_map_data.append({
                "county": county,
                "total_mw": round(total_mw, 1),
                "project_count": project_count,
                "fuel_summary": fuel_summary
            })
        
        return {"counties": county_map_data}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
