# Phase 2 Architecture & Evaluation Guide

**Purpose:** one document for the Phase 2 evaluation. It explains how the pipeline
keeps data consistent, how it catches errors, how the delivered work maps to the
reference architecture diagram (`docs/Sample Project Architecture Diagram.png`), what
actually lives in the Neon warehouse, and how an evaluator can safely try to break
the pipeline. It does not explain code.

**Status snapshot (2026-11-17):** WP-07–WP-10 merged and deployed; WP-11 recurring
ingestion implemented and run; requester-admin accepted G5/G6/G7 on 2026-11-13. The
final gate record still separates administrative sign-off from independent proof;
see [FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

---

## 1. Pipeline strength: consistency and error handling (start here)

### 1.1 The one rule

**Fail closed, never guess, never ship partial data as trusted.**

Every stage follows the same pattern: validate, record what happened, and if
something is wrong either reject the bad row or stop the whole run. A silent wrong
number is treated as worse than a visible failure.

### 1.2 Defence layers

| Layer | What it protects against | How |
|---|---|---|
| 1. Input validation before any work | Bad dates, bad station codes, unknown sources, accidental `--apply` | Arguments are checked before fetching or connecting to the database |
| 2. Source fetching | Network errors, rate limits, wrong content | Retries up to 3 attempts with backoff; non-retryable errors fail immediately and name the source URL; non-JSON / empty / oversized responses fail |
| 3. Row-level cleaning | Bad timestamps, coordinates, units, missing keys | Normalizers raise a stable reject code; the row is moved to `stg_reject`, the batch continues |
| 4. Database safety net | One bad row aborting a whole batch; duplicate inserts on rerun | Per-row savepoints; batch fallback to row-by-row; unique natural keys + `ON CONFLICT DO NOTHING` |
| 5. Reconciliation identity | Counts silently not adding up | `rows_read = accepted + rejected + duplicate`, enforced in code **and** by a database `CHECK` constraint, **and** re-checked by a DQ rule |
| 6. Warehouse integrity checks | Orphans, duplicates, invalid ranges, broken pairs | 30+ DQ checks across completeness, uniqueness, accuracy, integrity, reconciliation, business rules |
| 7. Transaction gate | A critical failure leaving half-written data | Apply runs are one transaction; a CRITICAL DQ failure rolls everything back, then stores the failure evidence as its own run |
| 8. Access control | Accidental or malicious writes | Only CI can write (`aerogrid_etl`); every member is `aerogrid_reader` with `SELECT` only; apply jobs require the protected `warehouse` environment, `main`, and a typed confirmation |

### 1.3 Failure behaviour (what the evaluator will see)

| Situation | What the pipeline does | Evidence left behind |
|---|---|---|
| Unknown source name / bad station / reversed date window | Stops before any network or database activity with a plain message | Console / CI step log |
| `--apply` outside the approved CI job, or wrong confirmation string | Refuses to start | Guard message; no connection opened |
| Source returns HTTP 429 / 5xx / timeout | Retries 3 times with increasing pause, then fails naming the URL | Red workflow step; failure summary |
| Source returns a JSON error body (e.g. ArcGIS quota) | Same retry policy, then fails with the source's own message | Red workflow step |
| Source schema changed (missing / unexpected columns) | Row is rejected as `SCHEMA_DRIFT`; columns are never guessed | `stg_reject` row with file + row number |
| Invalid timestamp (`1970-01-01`, impossible date) | Rejected `INVALID_TIMESTAMP` | `stg_reject` |
| Latitude/longitude out of range | Rejected `INVALID_COORDINATE` | `stg_reject` |
| `(0,0)` placeholder coordinate | Rejected `ZERO_COORDINATE` | `stg_reject` |
| Altitude / speed / heading outside documented range | Rejected `ALTITUDE_OUT_OF_RANGE`, `SPEED_OUT_OF_RANGE`, `HEADING_OUT_OF_RANGE` | `stg_reject` |
| Duplicate row (same source record) | Counted as duplicate, not inserted twice | `rows_duplicate` in run log |
| Re-running the same load | No new facts; ids stay stable | Duplicate counters, unchanged row counts |
| Requested source yields **zero accepted rows** | The run **fails** with "missing coverage, not a measured zero" | Red workflow, coverage guard check `DQ-G-001` |
| One row has a database-level problem | Savepoint rolls back that row only; the batch continues | `stg_reject` (`SCHEMA_DRIFT`) |
| CRITICAL DQ check fails | Whole ingestion transaction rolled back; failure stored separately; workflow red | `etl_run_log` `FAILED` + `dq_result` rows |
| Fact row points at a missing dimension | DQ integrity check fails the run | `DQ-I-*` results with observed count |
| Someone with the reader role tries to write | PostgreSQL refuses with `42501 permission denied` | Server-side error |

### 1.4 Why reruns cannot duplicate data

- Every staging table has a unique key on the real source identity
  (`source_system + source_record_id`, station + observation time, zone ID, etc.).
- Every fact table has a unique key on its source identity or its grain.
- Loads use `ON CONFLICT DO NOTHING`, so a rerun of the same snapshot changes
  nothing and is counted as duplicates, not inserts.
- `source_manifest` is unique on `(source_name, sha256)`, so the same raw file is
  recorded once.
- Derived facts are rebuilt from the keyed facts with a recorded
  `algorithm_version`, so a re-derivation is reproducible and cannot create a
  second copy of the same episode.

---

## 2. Architecture in one paragraph

Public real sources are fetched by GitHub Actions, validated and cleaned in Python,
and written into `project_staging` together with a manifest, rejects, run log and DQ
results. Accepted rows are loaded into a star schema in `project_dw` (six
dimensions, five facts, every dimension with an unknown `-1` member). DQ checks run
after the load; a CRITICAL failure rolls the transaction back. Ten stable views in
`project_reporting` answer the business questions and are readable by all five
members through a read-only role. The warehouse and bucket are private; only CI can
write.

---

## 3. Mapping to the reference diagram

Status legend: **Followed** = implemented as shown (possibly with a different tool
name). **Partial** = the concept exists but is smaller than the diagram. **Later
phase** = deliberately not built yet, with a reason.

| # | Diagram block | Status | How we do it in Phase 2 | Reason if not fully followed |
|---|---|---|---|---|
| 1 | Multiple data sources | Followed | Tartan ADS-B, Nightjar / nominal-io DJI, NOAA AWC + IEM METAR, FAA airspace, OpenSky (optional, not loaded) | Source set fixed by scope and licences |
| 2 | Pipeline orchestration (extract → validate → transform → load → build marts → test & reconcile) | Followed | GitHub Actions workflow runs tests, then read-only validate or approved apply; steps map 1:1 to the diagram's boxes | GitHub Actions is the free-tier orchestrator; no scheduler server needed |
| 3 | Bronze layer: raw files + ingestion metadata (batch ID, source, timestamp, loaded-at) | Followed | Raw files are uploaded to `aerogrid-raw` under `raw/<sha256>/<file_name>` and linked from `source_manifest` with URL, licence, SHA-256, size, fetch time (`D3-018`); typed raw-shaped rows sit in `stg_*` tables | Historical pre-`D3-018` manifests have no stored bytes; live proof is `H3-011` |
| 4 | Data quality & validation: row counts, data type, duplicate, business rule, referential | Followed | Row-count reconciliation, type/parse rejects, duplicate detection, business rules (altitude, speed, heading, pairing), referential integrity checks | — |
| 4a | Reject / quarantine branch (invalid record + reason + source & batch + timestamp) | Followed | `stg_reject` stores reason code, detail, source, `etl_run_id`, timestamp; raw payload kept for replay. Reject catalog is stable (`etl/reject_codes.md`) | — |
| 5 | Silver: cleaning, standardization, deduplication, business transformations, load logs / DQ results / last updated | Followed in logic, **not as a separate layer** | Cleaning and conformance happen in normalizers and SQL; results land directly in staging/DW. Run log, DQ results and `loaded_at` provide the metadata the diagram shows | A separate silver schema would add storage and a copy step without changing the result at this data volume; staging already acts as the conformed hop |
| 5b | SCD processing (Type 1 overwrite, Type 2 history) | Type 1 only | Dimensions are keyed on natural keys and refreshed idempotently; history is not versioned | Documented scope decision: this is observation data; Phase 2 business questions don't need attribute history. Type 2 is listed as future work |
| 6 | Dimensional warehouse: surrogate keys, unknown members, inferred members, late-arriving handling, 5 dims + 3 facts | Followed, adapted to the project model | Six dimensions (time, site, vehicle, grid, weather, airspace zone) with `-1` unknown members; five facts (tracking, journey, occupancy, close encounter, restriction activation); required dimensions are never replaced by `-1` — missing ones reject the row | The project's real dimensions differ from the sample's (grid and airspace instead of channel/product); inferred members are deliberately **not** invented. Late-arriving rows are handled by re-running the bounded window, not by a special inference rule |
| 7 | Warehouse performance: PK/FK/composite indexes, views, materialized views, EXPLAIN ANALYZE, query optimization | Partial | Every foreign key and common time column is indexed in the fact DDL; reporting views are stable | Data volume is small and the free tier is 1 GB; materialized views and tuning are deferred to Phase 3 |
| 8 | Gold layer: product / sales / customer / inventory marts, aggregate tables | Later phase / adapted | `project_reporting` provides ten views that answer the ten business questions directly from `project_dw` | Physical marts and aggregates are Phase 3; views avoid duplicate storage and stale copies |
| 9 | Analytics & BI: Power BI semantic model, DAX, KPIs, slicers, insights | Later phase | Not built | Explicitly out of Phase 2 scope; views are shaped so Phase 3 BI can consume them |
| 10 | Auditing, monitoring, reconciliation: run log, rows read, rejected/updated, duration, source→DW reconciliation, pipeline status | Followed | `etl_run_log` (counts, status, code version, failure reason), `dq_result` (passes and failures), reject counts, reconciliation rules, GitHub Actions status and job summary | No external alerting/dashboard; CI history is the monitor at this team size |
| 11 | Metadata & data lineage: source → stage → silver → SCD → gold → BI | Partial | Every fact row carries `source_system`, `source_record_id`, `etl_run_id`, `loaded_at`; staging keeps file + row number; derived facts carry `algorithm_version`; manifest ties a run to a hashed raw file | No automated column-level lineage tool; lineage is ID-based and documented |
| 12 | Business glossary & data dictionary | Followed | `data/data_dictionary.md` (columns) and `Phase2/docs/12_glossary.md` (terms) | — |
| 13 | DW performance & scalability: partitioning, incremental loads, cloud scaling | Partial | Cloud-managed Neon; incremental loads via natural keys; indexes in place | Partitioning is unnecessary at current volume and would not fit the free tier's operation budget |

---

## 4. What is actually in the Neon warehouse

### 4.1 Platform

| Item | Value |
|---|---|
| Neon project | `AeroGrid-DW`, branch `production`, region `aws-us-east-2` |
| Database | `neondb` (one shared database for all five members) |
| Schemas | `project_staging`, `project_dw`, `project_reporting` |
| Writer role | `aerogrid_etl` — used only by the protected CI job |
| Reader role | `aerogrid_reader` — `SELECT` only; all team members |
| Raw archive | Private object-storage bucket `aerogrid-raw` (apply runs archive raw files and link them from `source_manifest`, `D3-018`) |
| Orchestrator | GitHub Actions: weekly schedule (Monday 06:00 UTC) + manual dispatch |

### 4.2 Table purposes

**`project_staging` — landing, audit and quality evidence**

| Table | What it is for |
|---|---|
| `source_manifest` | One row per fetched raw file: provenance (URL, licence, hash, size, fetch time) |
| `etl_run_log` | One row per pipeline run: mode, counts, status, code version, failure reason |
| `stg_reject` | Every rejected row with a stable reason code and the original payload |
| `dq_result` | One row per DQ check per run, including passes, warnings and failures |
| `stg_adsb_position` | Aircraft position records from Tartan (typed, source-shaped) |
| `stg_uas_position` | Drone flight-position records from Nightjar / nominal-io DJI |
| `stg_weather_metar` | Airport weather observations from AWC and IEM |
| `stg_airspace_zone` | FAA airspace and UAS facility zone definitions |
| `stg_restriction_snapshot` | Time-stamped restriction status from real snapshots |
| `stg_opensky_state` | Optional OpenSky snapshot landing table (schema exists; not loaded, per `D-013`) |

**`project_dw` — the star schema (trusted, keyed data only)**

| Table | What it is for |
|---|---|
| `dim_time` | Hourly time dimension |
| `dim_site` | Study sites |
| `dim_vehicle` | Aircraft and drones, one row per real source identity |
| `dim_spatial_grid` | Real 2D grid cells per site (3,658 cells) |
| `dim_weather` | Real METAR observations |
| `dim_airspace_zone` | Real FAA zones |
| `fact_vehicle_tracking` | Core movement fact: one row per accepted position (27,479 rows) |
| `fact_flight_journey` | One row per detected flight (178 rows) |
| `fact_airspace_occupancy` | Hourly grid-cell utilization (1,754 rows) |
| `fact_close_encounter` | One row per detected conflict episode (currently **0**) |
| `fact_restriction_activation` | One row per zone evaluation (currently **0**) |

Every dimension has a `-1` unknown member. Facts reference dimensions by surrogate
key and carry source lineage and the ETL run that loaded them.

**`project_reporting` — ten stable views**

| View | Question it answers |
|---|---|
| `vw_traffic_density_hour_grid` | How busy is each cell per hour? |
| `vw_occupied_grid_hours` | Which cell-hours have observed occupancy? |
| `vw_monthly_traffic` | Monthly traffic volume by site |
| `vw_peak_site_hours` | Busiest hours per site, split by source |
| `vw_daily_encounter_hotspots` | Which days/cells had detected encounters? |
| `vw_encounter_vehicle_types` | Which source categories were involved? |
| `vw_restriction_traffic_impact` | Restriction context vs observed traffic |
| `vw_weather_operations` | Traffic and encounters by weather key |
| `vw_corridor_capacity_inputs` | Observed cell utilization evidence |
| `vw_candidate_corridor_cells` | Low-observed-traffic cell screening |

### 4.3 Why some tables are empty (say this honestly)

- **`fact_close_encounter` and `fact_restriction_activation` are 0 rows.** The
  historical Tartan window and the current weather/UAS/restriction sources do not
  overlap in time, and no real restriction snapshot exists for the study window.
  Zero here means **insufficient overlapping real evidence**, not "zero conflicts".
  This is tracked in the accepted-limitations register
  ([13_accepted_data_limitations.md](13_accepted_data_limitations.md)).
- **Weather / UAS / airspace staging was empty before WP-11.** Run `43502710978`
  loaded 23,254 staging rows and 8 manifests. The DQ coverage guards mark those
  sources as warnings until they are loaded, so an empty table can never be
  mistaken for "no events".
- `stg_opensky_state` is intentionally unloaded.

### 4.4 Recorded evidence snapshot

| Item | Recorded value | Source |
|---|---|---|
| Tracking facts | 27,479 | Member E deployment facts |
| Journeys | 178 | Member E deployment facts |
| Grid cells | 3,658 | Member E deployment facts |
| Occupancy facts | 1,754 | Member E deployment facts |
| Persisted DQ results (WP-07–10) | 32 (29 PASS / 3 WARN / 0 FAIL) | Member E deployment facts |
| WP-11 apply run | 23,254 staging rows, 8 manifests, 820 dimension rows, 36 DQ (32 PASS / 4 WARN / 0 FAIL), `etl_run_id=11` | Run `43502710978` |
| Reporting views | 10 | `WP-10` |

These are the last recorded values, not a live reading; quote them with their date.

---

## 5. Evaluator failure-injection playbook

All steps below are **safe**: no destructive SQL, no secrets, no production writes.
Never paste a connection string into chat; use the approved reader secret.

### A. Prove the guards without any database or network

Run from `Phase2/`:

```text
python -m etl.run --sources not_a_source
python -m etl.run --sources weather --stations XX
python -m etl.run --start 2026-11-16 --end 2026-11-09
python -m etl.run --start 2026-11-16
python -m etl.run --apply --confirm WRONG
```

Expected: each command stops immediately with a plain message. The last one also
proves that `--apply` cannot run outside the approved CI job, even with the right
confirmation string.

### B. Prove row-level error handling with the test suite (no database needed)

From the repository root:

```text
python -m pip install 'pytest>=8,<10' 'psycopg[binary]>=3.2,<4'
python -m pytest -q Phase2/tests
```

Targeted proofs if the evaluator wants specific ones:

```text
python -m pytest -q Phase2/tests/test_staging_writer.py::test_rejected_rows_are_counted_and_recorded
python -m pytest -q Phase2/tests/test_staging_writer.py::test_db_error_rolls_back_savepoint_and_continues_batch
python -m pytest -q Phase2/tests/test_loaders.py::test_load_tartan_rejects_bad_row_and_accepts_next
python -m pytest -q Phase2/tests/test_wp11_run.py::test_run_validate_fails_when_a_source_has_no_accepted_rows
python -m pytest -q Phase2/tests/test_wp11_run.py::test_apply_guard_requires_ci_environment_and_confirmation
python -m pytest -q Phase2/tests/test_dq.py
```

These tests feed malformed rows and prove: the bad row is rejected with a reason,
the next row is still accepted, the savepoint recovers, an empty source fails the
run, and the apply guard blocks.

### C. Prove real-source validation, read-only (network, no database)

```text
python -m etl.run --sources weather --stations KBTP,KAGC --start 2026-11-09 --end 2026-11-16 --summary-path summary.md
python -m etl.run --sources airspace --summary-path airspace.md
python -m etl.run --sources uas --summary-path uas.md
```

Expected: fetched-file table, rows read / accepted / rejected per file with reject
reasons, and a statement that nothing was written. If the upstream API is rate
limited, the run fails **closed** and names the source — also correct behaviour.

### D. Read-only database checks (if the evaluator has the team reader connection)

Set the approved reader connection in the environment (never in chat), then:

```text
cd Phase2
python -m etl.dq
```

Expected: `PASS` / `WARN` / `FAIL` per check with observed values; exit code
non-zero only on FAIL. Then inspect evidence:

```sql
SELECT etl_run_id, status, rows_read, rows_accepted, rows_rejected, rows_duplicate,
       critical_dq_failures, failure_reason
FROM project_staging.etl_run_log ORDER BY etl_run_id DESC LIMIT 5;

SELECT check_id, severity, status, observed_value
FROM project_staging.dq_result
WHERE etl_run_id = (SELECT max(etl_run_id) FROM project_staging.dq_result)
ORDER BY check_id;

SELECT source_system, reason_code, count(*)
FROM project_staging.stg_reject GROUP BY 1,2 ORDER BY 3 DESC;
```

And prove the reader cannot write:

```sql
INSERT INTO project_dw.dim_site (site_code) VALUES ('X');
-- expected: ERROR 42501 permission denied for table dim_site
```

### E. What we will not do

- No `DELETE`, `DROP`, `TRUNCATE`, or orphan injection on the shared warehouse.
- No writer credentials shared with evaluators.
- No secrets in chat or screenshots.

If the evaluator asks "what if an orphan existed?", answer with the check that
catches it (`DQ-I-001` … `DQ-I-010`) and the fact that the database also enforces
foreign keys, so a real orphan cannot commit in the first place.

---

## 6. Anticipated architectural questions

| Question | Model answer |
|---|---|
| Why no SCD Type 2? | Phase 2 answers observation questions, not attribute-history questions. History is a recorded future item, not an omission. |
| Where is the raw data? | Manifests pin every file by SHA-256 and apply runs archive the bytes to `aerogrid-raw` (`D3-018`); pre-`D3-018` manifests are hash-only. Raw data is never committed to Git. |
| How do you know data is real? | Every fact carries source identity and run ID; every run links to hashed manifests; the legacy synthetic sample is explicitly excluded (`D-017`). |
| How do you stop a duplicate load? | Natural-key unique constraints plus `ON CONFLICT DO NOTHING`; reruns count as duplicates and insert nothing. |
| How does one bad row not break a load? | Per-row savepoints; the row becomes a reject with a stable reason code and the batch continues. |
| How is a critical failure handled? | One transaction; a CRITICAL DQ failure rolls it back, stores failure evidence in a separate run, and turns CI red. |
| How do you reconcile staging to facts? | Exact identity in the run log (code + DB constraint + DQ rule) and a source-to-fact check for accepted Tartan rows. |
| Why can an empty table be "correct"? | It is either measured-empty or missing-coverage; coverage guards label the second case as WARN/FAIL, never as zero events. |
| Why are encounters zero? | The real sources do not overlap in time for the study window; this is a coverage limitation, not a safety finding. |
| Who can change data? | Only the CI writer role. Members are `SELECT`-only, proven by a permission-denied test. |
| Why not Docker or a local database? | Project constraint: shared cloud warehouse only, no local services. |
| Why GitHub Actions instead of Airflow? | Free, auditable, no always-on server; weekly/manual cadence matches the requirement. |
| How would this scale? | Indexed star schema now; partitioning and physical marts in Phase 3 if volume grows. The 1 GB tier is the current budget. |
| What is the single source of truth? | `project_dw`. Reporting views are read-only projections; no base tables in `project_reporting`. |
| How is a failed scheduled run handled? | The run fails closed, the workflow is red, and the job summary states what failed. For the FAA quota case, retries exhausted and nothing was written. |
| What was verified vs accepted? | Administrative acceptance is documented separately from independent technical proof in the final gate record. We state the difference rather than blur it. |

---

## 7. Known gaps (be upfront; each has a reason)

| Gap | Impact | Reason / tracking |
|---|---|---|
| Historical raw manifests have no stored bytes | Pre-`D3-018` runs cannot replay exact bytes; new apply runs can | `L-010` closed by `D3-018`; live proof `H3-011` |
| No SCD Type 2 history | Cannot answer "how did this attribute change" | Scope decision; documented in `04_data_model.md` |
| Dimension refresh is insert-only | `last_seen_ts` does not advance after first sight | Idempotent-by-construction choice; revisit with SCD work |
| No physical marts or BI layer | Views only | Phase 3 scope |
| No partitioning / materialized views | Large-scale performance untested | Dataset is small; free tier |
| No late-arriving inference | Late rows load on a later bounded run | Simpler and safer than inference; documented |
| Encounter and restriction facts are 0 | Some business questions answer "insufficient evidence" | Source overlap limitation; see limitations register |
| FAA ArcGIS quota can fail a scheduled run | A run can fail before writing anything | External rate limit; retries are bounded by design. Airspace is static data and can be fetched less often |
| Independent G7 replay and all-member reader tests | Declared accepted, not independently re-proven | Tracked in the final gate record |

---

## 8. Evidence index

| Evidence | Location |
|---|---|
| Reference architecture diagram | `docs/Sample Project Architecture Diagram.png` |
| Architecture and platform | [02_architecture_and_platform.md](02_architecture_and_platform.md) |
| ETL stages and idempotency | [05_etl_pipeline.md](05_etl_pipeline.md) |
| DQ catalog and severity model | [06_data_quality_and_reports.md](06_data_quality_and_reports.md) |
| Logical model and grains | [04_data_model.md](04_data_model.md) |
| Column dictionary | `data/data_dictionary.md` |
| Reject reason catalog | `Phase2/etl/reject_codes.md` |
| Access model and roles | [07_operations_access_and_security.md](07_operations_access_and_security.md) |
| Accepted limitations | [13_accepted_data_limitations.md](13_accepted_data_limitations.md) |
| Release evidence | [WP12_RELEASE_EVIDENCE_2026-11-14.md](WP12_RELEASE_EVIDENCE_2026-11-14.md) |
| Gate record | [FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md) |
| Demo sheet | [14_demo_script.md](14_demo_script.md) |
| CI workflows | `.github/workflows/` (`wp04`–`wp11`, `ci`, `platform-validation`) |
| WP-11 apply run | GitHub Actions run `43502710978` |

---

## 9. One-page cheat sheet

**Say this**

- "Staging can contain rejects; the warehouse never does."
- "Counts must reconcile — in code, in a database constraint, and in a DQ rule."
- "A CRITICAL failure rolls back the whole run and leaves auditable evidence."
- "Reruns never duplicate: natural keys plus `ON CONFLICT`."
- "Empty means missing coverage; we refuse to report it as zero events."
- "Only CI writes; every member reads through a SELECT-only role."
- "Encounters are zero because the real sources don't overlap in time — that is a
  coverage limitation, not a safety claim."

**Do not claim**

- That SCD Type 2, physical marts, materialized views, partitioning, or BI exist.
- That raw files are archived today (manifest only).
- That the zero encounter/restriction facts prove anything about real-world safety.
- That every gate was independently re-verified; cite the gate record's wording.
