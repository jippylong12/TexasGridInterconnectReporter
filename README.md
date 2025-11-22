# ⚡ ERCOT Generator Interconnection Report Generator

## 💡 Project Overview

This project is a modular, factorable **Python data pipeline** designed to process and analyze monthly **ERCOT Generator Interconnection Status Reports**.

The primary goal is to **ingest** data from various sheets within the provided Excel reports, **transform** and clean the raw data, and **generate** several distinct, structured output reports for analysis and tracking of large and small-scale power generation projects connecting to the Texas grid.



[Image of a data processing pipeline]

# Texas Grid Interconnect Reporter

A Python tool to extract and analyze ERCOT (Electric Reliability Council of Texas) Generation Interconnection and Modeling (GIM) monthly reports.

## Overview

This project processes ERCOT GIM reports in Excel format to extract project details for large generators. The reports contain information about interconnection studies, project statuses, and grid capacity planning.

## Project Structure

```
TexasGridInterconnectReporter/
├── inputs/                  # Excel files organized by month
│   ├── 08/
│   │   └── file.xlsx       # August report
│   ├── 09/
│   │   └── file.xlsx       # September report
│   └── README.md
├── extract_large_gen.py    # Main extraction script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Excel file:**
   - Create a month folder in `inputs/` (e.g., `inputs/08/` for August)
   - Place your ERCOT GIM Excel report as `file.xlsx` in that folder

## Usage

### Extract Large Gen Data

Run the script with the default path (`inputs/08/file.xlsx`):
```bash
python extract_large_gen.py
```

Or specify a custom file path:
```bash
python extract_large_gen.py inputs/09/file.xlsx
```

### Output

The script will:
1. Display the sheet contents in the console
2. Show row and column counts
3. List all column names
4. Save the data as a CSV file in the same directory (e.g., `inputs/08/file_large_gen.csv`)

## ERCOT GIM Report Sheets

The Excel files contain the following sheets:
- **Disclaimer and References** - Usage disclaimer and ERCOT Binding Documents
- **Acronyms** - List of acronyms used throughout the report
- **Summary** - Project aggregate counts and megawatt capacities by GIM phase and fuel type
- **Project Details - Large Gen** ⭐ *Currently extracted by this tool*
- **Project Details - Small Gen** - Small Generator project details
- **GIM Trends** - Historical and projected interconnection study trends
- **Commissioning Update** - Monthly commissioning approval milestones
- **Inactive Projects** - List of inactive projects
- **Cancellation Update** - Projects cancelled for the month

## Future Enhancements

- Support for comparing multiple months
- Extraction of additional sheets
- Data analysis and visualization
- Automated report generation

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- openpyxl >= 3.1.0