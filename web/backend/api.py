import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
import zipfile
import os
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

# Import report generation logic
# Assuming src is in path (handled in main.py)
from src.extract_large_gen import extract_large_gen_data

from src.constants import normalize_fuel_type, normalize_technology_type, FUEL_COLORS
import calendar

router = APIRouter()

# Define paths
# We need to be careful with paths. 
# main.py adds project root to sys.path.
# So we can find 'inputs' relative to project root.
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUTS_DIR = PROJECT_ROOT / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
STATIC_DIR = PROJECT_ROOT / "web" / "frontend" / "dist"

def get_input_file(year: Optional[str] = None, month: Optional[str] = None) -> Path:
    """
    Resolves the input file path based on the provided year and month.
    If year/month are None, tries to find the latest available file.
    """
    if year and month:
        input_file = INPUTS_DIR / year / month / "file.xlsx"
        if input_file.exists():
            return input_file
    
    # If not specified or not found, find latest
    # 1. Find latest year
    year_dirs = [d for d in INPUTS_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
    if not year_dirs:
        # Fallback for old structure (flat months) - though we moved them
        month_dirs = [d for d in INPUTS_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
        if month_dirs:
             month_dirs.sort(key=lambda x: int(x.name), reverse=True)
             return month_dirs[0] / "file.xlsx"
        raise HTTPException(status_code=404, detail="No input data directories found")
    
    year_dirs.sort(key=lambda x: int(x.name), reverse=True)
    
    for y_dir in year_dirs:
        # 2. Find latest month in this year
        month_dirs = [d for d in y_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        month_dirs.sort(key=lambda x: int(x.name), reverse=True)
        
        for m_dir in month_dirs:
            input_file = m_dir / "file.xlsx"
            if input_file.exists():
                return input_file

    raise HTTPException(status_code=404, detail="No input Excel file found")

@router.get("/years")
async def get_years():
    """
    Returns a list of available years.
    """
    try:
        year_dirs = [d for d in INPUTS_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
        year_dirs.sort(key=lambda x: int(x.name), reverse=True)
        return {"years": [d.name for d in year_dirs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/months")
async def get_months(year: Optional[str] = Query(None)):
    """
    Returns a list of available months for a given year.
    """
    try:
        if not year:
            # If no year provided, try to find latest year
            year_dirs = [d for d in INPUTS_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
            if year_dirs:
                year_dirs.sort(key=lambda x: int(x.name), reverse=True)
                year = year_dirs[0].name
            else:
                return {"months": []}

        year_dir = INPUTS_DIR / year
        if not year_dir.exists():
             return {"months": []}

        month_dirs = [d for d in year_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        month_dirs.sort(key=lambda x: int(x.name), reverse=True)
        
        months = []
        for d in month_dirs:
            try:
                month_num = int(d.name)
                month_name = calendar.month_name[month_num]
                months.append({
                    "value": d.name,
                    "label": f"{month_name}"
                })
            except:
                continue
                
        return {"months": months}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
# We will mount it in main.py usually, but since api.py is a router, we might need to do it in main.py.
# However, the user wants "single Google cloud platform project" and "backend to be serverless".
# Serving static files from FastAPI is a good way to do this.
# Let's check main.py first to see where the app is defined.

import json

from pydantic import BaseModel




@router.get("/quarters")
async def get_quarters(year: Optional[str] = Query(None), month: Optional[str] = Query(None)):
    """
    Returns a list of available quarters from the dataset.
    """
    try:
        # Find input file
        input_file = get_input_file(year, month)
        print(f"Using input file: {input_file}")

        df = extract_large_gen_data(input_file)
        
        # Extract quarters
        df['Projected COD'] = pd.to_datetime(df['Projected COD'], errors='coerce')
        df = df[df['Projected COD'].notna()]
        quarters = sorted(df['Projected COD'].dt.to_period('Q').astype(str).unique())
        
        # Determine report period based on file path (folder name)
        report_period = "Report"
        try:
            # Structure: inputs/year/month/file.xlsx
            if input_file.parent.name.isdigit() and input_file.parent.parent.name.isdigit():
                month_num = int(input_file.parent.name)
                year_num = input_file.parent.parent.name
                month_name = calendar.month_name[month_num]
                report_period = f"{month_name} {year_num}"
        except:
            pass

        return {"quarters": quarters, "report_period": report_period}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quarter-data")
async def get_quarter_data(quarters: List[str] = Query(None), year: Optional[str] = Query(None), month: Optional[str] = Query(None)):
    """
    Returns aggregated data for the Quarter Report dashboard.
    """
    try:
        # Find input file
        input_file = get_input_file(year, month)

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
async def get_county_details(county: str, quarters: List[str] = Query(None), year: Optional[str] = Query(None), month: Optional[str] = Query(None)):
    """
    Returns detailed data for a specific county and quarters.
    """
    try:
        # Find input file
        input_file = get_input_file(year, month)

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
async def get_county_map_data(quarters: List[str] = Query(None), year: Optional[str] = Query(None), month: Optional[str] = Query(None)):
    """
    Returns county-level data optimized for map visualization.
    """
    try:
        # Find input file
        input_file = get_input_file(year, month)

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


@router.get("/comparison-data")
async def get_comparison_data(
    base_year: str, 
    base_month: str, 
    target_year: str, 
    target_month: str
):
    """
    Compares two report months and returns added projects and updates.
    """
    try:
        base_file = get_input_file(base_year, base_month)
        target_file = get_input_file(target_year, target_month)
        
        df_base = extract_large_gen_data(base_file)
        df_target = extract_large_gen_data(target_file)
        
        # Identify projects by INR (Interconnection Request)
        # Use 'INR' column as unique identifier
        if 'INR' not in df_base.columns or 'INR' not in df_target.columns:
             raise HTTPException(status_code=400, detail="INR column missing in one or both files")
             
        # 1. Added Projects
        # Projects in target but not in base
        base_inrs = set(df_base['INR'].dropna())
        target_inrs = set(df_target['INR'].dropna())
        
        added_inrs = target_inrs - base_inrs
        added_projects = df_target[df_target['INR'].isin(added_inrs)].copy()
        
        # Normalize Fuel Type
        def refine_fuel(row):
            fuel = normalize_fuel_type(row['Fuel'])
            if fuel in ['Other', 'Unknown']:
                tech = normalize_technology_type(row['Technology'])
                if tech != 'Unknown':
                    return tech
            return fuel

        added_projects['Fuel_Normalized'] = added_projects.apply(refine_fuel, axis=1)
        
        # Format added projects
        # Include Fuel_Normalized as 'Fuel Type'
        added_projects['Fuel Type'] = added_projects['Fuel_Normalized']
        
        added_projects_list = added_projects.where(pd.notnull(added_projects), None).to_dict(orient='records')
        
        # 2. Flagged Changes from Target Report
        # Look for the "Change indicators" column in the TARGET report and list any projects
        # that have a non-empty value. This column flags what changed in that specific report month.
        
        flagged_changes_list = []
        
        # Helper to check if a value is valid (not NaN, not empty string, not 'nan' string)
        def is_valid_value(v):
            if pd.isna(v): return False
            if str(v).lower() == 'nan': return False
            if str(v).strip() == '': return False
            return True
        
        # Let's check available columns in df_target
        available_columns = df_target.columns.tolist()
        
        # Find the "Change indicators" column (it has a long name with various change types)
        change_indicator_col = next(
            (c for c in available_columns if 'Change indicator' in c or 'Change Indicator' in c),
            None
        )
        
        if change_indicator_col:
            # Iterate through all target projects and find ones with flagged changes
            for _, row in df_target.iterrows():
                change_value = row.get(change_indicator_col)
                if is_valid_value(change_value):
                    flag_str = str(change_value).strip()
                    
                    # Build a list of new values based on what's flagged
                    new_values = []
                    
                    # Map flag types to their corresponding column values
                    if 'COD' in flag_str:
                        cod_val = row.get('Projected COD')
                        if is_valid_value(cod_val):
                            # Format datetime nicely
                            try:
                                cod_formatted = pd.to_datetime(cod_val).strftime('%Y-%m-%d')
                            except:
                                cod_formatted = str(cod_val)
                            new_values.append(f"New COD: {cod_formatted}")
                    
                    if 'MW' in flag_str:
                        mw_val = row.get('Capacity (MW)')
                        if is_valid_value(mw_val):
                            new_values.append(f"New MW: {mw_val}")
                    
                    if 'Proj Name' in flag_str:
                        name_val = row.get('Project Name')
                        if is_valid_value(name_val):
                            new_values.append(f"New Name: {name_val}")
                    
                    if 'SFS' in flag_str or 'NtP' in flag_str:
                        # Try to find SFS/NtP related columns
                        sfs_val = row.get('SFS') or row.get('NtP') or row.get('SFS/NtP')
                        if is_valid_value(sfs_val):
                            new_values.append(f"SFS/NtP: {sfs_val}")
                    
                    if 'FIS Request' in flag_str:
                        fis_val = row.get('FIS Requested')
                        if is_valid_value(fis_val):
                            try:
                                fis_formatted = pd.to_datetime(fis_val).strftime('%Y-%m-%d')
                            except:
                                fis_formatted = str(fis_val)
                            new_values.append(f"FIS Requested: {fis_formatted}")
                    
                    if 'INA-to-PLN' in flag_str or 'Status' in flag_str:
                        # Look for status column
                        status_col = next((c for c in available_columns if 'GIM Study Phase' in c or 'Status' in c), None)
                        if status_col:
                            status_val = row.get(status_col)
                            if is_valid_value(status_val):
                                new_values.append(f"Status: {status_val}")
                    
                    flagged_changes_list.append({
                        "INR": row.get('INR', 'N/A'),
                        "Project Name": row.get('Project Name', 'N/A'),
                        "County": row.get('County', 'N/A'),
                        "change_flag": flag_str,
                        "new_values": new_values
                    })
        
        # Sort Added Projects: 1. COD (Earliest first), 2. County
        # Ensure COD is datetime for sorting
        def get_cod_date(x):
            try:
                return pd.to_datetime(x.get('Projected COD'), errors='coerce')
            except:
                return pd.NaT

        added_projects_list.sort(key=lambda x: (get_cod_date(x) or pd.Timestamp.max, str(x.get('County', '') or '')))
        
        # Sort Flagged Changes: County
        flagged_changes_list.sort(key=lambda x: str(x.get('County', '') or ''))
        
        # 3. Full Comparison - Compare ALL columns for common projects
        full_comparison_list = []
        
        # Projects in both base and target
        common_inrs = base_inrs.intersection(target_inrs)
        
        # Create indexed dataframes for faster lookup
        df_base_indexed = df_base.set_index('INR')
        df_target_indexed = df_target.set_index('INR')
        
        # Columns to skip in comparison (identifiers, metadata, already shown in Tab 2)
        skip_columns = {'INR', 'County'}
        # Also skip any column containing "Change indicator" as it's shown in Tab 2
        
        # Get all columns from target (use as reference)
        all_columns = [c for c in df_target.columns if c not in skip_columns and 'Change indicator' not in c]
        
        for inr in common_inrs:
            try:
                base_row = df_base_indexed.loc[inr]
                target_row = df_target_indexed.loc[inr]
            except KeyError:
                continue
            
            changes = []
            
            for col in all_columns:
                # Get values from both rows
                val_base = base_row.get(col) if col in base_row.index else None
                val_target = target_row.get(col) if col in target_row.index else None
                
                # Normalize values for comparison
                def normalize_val(v):
                    if pd.isna(v):
                        return None
                    s = str(v).strip()
                    if s.lower() == 'nan' or s == '':
                        return None
                    return s
                
                norm_base = normalize_val(val_base)
                norm_target = normalize_val(val_target)
                
                # Skip if both are None/empty
                if norm_base is None and norm_target is None:
                    continue
                
                # Check if values differ
                if norm_base != norm_target:
                    # Format datetime values nicely
                    def format_val(v):
                        if v is None:
                            return "(empty)"
                        try:
                            dt = pd.to_datetime(v, errors='raise')
                            return dt.strftime('%Y-%m-%d')
                        except:
                            return str(v)
                    
                    changes.append({
                        "column": col,
                        "old_value": format_val(norm_base),
                        "new_value": format_val(norm_target)
                    })
            
            # Only include projects with at least one change
            if changes:
                full_comparison_list.append({
                    "INR": inr,
                    "Project Name": target_row.get('Project Name', 'N/A'),
                    "County": target_row.get('County', 'N/A'),
                    "change_count": len(changes),
                    "changes": changes
                })
        
        # Sort by County first, then by change count descending
        full_comparison_list.sort(key=lambda x: (str(x.get('County', '') or ''), -x['change_count']))
                
        return {
            "added_projects": added_projects_list,
            "flagged_changes": flagged_changes_list,
            "full_comparison": full_comparison_list,
            "base_period": f"{base_month}/{base_year}",
            "target_period": f"{target_month}/{target_year}"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
