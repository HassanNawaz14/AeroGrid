# WP-12 — Integration, acceptance, and release evidence (2026-11-14)

**Work package:** `WP-12` — integration, acceptance, and release
**Owner:** Member A (HassanNawaz14)
**Reviewers:** Members B–E
**Gate:** `G7`
**Status:** `READY_FOR_REVIEW` — technical evidence captured; human release acceptance and the two open follow-ups below are still pending.

This record follows the WP-12 deliverables in
[dev_plan/01_work_breakdown.md](../dev_plan/01_work_breakdown.md#wp-12-integration-acceptance-and-release):
rubric audit, report audit, access audit, documentation and link audit, accepted-limitation
audit, demo script, and final status. It records only runs that were actually dispatched.
It does not upgrade the 2026-11-13 administrator declaration into proof of work that was
not executed.

## 1. Release identity

| Item | Value |
|---|---|
| Release review commit | `6d23d38` (`main`, merge of PR #28), verified on branch `docs/wp12-release` |
| Warehouse | Neon Free `AeroGrid-DW`, branch `production`, database `neondb`, PostgreSQL 18.6 |
| Latest warehouse write | WP-11 apply run [43502710978](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43502710978) on `165d59d`, `etl_run_id=11` |
| Read-only verification | WP-08 [43508430448](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43508430448), WP-10 [43508438840](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43508438840), WP-09 [43508445375](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43508445375) |
| Reports in this release | [Data Cleaning](../reports/Data_Cleaning_Report.pdf) (4 pages), [Data Quality](../reports/Data_Quality_Report.pdf) (3 pages), both regenerated from the live warehouse at run 11 |

The three verification runs were dispatched on `main` after the release commit and are
read-only: they apply DDL/seed inside a transaction, assert, and roll back. None of them
wrote warehouse rows.

## 2. Rubric audit — course requirements

Source: [DWBI Lab Phase 2](../DWBI%20Lab%20Phase%202.pdf), restated in
[01_phase2_scope_and_objectives.md](01_phase2_scope_and_objectives.md).

| Requirement | Evidence | Status |
|---|---|---|
| PostgreSQL database SQL scripts | [`Phase2/sql/`](../sql/) — schemas, staging, dimensions, facts, reporting; all idempotent | Met |
| Staging schema SQL | [`01_staging/`](../sql/01_staging/) tables plus reject ledger `project_staging.stg_reject` | Met |
| Data warehouse schema SQL | [`02_dimensions/`](../sql/02_dimensions/), [`03_facts/`](../sql/03_facts/) | Met |
| ETL scripts in SQL or Python | [`Phase2/etl/`](../etl/) — `fetch.py`, `loaders.py`, `staging_writer.py`, `dimension_loaders.py`, `facts.py`, `derived_facts.py`, `dq.py`, `run.py` | Met |
| Dimension load scripts | `etl/dimension_loaders.py`, `etl/verify_wp05_dimensions.py` | Met |
| Fact load scripts | `etl/facts.py`, `etl/derived_facts.py`, `etl/verify_wp06_facts.py`, `etl/verify_wp07_facts.py` | Met |
| Data Cleaning Report PDF | [Data_Cleaning_Report.pdf](../reports/Data_Cleaning_Report.pdf) | Met |
| Data Quality Report PDF | [Data_Quality_Report.pdf](../reports/Data_Quality_Report.pdf) | Met |
| GitHub repository link | This repository, `main` | Met |
| At least 100 dimension records | Six dimensions; run 11 alone inserted `dim_weather` 400, `dim_airspace_zone` 252, `dim_time` 166, `dim_vehicle` 2, on top of the WP-05 seed (`dim_time` 169, `dim_site` 5) and `dim_spatial_grid` 3,658 real cells | Met |
| At least 10,000 fact records | `fact_vehicle_tracking` 27,479, `fact_flight_journey` 178, `fact_airspace_occupancy` 1,754; grid 3,658 cells; encounter and restriction facts 0 by documented limitation | Met |

### Required schemas

| Schema | Evidence |
|---|---|
| `project_staging` | [`00_schemas.sql`](../sql/00_schemas.sql), staging DDL, reject ledger, manifests, `etl_run_log` |
| `project_dw` | Six dimensions with `-1` unknown members; tracking, journey, occupancy, encounter, restriction facts |
| `project_reporting` | Ten views in [`05_reporting/01_reporting_views.sql`](../sql/05_reporting/01_reporting_views.sql) |

### Required techniques

| Technique | Where it is implemented | How it is proven |
|---|---|---|
| Deduplication | `insert_on_conflict_do_nothing` in [staging_writer.py:146](../etl/staging_writer.py#L146); `ON CONFLICT DO NOTHING` in staging and fact inserts; `DISTINCT ON (station_icao, observation_ts)` in [dimension_loaders.py:73](../etl/dimension_loaders.py#L73) | Run 11 recorded 0 duplicate rows; DQ `DQ-U-001`–`DQ-U-004` assert zero natural-key and grain duplicates |
| Null handling | Required-key values map to explicit reject codes and `stg_reject` rows; optional references fall back to `-1` unknown members instead of inventing values; `L-002` keeps the real NULL `on_ground` | 160 rejects in run 11 by named rule; DQ `DQ-C-001`, `DQ-C-003`, `DQ-C-005`, `DQ-C-006` |
| Text standardization | `strip().upper()` normalization of site codes, ICAO identifiers, and source systems — [facts.py:213](../etl/facts.py#L213), [facts.py:275](../etl/facts.py#L275), [loaders.py:463](../etl/loaders.py#L463); `normalize_site_code` in [dimensions.py:12](../etl/dimensions.py#L12) | DQ `DQ-C-003` warning reports the surviving non-standard optional reference; dimension joins succeed for all 27,479 facts |
| Type conversion | `transforms.py` unit conversions and parsers (C/F, hPa/inHg, m/s and mph to knots, visibility, ceiling, flight category); `::numeric` casts in [dimension_loaders.py](../etl/dimension_loaders.py) | Unit tests in `tests/test_transforms.py`; `DQ-A-001`, `DQ-A-002`, `DQ-A-007`, `DQ-A-008` |
| Surrogate keys for dimensions | `bigint GENERATED ALWAYS AS IDENTITY` primary keys in [01_dimensions.sql:8](../sql/02_dimensions/01_dimensions.sql#L8) and the other five dimensions | `verify_wp05_dimensions.py` asserts six tables, one `-1` row each, no duplicate natural keys |
| Fact loading by business key → surrogate key | `load_dimension_lookups` and the loaders in [facts.py:367](../etl/facts.py#L367), [facts.py:864](../etl/facts.py#L864); source lineage columns on every fact | `DQ-I-001`–`DQ-I-010` (0 orphan keys), `DQ-C-006` (0 facts without lineage) |
| DQ for completeness | `DQ-C-001`, `DQ-C-005`, `DQ-C-006`, `DQ-R-001`, coverage guards `DQ-G-001`–`DQ-G-004` | Run 11: all PASS except the documented warnings |
| DQ for accuracy | `DQ-A-001`, `DQ-A-002`, `DQ-A-007`, `DQ-A-008`, `DQ-R-002`, `DQ-R-004`, `DQ-R-005`, `DQ-R-006`, `DQ-B-001` | 0 critical failures |
| DQ for integrity | `DQ-I-001`–`DQ-I-010`, `DQ-U-001`–`DQ-U-004`, `DQ-B-003`, `DQ-B-004` | 0 critical failures |

### Deliverable outcomes

| Outcome | Evidence | Status |
|---|---|---|
| Reproducible schema | Idempotent DDL applied twice by the WP-05/WP-10 verifiers | Met |
| Real ingestion | 8 source manifests with URLs, licenses, SHA-256 and timestamps in `project_staging.source_manifest` | Met |
| Clean staging | 23,254 accepted / 160 rejected / 0 duplicate in run 11, plus stored reject reasons | Met |
| Dimensions | 100+ rows; natural and surrogate keys; `-1` unknown members | Met |
| Facts | 10,000+ rows; zero orphan foreign keys; source lineage | Met (`DQ-I-*`, `DQ-C-006`) |
| Data quality | 36 persisted checks and the Data Quality PDF | Met |
| Data cleaning | Data Cleaning PDF with per-source accepted/rejected detail | Met |
| Shared access | `aerogrid_reader` SELECT proof in the WP-11 reader job; per-member probe documented and open (`H-017`) | Partially met |
| Automation | `wp11-ingest.yml` validate/apply/schedule/reader jobs; `ci.yml` unit tests | Met for manual runs; first scheduled run pending 2026-11-16 |

## 3. Report audit

The PDFs committed before this release were generated from an earlier warehouse state
(5,736 and 7,003 bytes). The copies in this branch were regenerated by WP-09 run
43508445375 from the live warehouse and show:

| Check | Observed |
|---|---|
| Report source run | Latest ETL run ID 11 |
| Pages | Data Cleaning 4, Data Quality 3 |
| Coverage table | `LOADED` rows for METAR, UAS, airspace, and Tartan sources |
| Rejected records | Stored rejection records reported with the "do not add across runs" note |
| Airspace zones | 252 real zones |
| DQ run | 11 — 0 critical `FAIL`, 4 warnings |
| File sizes | 9,500 and 8,083 bytes |

Both PDFs are generated only from stored warehouse rows; no synthetic values are added.
The stored-reject note exists because `stg_reject` spans ETL runs (`L-006`).

## 4. Access audit

| Check | Evidence | Status |
|---|---|---|
| Read-only role exists and can `SELECT` every reporting view | WP-11 `reader-check` job `PASS` on apply run 43502710978 | Met |
| Read-only role cannot write | Same job recorded the denied write with SQLSTATE `42501` | Met |
| Every member can read without local PostgreSQL | Probe procedure documented in [10_human_operating_manual.md](10_human_operating_manual.md#first-action-for-every-team-member-reader-proof) | **Open — `H-017`** |
| Connection uses TLS | Neon pooled connection; `sslmode=require` is the accepted proof because the pooler hides TLS state from `pg_stat_ssl` | Met |
| Credentials outside Git | `DATABASE_URL`/`READONLY_DATABASE_URL` are GitHub secrets, read only inside the protected `warehouse` environment | Met |

`H-017` stays open until Members B–E run the probe themselves; the role-level proof does
not substitute for each member's own credentials.

## 5. Documentation and link audit

| Check | Result |
|---|---|
| Relative links | 386 checked across all Markdown outside `payloads/`; 0 broken after URL-decoding (the four `%20` links resolve to `DWBI Lab Phase 2.pdf`) |
| Fixes made | [reports/README.md](../reports/README.md) missing `../`; [data/data_dictionary.md](../../data/data_dictionary.md) missing `../` |
| Excluded from link audit | `payloads/*.md` — updater snippets, not navigation documents; they are not linked from any canonical doc |
| Secret scan | 0 matches for connection strings with embedded credentials, private keys, GitHub/OpenAI/AWS token patterns in tracked text files |
| Raw data | No raw archives, database dumps, or `.csv` source files tracked; only the documented offline demo files under [`data/sample/`](../../data/sample/) (`D-017`) |
| PDFs | Both are generated artifacts committed intentionally as release deliverables |
| Whitespace check | `git diff --check -- '*.md'` is clean. The unfiltered command flags trailing spaces inside the PDF byte stream because the repository sets no binary attribute for `*.pdf`; add `*.pdf binary` to `.gitattributes` if a clean unfiltered check is required. This is audit noise, not a document defect |

## 6. Accepted-limitation audit

Source of truth: [13_accepted_data_limitations.md](13_accepted_data_limitations.md).
"Trigger" means the condition that requires revisiting the limitation.

| ID | Observed value in this release | Trigger status | Owner |
|---|---|---|---|
| `L-001` | Weather dimension refreshed with 400 real METAR rows; the 27,479 January-2022 tracking facts still cannot be weather-linked and keep the `-1` unknown member | Historical window mismatch persists | Member D (`WP-06`) |
| `L-002` | `on_ground` NULL for all 27,479 tracking facts; 7,433 inferred airborne positions are analytical, not observed | Source field remains NULL | Member D (`WP-06`), Member E (`WP-07`) |
| `L-003` | 3,658 real 2D cells, 0.01° WGS84; 60-second adjacent-sample occupancy cap | No 3D/altitude model approved | Member E (`WP-07`) |
| `L-004` | Encounter facts 0; `wp07-v1` requires identical timestamps | No matcher change approved | Member E (`WP-07`) |
| `L-005` | Restriction activation facts 0; no historical 2022 TFR snapshot | No snapshot source approved | Member E (`WP-07`) |
| `L-006` | Stored rejects span runs; per-run ledger reconciles (run 11: 160 rejected) | Cross-run totals still not additive | Member B (`WP-04`) |
| `L-007` | Corridor views are screening metrics over observed cells | No approved corridor validation | Member E (`WP-10`) |
| `L-008` | UAS staging now `LOADED` with 22,602 accepted positions; **no UAS fact loader exists** | Trigger met if UAS facts are claimed — do not claim them | Member A (`WP-11`) |
| `L-009` | Airspace staging `LOADED` with 252 zones; OpenSky still unused; no restriction loader | Trigger met if restriction facts are claimed — do not claim them | Member A (`WP-11`) |
| `L-010` | Raw source files are hashed and manifested but not archived to object storage | Trigger met before any re-download-dependent claim | Member A (`WP-11`) |

All ten remain `OPEN`. A green coverage guard proves the source was ingested; it does not
close the limitation. The WP-11 run summary prints every `L-###` with its linked DQ status
so this audit is reproducible from CI output.

## 7. Reproducibility

**Proven:**

- `validate` mode fetches and parses the same 23,414 rows and rejects the same 160 rows
  without any warehouse access.
- `apply` mode completed a green write on `main` (run 43502710978), and the loaders are
  idempotent (`ON CONFLICT DO NOTHING` plus natural-key constraints).
- The three read-only verifiers reproduce the persisted DQ (36 checks: 32 PASS / 4 WARN /
  0 FAIL), the 10 reporting views with their row counts, and the PDFs from live data.

**Not yet proven:**

- A **second** authorized `apply` run on the release commit has not been dispatched, so
  "a fresh authorized run reproduces the result" is demonstrated only by the first apply
  run plus the idempotency design and verifiers. Human dispatch is required (`H-018`).
  On a re-run, expect 0 duplicate rows for the static UAS and airspace files and 0
  critical failures; weather rows can legitimately differ if the rolling 7-day window
  moved, so the check is reconciliation and zero failures, not identical totals.
- The first scheduled run (Monday 2026-11-16 06:00 UTC) has not happened yet (`H-019`).

## 8. WP-10 view reconciliation (run 43508438840)

| View | Rows |
|---|---:|
| `vw_traffic_density_hour_grid` | 6,658 |
| `vw_occupied_grid_hours` | 1,754 |
| `vw_monthly_traffic` | 1 |
| `vw_peak_site_hours` | 20 |
| `vw_daily_encounter_hotspots` | 0 |
| `vw_encounter_vehicle_types` | 0 |
| `vw_restriction_traffic_impact` | 0 |
| `vw_weather_operations` | 1 |
| `vw_corridor_capacity_inputs` | 808 |
| `vw_candidate_corridor_cells` | 808 |

Zero-row views are the documented `L-004`/`L-005` limitations, not defects.

## 9. Final status

| WP-12 acceptance evidence | Status |
|---|---|
| All rubric items have evidence | Met (section 2) |
| 100+ dimension rows and 10,000+ fact rows demonstrated | Met (section 2) |
| Both PDFs are final | Met (section 3) |
| Read-only access works for members | Role-level met; per-member open (`H-017`) |
| No critical DQ failures | Met — 0 `FAIL` |
| No secrets/raw data in Git | Met (section 5) |
| A fresh authorized run reproduces the result | Partially met (section 7) |
| Every open `L-###` reported with observed value, trigger, owner | Met (section 6) |
| Human accepts the release | **Pending** |

**Next actions** (stable IDs; the same list is at the top of [PROGRESS.md](../PROGRESS.md#next-session-open-gaps-start-here))

1. `H-018` — Human: after this branch merges, dispatch one `mode=apply` run on `main` and
   record the run URL, `etl_run_id`, reconciliation, and any duplicate count.
2. `H-017` — Members B–E: run the reader probe as their first action and report pass/fail
   plus each rejected write's SQLSTATE.
3. `H-019` — Human: confirm the scheduled run on 2026-11-16; if no `schedule` run appears,
   add repository-level schedule variables (the `H-016` values are environment-scoped).
4. `B-016` — Human: decide on the `payloads/` snippet directory so link audits stop
   reporting 16 false breaks.
5. Human: record release acceptance in [PROGRESS.md](../PROGRESS.md) to clear `G7`.

## Change history

| Date | Change |
|---|---|
| `2026-11-14` | Created from WP-12 verification runs 43508430448, 43508438840, 43508445375 and apply run 43502710978; regenerated release PDFs; audited rubric, limitations, access, links, and secrets. |
| `2026-11-14` | Converted the open items into stable IDs (`H-018` confirmatory apply, `H-019` scheduled-run check, `B-016` `payloads/` link noise) with expected results and failure handling, and documented the PDF whitespace-check noise. |
