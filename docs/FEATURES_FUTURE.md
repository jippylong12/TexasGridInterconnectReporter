# Features Future

Prioritized backlog for the Texas Grid Interconnect Reporter, focused on improving ERCOT report coverage, reliability, and user-facing analytics.

Last reviewed: 2026-02-15

## Progress snapshot

| Priority | Backlog | Planned | In Progress | Blocked | Shipped | Dropped | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| High | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| Medium | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| Low | 5 | 0 | 0 | 0 | 0 | 0 | 5 |
| **All** | **17** | **0** | **0** | **0** | **0** | **0** | **17** |

## High

| ID | Suggestion | Why this matters | Status | Owner | Target Version | Implemented On | Notes |
|---|---|---|---|---|---|---|---|
| H-01 | Ingest all required ERCOT sheets into a normalized data model (`Large Gen`, `Small Gen`, `Commissioning`, `Inactive`, `Cancellation`, `Summary`). | Expands the product from single-sheet analytics to complete interconnection visibility and prevents blind spots in user decisions. | Backlog | Unassigned | v0.4 | - | Success metric: >= 95% of required sheet fields mapped with schema docs. |
| H-02 | Add schema validation and data-quality gates (missing columns, bad date formats, invalid MW values) with a human-readable validation report. | Reduces silent data corruption and improves trust before report generation and API responses. | Backlog | Unassigned | v0.4 | - | Include validation summary JSON + CSV in `outputs/`. |
| H-03 | Build monthly historical dataset snapshots and trend APIs (capacity growth, project count, status movement by month/quarter). | Enables longitudinal analysis instead of one-month-only views, which is core for grid planning decisions. | Backlog | Unassigned | v0.5 | - | Reuse existing `inputs/<year>/<month>/file.xlsx` structure. |
| H-04 | Add idempotent pipeline runs with run metadata (`input hash`, `run_id`, `generated_at`, source month). | Makes outputs reproducible, debuggable, and safer for automation/deployment. | Backlog | Unassigned | v0.4 | - | Emit manifest file per run in `outputs/`. |
| H-05 | Introduce background report jobs with status endpoints (`queued`, `running`, `failed`, `done`) for heavier generation tasks. | Prevents UI/API timeouts and improves reliability under larger datasets. | Backlog | Unassigned | v0.5 | - | Start with in-process queue, then evaluate external worker later. |
| H-06 | Expand automated tests with multi-month fixtures and API contract checks for `/api/quarters`, `/api/quarter-data`, `/api/comparison-data`. | Protects against regressions when parser logic or sheet layouts evolve month to month. | Backlog | Unassigned | v0.4 | - | Add fixture coverage for at least 3 distinct report months. |

## Medium

| ID | Suggestion | Why this matters | Status | Owner | Target Version | Implemented On | Notes |
|---|---|---|---|---|---|---|---|
| M-01 | Add downloadable tabular exports (CSV/XLSX) for quarter and comparison screens. | Users can reuse analyzed data in downstream workflows without manual copy/paste. | Backlog | Unassigned | v0.5 | - | Include selected filters in filename and metadata. |
| M-02 | Add county and fuel trend deltas (MoM and QoQ) with "largest increases/decreases" highlights. | Surfaces key signal quickly without users manually comparing multiple screens. | Backlog | Unassigned | v0.5 | - | Reuses historical snapshot layer from H-03. |
| M-03 | Add filter facets in UI: study phase, technology type, and project status. | Improves decision speed for targeted analysis (for example, only battery or only late-stage projects). | Backlog | Unassigned | v0.5 | - | Extend `quarter-data` and `county-details` query params. |
| M-04 | Improve comparison mode with explicit "removed projects" and COD shift quantification (days moved earlier/later). | Makes change analysis more complete and actionable than added/changed only. | Backlog | Unassigned | v0.5 | - | Add new tab and sortable delta columns. |
| M-05 | Add API pagination and server-side sorting for county details and project tables. | Keeps response times predictable as dataset size grows. | Backlog | Unassigned | v0.4 | - | Add `limit`, `offset`, `sort_by`, `sort_dir` query params. |
| M-06 | Publish a data dictionary endpoint and docs page for normalized fields and source mappings. | Reduces onboarding friction and ambiguity for analysts and external integrators. | Backlog | Unassigned | v0.4 | - | Generate from schema definitions to avoid drift. |

## Low

| ID | Suggestion | Why this matters | Status | Owner | Target Version | Implemented On | Notes |
|---|---|---|---|---|---|---|---|
| L-01 | Save and reload user filter presets in the web UI. | Improves repeat workflows for frequent users with similar reporting slices. | Backlog | Unassigned | v0.6 | - | Store presets in browser local storage initially. |
| L-02 | Add map legends with dynamic MW bins and a county search jump-to control. | Helps discoverability in dense maps and improves usability for non-expert users. | Backlog | Unassigned | v0.6 | - | Keep default interaction simple. |
| L-03 | Add downloadable "change brief" markdown report from comparison results. | Creates a lightweight artifact for stakeholder updates and decision logs. | Backlog | Unassigned | v0.6 | - | Include period pair, counts, top changes, and links to exports. |
| L-04 | Add deployment smoke test script that validates key API routes post-startup/deploy. | Catches broken deployments quickly before users encounter failures. | Backlog | Unassigned | v0.4 | - | Validate `/api/years`, `/api/months`, and one data endpoint. |
| L-05 | Add a "sample input validator" command for quick local checks before full run. | Speeds developer feedback loop and reduces failed full pipeline runs. | Backlog | Unassigned | v0.5 | - | CLI output should list pass/fail checks per required sheet. |

## Top 3 next items (execution order)

1. `H-01` Ingest all required sheets into a normalized model.
2. `H-02` Add schema validation and quality gates.
3. `H-06` Expand automated tests with multi-month fixtures and API contract checks.

## Dependencies and sequencing risks

- `H-03`, `M-02`, and parts of `M-04` depend on `H-01` normalized multi-sheet ingestion.
- `M-06` should be generated from schema artifacts introduced by `H-01/H-02` to avoid stale docs.
- `H-05` should follow `H-02` validation so bad inputs fail fast before queueing long jobs.
