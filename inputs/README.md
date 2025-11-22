# Inputs Directory

This directory contains ERCOT GIM (Generation Interconnection and Modeling) monthly reports.

## Directory Structure

```
inputs/
├── 08/
│   └── file.xlsx
├── 09/
│   └── file.xlsx
└── ...
```

## File Naming Convention

- Each month's report should be placed in a folder named with the two-digit month number (e.g., `08` for August, `09` for September)
- The Excel file should be named `file.xlsx`
- Files must be in `.xlsx` format

## Example

To add the August 2025 report:
1. Create directory: `inputs/08/`
2. Place the ERCOT GIM report as: `inputs/08/file.xlsx`

## Sheet Information

The Excel files contain multiple sheets:
- **Disclaimer and References** - Disclaimer and ERCOT Binding Documents
- **Acronyms** - List of acronyms used in the report
- **Summary** - Project aggregate counts and megawatt capacities
- **Project Details - Large Gen** - Large Generator project details (Full Interconnection Study requested)
- **Project Details - Small Gen** - Small Generator project details (Resource Registration approved)
- **GIM Trends** - Historical and projected interconnection study trends
- **Commissioning Update** - Monthly commissioning approval milestones
- **Inactive Projects** - List of inactive projects
- **Cancellation Update** - Projects cancelled for the month
