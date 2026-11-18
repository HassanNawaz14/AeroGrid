# Phase 3 Architecture and Platform

**Status:** target architecture for Phase 3. It extends the accepted Phase 2
architecture and follows the gold-layer → BI blocks of the reference diagram
(`docs/Sample Project Architecture Diagram.png`).

## Design goals

- Consume, never weaken: Phase 3 adds no write paths to the warehouse and changes
  no Phase 2 grain, key, or source.
- Every analytics artifact is reproducible from stored data via a recorded query.
- The gold layer answers the course's OLAP and dashboard requirements while keeping
  the fail-closed pipeline properties of Phase 2 (idempotency, reconciliation,
  coverage semantics).
- One BI owner for all dashboard artifacts (see
  [08_team_work_division.md](08_team_work_division.md)).

## Platform (unchanged from Phase 2, `D3-006`)

| Component | Choice | Phase 3 role |
|---|---|---|
| Warehouse | Neon Free PostgreSQL, `aws-us-east-2`, database `neondb` | Same three schemas; analytics read from `project_dw` / `project_reporting` |
| Orchestration | GitHub Actions | Analytics verification workflows, artifact packaging |
| BI tool | Power BI Desktop (free), PostgreSQL connector | Dashboard over the reader connection (`D3-005`) |
| Reports | ReportLab (existing) + PDF tooling | Indexing report, screenshots PDF, insights report |
| Team access | `aerogrid_reader` read-only role | BI and all members query through it |

No local databases, no Docker, no paid connectors, no Power BI Service publishing
without a human-owned account.

## Target data flow

```text
project_dw (star schema, Phase 2, unchanged)
    -> project_reporting (Phase 2 views, unchanged)
    -> project_reporting Phase 3 gold views (analytics + OLAP)
    -> optional materialized marts (only with EXPLAIN evidence, D3-007)
    -> Power BI Desktop (reader role) -> dashboard pages
    -> insights report + final presentation (evidence-cited)
```

The Phase 2 pipeline (sources → staging → DW → DQ) continues unchanged underneath;
Phase 3 sits strictly above `project_reporting`.

## Layer responsibilities

| Layer | Responsibility | Canonical detail |
|---|---|---|
| Gold views | Analytical, OLAP, and dashboard-facing queries as idempotent `CREATE OR REPLACE VIEW`s | [04_data_model.md](04_data_model.md) |
| Optimization | Index decisions backed by before/after EXPLAIN ANALYZE; optional materialized marts | [05_etl_pipeline.md](05_etl_pipeline.md) |
| BI | Power BI semantic model + three pages; zero fabrication | [06_data_quality_and_reports.md](06_data_quality_and_reports.md) |
| Evidence | Indexing report, screenshots, insights report with query citations | [dev_plan/04](../dev_plan/04_acceptance_and_definition_of_done.md) |

## Mapping to the reference diagram (blocks 7–9 and 12)

| Diagram block | Phase 3 status | How |
|---|---|---|
| 7. Warehouse performance (indexes, views, EXPLAIN ANALYZE) | **Built in Phase 3** | WP-P3-05 with a before/after evidence report |
| 8. Gold layer / data marts | **Built in Phase 3** | Three gold views first; physical marts only if evidence demands it (`D3-007`) |
| 9. Analytics & BI (semantic model, KPIs, slicers, decision page) | **Built in Phase 3** | WP-P3-06 … WP-P3-08 |
| 12. Business glossary & data dictionary | **Extended** | KPI dictionary in [04](04_data_model.md); terms in [12](12_glossary.md) |
| 10–11. Auditing, monitoring, lineage | Carried unchanged | Phase 2 run log, DQ results, and provenance IDs continue to back every KPI |

## Failure behaviour (unchanged from Phase 2)

- Analytics workflows are read-only against the warehouse; a failure cannot corrupt
  data.
- A view that returns zero rows is treated as missing coverage and must be labeled
  as such in BI artifacts (`D3-009`).
- BI refresh failures never trigger warehouse writes; they fail the CI job only.
- Capacity guards stay in force: database warn at 700 MB, stop and ask; new indexes
  and materialized views must state their size impact in WP-P3-05.

## Non-goals

- Power BI Service deployment, scheduled cloud refresh, or embedded dashboards.
- Column-level data lineage tooling.
- Any change to the Phase 2 ETL, DQ, or access model outside the optional hardening
  track.
