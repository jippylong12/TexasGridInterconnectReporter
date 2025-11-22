#!/usr/bin/env python3
"""Debug script to find where the actual column headers are"""

import pandas as pd
from pathlib import Path

file_path = Path("inputs/10/file.xlsx")
sheet_name = "Project Details - Large Gen"

# Read rows 28-35 to see the header structure
df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', skiprows=28, header=None, nrows=8)

print("Rows 29-36 (skiprows=28, showing 8 rows):")
print("=" * 120)
for idx in range(len(df)):
    print(f"\nRow {29+idx} (index {idx}):")
    for col_idx in range(min(12, len(df.columns))):  # Show first 12 columns
        val = df.iloc[idx, col_idx]
        if pd.notna(val) and str(val).strip():
            print(f"  Col {col_idx}: {val}")
