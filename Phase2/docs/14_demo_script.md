# Demo script — Phase 2 warehouse (10–12 minutes)

**Audience:** course evaluator and team members.
**Purpose:** show a real, reproducible warehouse — not a slide deck.
**Rule:** every number shown comes from the shared Neon warehouse and is reproducible with
the query beside it. Do not paste the connection string on screen; keep it in a shell
variable and blur it if a terminal is projected.

## Before you start (5 minutes earlier)

1. Set the read-only connection string privately in your own shell:
   `export READONLY_DATABASE_URL='...'` — never in a file, never in chat.
2. Install the two client libraries once: `pip install "psycopg[binary]" boto3`.
3. Run the access probe:
   `python .github/scripts/platform_probe.py --mode reader`
   Expect a table with every row `PASS` and `Overall: **PASS**`. If it fails, stop the
   demo and report the SQLSTATE.
4. Open these tabs:
   - [PROGRESS.md](../PROGRESS.md) — status board.
   - [WP-12 release evidence](WP12_RELEASE_EVIDENCE_2026-11-14.md) — evidence record.
   - GitHub Actions run [43502710978](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43502710978) — the real apply run.
5. Warm the views once so the demo is not waiting on cold Neon compute:
   `SELECT count(*) FROM project_reporting.vw_traffic_density_hour_grid;`
6. Keep every query filtered and `LIMIT`ed. Do not run full-table scans during a shared
   demo.

## 1. What this is (1 minute)

> "Phase 2 turns the Phase 1 model into a PostgreSQL warehouse fed only by real public
> data: Tartan ADS-B for KBTP, three UAS flight datasets, FAA weather, and FAA airspace.
> One protected GitHub Actions job writes; everyone else reads."

Show `PROGRESS.md` rows for WP-07–WP-12. State the pinned facts: **27,479** tracking facts,
**178** journeys, **3,658** grid cells, **1,754** occupancy facts, **10** views, **36** DQ
checks with **0** failures.

## 2. The three schemas (1 minute)

```sql
SELECT table_schema, count(*) AS tables
FROM information_schema.tables
WHERE table_schema IN ('project_staging','project_dw','project_reporting')
GROUP BY 1 ORDER BY 1;
```

Point at the split: staging (accepted rows, rejects, manifests, run log), warehouse
(dimensions with `-1` unknown members, five fact grains), reporting (ten views you are
allowed to use first).

## 3. One real source row through the pipeline (2 minutes)

```sql
SELECT source_name, sha256, captured_at
FROM project_staging.source_manifest
ORDER BY captured_at DESC LIMIT 5;

SELECT etl_run_id, run_mode, rows_read, rows_accepted, rows_rejected, status
FROM project_staging.etl_run_log
ORDER BY etl_run_id DESC LIMIT 3;
```

Narration:

- Every run records what was fetched, its SHA-256, and how many rows were read, accepted,
  rejected, and duplicated. Run 11 read 23,414, accepted 23,254, rejected 160.
- Rejects are stored with a reason: 159 zero coordinates in one DJI dataset and one
  epoch-zero timestamp in Nightjar. Nothing is silently dropped.
- The apply is a single transaction: a critical DQ failure rolls the whole run back.

Show the job summary in Actions and the two PDFs. Point out the stored-reject footnote:
reject totals span runs, so they are not added to a single run's accepted count.

## 4. Dimensions and surrogate keys (1 minute)

```sql
SELECT 'dim_site' AS dim, count(*) FROM project_dw.dim_site
UNION ALL SELECT 'dim_weather', count(*) FROM project_dw.dim_weather
UNION ALL SELECT 'dim_airspace_zone', count(*) FROM project_dw.dim_airspace_zone
UNION ALL SELECT 'dim_spatial_grid', count(*) FROM project_dw.dim_spatial_grid;
```

Explain the `-1` unknown member: when a real fact has no real dimension match, the fact
points at `-1` and the gap stays visible instead of being invented. Example: January 2022
flights have no matching weather observation, so their weather key is the unknown member.

```sql
SELECT w.weather_key, w.station_icao, w.observation_ts
FROM project_dw.dim_weather w
WHERE w.weather_key = -1;
```

## 5. Facts by business key → surrogate key (2 minutes)

```sql
SELECT count(*) AS tracking_facts,
       count(DISTINCT vehicle_key) AS vehicles,
       count(DISTINCT grid_key) AS grids_used,
       count(DISTINCT etl_run_id) AS contributing_runs
FROM project_dw.fact_vehicle_tracking;
```

Expected: 27,479 / 2 / a few thousand / 0.

```sql
SELECT count(*) AS orphan_time FROM project_dw.fact_vehicle_tracking f
LEFT JOIN project_dw.dim_time d ON d.time_key = f.time_key
WHERE d.time_key IS NULL;
```

Expected 0. Say the DQ checks `DQ-I-001`–`DQ-I-010` assert this for every fact table.

## 6. Reporting views (2 minutes)

```sql
SELECT count(*) FROM project_reporting.vw_traffic_density_hour_grid;   -- 6,658
SELECT count(*) FROM project_reporting.vw_occupied_grid_hours;         -- 1,754
SELECT * FROM project_reporting.vw_monthly_traffic ORDER BY 1;
SELECT * FROM project_reporting.vw_peak_site_hours ORDER BY 1 LIMIT 10;
```

Then show the screening views:

```sql
SELECT count(*) FROM project_reporting.vw_candidate_corridor_cells;    -- 808
SELECT count(*) FROM project_reporting.vw_daily_encounter_hotspots;    -- 0
SELECT count(*) FROM project_reporting.vw_restriction_traffic_impact;  -- 0
```

Say plainly why two views are empty: encounters need identical timestamps under the
approved `wp07-v1` method, and no historical 2022 TFR snapshot exists. Empty means "not
observed under this method", never "no conflicts happened".

## 7. Data quality evidence (1 minute)

Open [Data_Quality_Report.pdf](../reports/Data_Quality_Report.pdf) and
[Data_Cleaning_Report.pdf](../reports/Data_Cleaning_Report.pdf).

> "36 checks: completeness, accuracy, integrity, uniqueness, reconciliation, and a
> coverage guard per approved source. 32 PASS, 4 WARN, 0 FAIL. The warnings are stored as
> warnings — we did not convert missing data into a pass."

Name the four warnings: `DQ-C-003` unknown optional weather, `DQ-C-008` unknown ground
state, `DQ-A-008` invalid stored wind direction, `DQ-T-003` no restriction snapshots.

## 8. Automation and access (1 minute)

- `wp11-ingest.yml`: `validate` is read-only; `apply` needs `main`, the `warehouse`
  environment, a typed confirmation, and `WAREHOUSE_CI_APPROVED`. Weekly Monday 06:00 UTC
  schedule, manual dispatch, and a reader-check job.
- Show the green apply run and its reader job (`PASS`; writes denied with `42501`).
- Say that every member's own credentials are verified by the probe in the pre-flight,
  not assumed from the shared role (`H-017`).

## 9. Limitations and close (1 minute)

Read four lines from the [limitation register](13_accepted_data_limitations.md):

- One week of Tartan, not a year — free-tier size limit (`L-003` scale, `D-006`).
- January 2022 flights, November 2026 airspace — never join them (`L-005`).
- UAS and airspace are staged but have no fact loaders yet (`L-008`, `L-009`).
- Raw files are hashed but not archived yet (`L-010`).

Close: "The warehouse is reproducible from a pinned commit, the numbers are stored checks
rather than slide claims, and every gap has an ID, an owner, and a trigger."

## If something fails during the demo

| Symptom | Say | Do |
|---|---|---|
| Probe fails with `42501` on SELECT | "The reader grant is missing for this credential." | Stop; report the SQLSTATE; do not retry writes |
| Query times out | "Neon compute is cold." | Re-run once; reduce rows with a `WHERE` filter |
| A view is empty | "That is a documented limitation, not a defect." | Quote the `L-###` ID |
| Apply run is red | "The transaction rolled back; no partial data exists." | Show the run summary artifact |

## Prohibited during the demo

- No writes, no DDL, no `DROP`, no index creation.
- No connection string, token, or `.env` content on screen.
- No claim that empty encounter/restriction facts mean zero real-world events.
- No synthetic data to make a chart look better.
