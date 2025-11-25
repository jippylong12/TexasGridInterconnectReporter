#!/usr/bin/env python3
"""
Texas Grid Interconnect Reporter
Extracts and displays the "Project Details - Large Gen" sheet from ERCOT GIM reports.
"""

import pandas as pd
import sys
from pathlib import Path


def extract_large_gen_data(file_path: Path) -> pd.DataFrame:
    """
    Extract the 'Project Details - Large Gen' sheet from an Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        DataFrame containing the Large Gen project details
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the sheet is not found in the workbook
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the specific sheet
    sheet_name = "Project Details - Large Gen"
    
    try:
        # The header structure is complex:
        # - UI Row 31 (0-indexed row 30, index 0 after skip) contains headers for columns 0-10
        # - UI Rows 32-35 (indices 1-4 after skip) contain multi-row headers for columns 11+
        # - UI Row 36 (index 5 after skip) is the first data row
        
        # Read starting from UI row 31 (skiprows=30)
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', skiprows=30, header=None)
        
        # Extract the header rows
        main_header = df.iloc[0]  # Row 32: INR, Project Name, GIM Study Phase, etc.
        multi_header_1 = df.iloc[1]  # Row 33
        multi_header_2 = df.iloc[2]  # Row 34
        multi_header_3 = df.iloc[3]  # Row 35
        multi_header_4 = df.iloc[4]  # Row 36
        
        # Build column names
        column_names = []
        for col_idx in range(len(df.columns)):
            # For columns 0-10, use the main header from row 32
            main_val = main_header.iloc[col_idx] if col_idx < len(main_header) else None
            
            if pd.notna(main_val) and str(main_val).strip():
                column_names.append(str(main_val).strip())
            else:
                # For columns 11+, combine the multi-row headers
                parts = []
                for header_row in [multi_header_1, multi_header_2, multi_header_3, multi_header_4]:
                    val = header_row.iloc[col_idx] if col_idx < len(header_row) else None
                    if pd.notna(val) and str(val).strip():
                        parts.append(str(val).strip())
                
                if parts:
                    column_names.append(' '.join(parts))
                else:
                    column_names.append(f'Column_{col_idx}')
        
        # Set column names and drop the header rows (rows 0-5)
        df.columns = column_names
        df = df.iloc[5:].reset_index(drop=True)
        
        # Clean Capacity (MW) column
        if 'Capacity (MW)' in df.columns:
            # Convert to numeric, coercing errors to NaN
            df['Capacity (MW)'] = pd.to_numeric(df['Capacity (MW)'], errors='coerce')
            # Fill NaNs with 0
            df['Capacity (MW)'] = df['Capacity (MW)'].fillna(0)
            # Ensure all values are positive (handle negative values like -100 or (100))
            df['Capacity (MW)'] = df['Capacity (MW)'].abs()
        
        return df
    except ValueError as e:
        raise ValueError(f"Sheet '{sheet_name}' not found in {file_path}. Error: {e}")


def main():
    """
    Main function to process the Excel file and display results.
    """
    # Default file path pattern: inputs/MM/file.xlsx
    # For now, we'll look for inputs/10/file.xlsx
    # Script is in src/, so we need to go up one level
    default_path = Path("../inputs/10/file.xlsx")
    
    # Allow command line argument to override default path
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = default_path
    
    print(f"Reading file: {file_path}")
    print("=" * 80)
    
    try:
        # Extract the data
        df = extract_large_gen_data(file_path)
        
        # Display basic information
        print(f"\nSheet: Project Details - Large Gen")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print("\n" + "=" * 80)
        
        # Display column names
        print("\nColumn Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        print("\n" + "=" * 80)
        
        # Display the first 10 rows
        print("\nData (first 10 rows):")
        print(df.head(10).to_string())
        
        # Optionally save to CSV for easier viewing
        output_path = file_path.parent / f"{file_path.stem}_large_gen.csv"
        df.to_csv(output_path, index=False)
        print(f"\n" + "=" * 80)
        print(f"\nData also saved to: {output_path}")
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(f"\nPlease place your Excel file at: {file_path}")
        print(f"Or run with a custom path: python extract_large_gen.py <path_to_file>")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
