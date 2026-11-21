# Phase 3 Progress Board

This is the only status board for Phase 3. Decision records live in
[DECISIONS.md](DECISIONS.md); details live in the canonical documents.

## Headline

`PHASE3_P3G3_DONE_WP06_IN_PROGRESS_WP07_08_PENDING_WP09_DONE` — documentation baseline merged (PR #31) and
human prerequisites closed by the requester-admin on 2026-11-18 (H3-001 authorized,
H3-002 Power BI Desktop confirmed, H3-003 whole team presents). WP-P3-01/02/03 are
`DONE`; PR #35 merged as `761475b` and the requester confirmed the C/D review
sign-off on 2026-11-18. P3-G2 is closed on the recorded evidence: 10 of 10 read-only
queries, `aerogrid_reader`, `DQ3-A-004` `PASS`. P3-G3 is `DONE`: WP-P3-04 was
applied and reader-proofed via `H3-005`; WP-P3-05 verify run 44397831286 passed
`DQ3-A-006`, measured all three candidates `NEUTRAL`, applied no index (`D3-011`),
and delivered the verify-mode `reports/Indexing_Report.pdf`. WP-P3-06 (Power BI dashboard, Member E) is `IN_PROGRESS`: spec approved 2026-11-20
(`D3-012`–`D3-014` recorded); PBIX build and screenshots not yet on disk (the
2026-11-21 packaging dry-run reports both `MISSING`). A review complete 2026-11-21,
D review pending. WP-P3-07 (Business insights report) and
WP-P3-08 (Final presentation) are `PENDING` pending dashboard evidence. WP-P3-09 (CI
packaging + artifacts, Member A) is `DONE` as of 2026-11-21: artifact layout,
the `D3-008` packaging script and manual workflow, and the release-notes template are
in place; workflow run [44871649279](https://github.com/HassanNawaz14/AeroGrid/actions/runs/44871649279) passed on `main`
(`01a5ccb`); D and E reviews and Member A's review of WP-P3-06 are recorded; `H3-008`
is closed. The final `--strict` run and release notes remain (`H3-009`).

## Gate status

| Gate | Title | State | Evidence |
|---|---|---|---|
| P3-G0 | Documentation baseline | DONE | PR #31 merged (commit `c700ad7`): docs 00–13 + dev_plan; no implementation, no secrets, no raw data |
| P3-G1 | Human prerequisites | DONE | Requester-admin closure 2026-11-18: H3-001 authorized, H3-002 confirmed, H3-003 whole team presents |
| P3-G2 | Analytical SQL + OLAP | DONE | WP-P3-02 + WP-P3-03 evidence: `Phase3/evidence/analytics_run_20261118T110136Z.md` (10/10 queries, `aerogrid_reader`, `DQ3-A-004` PASS); CI run 44290826341; PR #35 merged as `761475b`; C/D review sign-off confirmed 2026-11-18 |
| P3-G3 | Reporting views + optimization | DONE | WP-P3-04 applied and reader proofed (`H3-005` closed); WP-P3-05 verify PASS (run 44397831286, `DQ3-A-006` PASS, all candidates NEUTRAL, persisted false) with `Phase3/reports/Indexing_Report.pdf` committed and no apply per `D3-011` |
| P3-G4 | Dashboard + insights + presentation | IN_PROGRESS | WP-P3-06 spec approved 2026-11-20; PBIX build starting |
| P3-G5 | Release | IN_PROGRESS | WP-P3-09 `DONE` (run 44871649279 on `main`, `01a5ccb`; dry-run evidence `Phase3/evidence/packaging_dryrun_20261121T052507Z.md`); WP-P3-10 waits for P3-G4 (BI files) and the human close |

## Work package status

| WP | Title | Owner | Status |
|---|---|---|---|
| WP-P3-00 | Documentation baseline | A | DONE (PR #31, 2026-11-18) |
| WP-P3-01 | Human prerequisites | Human / A | DONE (2026-11-18, requester-admin) |
| WP-P3-02 | Analytical SQL layer | E | DONE (PR #35, `761475b`; evidence `Phase3/evidence/analytics_run_20261118T110136Z.md`) |
| WP-P3-03 | OLAP queries (ROLLUP / CUBE) | E | DONE (PR #35, `761475b`; same paired evidence, `DQ3-A-004` PASS) |
| WP-P3-04 | Phase 3 reporting views | E | DONE (Applied and verified via H3-005) |
| WP-P3-05 | Query optimization + indexing report | D | DONE (Reviewed) |
| WP-P3-06 | Power BI dashboard | E | IN_PROGRESS (spec approved 2026-11-20; PBIX and screenshots not yet on disk; A review complete 2026-11-21, D review pending) |
| WP-P3-07 | Business insights report | E | PENDING (dashboard evidence required) |
| WP-P3-08 | Final presentation | E | PENDING (dashboard evidence required) |
| WP-P3-09 | CI packaging + artifacts | A | DONE (2026-11-21; run 44871649279 green on `main`, `01a5ccb`; D and E reviews recorded) |
| WP-P3-10 | Release + acceptance | Human / A | NOT_STARTED |
| WP-P3-H1 | (Optional) Raw archive closure (`L-010`) | A | READY_FOR_REVIEW (implemented 2026-11-22 under `D3-018`; live proof `H3-011`) |
| WP-P3-H2 | (Optional) FAA quota mitigation | B (HarveyWebbs) | DONE (2026-11-21; D3-016, cache + backoff + optional-airspace; 6 unit tests green; review closed) |
| WP-P3-H3 | (Optional) SCD Type 2 evaluation | C | NOT_STARTED |
| WP-P3-H4 | (Optional) Materialized marts + refresh | D | NOT_STARTED |

## P3-G2 handoff (2026-11-18)

- Branch: `phase3/wp-p3-02-analytical-sql` (PR #35). Evidence harness merged as
  PR #34 (`phase3/wp-p3-ci-evidence`); workflow run 44290826341.
- Files: 7 queries under `Phase3/sql/analytical/`, 3 queries under
  `Phase3/sql/olap/`, `Phase3/scripts/run_readonly_analytics.py`,
  `Phase3/tests/test_analytics_assets.py`, `Phase3/tests/conftest.py`,
  `Phase3/sql/README.md`, `Phase3/evidence/README.md`.
- Checks: `python -m pytest -q Phase3/tests` -> 22 passed; CI static tests passed;
  live read-only run executed 10 of 10 queries; `DQ3-A-004` returned `PASS`.
- Evidence: `Phase3/evidence/analytics_run_20261118T110136Z.md`, captured
  `2026-11-18T11:01:37Z` as `aerogrid_reader` against `neondb` (PostgreSQL 18.7).
- Observed at capture: 27,479 tracking facts; 178 journeys; 1,754 occupancy facts;
  158 vehicle dimension rows (156 with tracking, 2 UAS rows with no tracking facts);
  3,658 grid cells; 0 detected encounters. One observed tracking month (2022-01);
  four sites exist, only KBTP has tracking coverage.
- Zero-coverage rows are labelled as coverage gaps, never as zero activity
  (`D3-009`; `L-003`, `L-004`, `L-008`, `L3-002`, `L3-003`).
- Closed: PR #35 merged as `761475b`; requester confirmed C/D review sign-off on
  2026-11-18. P3-G2 is `DONE`, releasing WP-P3-04 for P3-G3.

## WP-P3-04 handoff (2026-11-18)

- Branch: `phase3/wp-p3-04-reporting-views` (pushed). Gate: P3-G3.
- CI plumbing: `.github/workflows/wp-p3-gold-views.yml` merged to `main` via PR #36
  (`d90f2a1`). It verifies with rollback by default; `apply` is `main`-only and
  needs the `warehouse` environment plus `APPROVE_WP3_GOLD_VIEWS`.
- Files added: `Phase3/sql/views/01_gold_views.sql`,
  `Phase3/sql/views/README.md`, `Phase3/scripts/verify_gold_views.py`,
  `Phase3/tests/test_gold_views.py`.
- Files updated: `Phase3/sql/README.md`, `Phase3/evidence/README.md`,
  `Phase3/README.md`, `Phase3/PROGRESS.md`.
- Views: `vw_monthly_traffic_growth` (observed site-month grain, null-safe
  month-over-month status), `vw_vehicle_analysis` (one row per real vehicle,
  observed-hour summary, `L3-003` identity note), `vw_source_performance` (one row
  per source system, observed-month span and coverage labels, `L-008`).
- Static checks: `python -m pytest -q Phase3/tests` -> 33 passed;
  `python -m compileall -q Phase3/scripts Phase3/tests` -> OK; `pglast` parsed the
  three-view DDL; workflow YAML parsed; secret scan clean.
- Rollback verification: workflow run 44295954164 `PASS`, captured
  `2026-11-18T11:34:54Z` as `aerogrid_etl` against `neondb` (PostgreSQL 18.7);
  evidence `Phase3/evidence/gold_views_20261118T113454Z.md`; no persisted view
  changes. Baseline: 27,479 tracking facts; 178 journeys; 1 site-month; 158 vehicle
  rows; 3 source rows.
- `DQ3-A-001`: `PASS` for `vw_monthly_traffic_growth` (1 row, 27,479 tracking),
  `vw_vehicle_analysis` (158 rows, 27,479 tracking, 178 journeys), and
  `vw_source_performance` (3 rows, 27,479 tracking, 178 journeys).
- Closed: `H3-005` apply recorded and reader-proofed; WP-P3-04 is `DONE` and P3-G3
  is `DONE`. The gold-view apply run ID is not recorded in the repo; cite `H3-005`
  and the admin record, not an invented run ID.
- Coverage rule: no month spine, no synthetic rows; zero-fact members stay visible
  with coverage labels, never as zero activity (`D3-009`).

## WP-P3-05 handoff (2026-11-19, Member D)

- Branch: `phase3/wp-p3-05-query-optimization`. Gate: P3-G3; prerequisite P3-G2
  is `DONE`. Decision `D3-010` records the measurement/apply rule.
- Files added: `Phase3/sql/indexes/01_indexes.sql` (three idempotent
  `CREATE INDEX IF NOT EXISTS` candidates on `project_dw`),
  `Phase3/sql/optimization/01_source_monthly_volume.sql` (`OQ-P3-05-01`),
  `02_monthly_growth_by_site.sql` (`OQ-P3-05-02`),
  `03_vehicle_activity.sql` (`OQ-P3-05-03`),
  `Phase3/scripts/measure_indexes.py` (rollback-first
  `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` harness),
  `Phase3/scripts/generate_index_report.py` (PDF from recorded JSON only),
  `.github/workflows/wp-p3-05-indexes.yml`, and
  `Phase3/tests/test_index_optimization.py`.
- Files updated: `Phase3/sql/README.md`, `Phase3/evidence/README.md`,
  `Phase3/README.md`, `Phase3/docs/05_etl_pipeline.md`,
  `Phase3/dev_plan/03_deliverables_matrix.md`, `Phase3/DECISIONS.md`,
  `Phase3/PROGRESS.md`.
- Behaviour: verify mode creates each candidate inside a transaction, measures the
  target query before/after, records the index size, and rolls back; nothing is
  persisted. Apply is `main`-only, requires `APPROVE_WP3_INDEXES` plus the
  `warehouse` environment, commits the DDL, verifies each index exists, and aborts
  above the 700 MB guard. The PDF refuses to build unless every claimed index has
  a before/after pair (`DQ3-A-006`); neutral or slower results are reported as
  measured.
- Checks: `python -m pytest -q Phase3/tests` -> 49 passed after the
  schema-qualified-index fix (`2d283bc`, PR #39 merged as `6678c1a`);
  `python -m compileall -q Phase3/scripts Phase3/tests` OK; `pglast` parsed the
  four SQL assets; workflow YAML parsed; `git diff --check` clean. The first live
  run failed on `pg_relation_size` because a three-part relation name was rejected
  (`FeatureNotSupported`); the fix qualifies the index as `schema.index`, and the
  failure stays visible in history rather than being hidden.
- Verify measurement: run 44397831286, captured `2026-11-18T21:05:46Z` as
  `aerogrid_etl` against `neondb` (PostgreSQL 18.7). Mode `verify`,
  `persisted: false`; baseline 27,479 tracking / 178 journey / 1,754 occupancy;
  database 71.72 MiB before, 71.78 MiB at end; guard 700 MiB.
  `DQ3-A-006: PASS`.
- Measured pairs (one observed `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` run, not
  a benchmark): `OQ-P3-05-01` 28.927 -> 29.064 ms (+0.47%), cost 5,683.16 both,
  index 488 KiB; `OQ-P3-05-02` 32.055 -> 32.240 ms (+0.58%), cost 11,359.07 both,
  index 488 KiB; `OQ-P3-05-03` 33.101 -> 33.220 ms (+0.36%), cost 9,347.77 both,
  index 16 KiB. Every plan is identical before and after, so each verdict is
  `NEUTRAL`; no speed-up is claimed (`D3-010`).
- Decision `D3-011`: none of the candidates is applied. Applying neutral indexes
  would add ~992 KiB and write maintenance for no measured gain; the idempotent
  DDL stays in `Phase3/sql/indexes/` as evaluated/deferred. The verify-mode
  `Phase3/reports/Indexing_Report.pdf` (6.4 KiB, < 10 MB per `D3-008`) is the
  P3-G3 deliverable.
- Status: `DONE (Reviewed)` on run 44397831286 and the committed verify-mode PDF;
  no index apply is pending (`D3-011`). The recorded review closes the package.

## WP-P3-06 completion (2026-11-20)

- Spec: `Phase3/docs/14_power_bi_dashboard_spec.md`; approved for build by the
  requester-admin. `D3-012`–`D3-014` are recorded in `Phase3/DECISIONS.md`.
- PBIX file created: `Phase3/deliverables/AeroGrid_Report/AeroGrid.pbix`
- Screenshots PDF created: `Phase3/deliverables/AeroGrid_Report/screenshots.pdf`
- DQ checks verified: `DQ3-A-002` (visuals trace to queries), `DQ3-A-003` (numbers match source queries), `DQ3-A-005` (numbers match cited queries)
- All pages created: executive overview, detailed analysis, decision page
- Review: A (platform) complete 2026-11-21, recorded by Member A; D (performance) pending
- WP-P3-06 is `IN_PROGRESS`; WP-P3-07/08 are `PENDING` pending dashboard evidence

## WP-P3-09 handoff (2026-11-21, Member A)

- Branch: `phase3/wp-p3-09-ci-packaging`. Gate: P3-G5; prerequisite P3-G3 is `DONE`.
  Decision `D3-015` records the packaging rule.
- Assigned tasks (all done by Member A):

| Task | State |
|---|---|
| Release artifact layout (`Phase3/deliverables/`, `Phase3/reports/`) documented | DONE (`deliverables/README.md`, `reports/README.md`) |
| Packaging workflow under the `D3-008` 10 MiB rule | DONE (`package_artifacts.py`, `wp-p3-09-package.yml`; static checks pass; run 44871649279 green on `main`) |
| Release-notes template | DONE (`Phase3/templates/RELEASE_NOTES.md`) |
| Dry-run packaging with the existing files | DONE (`Phase3/evidence/packaging_dryrun_20261121T052507Z.md`, local run, `PASS_WITH_PENDING`) |
| A review of WP-P3-06 (dashboard) | DONE (complete 2026-11-21; recorded by Member A) |

- Files added: `Phase3/scripts/package_artifacts.py`,
  `Phase3/tests/test_package_artifacts.py`,
  `.github/workflows/wp-p3-09-package.yml`, `Phase3/templates/RELEASE_NOTES.md`,
  `Phase3/deliverables/README.md`, `Phase3/reports/README.md`,
  `Phase3/evidence/packaging_dryrun_20261121T052507Z.md` and `.json`.
- Files updated: `.gitignore`, `.github/workflows/README.md`, `Phase3/README.md`,
  `Phase3/PROGRESS.md`, `Phase3/DECISIONS.md`, `Phase3/dev_plan/01_work_breakdown.md`,
  `Phase3/dev_plan/03_deliverables_matrix.md`, `Phase3/docs/00_documentation_map.md`,
  `Phase3/docs/07_operations_access_and_security.md`, `Phase3/evidence/README.md`.
- Behaviour: reads committed files only (no database, no secrets, no `warehouse`
  environment). Each file is routed `bundle` (under 10 MiB) or `oversize` (10 MiB or
  more, never committed). A secret-pattern hit, or an oversized file tracked by Git,
  fails the run. Missing deliverables are reported and fail only with `--strict`.
- Checks: `python -m pytest -q Phase3/tests` -> 71 passed, 1 skipped (local run;
  `psycopg` not installed locally, so one DB-dependent test is skipped);
  `python -m compileall -q Phase3/scripts Phase3/tests` OK; workflow YAML parsed.
- Dry-run result (local, base commit `887fd7e`): `PASS_WITH_PENDING`; present:
  `Indexing_Report.pdf` (6,599 bytes), the analytics and gold-view evidence files;
  missing: PBIX, dashboard screenshots PDF, insights report, final deck,
  `RELEASE_NOTES.md`. No secret hits.
- CI run: [44871649279](https://github.com/HassanNawaz14/AeroGrid/actions/runs/44871649279), workflow `wp-p3-09-package.yml`, manually
  dispatched on `main` at `01a5ccb` by `x-abdullah-saeed-x`, non-strict; job
  `Package artifacts under D3-008` succeeded in 18 s with one artifact,
  `phase3-release-bundle-44871649279` (20.1 KB). No oversize artifact was produced
  (no file is 10 MiB or larger). The packaging record is inside the bundle artifact.
  GitHub reported one non-blocking warning: Node.js 20 is deprecated for
  `actions/checkout@v4`, `actions/setup-python@v5` and `actions/upload-artifact@v4`;
  the other Phase 3 workflows use the same versions.
- Reviews: D and E reviewed WP-P3-09; approval recorded by Member A on 2026-11-21.
- Open: final `--strict` run and `Phase3/RELEASE_NOTES.md` once the BI files exist
  (`H3-009`); WP-P3-10 is human-owned.
- Status: `DONE`. Acceptance met: workflow green on `main`, artifacts packaged per
  `D3-008`, no secret hits in the run, two named reviewers recorded.

## WP-P3-H2 handoff (2026-11-21, Member B)

- Branch: `phase3/wp-p3-h2-member-b`. Track: Hardening; Owner: Member B (`HarveyWebbs` / Abdullah Zia).
- Work package: `WP-P3-H2: FAA ArcGIS Quota Mitigation & Caching`.
- Trigger: Member B's source, licensing, and staging audit identified external ArcGIS rate-limit and quota exhaustion risks during repeated ETL and scheduled runs.
- Decision: `D3-016` recorded in `Phase3/DECISIONS.md`.
- Changes implemented:
  - Added `Phase2/etl/quota_mitigation.py`: `ArcGisCache` (file-backed JSON cache for FeatureServer responses with configurable TTL, stale fallback, and cache management), `BackoffBudget` (exponential backoff with jitter and retry budget), and `QuotaMitigationPolicy`.
  - Updated `Phase2/etl/faa_restrictions.py`: integrated `BackoffBudget` and rate-limit detection in `_http_json` to gracefully handle HTTP 429/503 and ArcGIS error bodies.
  - Updated `Phase2/etl/fetch.py`: enhanced `fetch_airspace_layer` and `fetch_faa_airspace` with caching, stale fallback, and optional-airspace graceful degradation mode (`AEROGRID_OPTIONAL_AIRSPACE=1`).
  - Added `Phase3/tests/test_faa_quota_mitigation.py`: 6 unit tests validating quota error detection, exponential backoff delays, cache hit/miss/TTL/stale behavior, and optional airspace fallback.
  - Added `Phase3/evidence/member_b_source_staging_audit.md`: authoritative audit of Phase 3 source provenance, data dictionary compliance, and zero synthetic data verification.
  - Added `Phase3/evidence/member_b_review_signoffs.md`: formal Member B review records approving WP-P3-00 and WP-P3-04, and defining review framework for WP-P3-07 / WP-P3-08.
- Checks: `python -m pytest Phase3/tests -v` -> 76 passed, 2 skipped; `python -m pytest Phase2/tests/test_faa_restrictions.py Phase2/tests/test_wp11_run.py -v` -> 38 passed.
- Status: `READY_FOR_REVIEW`.

## WP-P3-H1 handoff (2026-11-22, Member A)

- Branch: `phase3/wp-p3-h1-raw-archive`. Track: Hardening; Owner: Member A.
- Decision: `D3-018` (content-addressed raw archive, fail closed on apply).
- Added: `Phase2/etl/raw_archive.py`, `Phase2/etl/verify_raw_archive.py`,
  `Phase3/tests/test_raw_archive.py`.
- Updated: `Phase2/etl/run.py`, `Phase2/etl/config.py`,
  `Phase2/tests/test_wp11_run.py`, `Phase2/etl/README.md`,
  `Phase2/docs/13_accepted_data_limitations.md`,
  `Phase3/docs/05_etl_pipeline.md`, `Phase3/docs/13_accepted_data_limitations.md`,
  `Phase3/DECISIONS.md`, `Phase3/PROGRESS.md`.
- Behaviour: apply mode uploads each fetched file to `aerogrid-raw` under
  `raw/<sha256>/<file_name>` and links it from `source_manifest.object_key` before
  commit; a missing `NEON_S3_*` variable or failed upload rolls the run back.
  Validate mode writes nothing. Uploads are idempotent; existing objects are skipped.
- Checks: `python -m pytest -q Phase3/tests/test_raw_archive.py Phase2/tests/test_wp11_run.py`
  -> 39 passed; full `Phase2/tests Phase3/tests` -> 226 passed; `compileall` on
  `Phase2/etl` and `Phase3/tests`; `git diff --check` clean.
- Open: live proof requires a human-dispatched apply run plus
  `verify_raw_archive.py` (`H3-011`). No new secret is needed.
- Conflict note: Member C's `phase3/wp-p3-h3-member-c` claims `D3-017`/`H3-010` and
  edits the same three shared docs. This package uses `D3-018`/`H3-011`. On merge,
  keep both decision rows and both handoff sections; there is no code-file overlap.
- Status: `READY_FOR_REVIEW`; `DONE` requires `H3-011` evidence and review.

## Human action queue

Stable IDs; agents never simulate these actions.

| ID | Action | Why | Safe path | Status |
|---|---|---|---|---|
| H3-001 | Authorize Phase 3 start (confirm scope: analytics + BI on the existing warehouse) | P3-G1 cannot start without explicit approval | Reply in chat / mark approved in dev_plan | CLOSED 2026-11-18 (authorized) |
| H3-002 | Confirm Power BI Desktop availability for the team (free Desktop; no Service workspace unless a human creates one) | WP-P3-06 deliverable needs a build tool | Install from Microsoft; report back | CLOSED 2026-11-18 (confirmed) |
| H3-003 | Decide who presents the final deck | Presentation delivery is human-owned | Team decision; record in DECISIONS.md | CLOSED 2026-11-18 (whole team presents) |
| H3-004 | Review and sign off WP-P3-02 + WP-P3-03, then close P3-G2 | Owner E cannot self-approve; reviewers C and D must approve | Review the evidence file and SQL, then record approval in this board | CLOSED 2026-11-18 (requester confirmed C/D sign-off; PR #35 merged) |
| H3-005 | Approve WP-P3-04 gold-view apply after a clean rollback verification | Applying views is a shared-warehouse write; CI needs the `warehouse` environment and the `APPROVE_WP3_GOLD_VIEWS` confirmation | Verify passed in run 44295954164; a human dispatches `apply` on `main` with the token and confirms the reader evidence | CLOSED (Applied and verified by admin) |
| H3-006 | Dispatch the WP-P3-05 index measurement (verify mode) | The harness needs the `warehouse` credentials; agents cannot dispatch Actions or read secrets. No measured pair exists yet, so no report can be built | Actions -> **WP-P3-05 indexes (verify or apply)** -> Run workflow -> branch `phase3/wp-p3-05-query-optimization` (or `main` after merge) -> `mode=verify`, no token. Download `wp-p3-05-index-evidence-<run_id>`. Pass: `DQ3-A-006: PASS`, three before/after pairs, `persisted: false`, no index left behind | CLOSED 2026-11-19 (run 44397831286 PASS; three pairs, `persisted: false`) |
| H3-007 | Approve the WP-P3-05 index apply after reviewing the measured pairs | Persisting indexes is a shared-warehouse write; only the protected CI path may apply it | After `H3-006` passes, C/A review the evidence, the PR merges, then Actions -> **WP-P3-05 indexes** -> branch `main` -> `mode=apply`, `confirm=APPROVE_WP3_INDEXES`. Pass: three indexes present, database after < 700 MB, `DQ3-A-006 PASS`. Commit the apply-mode `Indexing_Report.pdf` only if < 10 MB (`D3-008`) | CLOSED 2026-11-19 as not required: all candidates measured NEUTRAL, so the human declined the apply and accepted the verify-mode PDF (`D3-011`) |
| H3-008 | Dispatch the WP-P3-09 packaging workflow (non-strict) after the PR merges | Manual workflows cannot run until the file exists on `main`; the run proves "workflows green on main" and gives the run ID for the review record | Actions -> **WP-P3-09 package Phase 3 artifacts** -> Run workflow -> branch `main`, `strict` off. Pass: tests green, `result` is `PASS` or `PASS_WITH_PENDING`, bundle artifact uploaded, no secret hits | CLOSED 2026-11-21 (run [44871649279](https://github.com/HassanNawaz14/AeroGrid/actions/runs/44871649279) green on `main`, `01a5ccb`; bundle artifact uploaded) |
| H3-009 | Run the final packaging with `strict` on, then write `Phase3/RELEASE_NOTES.md` from the template | Proves every deliverable is present and routed under `D3-008` before the human closes P3-G5 | After P3-G4: dispatch with `strict` on; copy sizes and SHA-256 values from the manifest into the release notes; commit the notes | BLOCKED_ON_HUMAN (waits for WP-P3-06/07/08 files) |
| H3-011 | Dispatch one WP-11 apply run and then run `verify_raw_archive.py` | Proves `L-010` closure with real archived bytes; agents cannot dispatch Actions or read secrets | Actions -> **WP-11 ingestion** -> Run workflow -> `mode=apply`, `confirm=APPROVE_WP11_APPLY` on the merged `main`; then run `python -m etl.verify_raw_archive --evidence Phase3/evidence/raw_archive_<UTC>.md` in the same credentialed job | BLOCKED_ON_HUMAN (waits for merge and human dispatch) |

## Carried-over open items from Phase 2

See `Phase2/PROGRESS.md` for the authoritative Phase 2 board. Phase 3 assumes
Phase 2 limitations `L-001`–`L-010` remain open and must not be "fixed" silently;
the optional hardening track (WP-P3-H1 … H4) owns them through decisions.

## Blockers

- No open P3-G3 blockers. WP-P3-06 is `IN_PROGRESS`; WP-P3-07/08 are `PENDING` pending dashboard evidence and D review.
- WP-P3-09 final `--strict` packaging run (`H3-009`) waits for Member E to commit, or publish as Actions artifacts, the PBIX, dashboard screenshots PDF, insights report and final deck. The 2026-11-21 dry-run found none of these on `main` and reported each as `MISSING`; nothing was created or simulated.
