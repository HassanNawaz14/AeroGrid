# Phase 3 Data Model

**Status:** target model. The Phase 2 star schema is unchanged (`D3-001`); Phase 3
adds a gold layer of views and a KPI dictionary on top of it. The Phase 2 canonical
model remains `Phase2/docs/04_data_model.md`.

## What carries forward

- Six dimensions with `-1` unknown members; five facts with provenance and
  `algorithm_version`; ten Phase 2 reporting views.
- All Phase 2 grains and keys. Phase 3 introduces **no new base tables**.

## Gold layer additions (WP-P3-04)

| Brief requirement (`D3-004`) | Phase 3 view | Grain |
|---|---|---|
| `vw_monthly_sales` | `project_reporting.vw_monthly_traffic_growth` | One row per site per UTC month, with month-over-month growth % |
| `vw_customer_analysis` | `project_reporting.vw_vehicle_analysis` | One row per vehicle (observed activity, site span, time-of-day pattern) |
| `vw_product_performance` | `project_reporting.vw_source_performance` | One row per source system (volume, sites covered, trend) |

Rules for every gold view:

- `CREATE OR REPLACE VIEW`, idempotent, reads only `project_dw` and Phase 2 views.
- Explicit column lists; documented grain and the business question answered.
- No synthetic rows, no extrapolation; zeros and nulls keep Phase 2 coverage
  semantics (`D3-009`).
- Each view cites the query and check IDs that reproduce its numbers.

## OLAP design (WP-P3-03)

- **ROLLUP hierarchy:** site → source category (manned ADS-B / UAS) → vehicle type,
  producing subtotals per level and a grand total.
- **CUBE:** site × source system, producing all marginal combinations.
- Both are implemented as SQL queries against `fact_vehicle_tracking` (and derived
  facts where relevant), stored under `Phase3/sql/` with run evidence.

## KPI dictionary (basis for the dashboard)

| KPI | Definition | Source | Zero semantics |
|---|---|---|---|
| Observed traffic positions | COUNT of tracking rows in scope | `fact_vehicle_tracking` | 0 = missing coverage, label required |
| Distinct vehicles observed | COUNT(DISTINCT vehicle_key) | `fact_vehicle_tracking` | same |
| Journeys observed | COUNT of journey rows | `fact_flight_journey` | same |
| Occupied cell-hours | SUM/occupancy rows | `fact_airspace_occupancy` | same |
| Detected encounters | COUNT of encounter rows | `fact_close_encounter` | 0 = no detected episodes **and** insufficient overlapping evidence; label both |
| Month-over-month growth | (this month − last month) / last month | `vw_monthly_traffic_growth` | null when last month is 0; never show ±∞ |
| Avg altitude / speed | AVG over valid rows only | `fact_vehicle_tracking` | null when no valid rows |

Any KPI not in this table requires a decision in `Phase3/DECISIONS.md` before it
appears in an artifact.

## Measures, not facts

Aggregations in the gold layer are **measures derived from facts**, not new facts.
They are reproducible by re-running their recorded query and carry no lineage of
their own beyond the facts they read.
