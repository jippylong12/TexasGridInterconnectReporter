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
- **Topic:** Feature backlog tracking
- **Rule:** Maintain future feature ideas in `docs/FEATURES_FUTURE.md` with High/Medium/Low tables and the columns `ID`, `Suggestion`, `Why this matters`, `Status`, `Owner`, `Target Version`, `Implemented On`, and `Notes`; update item status instead of deleting history.
- **Reason:** Keeps roadmap prioritization durable and prevents duplicate or drifting feature proposals across sessions.
- **Topic:** GA4 normalized tracking
- **Rule:** Keep analytics helpers centralized in `web/frontend/src/lib/analytics.ts`, track link clicks via one delegated `document` listener (`portfolio_link_click`), and use explicit `portfolio_ui_interaction` events for key non-link controls with `section` and IDs/counts.
- **Reason:** Ensures consistent GA4 reporting dimensions across pages while minimizing instrumentation churn in UI components.
