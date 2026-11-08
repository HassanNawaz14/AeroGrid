# Phase 2 Progress and Handoff Board

This is the canonical status board for AeroGrid Phase 2. Every agent and human must
read it before acting. Update it at the end of every work session.

| Field | Value |
|---|---|
| Last updated | `2026-11-08` |
| Phase state | `G2_DONE_WP-03_DONE_WP-04_BLOCKED_ON_HUMAN_WP-05_READY` |
| Implementation authorized | `YES` (`H-007`, 2026-11-04) |
| Current gate | `G3 - Staging and dimensional schema` |
| Current gate status | `IN_PROGRESS (WP-05 READY; WP-04 DDL applied on Neon, real-sample evidence pending)` |
| Active work package | `WP-05` dimensions and keys (Member C) |
| Active work package status | `READY` (`D-022` start condition met: `WP-03`/`WP-04` merged as `f9087f4`) |
| Next work package | `WP-06` tracking and journey facts (after `G3`) |
| Next action owner | Member C starts `WP-05`; human reruns `Phase2/sql/00_grants.sql` and Member B produces real-sample loader evidence (`H-011`); HassanNawaz14 records `G3` after `WP-04`/`WP-05` acceptance |

## Status vocabulary

| Status | Meaning |
|---|---|
| `NOT_STARTED` | No work has begun. |
| `READY` | Dependencies and gates are satisfied. |
| `IN_PROGRESS` | An authorized owner is actively working. |
| `BLOCKED` | A technical or dependency issue prevents progress. |
| `BLOCKED_ON_HUMAN` | A human-only action is required. |
| `READY_FOR_REVIEW` | Work and evidence are complete; review pending. |
| `DONE` | Accepted against the work package acceptance criteria. |
| `CANCELLED` | Human-approved removal from scope. |

Agents must not mark a package `DONE`. They may set `READY_FOR_REVIEW` and provide
evidence. The human or the accountable owner with explicit human confirmation closes
the package.

## Gate status

Gate definitions are canonical in
[`dev_plan/02_dependencies_and_gates.md`](dev_plan/02_dependencies_and_gates.md).

| Gate | Exit criterion | Status | Owner |
|---|---|---|---|
| `G0` | Documentation, plan, and folder baseline exist and links are valid | `DONE` | HassanNawaz14 |
| `G1` | Human approvals, named owners, Neon/GitHub access, and secrets ready | `DONE` (`H-007`; `H-002` deferred) | HassanNawaz14 |
| `G2` | Platform access and source validation spikes pass | `DONE` 2026-11-08 (`WP-02` and `WP-03` accepted; PR #5 merged as `f9087f4`) | HassanNawaz14 / Member B |
| `G3` | Staging, physical schema, constraints, indexes, keys, and seeds validated | `IN_PROGRESS` (`WP-05` `READY`; `WP-04` blocked on `H-011`) | Members B/C |
| `G4` | Core tracking and journey facts loaded and reconciled | `NOT_STARTED` | Member D |
| `G5` | Derived facts and approved thresholds validated | `NOT_STARTED` | Member E |
| `G6` | DQ, reports, reporting views, and automation validated | `NOT_STARTED` | Member E / HassanNawaz14 |
| `G7` | A clean end-to-end run and team read access are demonstrated | `NOT_STARTED` | HassanNawaz14 |

`G0`, `G1`, and `G2` are closed. `G0` was accepted via `H-001`; `G1` was closed and implementation authorized via `H-007` on 2026-11-04; `G2` was accepted by HassanNawaz14 on 2026-11-08 after `WP-03` review and PR #5 merge. The next gate is `G3`.

## Work package status

| WP | Title | Owner | Depends on | Status | Next action |
|---|---|---|---|---|---|
| `WP-00` | Documentation and folder baseline | HassanNawaz14 | none | `DONE` | Accepted via `H-001` |
| `WP-01` | Human prerequisites and shared platform | HassanNawaz14 | `WP-00` | `DONE` | G1 cleared; proceed with WP-02 and WP-03. |
| `WP-02` | Platform validation and access proof | HassanNawaz14 | `WP-01` | `DONE` | Accepted 2026-11-07 by HassanNawaz14; run [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288) `PASS`; PR #3 merged as `b6b76b9` |
| `WP-03` | Source validation and georeferencing | Member B (Hamid4325) | `WP-01` | `DONE` | Accepted 2026-11-08 by HassanNawaz14 after review; PR #5 merged as `f9087f4`. Tartan, Nightjar, nominal-io DJI, FAA facility/TFR plus granular airspace (`D-020`), and METAR/AWC/IEM are validated; capacity estimate recorded; temp raw samples removed. `G2` closed on this evidence. |
| `WP-04` | Staging DDL and loaders | Member B (Hamid4325) | `WP-03` | `BLOCKED_ON_HUMAN` | Code merged (`f9087f4`); 38 local tests pass. DDL evidence recorded 2026-11-08: run [42474788058](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42474788058) applied the three SQL files twice as `aerogrid_etl` and created 11 empty `project_staging` tables. Remaining on `H-011`: rerun `00_grants.sql` so the reader can read those tables, then a real Tartan sample load/rerun for reconciliation and idempotency evidence. |
| `WP-05` | Dimensions, keys, and dictionary | Member C | `WP-02`, model approval | `READY` | `D-022` start condition met (`WP-03`/`WP-04` merged). Member C starts dimension DDL, keys, and the data dictionary; acceptance is recorded at `G3`. |
| `WP-06` | Tracking and journey facts | Member D | `WP-04`, `WP-05` | `NOT_STARTED` | Wait for `G3` |
| `WP-07` | Derived facts | Member E | `WP-06` | `NOT_STARTED` | Wait for `G4` and threshold approval |
| `WP-08` | Data-quality framework | Member E | `WP-04` to `WP-07` | `NOT_STARTED` | Wait for derived facts |
| `WP-09` | PDF reports | Member E | `WP-08` | `NOT_STARTED` | Wait for DQ results |
| `WP-10` | Reporting views and corridor metrics | Member E | `WP-06`, `WP-07` | `NOT_STARTED` | Wait for core/derived facts |
| `WP-11` | CI, access, and deployment | HassanNawaz14 | `WP-02`, `WP-04` to `WP-10` | `NOT_STARTED` | Wait for work packages |
| `WP-12` | Integration, acceptance, and release | HassanNawaz14 + all | `WP-11` | `NOT_STARTED` | Final gate |

## Human action queue

| ID | Action | Why it is needed | Safe path | Status |
|---|---|---|---|---|
| `H-001` | Review and approve the documentation baseline, `G0`, and proposed decisions | Confirms scope, model, sources, and plan | Reviewed and accepted by HassanNawaz14 (`D-001` through `D-014` accepted) | `DONE` |
| `H-002` | Assign real names to Members B-E | Work packages need accountable owners | Names are recorded in [docs/08_team_work_division.md](docs/08_team_work_division.md): Hamid4325 (B), HarveyWebbs (C), ahmadazad-dev (D), x-abdullah-saeed-x (E). Formal closure remains deferred by HassanNawaz14; this does not block `WP-02`/`WP-03`. | `BLOCKED` (deferred) |
| `H-003` | Create the Neon project, database, and object-storage bucket | The shared warehouse and raw archive are human-owned resources | Recorded in the Neon resource record: project `AeroGrid-DW`, branch `production`, database `neondb`, bucket `aerogrid-raw`, ETL role `aerogrid_etl` | `DONE` |
| `H-004` | Add GitHub environment secrets for the warehouse | CI cannot connect to Neon without secrets | `warehouse` environment created and the six required secrets added; values not recorded | `DONE` |
| `H-005` | Invite the other members and create read-only access | All five members must read the shared warehouse | Invitations sent; `aerogrid_reader` role and read-only plan recorded; HassanNawaz14 confirmed the role exists on 2026-11-06. Recurring member grants are in `Phase2/sql/00_grants.sql` (`H-011`). | `DONE` |
| `H-006` | Confirm data licenses, attribution, and optional OpenSky access | Redistribution and source-use terms must be confirmed | Confirmed data licenses, attribution requirements, and optional OpenSky access (`D-011`, `D-012`, `D-013`, `docs/03_data_sources_and_licensing.md`) | `DONE` |
| `H-007` | Explicitly authorize Phase 2 implementation | Opens the implementation phase | **DONE 2026-11-04** — Authorized implementation; G1 closed; WP-02/WP-03 assigned | `DONE` |
| `H-008` | Confirm handling of the tracked legacy synthetic samples under `data/sample/` | Prevents synthetic demo files from being mistaken for real Phase 2 data | HassanNawaz14 confirmed the five files are intentionally retained as demo-only artifacts for offline user/evaluator viewing; excluded from all Phase 2 loads and reports; `D-017` | `DONE` |
| `H-009` | Run the `WP-02` validation workflow and confirm read-only access | The probe needs the `warehouse` secrets, and the read-only connection string is member-only | Runs [42266493857](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42266493857) and [42272052476](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42272052476) are done. `aerogrid_reader` was replaced on 2026-11-07 (console delete, SQL recreate, password reset, secret updated). Final run [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288) `PASS`: 22 pass, 1 warn, 0 fail, 0 skip; every negative reader check rejected with SQLSTATE `42501`. | `DONE` |
| `H-010` | Confirm the FAA Airspace source license/provenance or approve a replacement | The `Airspace` ArcGIS item is titled `Airspace (DEMO)` and has no `licenseInfo` or `accessInformation`; loading it without confirmation risks an unapproved source | Human approved the granular FAA services (`Class_Airspace`, `Special_Use_Airspace`, `Route_Airspace`) on 2026-11-07; `D-020` records the decision and the DEMO layer is excluded. | `DONE` |
| `H-011` | Apply `Phase2/sql/00_grants.sql` as `neondb_owner` | WP-04 DDL verify connected as `aerogrid_etl` to `neondb` but failed with `InsufficientPrivilege: permission denied for schema project_staging` on `CREATE TABLE IF NOT EXISTS project_staging.source_manifest` (2026-11-07, Member B local run of `Phase2/etl/verify_wp04_staging.py`; no secrets recorded). The same gap would block every later schema and every member read. | Human ran `Phase2/sql/00_grants.sql` as `neondb_owner` on 2026-11-08: all 13 self-check rows returned `true`. WP-04 DDL verify run [42474788058](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42474788058) then applied the staging DDL twice as `aerogrid_etl` with no privilege error and created the 11 expected tables. Remaining: (1) have `aerogrid_etl` grant `SELECT` on the 10 staging tables it owns — the updated self-check returned `false` for `reader can select every existing table` because `neondb_owner` cannot grant on another role's tables (verified 2026-11-08: all 10 tables `owner=aerogrid_etl`, `reader_select=false`; only the owner-created `wp02_read_probe` was readable); `00_schemas.sql` now grants these on every ETL run; (2) rerun `00_grants.sql` to confirm all 15 rows; (3) produce real-sample loader/idempotency evidence. | `BLOCKED_ON_HUMAN` |
| `H-012` | Confirm the authoritative start gate for `WP-05` | `PROGRESS.md` and `dev_plan/01_work_breakdown.md` said `WP-05` waits for `G3`, but `dev_plan/02_dependencies_and_gates.md` said `G2`; `G3` itself requires `WP-05`, so the records could not all be correct. Starting Member C work without a decision would violate the gate rules. | Human decided on 2026-11-08: do not start `WP-05` until `WP-03` and `WP-04` are merged; `D-022` records the rule and `G3` remains the acceptance gate after both packages. | `DONE` |

`H-002` remains `BLOCKED` until Members B-E choose roles and provide real names.
`H-008` is resolved by `D-017`; the legacy samples are retained as demo-only artifacts
and are never loaded into Phase 2.

No human action may be simulated, inferred, or performed by an agent.

## G1 execution checklist

`H-002` remains blocked; `H-003` is done; `H-008` is resolved by `D-017`. Detailed
canonical steps for the Neon setup are also in
[docs/10_human_operating_manual.md](docs/10_human_operating_manual.md).

| ID | G1 action | Exact steps | Status / done when |
|---|---|---|---|
| `H-003` | Create the Neon project, database, and private object-storage bucket | Sign in to the Neon Console; create a project named `AeroGrid-DW` in `aws-us-east-2`; keep Postgres enabled and enable Object storage under Services; use the default `neondb` database or add a dedicated database; open the `production` branch's Object storage tab and create a private bucket named `aerogrid-raw`; record project ID, branch ID, region, database name, bucket name, and storage endpoint (never passwords or keys). | **DONE 2026-11-04** — recorded in the Neon resource record |
| `H-004` | Configure the GitHub `warehouse` environment and secrets | Confirm the repo is public (or accept the private-repo Actions budget); create the `warehouse` environment; add `DATABASE_URL` from the `aerogrid_etl` role (not `neondb_owner`), `NEON_S3_ENDPOINT`, `NEON_S3_REGION` (`us-east-2`), `NEON_S3_BUCKET` (`aerogrid-raw`), `NEON_S3_ACCESS_KEY_ID`, `NEON_S3_SECRET_ACCESS_KEY`; optional `OPENSKY_CLIENT_ID`, `OPENSKY_CLIENT_SECRET`, `SOURCE_TIMEZONE`, `REPORT_PUBLISH_MODE`; enable required reviewers if available; never paste values into chat or repository files. | **DONE 2026-11-04** — environment and six required secrets confirmed |
| `H-005` | Invite members and establish read-only access | Invite Members B-E to the Neon organization and GitHub as needed; create `aerogrid_reader`; grant `CONNECT`, `USAGE`, and `SELECT` after the schema/views exist; test one `SELECT` per reporting view; share the read-only connection string privately. At `G1`, invitations sent plus a recorded read-only plan is sufficient; actual grants follow `WP-04`/`WP-05`/`WP-10`. | **DONE 2026-11-04** — invitations sent; `aerogrid_reader` confirmed to exist 2026-11-06; grants follow `WP-04`/`WP-05`/`WP-10` |
| `H-006` | Confirm licenses, attribution, and optional OpenSky access | Review [docs/03_data_sources_and_licensing.md](docs/03_data_sources_and_licensing.md); confirm Tartan (CC BY 4.0), Nightjar (CC BY 4.0), nominal-io DJI (MIT), FAA/NOAA open data, and IEM terms; confirm or explicitly defer OpenSky; record the decision. | **DONE 2026-11-04** — licenses and OpenSky terms confirmed (`D-011`, `D-012`, `D-013`) |
| `H-007` | Explicitly authorize Phase 2 implementation | Confirm `H-002` to `H-006` are resolved (`H-008` is resolved by `D-017`); set `implementation_authorized: YES`; mark `G1` `DONE` with date and approver; record the authorization scope; assign `WP-02` and `WP-03`. | `G1` `DONE`; `WP-02`/`WP-03` assigned |
| `G-01` | Protect `main` and confirm repository settings | Settings > Branches: require pull requests, one approval, status checks when workflows exist, and disallow direct pushes; confirm the `warehouse` environment reviewers; confirm repository visibility. | **DONE 2026-11-04** — confirmed by HassanNawaz14 |
| `G-02` | Confirm schedule and report parameters | Choose the weekly cron time (for example Monday 06:00 UTC); confirm manual dispatch inputs (`start_date`, `end_date`, `publish_reports`, `sites`); choose `REPORT_PUBLISH_MODE` (`artifact` or `commit`); record the choices. | **DONE 2026-11-04** — Monday 06:00 UTC; dispatch inputs (7d, reports: true, sites: KBTP, KAGC); mode: `artifact` |

### Neon resource record (non-secret)

| Item | Value |
|---|---|
| Project name | `AeroGrid-DW` |
| Project ID | `curly-unit-79242299` |
| Region | `aws-us-east-2` (AWS US East 2 Ohio); S3 region `us-east-2` |
| Branch | `production` |
| Branch ID | `br-royal-cherry-beij6hxw` |
| Database | `neondb` |
| Bucket | `aerogrid-raw` |
| Storage endpoint | `https://br-royal-cherry-beij6hxw.storage.c-9.us-east-2.aws.neon.tech` |
| ETL role | `aerogrid_etl` (created; owns nothing; grants pending) |
| Admin role | `neondb_owner` (do not use for CI) |

## Blockers

| ID | Blocker | Impact | Human action | Status |
|---|---|---|---|---|
| `B-001` | Phase 2 implementation was not authorized | No SQL, ETL, CI, or cloud resource work could begin | `H-007` | `RESOLVED` (Authorized 2026-11-04; `WP-02`/`WP-03` assigned) |
| `B-002` | Member access is incomplete | Cannot give Members B-E read access | `H-005` | `RESOLVED` (Members invited; H-002 deferred) |
| `B-003` | Proposed platform and source decisions need confirmation | Cannot freeze architecture or source contracts | `H-001`, `H-006` | `RESOLVED` (Accepted by HassanNawaz14 via `H-001`) |
| `B-004` | TartanAviation georeferencing is not yet validated | Spatial facts may need a fallback design | `WP-03` (authorized 2026-11-04) | `RESOLVED` (Validated 2026-11-07 against KBTP receiver reference; median 0.027 nm, p95 0.062 nm; see `docs/source_validation/SRC-TARTAN.md`) |
| `B-005` | Documentation baseline is awaiting human acceptance | `G0`/`G1` cannot close | `H-001` | `RESOLVED` (Accepted by HassanNawaz14) |
| `B-006` | Legacy synthetic files remain tracked under `data/sample/` | They are intentionally retained for offline demo/evaluator viewing and must not be mistaken for real data | `H-008`, `D-017` | `RESOLVED` (Retained as documented demo-only samples via `D-017`) |
| `B-007` | `aerogrid_reader` could insert into `project_staging.wp02_read_probe` | The read-only guarantee was not met, and `WP-02`/`G2` could not close | Root cause: the platform-created role was a member of `neon_superuser`, and `neondb_owner` has no ADMIN on it, so it could not be revoked, altered, or dropped from SQL. Fixed 2026-11-07 by deleting the role in the Neon Console and recreating it from SQL with `SELECT`-only grants; run `42276737288` shows `42501` on insert, update, delete, create table, and create schema. | `RESOLVED` |
| `B-008` | FAA Airspace source provenance/license is unresolved | Airspace facts cannot be loaded; `WP-03`/`G2` cannot close | `H-010` | `RESOLVED` (Human approved granular `Class_Airspace`, `Special_Use_Airspace`, and `Route_Airspace` services via `D-020`; DEMO layer excluded) |
| `B-009` | `aerogrid_etl` lacks `project_staging` DDL rights for WP-04 acceptance | Staging DDL cannot be applied; real-sample load/reconciliation evidence cannot be collected | `H-011` | `OPEN` (Fix authored 2026-11-08: `Phase2/sql/00_grants.sql` plus a fast-fail privilege preflight in `Phase2/etl/verify_wp04_staging.py`; awaiting the owner run) |
| `B-010` | `WP-05` start gate conflicts across canonical documents | Member C work cannot start without violating either the gate record or the dependency table; `G3` also requires `WP-05` | `H-012`, `D-022` | `RESOLVED` (Human directed no `WP-05` start until `WP-03`/`WP-04` merge; `D-022`) |

## Documentation baseline evidence

Captured for the `WP-00` baseline on 2026-11-03. Later authorized packages add
implementation files; see the handoff log.

| Evidence | Result |
|---|---|
| Canonical docs `00`-`12` | Present |
| Dev plan and acceptance files | Present |
| Templates | Present |
| Folder README placeholders | Present |
| `.gitignore` | Present |
| Root README | Updated for Phase 2 |
| Data source summary | Updated for real sources and weekly cadence |
| Data dictionary and schema overview | Updated for six dimensions/five facts |
| DBML | Updated; historical exports marked |
| Phase 1 guide | Supersession banner added |
| Implementation files | None created |
| Secrets/raw data | None added |
| Relative links | 213 checked across 41 markdown files; all targets exist |
| Document checks | Code fences balanced; no conflict markers; DBML braces balanced |
| Implementation scan | 0 SQL, Python, or workflow files in `Phase2/` or `.github/` |
| Secret scan | No live connection string, token, or private key pattern found |
| Ignore check | Legacy `data/sample/` files intentionally tracked and documented as demo-only; excluded from Phase 2 loads |
| Whitespace check | `git diff --check` clean apart from expected LF→CRLF warnings |

## WP-02 platform validation evidence

Captured 2026-11-06 from run
[42266493857](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42266493857)
(`platform-validation.yml`, `warehouse` environment, explicitly delegated by
HassanNawaz14). Overall `PARTIAL`: 13 pass, 2 warn, 1 skip, 0 fail. The job exits 0 on
`PARTIAL`; only `FAIL` fails the run.

| Check | Result | Evidence |
|---|---|---|
| Writer connection | `PASS` | 402 ms connect, 460 ms first query; pooled endpoint; `sslmode=require` |
| TLS | `PASS` | libpq cannot complete a `sslmode=require` connection without TLS |
| TLS certificate verification | `INFO` | `verify-full` from the runner failed chain validation; see caveat 1 |
| Identity | `PASS` | `user=aerogrid_etl`, `database=neondb`, server 18.6, `server_addr=127.0.0.1/32` |
| Schemas | `WARN` | `project_staging`, `project_dw`, `project_reporting` absent; created in `WP-04`/`WP-05` |
| Database write | `PASS` | temp table create/insert/select/drop |
| Statement timeout | `PASS` | `pg_sleep(3)` cancelled after 1058 ms with a 1 s timeout |
| Database size | `PASS` | 7.4 MiB of 1 GiB free tier |
| Warehouse objects | `INFO` | 0 tables/views in the three schemas; no production data present |
| Read-only probe table | `WARN` | absent, and `aerogrid_etl` lacks `CREATE` on `project_staging`; owner snippet pending |
| Warm connection | `PASS` | 400 ms |
| Storage write | `PASS` | marker object written in 505 ms |
| Storage head / read-back | `PASS` | 197 bytes; sha256 matches the written marker |
| Storage delete / cleanup | `PASS` | marker removed; no residue |
| Bucket size | `PASS` | 0 objects, 0.0 MiB of 5 GiB free tier |
| Compute and egress quota | `INFO` | 100 CU-hours and 5 GiB egress are console metrics; confirm after the first real run |
| Reader connection | `SKIP` | `READONLY_DATABASE_URL` is not set; manual proof pending |

Second run, [42272052476](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42272052476)
(2026-11-06), included the reader secret and returned `FAIL`: 17 pass, 1 warn, 1 fail,
0 skip. Reader connection, `SELECT 1`, and the probe-table read passed; the negative
`INSERT` check failed because the statement succeeded.

| Check | Result | Evidence |
|---|---|---|
| Reader connection | `PASS` | connected as `aerogrid_reader` in 120 ms |
| Reader select | `PASS` | `SELECT 1` succeeded |
| Reader select probe table | `PASS` | 1 row visible in `project_staging.wp02_read_probe` |
| Reader insert | `FAIL` | statement succeeded; write privilege is present |

This is a real access-control defect, tracked as `B-007`: `aerogrid_reader` must only
hold `SELECT`, so `WP-02` cannot close until the write privilege is removed and a
rerun shows `INSERT` rejected with SQLSTATE `42501`. Diagnosis on 2026-11-07: the table
ACL grants the reader only `r`, but the role is a member of `neon_superuser`, which
carries `pg_write_all_data` project-wide. `neondb_owner` cannot revoke that membership
(no ADMIN option) and cannot drop or alter the platform-created role, so the role is
replaced through the Neon Console and recreated from SQL. The run left probe row `999`
in the table; the probe now removes that row when the insert unexpectedly succeeds,
and the remediation steps in `docs/07` delete the existing one.

Third run, [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288)
(2026-11-07), after the role was replaced: `PASS`, 22 pass, 1 warn, 0 fail, 0 skip.

| Check | Result | Evidence |
|---|---|---|
| Reader connection | `PASS` | connected as `aerogrid_reader` in 72 ms |
| Reader select | `PASS` | `SELECT 1` succeeded |
| Reader select probe table | `PASS` | 1 row visible |
| Reader insert / update / delete | `PASS` | each rejected with SQLSTATE `42501` |
| Reader create table / create schema | `PASS` | each rejected with SQLSTATE `42501` |
| Writer, storage, TLS, timeout, size, quota | `PASS` | same evidence as the first run; warm connection 90 ms |

The single warning is the absent `project_dw` and `project_reporting` schemas, which
`WP-04`/`WP-05` create. `project_staging` now exists because `WP-02` needed a probe
object; `WP-04` owns the real staging tables.

Caveats:

1. Neon terminates client TLS at its proxy, so `pg_stat_ssl` on the compute reports no
   TLS and `server_addr` is loopback. The `sslmode=require` connection is the accepted
   encryption proof. A `verify-full` handshake from the GitHub runner failed chain
   validation (system CA store); this is a runner-trust detail, not a connection defect,
   and does not gate `WP-02`.
2. The missing schemas and probe table are expected: physical DDL belongs to `WP-04`
   and `WP-05`. The read-only proof therefore needs the owner snippet in
   [docs/07_operations_access_and_security.md](docs/07_operations_access_and_security.md)
   before the reader checks can run.
3. The temporary branch-scoped `push` trigger used to iterate on the workflow was
   removed; `platform-validation.yml` is back to `workflow_dispatch` only. The
   `warehouse` environment was restored to `prevent_self_review: true` after each
   approval.

## Handoff log

| Date | From | To | Work package | Summary | Files | Checks | Next step |
|---|---|---|---|---|---|---|---|
| `2026-11-03` | Member A | Human | `WP-00` | Completed Phase 2 documentation, plan, templates, folder boundaries, and stale-doc updates. No implementation created. | `AGENTS.md`, `Phase2/**`, root `README.md`, `data/**`, `docs/LowAltitude_..._Guide.md`, `.gitignore`, `.github/workflows/README.md` | 213 links checked; no implementation/secret files; DBML balanced; `git diff --check` clean | Human reviews `H-001` to `H-008` |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | Documented the demo-only retention of legacy samples and saved the remaining G1 human actions. No implementation created. | `data/sample/README.md`, `.gitignore`, `Phase2/PROGRESS.md`, `Phase2/DECISIONS.md`, `Phase2/README.md`, `Phase2/docs/01`, `03`, `06`, `07`, `08`, `09`, `10`, `11`, `Phase2/dev_plan/01`, `02`, root `README.md`, `data/all_data_summary.md` | Link/grep checks and `git diff --check`; no secrets/raw data added | Complete `H-004` to `H-007`; `H-002` remains blocked |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | Recorded `H-003` Neon resources; `H-003` done. | `Phase2/PROGRESS.md`, `Phase2/docs/07`, `Phase2/docs/10` | `git diff --check`; no secrets recorded | Complete `H-004` |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | `H-004` and `G-01` done: `warehouse` environment, six required secrets, and `main` protection confirmed. `H-005` is next; `H-002` remains blocked. | `Phase2/PROGRESS.md`, `Phase2/docs/10` | `git diff --check`; no secrets recorded | Complete `H-005` |
| `2026-11-06` | HassanNawaz14 | Team | `WP-01` closeout | Reconciled `G1`/authorization status across the board and canonical docs; recorded `aerogrid_reader` confirmation; left `H-002` deferred. No implementation created. | `Phase2/PROGRESS.md`, `Phase2/README.md`, `Phase2/AGENTS.md`, `Phase2/docs/01`-`12`, `Phase2/dev_plan/README.md` and `01`-`05`, root `README.md`, root `AGENTS.md`, `data/all_data_summary.md`, `Phase2/sql|etl|tests|reports/README.md`, `.github/workflows/README.md` | Stale-status grep and `git diff --check`; no secrets or raw data added | Start `WP-02` (Member A) and `WP-03` (Member B) |
| `2026-11-06` | HassanNawaz14 | Human | `WP-02` | Authored the platform validation probe and manual-dispatch workflow; documented the manual read-only proof; opened `H-009` to run it. No database or storage write was executed by the agent. | `.github/scripts/platform_probe.py`, `.github/workflows/platform-validation.yml`, `.github/workflows/README.md`, `Phase2/docs/07`, `Phase2/docs/10`, `Phase2/PROGRESS.md` | Python compile, YAML parse, link and secret scans | Human completes `H-009`, then record run evidence and close `G2` |
| `2026-11-06` | HassanNawaz14 | Human | `WP-02` | Ran the validation workflow on `phase2/wp-02-platform-validation` under explicit delegation. Final run [42266493857](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42266493857): 13 pass, 2 warn, 1 skip, 0 fail. Writer connect/write, storage put/head/read-back/delete, timeout, size, and quotas proven; TLS accepted via `sslmode=require`; read-only proof still open. Temporary push trigger removed and environment protection restored. | `.github/scripts/platform_probe.py`, `.github/workflows/platform-validation.yml`, `Phase2/PROGRESS.md` | Five workflow runs; log review; environment protection re-checked | Complete the read-only proof in `H-009`, then close `WP-02` and `G2` |
| `2026-11-06` | HassanNawaz14 | Human | `WP-02` | Reader proof run [42272052476](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42272052476) with the rotated reader secret: 17 pass, 1 warn, 1 fail. Reader can `SELECT` but also `INSERT`, so `B-007` opened; probe negative cases made non-destructive and the leaked test row is cleaned up. | `.github/scripts/platform_probe.py`, `.github/workflows/platform-validation.yml`, `Phase2/PROGRESS.md`, `Phase2/docs/07` | Workflow run log review; YAML and Python checks | Human revokes reader write privilege, then rerun `H-009` |
| `2026-11-07` | HassanNawaz14 | Reviewers B/C | `WP-02` | Replaced the platform-created reader role with a `SELECT`-only role, then reran validation: [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288) `PASS` (22 pass, 1 warn, 0 fail, 0 skip; all negative reader checks `42501`). `B-007` and `H-009` closed; `WP-02` moved to `READY_FOR_REVIEW`. Temporary push trigger removed and environment protection restored. | `.github/workflows/platform-validation.yml`, `Phase2/PROGRESS.md`, `Phase2/docs/07`, `Phase2/docs/10`, `README.md`, `AGENTS.md`, `Phase2/README.md`, `Phase2/AGENTS.md`, `Phase2/dev_plan/01`-`02`, `Phase2/dev_plan/README.md`, `Phase2/docs/01`, `Phase2/docs/09` | Run log review; YAML parse; link and stale-status greps | Members B and C review PR #3 and sign off; then close `WP-02` and `G2` |
| `2026-11-07` | HassanNawaz14 | Team | `WP-02` closeout | Review and merge completed; PR #3 merged as `b6b76b9`. Marked `WP-02` `DONE` on HassanNawaz14's explicit instruction; `G2` remains `IN_PROGRESS` for `WP-03`. | `Phase2/PROGRESS.md`, `README.md`, `AGENTS.md`, `Phase2/README.md`, `Phase2/AGENTS.md`, `Phase2/dev_plan/01`-`02`, `Phase2/dev_plan/README.md`, `Phase2/docs/01`, `07`, `09`, `10` | Stale-status grep and `git diff --check` | Member B completes `WP-03`; then close `G2` |
| `2026-11-07` | Member B | Reviewers D/E | `WP-03` | Validated Tartan KBTP raw ADS-B with two real range-read samples. Confirmed 13-field schema, units, WGS 84 lat/lon, km range, signed-degree bearing, feet altitude, and UTC inference. Georeferencing matches the KBTP receiver reference within 0.027 nm median / 0.062 nm p95. Resolved `B-004`; recommended a 2022-01-01 to 2022-01-07 UTC load window (~609k rows) because the full year (~22M rows) exceeds the database budget. | `Phase2/docs/source_validation/SRC-TARTAN.md`, `Phase2/docs/03_data_sources_and_licensing.md`, `Phase2/PROGRESS.md` | Two real member hashes; georeference reconstruction; row/nulls/duplicate counts; capacity estimate; `git diff --check` | Validate Nightjar, nominal-io DJI, FAA, and METAR/IEM; then assemble the WP-03 package for review |
| `2026-11-07` | Member B | Reviewers D/E | `WP-03` | Validated Nightjar `20260804` DJI CSV. Confirmed 12,448 rows, 12,447 valid timestamps, 119 columns, about 9.94 Hz, UTC absolute time, WGS 84 coordinates within 0.231 nm of the documented site, `OSD.height` feet AGL, `OSD.altitude` feet MSL after home initialization (site elevation 429.43 ft), speed components in m/s, and a consistent serial `5FSCK1601121D7`. One 1970 timestamp row and 758 duplicate timestamps require cleaning. | `Phase2/docs/source_validation/SRC-NIGHTJAR.md`, `Phase2/docs/03_data_sources_and_licensing.md`, `Phase2/PROGRESS.md` | Full CSV hash; timestamp/gap analysis; coordinate/site check; altitude datum check; speed-integral check; `git diff --check` | Validate nominal-io DJI, FAA, and METAR/IEM; then assemble the WP-03 package for review |
| `2026-11-07` | Member B | Reviewers D/E | `WP-03` | Validated nominal-io DJI three CSVs. Confirmed 189 columns, 10,314 rows, absolute epoch-second time, WGS 84 coordinates, feet AGL/MSL datums, explicit mph speeds, and one serial `1581F6Z9C241P003` across three flights. Found `timestamps_ns` is a misnomer (values are seconds), Colorado/Offshore have 1 s timestamp resolution, Colorado has 159 pre-GPS zero rows, and `DETAILS.totalDistance` is scaled by 1,000. | `Phase2/docs/source_validation/SRC-DJI-NOMINAL.md`, `Phase2/docs/03_data_sources_and_licensing.md`, `Phase2/docs/11_risks_and_validation.md`, `Phase2/PROGRESS.md` | Full CSV hashes; timestamp/unit analysis; coordinate/altitude check; speed-integral check; capacity estimate; `git diff --check` | Validate FAA and METAR/IEM; resolve DJI site-code mapping before `WP-05`; then assemble the WP-03 package for review |
| `2026-11-07` | Member B | Human | `WP-03` | Validated FAA UDDS facility map/TFR/airspace layers. Facility map has 370,441 national features (KAGC 317, Colorado 66, Palos 58, SF 50; KBTP and Nightjar 0); TFR is current-only with 5 features and none in study boxes; airspace has 16,789 features, max 2,000/pages. The `Airspace` item is titled `Airspace (DEMO)` and has no licenseInfo/accessInformation, so the source cannot be loaded without a human decision. | `Phase2/docs/source_validation/SRC-FAA-UDDS.md`, `Phase2/docs/03_data_sources_and_licensing.md`, `Phase2/PROGRESS.md` | Query/layer metadata; bbox counts; pagination checks; geometry/date-field checks; sample hashes; `git diff --check` | Human resolves `H-010` (accept DEMO layer, approve granular services, or exclude airspace); then finish METAR/IEM and close `WP-03` |
| `2026-11-07` | Member B | Reviewers D/E | `WP-03` | Closed `H-010`/`B-008` after human approval of granular FAA airspace services (`D-020`). Validated `Class_Airspace` (6,041 national), `Special_Use_Airspace` (1,545), and `Route_Airspace` (5,263); 0.25-degree study-box combined counts are KBTP 19, KAGC 26, Nightjar 52, Colorado 42, Palos 90, SF 54. Confirmed explicit public-use terms, FAA AIS attribution, `GLOBAL_ID` keys, EPSG:4269 native geometry, and `outSR=4326` output; recorded the observed `429` quota behavior. | `Phase2/docs/source_validation/SRC-FAA-UDDS.md`, `Phase2/docs/03_data_sources_and_licensing.md`, `Phase2/DECISIONS.md`, `Phase2/PROGRESS.md` | Metadata, counts, one-feature samples, hashes, quota backoff; `git diff --check` | Validate METAR/AWC and IEM; resolve DJI site-code mapping before `WP-05`; then assemble the WP-03 package for review |
| `2026-11-07` | Member B | Reviewers D/E | `WP-03` | Validated AWC METAR and IEM ASOS. AWC 24-hour KBTP/KAGC sample: 85 records, 43,913 bytes, `obsTime` epoch UTC, C/hPa/kt/statute-mile units, 30-day retention, 400-entry cap, 100 requests/minute. IEM six station-day samples: 133 routine rows, 31,949 bytes, UTC `valid`, deg F/knots/inHg/millibar/statute-mile units, public-domain terms, `report_type=3`+`4` required for `SPECI`, KTOA sparse, Nightjar nearest KAVP 13.4 nm. AWC/IEM cross-check: 48 common routine observations, 0 numeric differences after unit conversion. | `Phase2/docs/source_validation/SRC-METAR-AWC.md`, `Phase2/docs/source_validation/SRC-METAR-IEM.md`, `Phase2/docs/03_data_sources_and_licensing.md`, `Phase2/docs/11_risks_and_validation.md`, `Phase2/PROGRESS.md`, `AGENTS.md`, `README.md`, `Phase2/AGENTS.md`, `Phase2/README.md`, `Phase2/dev_plan/README.md`, `Phase2/docs/01_phase2_scope_and_objectives.md`, `Phase2/docs/09_agent_operating_manual.md`, `Phase2/docs/10_human_operating_manual.md` | Real JSON/CSV samples; hashes; schema/unit/null checks; station mapping; AWC/IEM cross-check; link check; `git diff --check` | Finalize WP-03 capacity/cleanup, delete temp samples, and assemble reviewer handoff; resolve DJI site-code mapping before `WP-05` |
| `2026-11-07` | Member B | Reviewers D/E | `WP-03` | Recorded the full-load capacity estimate: about 632k initial rows at 130-320 MB, below the 500 MiB target and 1 GiB limit; rejected the full Tartan year (~22M rows, ~4.4 GB). Deleted temporary raw samples after hashing; no raw data is tracked. Marked `WP-03` `READY_FOR_REVIEW`. | `Phase2/docs/11_risks_and_validation.md`, `Phase2/PROGRESS.md`, `AGENTS.md`, `README.md`, `Phase2/AGENTS.md`, `Phase2/README.md`, `Phase2/dev_plan/README.md`, `Phase2/dev_plan/01_work_breakdown.md`, `Phase2/dev_plan/02_dependencies_and_gates.md`, `Phase2/docs/01_phase2_scope_and_objectives.md`, `Phase2/docs/09_agent_operating_manual.md`, `Phase2/docs/10_human_operating_manual.md` | Capacity arithmetic; temp-dir cleanup; `git diff --check`; relative-link check | Reviewers D/E sign off; HassanNawaz14 closes `G2` |
| `2026-11-07` | Member B | Reviewers C/D/E | `WP-04` | Recorded `D-021`: the human approved starting `WP-04` before `G2` and reviewing `WP-03`/`WP-04` together. `WP-04` is now `IN_PROGRESS`; `G2` remains open. | `Phase2/DECISIONS.md`, `Phase2/PROGRESS.md`, `Phase2/dev_plan/01_work_breakdown.md` | Human approval recorded; status grep; `git diff --check` | Implement staging DDL, source loaders, rejects, and tests; keep WP-03 evidence separate |
| `2026-11-07` | Member B (Hamid4325) | Reviewers C/D | `WP-04` | Added staging bootstrap/DDL (`project_staging`, manifest/run/reject/DQ, source-shaped tables), reject code catalog, idempotent staging writer with reconciliation counts, file iterators for Tartan/Nightjar/Nominal/AWC/IEM/FAA, `etl` package init + pytest `conftest`, and staging-writer tests. Updated `data/data_dictionary.md` staging notes and `Phase2/sql/README.md`. Normalizers for Tartan/Nightjar/Nominal/FAA/AWC/IEM already present and covered by tests. | `Phase2/sql/00_schemas.sql`, `Phase2/sql/01_staging/*.sql`, `Phase2/sql/README.md`, `Phase2/etl/__init__.py`, `Phase2/etl/reject_codes.md`, `Phase2/etl/staging_writer.py`, `Phase2/etl/loaders.py`, `Phase2/tests/conftest.py`, `Phase2/tests/test_staging_writer.py`, `data/data_dictionary.md`, `Phase2/PROGRESS.md` | `python -m pytest -q` from `Phase2`: **24 passed**; `python -m pytest Phase2/tests -q` from repo root: **24 passed**; `git diff --check` clean | **DB acceptance pending (human/CI):** apply DDL to Neon `neondb` and run a real-sample load + rerun to prove reconciliation and idempotency. No local psycopg/credentials; do not paste secrets in chat. DJI site mapping remains unresolved before `WP-05`. |
| `2026-11-08` | Member B (Hamid4325) | Reviewers C/D | `WP-04` | Addressed PR #5 review blockers: raw iterators now yield source rows and row numbers; loaders add staging mappings and logical source files; writer uses per-row savepoints, reject fallback IDs, run-log/manifest helpers; Tartan reject IDs and AWC/IEM strict numeric/timestamp rejects added; DDL aliases staging columns; verifier can prove real-sample load/rerun in a rolled-back transaction; workflow runs pytest. Updated stale ETL/tests/pipeline/data-dictionary docs. DB evidence remains blocked by `H-011`. | `Phase2/etl/staging_writer.py`, `Phase2/etl/loaders.py`, `Phase2/etl/sources/tartan.py`, `Phase2/etl/sources/metar.py`, `Phase2/etl/verify_wp04_staging.py`, `Phase2/sql/01_staging/02_source_tables.sql`, `.github/workflows/wp04-staging-verify.yml`, `Phase2/tests/*`, `Phase2/etl/README.md`, `Phase2/tests/README.md`, `Phase2/docs/05_etl_pipeline.md`, `data/data_dictionary.md`, `Phase2/PROGRESS.md` | `python -m pytest -q`: **38 passed**; `python -m compileall -q Phase2\etl`: **OK**; `git diff --check`: **clean** (CRLF warnings only) | Human/Member A resolves `H-011`; then run DDL + optional real-sample verification and update PR #5. Do not start `WP-05` until `WP-03`/`WP-04` merge (`D-022`). |
| `2026-11-08` | Member B (Hamid4325) | Human | `WP-04` | Committed and pushed the PR #5 review fixes as `1ac7518`. Recorded `D-022` after the human directed that `WP-05` remain `NOT_STARTED` until `WP-03` and `WP-04` are merged; closed `H-012`/`B-010`. | `Phase2/DECISIONS.md`, `Phase2/PROGRESS.md`, `AGENTS.md`, `Phase2/AGENTS.md`, `Phase2/dev_plan/01_work_breakdown.md`, `Phase2/dev_plan/02_dependencies_and_gates.md`, `Phase2/docs/10_human_operating_manual.md` | `git push` updated `origin/phase2/wp03-wp04-source-validation-staging`; `python -m pytest -q`: **38 passed**; `git diff --check` clean | Resolve `H-011`; merge `WP-03`/`WP-04`; then start `WP-05` under `D-022`. |
| `2026-11-08` | HassanNawaz14 | Team | `WP-03` closeout / `G2` | Reviewed and merged PR #5 as `f9087f4`; recorded `WP-03` `DONE` and `G2` `DONE`, and started `WP-05` under `D-022`. Added the owner-run `Phase2/sql/00_grants.sql`, reader default privileges in the staging bootstrap, and a fast-fail privilege preflight in the WP-04 verifier for `H-011`. | `Phase2/PROGRESS.md`, `Phase2/sql/00_grants.sql`, `Phase2/sql/00_schemas.sql`, `Phase2/etl/verify_wp04_staging.py`, `AGENTS.md`, `Phase2/AGENTS.md`, `README.md`, `Phase2/README.md`, `Phase2/dev_plan/01`-`02`, `Phase2/dev_plan/README.md`, `Phase2/docs/01`, `05`, `07`, `09`, `10`, `Phase2/sql/README.md` | `pytest` 38 passed; `compileall`; stale-status grep; relative-link check; `git diff --check` | Member C starts `WP-05`; human runs `00_grants.sql` (`H-011`); HassanNawaz14 records `G3` after `WP-04`/`WP-05` acceptance. |
| `2026-11-08` | HassanNawaz14 | Human | `WP-04` | Recorded DDL evidence from run [42474788058](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42474788058): `aerogrid_etl` applied the three SQL files twice with no privilege error and created the 11 expected `project_staging` tables (all empty); the sample load was skipped. Because those tables were created after the first grants run, extended `00_grants.sql` with table-level self-checks and gave `00_schemas.sql` reader defaults for all three schemas. | `Phase2/sql/00_grants.sql`, `Phase2/sql/00_schemas.sql`, `Phase2/docs/07_operations_access_and_security.md`, `Phase2/PROGRESS.md` | `python -m pytest -q Phase2/tests`: **38 passed**; `python -m compileall -q Phase2\etl`: **OK**; `git diff --check`: **clean** | Human reruns the updated `00_grants.sql` (15 rows); Member B produces real-sample load/rerun evidence for `WP-04` |

## Change log

| Date | Change | Owner | Reference |
|---|---|---|---|
| `2026-11-03` | Initialized Phase 2 documentation and planning baseline | Member A | `WP-00` |
| `2026-11-03` | Added real-only, cloud-hosted, multi-site plan and Phase 2 gates | Member A | `DECISIONS.md` |
| `2026-11-03` | Completed docs `04`-`12`, dev plan, templates, folder READMEs, and `.gitignore` | Member A | `WP-00` |
| `2026-11-03` | Reconciled WP IDs and gate definitions across the plan | Member A | `dev_plan/02_dependencies_and_gates.md` |
| `2026-11-03` | Updated root README, data sources, dictionary, schema, DBML, and Phase 1 guide | Member A | `WP-00` |
| `2026-11-03` | Marked legacy synthetic samples as excluded, not usable evidence; opened `H-008`/`B-006` for human cleanup | Member A | `data/sample/README.md` |
| `2026-11-04` | Retained legacy synthetic samples as documented demo-only artifacts; added G1 execution checklist for `H-003` to `H-007` and repo/scheduling items; `H-002` remains blocked | HassanNawaz14 | `D-017`, `D-018`, `H-008` |
| `2026-11-04` | Recorded `H-003` Neon resources: project `AeroGrid-DW`, branch `br-royal-cherry-beij6hxw`, database `neondb`, bucket `aerogrid-raw`, storage endpoint | HassanNawaz14 | `H-003` |
| `2026-11-04` | Marked `H-004` and `G-01` done: `warehouse` environment, six required secrets, and `main` protection confirmed; `H-005` is next | HassanNawaz14 | `H-004`, `G-01` |
| `2026-11-06` | Synced status docs after `G1`: implementation authorized, `WP-02`/`WP-03` `READY`, `G2` next, `aerogrid_reader` confirmed, `H-002` remains deferred | HassanNawaz14 | `H-007`, `H-005`, `WP-01` closeout |
| `2026-11-06` | Added the `WP-02` probe and manual-dispatch validation workflow; `WP-02` is `BLOCKED_ON_HUMAN` on `H-009` | HassanNawaz14 | `WP-02`, `H-009` |
| `2026-11-06` | Executed the `WP-02` validation runs: CI writer and storage proof passed; TLS accepted via `sslmode=require`; read-only proof remains | HassanNawaz14 | `WP-02`, `H-009` |
| `2026-11-06` | Reader proof failed: `aerogrid_reader` holds write access to the probe table (`B-007`); remediation documented and rerun required | HassanNawaz14 | `WP-02`, `H-009`, `B-007` |
| `2026-11-07` | Closed `B-007`/`H-009` after replacing the reader role; `WP-02` is `READY_FOR_REVIEW` with a `PASS` validation run | HassanNawaz14 | `WP-02`, `H-009`, `B-007` |
| `2026-11-07` | Merged PR #3 and marked `WP-02` `DONE` on explicit human instruction; `G2` still waits on `WP-03` | HassanNawaz14 | `WP-02`, `G2` |
| `2026-11-07` | Validated nominal-io DJI; recorded epoch-second timestamps despite the `timestamps_ns` header, 1 s resolution on two flights, pre-GPS zeros, and the scaled `DETAILS.totalDistance` field | Member B | `WP-03`, `SRC-DJI-NOMINAL.md` |
| `2026-11-07` | Validated FAA UDDS; opened `H-010`/`B-008` because the Airspace item is titled `Airspace (DEMO)` and has no licenseInfo/accessInformation | Member B | `WP-03`, `SRC-FAA-UDDS.md`, `H-010`, `B-008` |
| `2026-11-07` | Human approved granular FAA airspace services; recorded `D-020`, closed `H-010`/`B-008`, and validated Class/Special Use/Route counts, fields, licenses, and study-box coverage | Member B | `WP-03`, `DECISIONS.md`, `SRC-FAA-UDDS.md`, `H-010`, `B-008` |
| `2026-11-07` | Validated AWC METAR and IEM ASOS; recorded AWC 30-day/400-entry limits, IEM units and missing/trace behavior, station mapping, and a 48-observation cross-check with zero numeric differences after unit conversion | Member B | `WP-03`, `SRC-METAR-AWC.md`, `SRC-METAR-IEM.md` |
| `2026-11-07` | Recorded the `WP-03` capacity estimate, removed temporary raw samples, and marked `WP-03` `READY_FOR_REVIEW` | Member B | `WP-03`, `docs/11_risks_and_validation.md` |
| `2026-11-07` | Human approved starting `WP-04` before `G2` and reviewing `WP-03`/`WP-04` together; recorded `D-021` and set `WP-04` to `IN_PROGRESS` | Member B | `WP-04`, `D-021` |
| `2026-11-07` | Added WP-04 staging DDL, reject catalog, idempotent writer/reconciliation helpers, source file iterators, and staging tests; local tests pass (24). DB apply/load/rerun acceptance still requires approved CI/human Neon path. | Member B (Hamid4325) | `WP-04`, `D-021` |
| `2026-11-08` | Applied PR #5 review fixes and added loader/writer tests; local tests pass (38). WP-04 set to `BLOCKED_ON_HUMAN` pending `H-011` DB grant/owner DDL path. | Member B (Hamid4325) | `WP-04`, `D-021`, `H-011` |
| `2026-11-08` | WP-04 DDL verified on Neon (run `42474788058`, two idempotent passes, 11 staging tables). Added table-level reader self-checks and ETL default privileges for all three schemas so staging tables created by the ETL role stay readable to members. | HassanNawaz14 | `WP-04`, `H-011` |
| `2026-11-08` | The 15-row self-check exposed an ownership gap: the 10 staging tables are owned by `aerogrid_etl` and `neondb_owner` cannot grant on them, so the reader had `SELECT` on none. `00_schemas.sql` now grants `SELECT` on all existing ETL-owned tables plus the defaults, on every ETL run. | HassanNawaz14 | `WP-04`, `H-011`, `B-009` |
| `2026-11-08` | Reviewed and merged PR #5; `WP-03` `DONE`, `G2` `DONE`, `WP-05` `READY`. Added `00_grants.sql` (ETL + reader grants, default privileges, self-check) and a verifier preflight so missing privileges fail fast with a fix. | HassanNawaz14 | `WP-03`, `G2`, `H-011`, `B-009` |

## Update protocol

When updating this file:

1. Keep the top metadata table accurate.
2. Update the gate and work package row you changed.
3. Add or close human actions and blockers with stable IDs.
4. Add a handoff row with files changed, checks run, and next step.
5. Add a change-log row for material changes.
6. Do not rewrite history or delete old handoff rows.
7. If a human action is required, set the work package to `BLOCKED_ON_HUMAN` and stop.

## Authorization record

| Field | Value |
|---|---|
| Authorized by | `HassanNawaz14` |
| Authorization date | `2026-11-04` |
| Authorized scope | Phase 2 implementation under gated work packages; `WP-02`/`WP-03` accepted, `WP-04` under `D-021` pending DB evidence, `WP-05` `READY` under `D-022` |
| Next gate to clear | `G3` |

### Package acceptance

| Package | Accepted by | Date | Evidence |
|---|---|---|---|
| `WP-02` | `HassanNawaz14` | `2026-11-07` | Run [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288) `PASS`; PR #3 merged as `b6b76b9`. The agent marked it `DONE` on HassanNawaz14's explicit instruction. |
| `WP-03` | `HassanNawaz14` | `2026-11-08` | Reviewed and merged via PR #5 (`f9087f4`). Source records in [`docs/source_validation/`](docs/source_validation/): Tartan, Nightjar, DJI, FAA, and METAR all `PASS` (IEM `PASS WITH LIMITATION`), capacity estimate recorded. The agent marked it `DONE` on HassanNawaz14's explicit instruction. |

### Gate acceptance

| Gate | Accepted by | Date | Evidence |
|---|---|---|---|
| `G2` | `HassanNawaz14` | `2026-11-08` | `WP-02` access proof (run `42276737288`) and `WP-03` source validation merged in PR #5. A later privilege gap is tracked separately as `H-011`/`B-009` and does not reopen `G2`. |
