# Phase 3 Scope and Objectives

**Status:** documentation baseline; awaiting P3-G1 human authorization (`D3-001`).

## Objective

Turn the Phase 2 warehouse into a decision-support system: analytical SQL, OLAP
queries, an optimized reporting layer, and a Power BI dashboard — using only the
trusted data Phase 2 already produces. Phase 3 is a **consumer** of the warehouse,
not a rewrite of it.

## Source requirements (course brief → AeroGrid mapping)

The Phase 3 brief (`Phase3/DWBI Lab Phase 3.pdf`) is written for a retail sample
dataset. AeroGrid has no revenue, orders, or customers; the intent of every
requirement is preserved through this mapping (`D3-003`):

| Brief term | AeroGrid meaning |
|---|---|
| Revenue | Observed traffic volume (tracking positions, occupancy minutes) |
| Orders | Flight journeys |
| Customers | Distinct vehicles / operators |
| Products | Sources and vehicle categories |
| Region | Study site |
| Channel | Source system (TARTAN, NIGHTJAR, DJI) |
| Monthly revenue + growth | Monthly observed traffic + month-over-month growth |
| "Sales trend" | Traffic trend over time |

A KPI that would imply money, fleet size, or certified capacity is out of scope;
see the KPI dictionary in [04_data_model.md](04_data_model.md).

## In scope

1. **Analytical SQL layer** — aggregation queries (SUM/AVG/COUNT) including a
   monthly trend with month-over-month growth (WP-P3-02).
2. **OLAP queries** — ROLLUP over a documented hierarchy (site → source category →
   vehicle type) and CUBE over site × source system (WP-P3-03).
3. **Reporting views** — the three gold-layer views the brief requires, renamed to
   meaningful AeroGrid names (`D3-004`): `vw_monthly_traffic_growth`,
   `vw_vehicle_analysis`, `vw_source_performance` (WP-P3-04).
4. **Query optimization** — EXPLAIN ANALYZE before/after, deliberate indexes, and
   an indexing report PDF with execution-time and cost comparison (WP-P3-05).
5. **Power BI dashboard** — three pages: executive overview (KPIs + trend),
   detailed analysis (source / site / vehicle segmentation), and a decision page
   (WP-P3-06).
6. **Business insights report** — the decision narrative with evidence citations
   (WP-P3-07).
7. **Final presentation** (WP-P3-08), release packaging (WP-P3-09), and acceptance
   (WP-P3-10).

## Out of scope

- New data sources, new facts, new grains, or changes to Phase 2 tables.
- Power BI Service workspaces (human-only; `D3-005`).
- Real-time streaming, alerting, or production SLAs.
- Closing Phase 2 limitations `L-001`–`L-010` (owned by the optional hardening
  track WP-P3-H1 … H4, only through recorded decisions).

## Deliverables and marks

| Deliverable | Marks | WP |
|---|---|---|
| Analytical SQL queries (`.sql`) | 10 | WP-P3-02 |
| OLAP queries (`.sql`) | 5 | WP-P3-03 |
| Reporting views (`.sql`) | — | WP-P3-04 |
| Indexing report (`.pdf`) | — | WP-P3-05 |
| Power BI dashboard (`.pbix`) | 10 | WP-P3-06 |
| Dashboard screenshots (`.pdf`) | — | WP-P3-06 |
| Business insights report (`.pdf`) | 5 | WP-P3-07 |
| Final presentation (`.pptx`) | — | WP-P3-08 |

## Success criteria

- Every number in every artifact is reproducible from stored warehouse data via a
  recorded query.
- Zero-value KPIs carry the Phase 2 coverage semantics (empty = missing coverage,
  never "no events"; `D3-009`).
- Optimization claims are backed by before/after `EXPLAIN ANALYZE` evidence.
- The five-member read model is unchanged; BI connects with the reader role only.
