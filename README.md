# ⚡ Texas Grid Interconnect Reporter (ERCOT)

A modern, end-to-end toolkit to parse monthly ERCOT Generator Interconnection Status Reports (Excel), generate curated analytics, and deliver them via a web UI and APIs.

- Python data pipeline (ETL) for extracting and transforming ERCOT report data
- FastAPI backend serving APIs and orchestrating report generation
- React + Vite frontend for an interactive dashboard and downloads
- CLI utilities for power users and automation
- Optional Docker and one-command deploy to Google Cloud Run

---

## ✨ What’s New
- Unified web application (frontend + backend) with one-click startup via `start_app.sh`
- ZIP download of all generated visualizations
- Cleaner project structure and deployment workflow
- Deployment guide for Google Cloud Run (`README_DEPLOY.md`)

---

## 🚀 Quick Start (Web App)
The easiest way to use the reporter is through the web interface.

1) Install dependencies
```bash
# Backend deps
pip install -r requirements.txt

# Frontend deps
cd web/frontend
npm install
cd ../..
```

2) Start the app
```bash
./start_app.sh
```
This launches both servers:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

3) Open the UI
- Visit http://localhost:5173
- Use the Dashboard to generate reports and download results

### Web App Features
- Dashboard overview and guided actions
- One-click generation of all visualization reports
- In-browser chart previews (when available)
- Download all artifacts as a ZIP

---

## 🧰 Command Line (CLI)
Prefer the terminal or automations? Use the CLI utilities directly.

Extract Large Gen data
```bash
python src/extract_large_gen.py
```

Generate all reports
```bash
python src/reports.py --report all
```

Notes
- Inputs are read from `inputs/`
- Outputs are written to `outputs/`

---

## 📁 Project Structure
```
TexasGridInterconnectReporter/
├── start_app.sh                 # One-click startup (frontend + backend)
├── web/                         # Web Application
│   ├── backend/                 # FastAPI Backend (serves API and static files in prod)
│   └── frontend/                # React + Vite Frontend (dev server at :5173)
├── src/                         # Core Python ETL and report generation
│   ├── extract_large_gen.py
│   └── reports.py
├── inputs/                      # Place ERCOT Excel files here
├── outputs/                     # Generated reports and artifacts
├── tests/                       # Test suite (pytest)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container build (backend + static frontend)
├── deploy.sh                    # Build + deploy to Cloud Run
├── config.yaml                  # Deploy config (project_id, region, etc.)
├── README_DEPLOY.md             # Detailed deployment guide for GCP Cloud Run
└── AGENTS.md                    # Development conventions and directives
```

---

## 📦 Data Inputs and Outputs
- Expected inputs: ERCOT monthly Generator Interconnection Status Report Excel files
- Common sheets consumed (see `AGENTS.md`):
  - `Disclaimer and References`, `Acronyms`, `Summary`
  - `Project Details - Large Gen`, `Project Details - Small Gen`
  - `GIM Trends`, `Commissioning Update`, `Inactive Projects`, `Cancellation Update`
- Outputs: curated tables, visualizations, and zipped bundles in `outputs/`

---

## 🧪 Testing and Quality
- Run tests
```bash
pytest -q
```
- Lint (ruff) and format (black)
```bash
ruff check src/
black src/
```
See `AGENTS.md` for conventions (PEP 8, typing, modular design).

---

## 🐳 Run with Docker (Optional)
Build and run locally as a container:
```bash
# Build image
docker build -t texas-grid-reporter .

# Run container
docker run -p 8080:8080 texas-grid-reporter
```
Open http://localhost:8080

---

## ☁️ Deploy to Google Cloud Run
Use the provided script and guide.

1) Configure `config.yaml` (project_id, region, service_name, image_name)
2) Follow prerequisites and IAM steps in `README_DEPLOY.md`
3) Deploy
```bash
./deploy.sh
```
Full details: see `README_DEPLOY.md`.

---

## ⚙️ Requirements
- Python 3.7+ (recommend 3.9 or newer)
- Node.js and npm (for frontend dev)
- Key Python packages: pandas, openpyxl, matplotlib, fastapi, uvicorn

Install backend deps
```bash
pip install -r requirements.txt
```
Install frontend deps
```bash
cd web/frontend && npm install && cd -
```

---

## 📝 Troubleshooting
- Frontend doesn’t load: ensure Node and npm are installed; reinstall with `npm install` in `web/frontend`
- Backend 500/connection error: verify `pip install -r requirements.txt` completed successfully; check port 8000 availability
- No outputs generated: confirm input Excel files exist in `inputs/` and match expected sheet names
- Port conflicts: change Vite dev port or FastAPI port in the respective configs/scripts

---

## 🔐 Notes
- This project processes public ERCOT reports; verify your usage aligns with ERCOT’s terms where applicable.
- For production, prefer running via Docker or Cloud Run for reproducibility.