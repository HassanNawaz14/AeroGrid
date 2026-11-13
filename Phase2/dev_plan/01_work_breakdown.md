# Work Breakdown

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](../docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Status summary

| WP | Name | Owner | Reviewer | Status |
|---|---|---|---|---|
| `WP-00` | Documentation and folder baseline | A | B + C | DONE |
| `WP-01` | Human prerequisites and approvals | A | Human | DONE |
| `WP-02` | Platform validation and access proof | A | B + C | DONE |
| `WP-03` | Source validation and georeferencing spike | B | D + E | DONE |
| `WP-04` | Staging DDL and loaders | B | C + D | DONE |
| `WP-05` | Dimensions, keys, and data dictionary | C | A + D | DONE |
| `WP-06` | Tracking and journey facts | D | C + E | DONE (PR #12 `f29b099`; `G4` recorded; `B-011` resolved) |
| `WP-07` | Derived facts | E | C + D | BLOCKED_ON_HUMAN (`H-013`) |
| `WP-08` | Data-quality framework | E | B + D | NOT_STARTED |
| `WP-09` | PDF reports | E | B + A | NOT_STARTED |
| `WP-10` | Reporting views and corridor metrics | E | C + D | NOT_STARTED |
| `WP-11` | CI, access, and deployment | A | B + C | NOT_STARTED |
| `WP-12` | Integration, acceptance, and release | A | B-E | NOT_STARTED |

Member A is HassanNawaz14; Members B-E are recorded in
[`../docs/08_team_work_division.md`](../docs/08_team_work_division.md). `H-002` remains
deferred by the human.

---

## WP-00: Documentation and folder baseline

**Status:** DONE (accepted via `H-001`)
**Owner:** Member A
**Reviewers:** Members B and C
**Prerequisites:** None
**Gate:** G0

### Objective

Create a complete, internally consistent Phase 2 documentation and folder baseline
that the human can review and that agents can follow without inventing scope.

### Scope

- Root and Phase 2 agent contracts.
- Phase 2 dashboard, progress board, and decision log.
- Canonical docs `00`-`12`.
- Development plan and templates.
- Folder README placeholders.
- Updated previous documentation.
- Link and status consistency.

### Out of scope

- SQL, ETL code, workflows, database objects, cloud resources, secrets.
- Any Phase 1 edit.

### Deliverables

- `AGENTS.md`
- `Phase2/AGENTS.md`
- `Phase2/README.md`
- `Phase2/PROGRESS.md`
- `Phase2/DECISIONS.md`
- `Phase2/docs/00` through `12`
- `Phase2/dev_plan/` plan files
- `Phase2/templates/` templates
- Folder READMEs and `.gitignore`
- Updated root README and existing data docs
- Updated DBML or historical pointer
- Phase 1 guide supersession note

### Acceptance evidence

- All links resolve.
- No implementation files or resources exist.
- Status, WPs, gates, sources, model, and actions are consistent.
- Human can identify the exact next action: review and clear `G1`.
- `PROGRESS.md` records files changed and checks run.

### Verification

- Run a relative-link check.
- Search for stale claims such as `synthetic`, `5-minute`, `Docker`, `local PostgreSQL`.
- Confirm Phase 1 files are unmodified.
- Confirm no secrets or raw data.

---

## WP-01: Human prerequisites and approvals

**Status:** DONE (`G1` closed via `H-007`)
**Owner:** Member A (coordinator)
**Reviewer:** Human
**Prerequisites:** WP-00 accepted
**Gate:** G1

### Objective

Obtain the accounts, approvals, resource names, and authorization required before
implementation.

### Scope

- Human reads and approves the baseline.
- Real names replace Members B-E (Member A is HassanNawaz14).
- Neon project and raw bucket created.
- GitHub `warehouse` environment and secrets created.
- Member invitations and read-only access planned.
- Licenses and optional OpenSky terms confirmed.
- Implementation authorization recorded.

### Out of scope

- Agents creating accounts, accepting terms, creating resources, adding secrets, or
  inviting members.

### Deliverables

- Human action queue `H-001` through `H-008` resolved or explicitly deferred (`H-002`).
- `implementation_authorized: YES`.
- G1 approval recorded with approver and date.

### Acceptance evidence

- G1 checklist complete.
- Resource existence confirmed without values.
- Secret names confirmed, not values.
- Member access plan confirmed.
- Human approval recorded in `PROGRESS.md`.

---

## WP-02: Platform validation and access proof

**Status:** DONE (validation run `42276737288` `PASS`, 2026-11-07; PR #3 merged `b6b76b9`; accepted by HassanNawaz14)
**Owner:** Member A
**Reviewers:** Members B and C
**Prerequisites:** WP-01, G1 cleared
**Gate:** G2 input

### Objective

Prove that CI, object storage, and read-only member access work before loading real
data.

### Scope

- Test write connection from CI.
- Test object-storage read/write with a small non-sensitive marker.
- Test read-only role connection.
- Confirm schemas and search path.
- Confirm TLS and connection pooling behavior.
- Record cold-start and timeout behavior.
- Confirm quota warning thresholds.

### Out of scope

- Loading production facts.
- Creating the full schema.
- Sharing credentials in the repository.
- Changing account settings.

### Deliverables

- Access proof notes in `Phase2/PROGRESS.md`.
- Row/object counts from the proof.
- Role permission matrix confirmed.
- CI connectivity evidence.

### Acceptance evidence

- CI can connect and write a scratch object.
- Read-only role can `SELECT` a known object and cannot write.
- No secret is printed.
- Quotas and timeouts are recorded.
- No production data exists.

---

## WP-03: Source validation and georeferencing spike

**Status:** DONE (Member B, Hamid4325; accepted by HassanNawaz14 2026-11-08; PR #5
merged `f9087f4`)
**Owner:** Member B
**Reviewers:** Members D and E
**Prerequisites:** WP-01, G1 cleared
**Gate:** G2 (closed on this package)

### Objective

Validate every required source's schema, license, units, time base, coordinates, and
volume using real samples before building the pipeline.

### Scope

- Tartan sample and georeferencing.
- Nightjar CSV/GeoJSON validation.
- Nominal-io DJI CSV validation.
- FAA layer/geometry validation.
- METAR/IEM validation.
- Optional OpenSky smoke test.
- Capacity estimate.

### Out of scope

- Full raw download beyond the approved load window.
- Synthetic test data.
- Production loads.
- Video/audio ingestion.

### Deliverables

- Completed `SOURCE_VALIDATION.md` records.
- Row counts, sizes, hashes, and sample evidence.
- Georeferencing notes and comparison.
- Unit/time-base mapping.
- Capacity estimate.
- Pass/fail recommendation per source.

### Acceptance evidence

- Each required source is marked PASS with evidence.
- Any FAIL has a documented blocker and human action.
- Tartan coordinates are plausibly inside KBTP.
- Nightjar/DJI time basis and altitude datum are known.
- Full-load estimate is below the approved database budget.
- No raw data is committed.

---

## WP-04: Staging DDL and loaders

**Status:** DONE (Member B, Hamid4325; delegated closeout under `D-023`; PR #7
merged; the sample run used the excluded demo CSV, tracked as `B-011` and closed by
`WP-06`)
**Owner:** Member B
**Reviewers:** Members C and D
**Prerequisites:** WP-03, G2 cleared
**Gate:** G2/G3

### Objective

Create the staging schema and reproducible source-to-staging loaders.

### Scope

- `project_staging` DDL.
- Source manifest, run log, rejects, DQ result.
- Source-shaped staging tables.
- Loaders for approved sources.
- Cleaning, deduplication, unit conversion, rejects.
- Idempotent reruns.

### Out of scope

- Warehouse dimensions/facts.
- Derived metrics.
- Report generation.
- Full production load unless separately authorized.

### Deliverables

- Staging SQL migration(s).
- Loader clients and tests.
- Reject reason catalog.
- Counts and reconciliation.
- Data dictionary staging additions.
- Source manifest evidence.

### Acceptance evidence

- Staging tables accept real samples.
- Exact read/accepted/rejected/duplicate reconciliation.
- Rerun of the same sample creates no duplicates.
- Every reject has a reason and source identifier.
- No raw payload is committed to Git.
- Critical staging checks pass.

### Agent brief (Member B, delegated `D-023`)

Goal: close `WP-04` without human involvement. Stop when `WP-04` is `DONE`; do not
touch `G3` or `WP-05`.

1. Work on a short-lived branch from `main`, for example
   `phase2/wp04-real-sample-evidence`. Never commit raw data or credentials.
2. Produce loader evidence in CI, not on a laptop (all database writes are CI-only):
   - Extract `kbtp/01-01-22/1.csv` from the public Tartan 2022 archive locally and
     confirm its SHA-256 is
     `86342d09e5004102d765b82d04d16b43b6f15f2e7d829bfbde7909187d08a762`.
   - Upload that one file with the Neon console **Object Storage** browser to
     `aerogrid-raw` at `samples/kbtp/01-01-22/1.csv`. Do not use laptop credentials,
     do not commit the file, and do not paste keys anywhere.
   - Extend `wp04-staging-verify.yml` with a download step that copies
     `samples/kbtp/01-01-22/1.csv` to `$RUNNER_TEMP` using the six existing
     `warehouse` secrets (`NEON_S3_*`), runs `sha256sum -c` against the hash above,
     and passes the path to `verify_wp04_staging.py --tartan-sample <path>`.
   - If the storage path is unavailable, use the optional `tartan_sample_path`
     dispatch input instead of committing anything. Keep the 15-minute timeout and
     the rollback-only sample transaction unchanged.
3. Dispatch **Actions → WP-04 staging DDL verify** from the branch. As a `warehouse`
   reviewer under `D-023`, approve your own run.
4. Required log evidence:
   - `preflight: project_staging privileges OK`
   - `pass1: applied 3 SQL files` and `pass2 (idempotency): applied 3 SQL files`
   - a `sample pass1 counts:` line where read = accepted + rejected + duplicate
   - `sample pass2 accepted=0` with duplicates equal to pass1 accepted + duplicate
   - `sample rows rolled back; no test data persisted`
   - `WP-04 verification PASS`
5. Record in `Phase2/PROGRESS.md`: run link and counts in the `WP-04` row, one handoff
   row, and one change-log row. Touching `Phase2/docs/05_etl_pipeline.md` is only
   needed if the verification path changes.
6. Run `python -m pytest -q Phase2/tests` (expect 38), `python -m compileall -q
   Phase2/etl`, and `git diff --check`. Open the PR, get one approval from Member C or
   D, then merge.
7. Mark `WP-04` `DONE` in `PROGRESS.md` (allowed by `D-023`) and leave `G3`
   `IN_PROGRESS`. The human records `G3` after `WP-05` is also `DONE`.

If a step needs a human-only action, set `BLOCKED_ON_HUMAN`, add an `H-###` row, and
stop. Do not change repository or environment settings and do not run loaders from a
laptop.

---

## WP-05: Dimensions, keys, and data dictionary

**Status:** DONE (Member C; delegated closeout under `D-023`; all dimension DDL,
seeds, verifier, workflow, data dictionary, DBML, and tests implemented; Neon DB
verifier PASS recorded 2026-11-08; PR #8 merged and `G3` recorded 2026-11-09)
**Owner:** Member C
**Reviewers:** Members A and D (Member D acts during the delegated window)
**Prerequisites:** WP-02, model approved
**Gate:** `D-022` start; `G3` acceptance

### Objective

Create the six dimensions, surrogate keys, unknown members, constraints, and
authoritative data dictionary.

### Scope

- `project_dw` schema and dimensions.
- `dim_time`, `dim_site`, `dim_vehicle`, `dim_spatial_grid`, `dim_weather`,
  `dim_airspace_zone`.
- Identity surrogate keys.
- `-1` unknown member seeding.
- Natural-key uniqueness.
- FK/index design for facts.
- Data dictionary and DBML consistency.

### Out of scope

- Fact loading.
- Derived metrics.
- Reporting views.
- Guessing identities or sites.

### Deliverables

- Dimension DDL and seed SQL.
- Data dictionary.
- Updated DBML.
- Dimension row counts.
- Key-map/reconciliation query.
- Model review notes.

### Acceptance evidence

- All six dimensions exist with PK/FK/unique constraints.
- Unknown member exists in every dimension.
- Dimension row count is at least 100 using real data.
- Data dictionary matches DDL.
- DBML matches DDL.
- No orphan or duplicate natural keys.

### Agent brief (Member C, delegated `D-023`)

Goal: implement and close `WP-05` without human involvement. Do not modify staging,
facts, or reporting objects.

1. Branch from `main`, for example `phase2/wp05-dimensions`.
2. Add `Phase2/sql/02_dimensions/*.sql`: the six dimensions, identity surrogate keys,
   `-1` unknown members, natural-key uniqueness, FK/index design for facts, and seeds.
   Keep every file idempotent (`IF NOT EXISTS`, `ON CONFLICT DO NOTHING`).
3. Grant path: tables created by `aerogrid_etl` belong to `aerogrid_etl`, and
   `neondb_owner` cannot grant on another role's tables. Run
   `Phase2/sql/00_schemas.sql` in the same ETL connection as your DDL (it grants the
   reader `SELECT` on existing ETL-owned tables and sets defaults for later ones), or
   issue the equivalent `GRANT SELECT ... TO aerogrid_reader` in your own bootstrap.
   Never run `00_grants.sql`; it is owner-only.
4. Add a verifier and workflow modelled on WP-04: `environment: warehouse`,
   `DATABASE_URL` from secrets, 15-minute timeout, DDL applied twice for idempotency.
   Assert the six tables exist, each has a `-1` row, no duplicate natural keys, FK
   targets exist, and reader access holds in CI:
   `SELECT NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid =
   c.relnamespace WHERE n.nspname = 'project_dw' AND c.relkind IN ('r','p') AND NOT
   has_table_privilege('aerogrid_reader', c.oid, 'SELECT'))` must return `true`.
5. Seed from approved real sources only (WP-03 findings). No invented sites, vehicles,
   zones, or weather rows. Unresolved DJI site mapping stays null and maps to `-1`.
   The 100-row floor can come from a deterministic hourly `dim_time` spine over the
   accepted 2022-01-01 to 2022-01-07 load window, the FAA airspace features, and the
   spatial grid; those are derived, not synthetic source records.
6. Update `data/data_dictionary.md` and the DBML so they match the DDL exactly, and add
   pytest coverage for key normalisation and seed logic.
7. Dispatch the workflow from your branch and approve your own `warehouse` run as a
   reviewer under `D-023`.
8. Record in `Phase2/PROGRESS.md`: run link, table and seed counts, idempotency and
   reader-check results, one handoff row, and one change-log row. Run
   `python -m pytest -q Phase2/tests`, `git diff --check`, open the PR, get one approval
   from Member D, then merge.
9. Mark `WP-05` `DONE` (allowed by `D-023`); `G3` was then recorded `DONE` on
   2026-11-09 on the human's explicit instruction, with `B-011` open.

If a step needs a human-only action, set `BLOCKED_ON_HUMAN`, add an `H-###` row, and
stop. Do not change repository or environment settings.

---

## WP-06: Tracking and journey facts

**Status:** DONE 2026-11-11 (PR #12 `f29b099`; `G4` recorded; `B-011` resolved)
**Owner:** Member D
**Reviewers:** Members C and E
**Prerequisites:** WP-04, WP-05
**Gate:** G4 (recorded 2026-11-11)

The `WP-06` agent briefs below are historical; the package is closed. The real
Tartan sample was loaded and WP-05 run `42689267328` and WP-06 run `42887782411`
passed on `phase2/wp06-tracking-facts` at `ecce8ec`.

### Objective

Load the two core movement facts from real tracking data with correct keys and grain.

### Scope

- `fact_vehicle_tracking`.
- `fact_flight_journey`.
- Natural-key-to-surrogate mapping.
- Exact timestamps and hourly time key.
- Journey segmentation.
- Idempotent loads.
- Reconciliation and tests.

### Out of scope

- Close encounters, occupancy, restrictions.
- Reporting views.
- Synthetic tracks or journeys.

### Deliverables

- Fact DDL and loaders.
- Journey algorithm and version.
- Tracking/journey counts.
- Reconciliation evidence.
- Tests for duplicates, gaps, and endpoint handling.

### Acceptance evidence

- Facts total at least 10,000 rows.
- Tracking uniqueness holds.
- Journey grain is documented and valid.
- Rerun creates no duplicates.
- Orphans are zero.
- Tracking facts reconcile to accepted staging.
- All timestamps and units are documented.

### Agent brief (Member C: dimension members and `G4` recording, delegated `D-024`)

Do this first; Member D's fact mapping depends on it. Goal: real dimension members for
key mapping, then verify Member D's load and record `G4`. Do not start `WP-07`.

1. Branch from `main`, for example `phase2/wp06-dimension-members`.
2. Use the same real Tartan artifact as Member D: `kbtp/01-01-22/1.csv` from the public
   2022 archive (`Phase2/docs/source_validation/SRC-TARTAN.md`), SHA-256
   `86342d09e5004102d765b82d04d16b43b6f15f2e7d829bfbde7909187d08a762`. Confirm the
   hash, upload that one file with the Neon console Object Storage browser to
   `aerogrid-raw` at `samples/kbtp/01-01-22/1.csv`, and tell Member D the object key.
   Never commit raw data and never load from `data/sample/` (`D-017`).
3. Add `Phase2/sql/02_dimensions/03_seed_real.sql` (idempotent, no deletes):
   - `dim_vehicle`: one row per distinct real `icao24` in the sample with
     `source_system='tartan'`, `source_entity_id=icao24`, and first/last seen
     timestamps taken from the real rows.
   - `dim_spatial_grid`: real cells covering the sample bounding box if you implement
     the model grid; otherwise document that facts use `-1` for grid.
   - Do not invent weather rows; `dim_weather` stays `-1` until real METAR rows are
     loaded. Keep every `-1` member and all natural-key uniqueness.
4. Extend the WP-05 verifier (or add `verify_wp06_dimensions.py`) to assert: real
   vehicle rows > 0, no duplicate natural keys, FK targets exist, and reader `SELECT`
   is true for every `project_dw` table. Run it through the `warehouse` workflow; keep
   writes CI-only.
5. Record the run link and vehicle count in `Phase2/PROGRESS.md`, open the PR, get one
   peer approval (Member D or B), and merge. Then tell Member D the dimension members
   are live.
6. After Member D closes `WP-06`, dispatch `wp06-facts-verify.yml` from `main` (it is
   dispatchable once merged) and verify `G4` against Neon: fact counts, tracking
   reconciliation to accepted staging, journey grain, duplicate and orphan checks, and
   the idempotent rerun. Record `G4` `DONE` in `PROGRESS.md` with the run link and
   results. This is the only gate recording allowed under `D-024`; later gates stay
   human.

### Agent brief (Member D, delegated `D-024`)

Goal: close `WP-06` with real facts. Start the staging load and fact code while Member C
lands the dimension members, but run the acceptance load only after those members
merge.

1. Branch from `main` after Member C's dimension PR, for example
   `phase2/wp06-tracking-facts`.
2. Source the same real object `samples/kbtp/01-01-22/1.csv` (SHA-256 above) from
   `aerogrid-raw` through the workflow's `NEON_S3_*` secrets. Do not use the legacy
   demo CSV or any other synthetic file.
3. Add `Phase2/sql/03_facts/01_facts.sql` with `fact_vehicle_tracking` and
   `fact_flight_journey` per [`docs/04_data_model.md`](../docs/04_data_model.md#fact-overview):
   identity surrogate PKs, FKs to the six dimensions, source-scoped uniqueness, and
   indexes on event/start/end time and the key columns. Keep it idempotent.
4. Add `Phase2/etl/facts.py`: insert only accepted staging rows; map keys through
   `dim_vehicle` (`source_system='tartan'`, entity `icao24`), the KBTP `dim_site`, and
   `dim_time` from the exact `event_ts`; use `-1` for grid and weather only when no
   real match exists. Segment journeys per vehicle by `event_ts` with a documented gap
   split (record the gap in seconds, `segment_reason`, and `algorithm_version`) and
   derive journey metrics from real rows only.
5. Add `Phase2/etl/verify_wp06_facts.py` and `wp06-facts-verify.yml`
   (`workflow_dispatch`, `environment: warehouse`, 15-minute timeout, `DATABASE_URL`
   secret). It must apply the DDL twice, load the real sample twice, and assert:
   accepted staging rows > 0, both facts exist, total facts >= 10,000, the rerun inserts
   no duplicate tracking or journey rows, zero orphans, and tracking counts equal
   accepted staging rows for the load window. Print counts only.
   - GitHub only offers a manual dispatch for a workflow that already exists on `main`.
     For the first runs, add a temporary `push` trigger scoped to your feature branch
     (the pattern `WP-02` used), dispatch or push to run it, then remove the `push`
     trigger before the PR merges. After the merge, Member C re-runs it from `main`.
6. Persist the acceptance load so members can read the facts, and keep the rerun
   idempotent. If you first run a rolled-back dry run, follow it with the persistent
   load and record both.
7. Dispatch the workflow; Member C (or B) approves the `warehouse` run because you are
   not an environment reviewer. If real rows are still rejected, inspect `stg_reject`
   reasons and fix the mapping; never lower the checks or drop rows silently.
8. Record in `Phase2/PROGRESS.md`: run link, accepted staging rows, fact counts,
   reconciliation, duplicate/orphan results, idempotency, journey grain and gap
   parameter, and close `B-011`. Run `python -m pytest -q Phase2/tests` and
   `git diff --check`, open the PR, get one peer approval (Member C or E), and merge.
9. Mark `WP-06` `DONE` and ask Member C to record `G4`. Do not start `WP-07`; it needs
   approved thresholds.

If a step needs a human-only action, set `BLOCKED_ON_HUMAN`, add an `H-###` row, and
stop. Do not change repository or environment settings, and do not run loaders from a
laptop.

---

## WP-07: Derived facts

**Status:** DONE — requester-admin accepted 2026-11-13; technical caveats in final gate record
**Owner:** Member E
**Reviewers:** Members C and D
**Prerequisites:** WP-06 (DONE), `H-013` approved
**Gate:** G5

**Start condition:** `G4` is recorded. The human must approve `H-013` before any
derived-fact code or data work starts. Candidate thresholds in
[`../docs/04_data_model.md`](../docs/04_data_model.md): severe encounter
horizontal `< 0.5 nm` and vertical `< 500 ft`; proximity horizontal `< 1.0 nm` and
vertical `< 1,000 ft`. Candidate `algorithm_version`: `wp07-v1` (proposed; the human
confirms or amends it in `H-013`). Occupancy is computed once per grid/hour from real
airborne tracking positions, not per query.

### Objective

Build the derived facts from real tracking rows with approved, versioned algorithms.

### Scope

- `fact_close_encounter`.
- `fact_airspace_occupancy`.
- `fact_restriction_activation`.
- Thresholds and algorithm versioning.
- Tests and evidence.

### Out of scope

- Fabricating encounters to reach a count.
- Reporting views.
- Final PDFs.

### Deliverables

- Derived-fact DDL and loaders.
- Algorithm documentation.
- Threshold decision record.
- Counts and sample evidence.
- Reconciliation to tracking.

### Acceptance evidence

- Every derived row traces to real tracking/restriction evidence.
- Thresholds are approved and unchanged after results review.
- Encounter vehicles are distinct and same-site/time.
- Occupancy uniqueness holds.
- Restriction activation has a real window/snapshot.
- No synthetic derived rows.
- Tests pass.

---

## WP-08: Data-quality framework

**Status:** DONE — requester-admin accepted 2026-11-13; technical caveats in final gate record
**Owner:** Member E
**Reviewers:** Members B and D
**Prerequisites:** WP-04 through WP-07
**Gate:** G6 input

### Objective

Implement the check catalog, persist results, and make critical failures block trusted
publication.

### Scope

- `dq_result` writes.
- Completeness, uniqueness, accuracy, integrity, reconciliation, timeliness,
  business-rule checks.
- Severity and CI behavior.
- Evidence queries.

### Out of scope

- Changing thresholds to make a run pass.
- Hiding failures.
- Report design.

### Deliverables

- DQ SQL/Python.
- Check catalog with IDs.
- Stored results from a real run.
- Failure-path test.
- Evidence for the report.

### Acceptance evidence

- Every run stores pass/fail results.
- Critical failures fail the run.
- Orphan and duplicate checks are zero on a valid run.
- Reconciliation is exact or explicitly explained.
- A deliberate failure is detected in a test.
- No synthetic data used to pass.

---

## WP-09: PDF reports

**Status:** DONE — requester-admin accepted 2026-11-13; technical caveats in final gate record
**Owner:** Member E
**Reviewers:** Members B and A
**Prerequisites:** WP-08
**Gate:** G6

### Objective

Generate the required Data Cleaning and Data Quality PDFs from stored evidence.

### Scope

- `Data_Cleaning_Report.pdf`.
- `Data_Quality_Report.pdf`.
- Run metadata, counts, rules, rejects, DQ table, capacity, limitations,
  attribution.
- Reproducible generation.

### Out of scope

- Writing unverifiable claims.
- Omitting critical failures.
- Embedding secrets or raw personal data.

### Deliverables

- PDF files in `Phase2/reports/`.
- Report source/template.
- Stored data backing each claim.
- Screenshot/verification of PDF readability.

### Acceptance evidence

- Both PDFs exist and open.
- Counts match the database.
- Critical failures are visible.
- Source licenses/attribution appear.
- "No synthetic data" statement is supported.
- Report can be regenerated from stored evidence.

---

## WP-10: Reporting views and corridor metrics

**Status:** DONE — requester-admin accepted 2026-11-13; technical caveats in final gate record
**Owner:** Member E
**Reviewers:** Members C and D
**Prerequisites:** WP-06, WP-07
**Gate:** G6

### Objective

Create stable `project_reporting` views that answer the Phase 2 analytics and corridor
questions.

### Scope

- Ten planned views.
- Density, occupancy, encounters, restrictions, weather, corridors.
- Grain/documentation for each view.
- Query performance review.

### Out of scope

- New facts not authorized.
- Synthetic corridor recommendations.
- Paid visualization tools.

### Deliverables

- `project_reporting` DDL/views.
- View catalog with grain and use.
- Example read-only queries.
- Performance evidence.

### Acceptance evidence

- All required views exist.
- Each view returns real data for the chosen period.
- Read-only role can select them.
- No row multiplication from role-playing joins.
- Corridor metrics state their assumptions.
- View definitions are documented.

---

## WP-11: CI, access, and deployment

**Status:** NOT_STARTED
**Owner:** Member A
**Reviewers:** Members B and C
**Prerequisites:** WP-01, WP-02, WP-04 through WP-10
**Gate:** G6/G7

### Objective

Automate weekly/manual execution and enforce critical DQ without local credentials.

### Scope

- GitHub Actions workflows.
- Environment secret references.
- Weekly schedule and manual dispatch.
- Concurrency and timeout.
- Report artifacts.
- Read-only access test.
- Run summary.
- Accepted-limitation regression checks (`L-001`–`L-009`) surfaced from the DQ results.
- Source-coverage guards (`DQ-G-001`–`DQ-G-004`) that separate "no data loaded" from a measured zero.

### Out of scope

- Five-minute polling.
- Secrets in repository files.
- Local database.
- Auto-upgrading paid plans.

### Deliverables

- Workflow YAML.
- CI check workflow.
- Access proof.
- Runbook update.
- Artifact links.
- Limitation audit lines in the run summary.

### Acceptance evidence

- Manual run succeeds on a controlled real window.
- Scheduled cadence is weekly, not minutes.
- Critical DQ fails the job.
- Reports upload as artifacts.
- No secret appears in logs.
- Read-only role cannot write.
- Run summary has counts.
- Run summary reports each open `L-###` limitation with its linked DQ status.
- Run summary reports per-source coverage, marking any approved source with zero accepted rows as "no data loaded".

---

## WP-12: Integration, acceptance, and release

**Status:** NOT_STARTED
**Owner:** Member A
**Reviewers:** Members B-E
**Prerequisites:** WP-02 through WP-11
**Gate:** G7

### Objective

Prove the full Phase 2 deliverable is integrated, reproducible, documented, and ready
for submission/demo.

### Scope

- End-to-end run.
- Rubric audit.
- Report audit.
- Access audit.
- Documentation and link audit.
- Accepted-limitation audit against [docs/13_accepted_data_limitations.md](../docs/13_accepted_data_limitations.md).
- Demo script.
- Final status.

### Out of scope

- Late scope additions.
- Destructive cleanup.
- Unapproved source changes.

### Deliverables

- Final acceptance checklist.
- Reproducible run evidence.
- Final PDFs.
- Demo script.
- Repository link.
- Limitation audit appendix.
- Updated `PROGRESS.md` and decisions.

### Acceptance evidence

- All rubric items have evidence.
- 100+ dimension rows and 10,000+ fact rows are demonstrated.
- Both PDFs are final.
- Read-only access works for members.
- No critical DQ failures.
- No secrets/raw data in Git.
- A fresh authorized run reproduces the result.
- Every open `L-###` limitation is reported with its observed value, trigger status, and owner.
- Human accepts the release.
