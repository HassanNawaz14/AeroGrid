# Phase 3 Progress Board

This is the only status board for Phase 3. Decision records live in
[DECISIONS.md](DECISIONS.md); details live in the canonical documents.

## Headline

`PHASE3_P3G3_VERIFY_PASSED_APPLY_PENDING` — documentation baseline merged (PR #31)
and human prerequisites closed by the requester-admin on 2026-11-18 (H3-001
authorized, H3-002 Power BI Desktop confirmed, H3-003 whole team presents).
WP-P3-01 is `DONE`. WP-P3-02 and WP-P3-03 are `DONE`; PR #35 merged as `761475b`
and the requester confirmed the C/D review sign-off on 2026-11-18. P3-G2 is closed
on the recorded evidence: 10 of 10 read-only queries, `aerogrid_reader`,
`DQ3-A-004` `PASS`. WP-P3-04 is `BLOCKED_ON_HUMAN`: the rollback verification
passed (run 44295954164, `DQ3-A-001` `PASS` for all three views), and only the
approved apply plus reader proof (`H3-005`) remains for P3-G3. WP-P3-05
implementation is `IN_PROGRESS` (Member D, 2026-11-19): a rollback-first
`EXPLAIN ANALYZE` harness, three candidate index blocks, a guarded verify/apply
workflow, and the PDF report generator are on
`phase3/wp-p3-05-query-optimization`; measured pairs and the report await the
human-dispatched `H3-006`/`H3-007` runs.

## Gate status

| Gate | Title | State | Evidence |
|---|---|---|---|
| P3-G0 | Documentation baseline | DONE | PR #31 merged (commit `c700ad7`): docs 00–13 + dev_plan; no implementation, no secrets, no raw data |
| P3-G1 | Human prerequisites | DONE | Requester-admin closure 2026-11-18: H3-001 authorized, H3-002 confirmed, H3-003 whole team presents |
| P3-G2 | Analytical SQL + OLAP | DONE | WP-P3-02 + WP-P3-03 evidence: `Phase3/evidence/analytics_run_20261118T110136Z.md` (10/10 queries, `aerogrid_reader`, `DQ3-A-004` PASS); CI run 44290826341; PR #35 merged as `761475b`; C/D review sign-off confirmed 2026-11-18 |
| P3-G3 | Reporting views + optimization | IN_PROGRESS | WP-P3-04 rollback verification PASS (run 44295954164; `Phase3/evidence/gold_views_20261118T113454Z.md`); apply/reader proof pending `H3-005`; WP-P3-05 harness implemented 2026-11-19, measurement pending `H3-006` |
| P3-G4 | Dashboard + insights + presentation | NOT_STARTED | WP-P3-06 … WP-P3-08 |
| P3-G5 | Release | NOT_STARTED | WP-P3-09, WP-P3-10 |

## Work package status

| WP | Title | Owner | Status |
|---|---|---|---|
| WP-P3-00 | Documentation baseline | A | DONE (PR #31, 2026-11-18) |
| WP-P3-01 | Human prerequisites | Human / A | DONE (2026-11-18, requester-admin) |
| WP-P3-02 | Analytical SQL layer | E | DONE (PR #35, `761475b`; evidence `Phase3/evidence/analytics_run_20261118T110136Z.md`) |
| WP-P3-03 | OLAP queries (ROLLUP / CUBE) | E | DONE (PR #35, `761475b`; same paired evidence, `DQ3-A-004` PASS) |
| WP-P3-04 | Phase 3 reporting views | E | BLOCKED_ON_HUMAN (verify PASS 2026-11-18; apply pending H3-005) |
| WP-P3-05 | Query optimization + indexing report | D | IN_PROGRESS (harness implemented 2026-11-19; measurement/apply/report pending H3-006/H3-007) |
| WP-P3-06 | Power BI dashboard | E | NOT_STARTED |
| WP-P3-07 | Business insights report | E | NOT_STARTED |
| WP-P3-08 | Final presentation | E | NOT_STARTED |
| WP-P3-09 | CI packaging + artifacts | A | NOT_STARTED |
| WP-P3-10 | Release + acceptance | Human / A | NOT_STARTED |
| WP-P3-H1 | (Optional) Raw archive closure (`L-010`) | A | NOT_STARTED |
| WP-P3-H2 | (Optional) FAA quota mitigation | B | NOT_STARTED |
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
- Pending: `H3-005` approval for the CI `apply`, then the separate
  `aerogrid_reader` proof; only then is WP-P3-04 ready for C/D review and P3-G3
  closure.
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
- Checks: `python -m pytest -q Phase3/tests` -> 46 passed with the optional
  `pglast` parser installed (45 passed, 1 skipped without it);
  `python -m compileall -q Phase3/scripts Phase3/tests` OK; `pglast` parsed the
  four SQL assets; workflow YAML parsed; `git diff --check` clean. No warehouse
  connection was made; no measured numbers exist yet and none were invented.
- Pending: `H3-006` dispatch of the verify measurement (human/CI), then `H3-007`
  apply approval after review. The committed `Phase3/reports/Indexing_Report.pdf`
  is produced from the apply-mode JSON and committed only if < 10 MB (`D3-008`).
- Next step after `H3-006`: read the evidence JSON, confirm three pairs and
  `DQ3-A-006 PASS`, review whether each measured delta justifies the index, then
  request C/A review and `H3-007`.

## Human action queue

Stable IDs; agents never simulate these actions.

| ID | Action | Why | Safe path | Status |
|---|---|---|---|---|
| H3-001 | Authorize Phase 3 start (confirm scope: analytics + BI on the existing warehouse) | P3-G1 cannot start without explicit approval | Reply in chat / mark approved in dev_plan | CLOSED 2026-11-18 (authorized) |
| H3-002 | Confirm Power BI Desktop availability for the team (free Desktop; no Service workspace unless a human creates one) | WP-P3-06 deliverable needs a build tool | Install from Microsoft; report back | CLOSED 2026-11-18 (confirmed) |
| H3-003 | Decide who presents the final deck | Presentation delivery is human-owned | Team decision; record in DECISIONS.md | CLOSED 2026-11-18 (whole team presents) |
| H3-004 | Review and sign off WP-P3-02 + WP-P3-03, then close P3-G2 | Owner E cannot self-approve; reviewers C and D must approve | Review the evidence file and SQL, then record approval in this board | CLOSED 2026-11-18 (requester confirmed C/D sign-off; PR #35 merged) |
| H3-005 | Approve WP-P3-04 gold-view apply after a clean rollback verification | Applying views is a shared-warehouse write; CI needs the `warehouse` environment and the `APPROVE_WP3_GOLD_VIEWS` confirmation | Verify passed in run 44295954164; a human dispatches `apply` on `main` with the token and confirms the reader evidence | OPEN (verify PASS 2026-11-18; apply pending) |
| H3-006 | Dispatch the WP-P3-05 index measurement (verify mode) | The harness needs the `warehouse` credentials; agents cannot dispatch Actions or read secrets. No measured pair exists yet, so no report can be built | Actions -> **WP-P3-05 indexes (verify or apply)** -> Run workflow -> branch `phase3/wp-p3-05-query-optimization` (or `main` after merge) -> `mode=verify`, no token. Download `wp-p3-05-index-evidence-<run_id>`. Pass: `DQ3-A-006: PASS`, three before/after pairs, `persisted: false`, no index left behind | OPEN |
| H3-007 | Approve the WP-P3-05 index apply after reviewing the measured pairs | Persisting indexes is a shared-warehouse write; only the protected CI path may apply it | After `H3-006` passes, C/A review the evidence, the PR merges, then Actions -> **WP-P3-05 indexes** -> branch `main` -> `mode=apply`, `confirm=APPROVE_WP3_INDEXES`. Pass: three indexes present, database after < 700 MB, `DQ3-A-006 PASS`. Commit the apply-mode `Indexing_Report.pdf` only if < 10 MB (`D3-008`) | OPEN |

## Carried-over open items from Phase 2

See `Phase2/PROGRESS.md` for the authoritative Phase 2 board. Phase 3 assumes
Phase 2 limitations `L-001`–`L-010` remain open and must not be "fixed" silently;
the optional hardening track (WP-P3-H1 … H4) owns them through decisions.

## Blockers

- WP-P3-04 apply and reader proof are blocked on `H3-005`; the rollback
  verification passed and no view has been persisted yet.
- WP-P3-04 final sign-off needs reviewers C/D after apply; owner E cannot
  self-approve.
- WP-P3-05 measurement and apply are blocked on `H3-006`/`H3-007` (human-dispatched
  CI). The harness is implemented and statically tested, but no warehouse
  measurement or `Indexing_Report.pdf` exists yet; do not fabricate one.
- WP-P3-05 final sign-off needs reviewers C/A; owner D cannot self-approve.
