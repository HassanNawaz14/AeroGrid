# AeroGrid Phase 3 — OLAP Analytics, Performance Optimization & BI

Phase 3 turns the Phase 2 warehouse into a decision-support system on top of the
architecture defined in `docs/Sample Project Architecture Diagram.png`: the gold
reporting layer, query optimization, and the BI dashboard. It consumes only the
trusted, keyed data that Phase 2 already produces; it does not weaken the pipeline
that produces it.

## Current state

- Phase 1 is frozen; Phase 2 is merged, deployed, and accepted (see
  `Phase2/PROGRESS.md` and the Phase 2 final gate record).
- Phase 3 implementation is in progress: WP-P3-02 and WP-P3-03 are merged and
  P3-G2 is closed. P3-G3 is `DONE`: WP-P3-04 was applied and reader-proofed via
  `H3-005`; WP-P3-05 verify run 44397831286 passed `DQ3-A-006`, measured all three
  candidates `NEUTRAL`, applied no index (`D3-011`), and delivered the verify-mode
  `reports/Indexing_Report.pdf`. WP-P3-06 (Power BI dashboard) is `IN_PROGRESS`:
  its specification was approved on 2026-11-20 and the PBIX build is starting.
  WP-P3-09 (CI packaging + artifacts, Member A) is `READY_FOR_REVIEW`: the artifact
  layout, the `D3-008` packaging script and workflow, and the release-notes template
  are in place and the dry-run is recorded; the green run on `main` (`H3-008`) and the
  D/E review are open. P3-G5 is `IN_PROGRESS`.
  P3-G0 is the documentation baseline; P3-G1 was authorized under H3-001.
- The canonical entry point is [docs/00_documentation_map.md](docs/00_documentation_map.md).

## What Phase 3 delivers (course brief)

| Brief requirement | Phase 3 mapping |
|---|---|
| Analytical SQL (SUM/AVG/COUNT, monthly trend with growth) | WP-P3-02 |
| OLAP queries (ROLLUP, CUBE) | WP-P3-03 |
| Reporting views (`vw_monthly_sales`, `vw_customer_analysis`, `vw_product_performance`) | WP-P3-04, renamed to AeroGrid-meaningful views (mapping table in [docs/01](docs/01_phase3_scope_and_objectives.md)) |
| Query optimization: EXPLAIN ANALYZE before/after, indexes | WP-P3-05 |
| Power BI dashboard (3 pages: executive, detailed, decision) | WP-P3-06 |
| Business insights report + decision narrative | WP-P3-07 |
| Final presentation | WP-P3-08 |
| Release packaging | WP-P3-09, WP-P3-10 |

Marks: analytical SQL 10, OLAP 5, dashboard 10, business insights 5 (total 30%).

## Hard rules carried from Phase 2

- Real public data only; no synthetic rows, ever.
- The warehouse schema and pipeline from Phase 2 are reused, not rebuilt.
- All BI deliverables (dashboard, screenshots, insights report, presentation) are
  owned by **one member** — see [docs/08_team_work_division.md](docs/08_team_work_division.md).
- Free tools and free tiers only; no local databases, no Docker, no secrets in Git.
- Documentation is updated in the same work package that changes a decision or interface.

## Start paths

- Human reviewer: [docs/01](docs/01_phase3_scope_and_objectives.md) →
  [docs/02](docs/02_architecture_and_platform.md) →
  [PROGRESS.md](PROGRESS.md).
- Coding agent: read [../AGENTS.md](../AGENTS.md), then
  [AGENTS.md](AGENTS.md), then [PROGRESS.md](PROGRESS.md), then this map's
  canonical table, then the assigned work package.
