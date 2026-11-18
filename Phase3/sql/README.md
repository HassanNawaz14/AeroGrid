# Phase 3 SQL layers

Read-only analytical and OLAP queries for WP-P3-02 and WP-P3-03. Both layers read
only `project_dw`; they create no objects and write no rows. All files are single
`SELECT`/`WITH` statements and are checked by `Phase3/scripts/run_readonly_analytics.py`.

## Layout

| Folder | Work package | Gate |
|---|---|---|
| `analytical/` | WP-P3-02 Analytical SQL layer | P3-G2 |
| `olap/` | WP-P3-03 OLAP queries (ROLLUP / CUBE) | P3-G2 |

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
