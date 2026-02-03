# Project Memory

## Architectural Decisions
- The `/api/months` endpoint returns year-scoped months when `year` is provided, and returns cross-year `YYYY-MM` values (sorted descending) when no year is provided to support the QuarterReport picker.

## Gotchas
- QuarterReport must parse `YYYY-MM` values into `year` and `month` params when calling backend endpoints; passing only `month` will ignore selection and default to latest input.
