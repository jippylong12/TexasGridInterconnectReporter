# Active Plan

## User Request
Add GA4 tracking with Measurement ID `G-B24WEF5K6V`, including normalized delegated link tracking, reusable analytics helpers, key UI interaction events, and SPA page view tracking with minimal edits and no behavior changes.

## Constraints (from .agent/project_context.md + AGENTS.md)
- Keep changes modular and focused (no monolithic script changes).
- Do not introduce new dependencies.
- Preserve existing behavior, routing, styling, and link destinations.
- Prefer minimal, targeted edits and reusable utilities.

## Steps
1. Confirm frontend entry points and current analytics state.
   - Constraint link: avoid unnecessary files/edits; preserve existing behavior.
2. Add GA4 bootstrap snippet to global HTML head if missing.
   - Constraint link: no UI or routing impact.
3. Create reusable analytics helpers:
   - `trackEvent(name, params)`,
   - `sanitizeDestinationUrl(url)`,
   - `isInternalDomain(host)`,
   plus one delegated `document` click listener for all `a[href]`.
   - Constraint link: modular utility, safe fallback when `gtag` is unavailable.
4. Wire SPA page view tracking on route changes and initialize delegated link tracking once.
   - Constraint link: keep compatibility with existing events and app behavior.
5. Add optional `data-ga-*` metadata and key `portfolio_ui_interaction` events on major non-link controls.
   - Constraint link: normalized reporting without changing UX behavior.
6. Run frontend lint/build validation for touched files.
   - Constraint link: ensure no regressions from instrumentation.
7. Run Sentinel audit; then update Chronicler/Historian memory entries for durable analytics patterns.
   - Constraint link: comply with project mandatory skill workflow.
