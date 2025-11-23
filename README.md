# ⚡ ERCOT Generator Interconnection Report Generator

## 💡 Project Overview

This project is a modular **Python data pipeline** designed to process and analyze monthly **ERCOT Generator Interconnection Status Reports**.

The primary goal is to **ingest** data from various sheets within the provided Excel reports, **transform** and clean the raw data, and **generate** visualization reports for analysis and tracking of large-scale power generation projects connecting to the Texas grid.

## Project Structure

```
TexasGridInterconnectReporter/
├── src/                        # Source code
│   ├── extract_large_gen.py   # Data extraction script
│   └── reports.py             # Report generation script
├── inputs/                     # Excel files organized by month
│   ├── 08/
│   │   └── file.xlsx          # August report
│   ├── 10/
│   │   └── file.xlsx          # October report
│   └── README.md
├── outputs/                    # Generated report visualizations (PNG)
│   ├── county_mw_breakdown.png
│   ├── cod_quarterly_buckets.png
│   └── fuel_type_breakdown.png
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md                   # This file
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Excel file:**
   - Create a month folder in `inputs/` (e.g., `inputs/10/` for October)
   - Place your ERCOT GIM Excel report as `file.xlsx` in that folder

## Usage

### Extract Large Gen Data

Run the extraction script with the default path (`inputs/10/file.xlsx`):
```bash
python src/extract_large_gen.py
```

Or specify a custom file path:
```bash
python src/extract_large_gen.py inputs/09/file.xlsx
```

**Output:**
- Displays sheet contents in the console
- Shows row and column counts
- Lists all column names
- Saves data as CSV in the same directory (e.g., `inputs/10/file_large_gen.csv`)

### Generate Reports

Generate all three visualization reports:
```bash
python src/reports.py
```

Or generate a specific report using the `--report` (or `-r`) argument:
```bash
# Generate only the county breakdown report
python src/reports.py --report county

# Generate only the COD quarterly buckets report
python src/reports.py --report cod

# Generate only the fuel type breakdown report
python src/reports.py --report fuel

# Generate only the technology type breakdown report
python src/reports.py --report technology

# Generate all reports (default)
python src/reports.py --report all
```

You can also specify a custom input file:
```bash
python src/reports.py inputs/09/file.xlsx --report county
```

**Report Options:**
- `county` - County MW breakdown (horizontal bar chart)
- `cod` - COD quarterly buckets (vertical bar chart)
- `fuel` - Fuel type breakdown (pie chart with table)
- `technology` - Technology type breakdown (pie chart with table)
- `all` - Generate all reports (default)

**Output:**
All reports are saved as high-resolution PNG files in the `outputs/` directory.

## Reports

### 1. County MW Breakdown
**File:** `outputs/county_mw_breakdown.png`

**Visualization:** Horizontal bar chart

**Description:** Shows the total megawatt (MW) capacity aggregated by county. Counties are sorted by total capacity, making it easy to identify which counties have the most generation capacity in the interconnection queue.

**Key Insights:**
- Identifies top counties by MW capacity
- Helps understand geographic distribution of projects
- Useful for regional planning and analysis

---

### 2. COD Quarterly Buckets
**File:** `outputs/cod_quarterly_buckets.png`

**Visualization:** Vertical bar chart

**Description:** Displays the count of projects grouped by their Projected Commercial Operation Date (COD) in quarterly buckets. This shows when projects are expected to come online over time.

**Key Insights:**
- Identifies peak quarters for project completions
- Shows trends in project timeline distribution
- Helps forecast grid capacity additions

---

### 3. Fuel Type Breakdown
**File:** `outputs/fuel_type_breakdown.png`

**Visualization:** Pie chart with detailed data table

**Description:** Analyzes the distribution of projects by fuel type (e.g., Solar, Wind, Natural Gas). Shows both the percentage distribution by total MW capacity and a detailed breakdown table with project counts and MW totals. Fuel type acronyms are automatically normalized to full names (e.g., SOL → Solar, WIN → Wind).

**Key Insights:**
- Shows energy mix in the interconnection queue
- Compares renewable vs. traditional fuel sources
- Displays both project count and capacity metrics

---

### 4. Technology Type Breakdown
**File:** `outputs/technology_type_breakdown.png`

**Visualization:** Pie chart with detailed data table

**Description:** Analyzes the distribution of projects by technology type (e.g., Battery Energy Storage, Photovoltaic Solar, Wind Turbine). This provides more granular detail than the fuel type report, showing specific technology implementations. Technology acronyms are automatically normalized to full names (e.g., PV → Photovoltaic Solar, BA → Battery Energy Storage).

**Key Insights:**
- Identifies specific technology trends (e.g., battery storage vs. solar PV)
- Shows technology diversity within fuel categories
- Helps understand technology adoption patterns

---

## ERCOT Data Acronyms

### Fuel Type Codes
The following fuel type acronyms are used in ERCOT GIM reports and are automatically normalized in the reports:

- **BIO** = Biomass
- **COA** = Coal
- **GAS** = Gas
- **GEO** = Geothermal
- **HYD** = Hydrogen
- **NUC** = Nuclear
- **OIL** = Fuel Oil
- **OTH** = Other
- **PET** = Petcoke
- **SOL** = Solar
- **WAT** = Water
- **WIN** = Wind

### Technology Type Codes
The following technology type acronyms are used in ERCOT GIM reports and are automatically normalized in the reports:

- **BA** = Battery Energy Storage
- **CC** = Combined-Cycle
- **CE** = Compressed Air Energy Storage
- **CP** = Concentrated Solar Power
- **EN** = Energy Storage
- **FC** = Fuel Cell
- **GT** = Combustion (Gas) Turbine
- **HY** = Hydroelectric Turbine
- **IC** = Internal Combustion Engine
- **OT** = Other
- **PV** = Photovoltaic Solar
- **ST** = Steam Turbine
- **WT** = Wind Turbine

---

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
- Extraction of additional sheets (Small Gen, GIM Trends, etc.)
- Time-series analysis across multiple reports
- Interactive dashboards
- Automated monthly report generation

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- matplotlib >= 3.7.0

## Data Source

Reports are sourced from ERCOT's Generator Interconnection and Modeling (GIM) monthly status reports, which track generation projects seeking to interconnect to the ERCOT grid.