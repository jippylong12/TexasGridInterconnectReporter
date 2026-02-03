# Project Context

## Constraints
- Follow AGENTS.md directives: modular Python (SRP), PEP 8, type hints, pandas, dependencies in requirements.txt.
- Update `reports/README.md` when generating new reports.
- Prefer `rg` for search when available.

## Anti-Patterns
- Avoid monolithic scripts that mix ingestion, processing, and generation.
- Do not introduce untracked dependencies.

## Patterns & Recipes
- **Topic:** Inputs layout
- **Rule:** Input reports are stored as `inputs/<year>/<month>/file.xlsx` and should be resolved by year+month.
- **Reason:** Supports monthly data across years and keeps selection logic consistent.
- **Topic:** Month picker API
- **Rule:** When no `year` is provided, `/api/months` returns `value` as `YYYY-MM` so the frontend must parse and pass both `year` and `month` back to data endpoints.
- **Reason:** Ensures correct selection across multiple years and keeps the latest month sorted first.
- **Topic:** Backend imports
- **Rule:** Backend modules should import `extract_large_gen` and `constants` directly (not via `src.`) because `src` is on `sys.path` but is not a package.
- **Reason:** Avoids `ModuleNotFoundError` when running Uvicorn.
- **Topic:** Deploy script guard
- **Rule:** `scripts/deploy.sh` validates the active gcloud project is `texas-grid-interconnect-report` before deploying.
- **Reason:** Prevents accidental deploys to the wrong GCP project.
