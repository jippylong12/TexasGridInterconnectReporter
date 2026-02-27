# Project Memory

## Architectural Decisions
- The `/api/months` endpoint returns year-scoped months when `year` is provided, and returns cross-year `YYYY-MM` values (sorted descending) when no year is provided to support the QuarterReport picker.
- Future roadmap planning is tracked in `docs/FEATURES_FUTURE.md` using High/Medium/Low priority groups with status fields so feature history stays durable.
- Frontend analytics uses a centralized `src/lib/analytics.ts` utility with safe `gtag` guards, a single delegated `document` listener for all `a[href]` clicks, and route-change `page_view` tracking from `App.tsx`.

## Gotchas
- QuarterReport must parse `YYYY-MM` values into `year` and `month` params when calling backend endpoints; passing only `month` will ignore selection and default to latest input.
