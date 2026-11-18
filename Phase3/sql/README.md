# Phase 3 SQL layers

Read-only analytical and OLAP queries for WP-P3-02 and WP-P3-03, the
WP-P3-04 gold-view DDL, and the WP-P3-05 optimization assets. The analytical and
OLAP layers read only `project_dw`; they create no objects and write no rows. The
`views/` layer creates three `project_reporting` views and writes no base-table
rows. The `optimization/` layer exercises the access paths of the
dashboard-critical view queries for `EXPLAIN ANALYZE` measurement; `indexes/` holds
idempotent candidate index DDL that
is only persisted by the protected WP-P3-05 apply workflow. All analytical/OLAP and
optimization files are single `SELECT`/`WITH` statements checked by
`Phase3/scripts/run_readonly_analytics.py`; the view files are checked by
`Phase3/scripts/verify_gold_views.py` and the index files by
`Phase3/scripts/measure_indexes.py`.

## Layout

| Folder | Work package | Gate |
|---|---|---|
| `analytical/` | WP-P3-02 Analytical SQL layer | P3-G2 |
| `olap/` | WP-P3-03 OLAP queries (ROLLUP / CUBE) | P3-G2 |
| `views/` | WP-P3-04 Phase 3 reporting views | P3-G3 |
| `optimization/` | WP-P3-05 dashboard-critical queries for EXPLAIN ANALYZE | P3-G3 |
| `indexes/` | WP-P3-05 idempotent candidate index DDL | P3-G3 |

## Query catalogue

| Query ID | File | Business question | KPI / check |
|---|---|---|---|
| QW-P3-02-01 | `analytical/01_monthly_traffic_growth.sql` | Monthly observed traffic and month-over-month growth by site | KPI dictionary; DQ3-A-001/002/003 |
| QW-P3-02-02 | `analytical/02_kpi_snapshot.sql` | Headline KPI snapshot with coverage labels | KPI dictionary; DQ3-A-002/003 |
| QW-P3-02-03 | `analytical/03_site_traffic_summary.sql` | Site-level traffic, journeys, and observed occupancy | KPI dictionary; DQ3-A-001/002/003 |
| QW-P3-02-04 | `analytical/04_vehicle_activity_summary.sql` | Per-vehicle observed activity and site span | KPI dictionary; L3-003; DQ3-A-001/002/003 |
| QW-P3-02-05 | `analytical/05_source_performance.sql` | Source-system volume, sites, and journey trend | KPI dictionary; L-008; DQ3-A-001/002/003 |
| QW-P3-02-06 | `analytical/06_time_of_day_pattern.sql` | Observed traffic by site and UTC hour | KPI dictionary; DQ3-A-001/002/003 |
| QW-P3-02-07 | `analytical/07_coverage_diagnostics.sql` | Coverage, unknown members, observed months | DQ3-A-002/003; L3-002 |
| QW-P3-03-01 | `olap/01_rollup_site_source_category_vehicle_type.sql` | ROLLUP: site → source category → vehicle type | DQ3-A-004 |
| QW-P3-03-02 | `olap/02_cube_site_source_system.sql` | CUBE: site × source system | DQ3-A-004 |
| QW-P3-03-03 | `olap/03_grand_total_reconciliation.sql` | Prove ROLLUP/CUBE grand totals equal the plain aggregation | DQ3-A-004 |
| OQ-P3-05-01 | `optimization/01_source_monthly_volume.sql` | Source-system monthly volume (vw_source_performance path) | DQ3-A-006 |
| OQ-P3-05-02 | `optimization/02_monthly_growth_by_site.sql` | Site monthly growth (vw_monthly_traffic_growth path) | DQ3-A-006 |
| OQ-P3-05-03 | `optimization/03_vehicle_activity.sql` | Vehicle activity and journey totals (vw_vehicle_analysis path) | DQ3-A-006 |

## Gold reporting views

`views/01_gold_views.sql` creates `vw_monthly_traffic_growth`,
`vw_vehicle_analysis`, and `vw_source_performance` in `project_reporting`. Their
grains, coverage labels, apply gate, and evidence rules are documented in
[views/README.md](views/README.md).

## Index optimization assets (WP-P3-05)

`indexes/01_indexes.sql` holds three commented candidate blocks. Each block names
its index, its target `OQ-P3-05-xx` query, and its rationale. The DDL is
`CREATE INDEX IF NOT EXISTS` on `project_dw` only; no base-table rows are touched.
`optimization/*.sql` are read-only mirrors of the gold-view access paths.

```powershell
# Static checks only (no database)
python -m pytest -q Phase3/tests
# Verify = measure with rollback; apply is main-only protected CI
python Phase3/scripts/measure_indexes.py
python Phase3/scripts/generate_index_report.py --evidence <json>
```

Verify mode creates each candidate inside a transaction, measures before/after with
`EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`, records the index size, and rolls back.
Only the protected `.github/workflows/wp-p3-05-indexes.yml` apply mode persists the
DDL, and it aborts if the database would exceed the 700 MB guard. The PDF is built
only from a recorded JSON evidence file; a missing before/after pair fails
`DQ3-A-006` and no report is produced.

## Coverage rules

- No query generates a month spine or an activity fact. A missing month, source, or
  site-hour means missing coverage, never "zero activity" (`D3-009`).
- Zero-valued KPI rows carry a `*_coverage` or `coverage_status` label.
- `UNSPECIFIED` vehicle type is used only because the real Tartan source does not
  define `vehicle_type`; it is not an invented category.
- `MANNED_ADSB` / `UAS` source categories are the documented mapping from Phase 3
  docs `01` and `04`, not a source-provided attribute.

## Run the evidence

The runner needs a reader connection supplied through the environment. It never prints
the connection string and always opens a `READ ONLY` transaction.

```powershell
$env:READONLY_DATABASE_URL = '<reader connection supplied privately>'
python Phase3/scripts/run_readonly_analytics.py --layer all --require-reader
```

```powershell
# List queries without connecting
python Phase3/scripts/run_readonly_analytics.py --list
# Local static checks (no database)
python -m pytest -q Phase3/tests
```

The evidence Markdown is written to `Phase3/evidence/analytics_run_<UTC>.md`. A zero-row
result is reported as missing coverage, and a `DQ3-A-004` result other than `PASS`
fails the runner.

## Non-negotiable

- Do not add `INSERT`, `UPDATE`, `DELETE`, DDL, or `GRANT` to these files.
- Do not hard-code KPI values, capture dates, or query outputs.
- Do not use retail names (`vw_monthly_sales`, `revenue`, etc.) as real objects; the
  mapping is in `Phase3/docs/01` (`D3-004`).
