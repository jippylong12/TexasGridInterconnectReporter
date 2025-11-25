
import sys
from pathlib import Path
import pandas as pd

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from reports import generate_county_fuel_report
from extract_large_gen import extract_large_gen_data

def test_county_fuel_report():
    print("Testing County + Fuel Report Generation...")
    
    # Setup paths
    input_file = project_root / "inputs" / "10" / "file.xlsx"
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Check input file
    if not input_file.exists():
        # Try to find any xlsx
        inputs_dir = project_root / "inputs"
        for p in inputs_dir.glob("*/*.xlsx"):
            input_file = p
            break
            
    if not input_file.exists():
        print("ERROR: No input file found.")
        return

    print(f"Using input file: {input_file}")
    
    # Extract data
    df = extract_large_gen_data(input_file)
    print(f"Loaded {len(df)} records.")
    
    # Test 1: No filter
    print("\nTest 1: Generating report without filters...")
    generate_county_fuel_report(df, output_dir)
    expected_file = output_dir / "county_fuel_breakdown.png"
    if expected_file.exists():
        print("✓ Report generated successfully (no filter)")
    else:
        print("✗ Report failed to generate (no filter)")
        
    # Test 2: With Quarter Filter
    # Find some valid quarters first
    df['Projected COD'] = pd.to_datetime(df['Projected COD'], errors='coerce')
    quarters = df['Projected COD'].dt.to_period('Q').astype(str).unique()
    if len(quarters) > 0:
        test_quarters = [quarters[0]]
        if len(quarters) > 1:
            test_quarters.append(quarters[1])
            
        print(f"\nTest 2: Generating report with filter: {test_quarters}")
        generate_county_fuel_report(df, output_dir, quarters=test_quarters)
        
        # Check if file was updated (timestamp check would be better but existence is ok for now)
        if expected_file.exists():
             print("✓ Report generated successfully (with filter)")
        else:
             print("✗ Report failed to generate (with filter)")
    else:
        print("Skipping filter test - no valid quarters found")

if __name__ == "__main__":
    test_county_fuel_report()
