# ⚡ ERCOT Generator Interconnection Report Generator

## 💡 Project Overview

This project is a modular **Python data pipeline** designed to process and analyze monthly **ERCOT Generator Interconnection Status Reports**.

It now includes a **Modern Web Application** to visualize and generate reports with a premium user interface.

## 🚀 Web Application (New!)

The easiest way to use the reporter is through the new web interface.

### Quick Start

1.  **Install Dependencies:**
    ```bash
    # Backend
    pip install -r requirements.txt
    
    # Frontend
    cd web/frontend
    npm install
    cd ../..
    ```

2.  **Run the App:**
    ```bash
    ./start_app.sh
    ```
    This will start both the backend and frontend servers.
    
3.  **Open in Browser:**
    Navigate to `http://localhost:5173`

### Features
- **Dashboard:** Beautiful landing page with project overview.
- **Report Generation:** One-click generation of all visualization reports.
- **Download:** Download all generated reports as a ZIP file.
- **Visualizations:** View generated charts directly in the browser.

---

## 🛠 CLI Usage (Legacy)

You can still use the command line tools if you prefer.

### Extract Large Gen Data
```bash
python src/extract_large_gen.py
```

### Generate Reports
```bash
python src/reports.py --report all
```

## Project Structure

```
TexasGridInterconnectReporter/
├── start_app.sh                # One-click startup script
├── web/                        # Web Application
│   ├── backend/               # FastAPI Backend
│   └── frontend/              # React + Vite Frontend
├── src/                        # Core Python Logic
│   ├── extract_large_gen.py
│   └── reports.py
├── inputs/                     # Excel Data Files
├── outputs/                    # Generated Reports
└── requirements.txt
```

## Requirements

- Python 3.7+
- Node.js & npm
- pandas, openpyxl, matplotlib, fastapi, uvicorn