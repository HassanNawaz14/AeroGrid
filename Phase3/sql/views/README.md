# Phase 3 gold views (WP-P3-04 / P3-G3)

`Phase3/sql/views/01_gold_views.sql` creates the three read-only reporting views
for the Power BI layer. It is the only Phase 3 DDL in this folder. The SQL is
idempotent and does not write, drop, or replace any Phase 2 base table.

## Views

| View | Grain | Business question | Query linkage |
| --- | --- | --- | --- |
| `project_reporting.vw_monthly_traffic_growth` | One row per real site per UTC calendar month with tracking observations | How does observed traffic change month over month at each site? | `Phase3/sql/analytical/01_monthly_traffic_growth.sql` (`QW-P3-02-01`) |
| `project_reporting.vw_vehicle_analysis` | One row per real `dim_vehicle` member (`vehicle_key > 0`) | How active is each observed vehicle, where, and at which UTC hour is its activity highest? | `Phase3/sql/analytical/04_vehicle_activity_summary.sql` (`QW-P3-02-04`) and the hour aggregation in `QW-P3-02-06` |
| `project_reporting.vw_source_performance` | One row per source system present in `dim_vehicle` | How much observed traffic and journey activity comes from each source, and what is its observed coverage? | `Phase3/sql/analytical/05_source_performance.sql` (`QW-P3-02-05`) |

All views list columns explicitly. No `SELECT *` is used.

## Coverage and grain rules

- Rows are observed facts only. There is no month spine, interpolation, or
  extrapolation.
- Absent rows mean missing coverage, never zero activity (`D3-009`).
- `vw_vehicle_analysis` and `vw_source_performance` keep zero-fact members and
  label them with `NO_TRACKING_COVERAGE` / `NO_JOURNEY_COVERAGE` text. The labels
  are not numeric zeros and must not be presented as zero activity.
- `vw_monthly_traffic_growth` includes only site-months with tracking facts, so a
  missing site-month is a coverage gap. Month-over-month growth is `NULL` when
  there is no prior observed month, when the prior observed month is not adjacent,
  or when the prior month has zero positions. The status column records why.
- `vw_vehicle_analysis` is source-scoped identity, not an operator identity
  (`L3-003`). Its time-of-day fields are a summary of observed hours, not a
  complete 24-hour profile.
- `vw_source_performance` uses the documented mapping: `TARTAN` = `MANNED_ADSB`;
  `NIGHTJAR`, `NOMINAL_DJI`, and `DJI` = `UAS`; anything else = `OTHER`.
  UAS sources staged in `dim_vehicle` without loaded facts appear with zero facts
  and coverage labels, not as proof of zero UAS activity (`L-008`).
- `vw_source_performance` reports the observed month count, first/last observed
  month and their position counts, and the peak observed month. It does not invent
  a new source growth percentage KPI.

## Apply and verification

No local database is used. The approved path is the protected
`.github/workflows/wp-p3-gold-views.yml` job:

1. `verify`: opens a writer transaction, runs the DDL, reconciles rows and
   measures, checks the `aerogrid_reader` grant, and **rolls back**. No view is
   persisted.
2. `apply`: runs the same checks, commits, then opens a separate
   `aerogrid_reader` connection in `READ ONLY` mode and selects every view.

The apply run requires the `warehouse` environment, the writer secret
`DATABASE_URL`, the reader secret `READONLY_DATABASE_URL`, a `main` ref, the
`WAREHOUSE_CI_APPROVED` environment variable, and the run-time confirmation
`APPROVE_WP3_GOLD_VIEWS`. The workflow may run `verify` on a work-package branch,
but it refuses `apply` there.

Local dry runs are allowed only with a temporary writer URL supplied through the
environment; the default is rollback-only:

```powershell
python Phase3/scripts/verify_gold_views.py
```

Never place a connection string in a file, command history, or chat. The script
redacts DSN-like text from its output and evidence.

## Evidence and checks

- Evidence: `Phase3/evidence/gold_views_<UTC>.md`, written by
  `Phase3/scripts/verify_gold_views.py`.
- `DQ3-A-001`: each view row count equals the documented fact/dimension grain;
  the sum of `tracking_positions` and `journeys_observed` equals the fact totals;
  the key count equals the row count.
- `DQ3-A-003`: zero-fact members carry coverage labels.
- Static tests: `python -m pytest -q Phase3/tests` checks the view count, names,
  grain comments, coverage labels, `LAG` rules, and the no-write/no-`SELECT *`
  guards.
- `pglast` parsing is run when the package is available in the environment.

## Reversibility

The views are read-only projections. The workflow does not drop or alter them.
If a future correction is needed, change the SQL in Git and rerun `verify`, then
`apply`; never run ad-hoc destructive SQL against the shared warehouse.
