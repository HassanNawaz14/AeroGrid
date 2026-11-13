# Phase 2 Progress and Handoff Board

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

This is the canonical status board for AeroGrid Phase 2. Every agent and human must
read it before acting. Update it at the end of every work session.

| Field | Value |
|---|---|
| Last updated | `2026-11-14` |
| Phase state | `G5_G6_G7_ADMIN_ACCEPTED_WP07_WP10_DEPLOYED_WP11_IMPLEMENTED` |
| Implementation authorized | `YES` (`H-007`, 2026-11-04) |
| Current gate | `G7` accepted administratively; independent technical proof follow-up |
| Current gate status | `DONE` by requester-admin declaration; end-to-end/second-reader proof not independently supplied |
| Active work package | `WP-11` CI, access, and deployment (Member A) |
| Active work package status | `READY_FOR_REVIEW` — ingestion job, workflow, and tests delivered; first approved apply run and reader proof pending |
| Next work package | `WP-12` integration, acceptance, and release |
| Next action owner | Human: peer-review the WP-11 PR, dispatch the first `mode=apply` run from `main`, then enable the schedule variables |

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
the package. Delegated exceptions: `D-023` let Members B and C close `WP-04`/`WP-05`;
`D-024` lets Member D close `WP-06` and Member C record `G4`. Every other gate is
recorded only by `HassanNawaz14`.

## Gate status

Gate definitions are canonical in
[`dev_plan/02_dependencies_and_gates.md`](dev_plan/02_dependencies_and_gates.md).

| Gate | Exit criterion | Status | Owner |
|---|---|---|---|
| `G0` | Documentation, plan, and folder baseline exist and links are valid | `DONE` | HassanNawaz14 |
| `G1` | Human approvals, named owners, Neon/GitHub access, and secrets ready | `DONE` (`H-007`; `H-002` deferred) | HassanNawaz14 |
| `G2` | Platform access and source validation spikes pass | `DONE` 2026-11-08 (`WP-02` and `WP-03` accepted; PR #5 merged as `f9087f4`) | HassanNawaz14 / Member B |
| `G3` | Staging, physical schema, constraints, indexes, keys, and seeds validated | `DONE` 2026-11-09 (recorded on `HassanNawaz14`'s explicit instruction; dimensions verified on Neon; real accepted-row staging proof under `B-011`) | HassanNawaz14 (delegated recording) |
| `G4` | Core tracking and journey facts loaded and reconciled | `DONE` 2026-11-11 (`WP-05` run `42689267328` and `WP-06` run `42887782411` `PASS`; PR #12 merged as `f29b099`; `B-011` resolved) | Member D; Member C recorded |
| `G5` | Derived facts and approved thresholds validated | `DONE` (requester-admin declaration, 2026-11-13; proof caveats disclosed) | Member E |
| `G6` | DQ, reports, reporting views, and automation validated | `DONE` (requester-admin declaration, 2026-11-13; proof caveats disclosed) | Member E / HassanNawaz14 |
| `G7` | A clean end-to-end run and team read access are demonstrated | `DONE` (requester-admin declaration, 2026-11-13; proof caveats disclosed) | HassanNawaz14 |

`G0`-`G4` are closed. `G0` was accepted via `H-001`; `G1` was closed and implementation authorized via `H-007` on 2026-11-04; `G2` was accepted by HassanNawaz14 on 2026-11-08 after `WP-03` review and PR #5 merge; `G3` was recorded on 2026-11-09 on HassanNawaz14's explicit instruction, with `B-011` open for the real staging load; `G4` was recorded on 2026-11-11 after the real Tartan `WP-05`/`WP-06` runs passed and `B-011` was resolved. `H-013` is approved (severe: horizontal `< 0.5 nm` / vertical `< 500 ft`; proximity: horizontal `< 1.0 nm` / vertical `< 1,000 ft`; `algorithm_version` `wp07-v1`). The next gate is `G5`; `WP-07` may now start.

## Work package status

| WP | Title | Owner | Depends on | Status | Next action |
|---|---|---|---|---|---|
| `WP-00` | Documentation and folder baseline | HassanNawaz14 | none | `DONE` | Accepted via `H-001` |
| `WP-01` | Human prerequisites and shared platform | HassanNawaz14 | `WP-00` | `DONE` | G1 cleared; proceed with WP-02 and WP-03. |
| `WP-02` | Platform validation and access proof | HassanNawaz14 | `WP-01` | `DONE` | Accepted 2026-11-07 by HassanNawaz14; run [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288) `PASS`; PR #3 merged as `b6b76b9` |
| `WP-03` | Source validation and georeferencing | Member B (Hamid4325) | `WP-01` | `DONE` | Accepted 2026-11-08 by HassanNawaz14 after review; PR #5 merged as `f9087f4`. Tartan, Nightjar, nominal-io DJI, FAA facility/TFR plus granular airspace (`D-020`), and METAR/AWC/IEM are validated; capacity estimate recorded; temp raw samples removed. `G2` closed on this evidence. |
| `WP-04` | Staging DDL and loaders | Member B (Hamid4325) | `WP-03` | `DONE` | DDL applied and readable (runs `42474788058`, `42477720902`; 15/15 self-check). Sample evidence recorded 2026-11-08 (4 read, 0 accepted, 4 rejected `INVALID_VEHICLE_ID`; idempotent; rolled back) used the legacy demo CSV, so accepted-row proof moves to `WP-06` under `B-011`. |
| `WP-05` | Dimensions, keys, and dictionary | Member C | `WP-02`, model approval | `DONE` | `D-022` start condition met. All deliverables implemented on branch `phase2/wp05-dimensions`: six dimension DDL (`01_dimensions.sql`) with identity surrogate keys, natural-key uniqueness, `-1` unknown members, `dim_site` FKs, idempotent; `02_seed.sql` derived `dim_time` hourly spine 2022-01-01..2022-01-07 (168 real-derived rows, ≥100 floor; site codes KBTP/KAGC/NIGHTJAR_PA/DJI_CO from WP-03; unresolved DJI site → `-1`); verifier (`verify_wp05_dimensions.py`) applied DDL+seed twice idempotently, asserts six tables, `-1` row each, no duplicate natural keys, FK targets exist, reader SELECT = true; workflow `wp05-dimensions-verify.yml` (15-min warehouse env, DATABASE_URL secret); `etl/dimensions.py` + `tests/test_dimensions.py`; data dictionary and DBML synchronized to DDL. Neon verifier PASS 2026-11-08: connected `aerogrid_etl` → `neondb` PG 18.6; six tables present; dim_time=169/dim_site=5/others=1 with `-1` row each; no duplicate natural keys; all dim_site FK targets exist; reader SELECT true. `WP-05` `DONE` under `D-023`; `G3` stays `IN_PROGRESS` for HassanNawaz14 to record. Artifacts: `Phase2/sql/02_dimensions/*`, `Phase2/etl/verify_wp05_dimensions.py`, `Phase2/etl/dimensions.py`, `.github/workflows/wp05-dimensions-verify.yml`, `Phase2/tests/test_dimensions.py`, `data/data_dictionary.md`, `data/diagrams/aerogrid_schema.dbml`, `Phase2/PROGRESS.md`. Checks: pytest 43 passed; compileall OK; git diff --check clean; Neon verifier PASS. Next: `G3` remains `IN_PROGRESS` (human records after WP-05); WP-06 waits for G3. |
| `WP-06` | Tracking and journey facts | Member D | `WP-04`, `WP-05` | `DONE` | Accepted 2026-11-11 under `D-024` after the real Tartan sample was uploaded and both workflows passed: WP-05 run [42689267328](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42689267328) and WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411) `PASS` on `phase2/wp06-tracking-facts` at `ecce8ec`; PR #12 merged as `f29b099`. The seed supplies 156 real Tartan `dim_vehicle` members; the verifier asserts accepted staging rows `> 0`, `fact_vehicle_tracking`/`fact_flight_journey` totals `>= 10,000`, 1-to-1 staging-to-tracking reconciliation, zero new inserts on Pass 2, zero FK orphans, and reader `SELECT = true`. `B-011` resolved; `G4` recorded. Exact staging/tracking/journey counts are in the run summary. |
| `WP-07` | Derived facts | Member E | `WP-06` | `DONE` (requester-admin accepted 2026-11-13) | Persisted via protected CI; 27,479 mapped, 3,658 real 2D cells, 1,754 occupancy; source limitations documented. |
| `WP-08` | Data-quality framework | Member E | `WP-04` to `WP-07` | `DONE` (requester-admin accepted 2026-11-13) | Run 7 persisted 32 DQ checks: 29 PASS, 3 WARN, 0 FAIL. |
| `WP-09` | PDF reports | Member E | `WP-08` | `DONE` (requester-admin accepted 2026-11-13) | Both improved source-linked PDFs on main after PR #20. |
| `WP-10` | Reporting views and corridor metrics | Member E | `WP-06`, `WP-07` | `DONE` (requester-admin accepted 2026-11-13) | Ten project_reporting views confirmed in Neon; CI run #2 passed. |
| `WP-11` | CI, access, and deployment | HassanNawaz14 | `WP-02`, `WP-04` to `WP-10` | `READY_FOR_REVIEW` | Implemented on `phase2/wp11-ingestion` under `D-030`: `etl/run.py` orchestrates fetch -> manifest -> staging -> dimension refresh -> DQ in one transaction; `wp11-ingest.yml` provides read-only `validate` and protected `apply` modes, a Monday 06:00 UTC schedule gated by `WP11_SCHEDULE_ENABLED`, and a manual reader-check job; the run summary reports every `L-001`–`L-010` entry with its linked DQ status and per-source coverage. Live validate 2026-11-14: 23,414 read / 23,254 accepted / 160 rejected, no database access. Checks: `pytest` 20 WP-11 tests pass; full local suite 127 passed with 2 environmental `reportlab` failures that pass in CI. Remaining acceptance evidence: merge, first approved `mode=apply` run on `main`, reader proof for Members B–E, then enable the schedule (`H-015`–`H-017`). |
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
| `H-011` | Apply `Phase2/sql/00_grants.sql` as `neondb_owner` | WP-04 DDL verify connected as `aerogrid_etl` to `neondb` but failed with `InsufficientPrivilege: permission denied for schema project_staging` on `CREATE TABLE IF NOT EXISTS project_staging.source_staging` (2026-11-07, Member B local run of `Phase2/etl/verify_wp04_staging.py`; no secrets recorded). The same gap would block every later schema and every member read. | `DONE` 2026-11-08: owner run applied the 15-row self-check (all `true`), runs [42474788058](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42474788058) and [42477720902](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42477720902) applied the DDL and the ETL reader grants. Remaining sample evidence is delegated to Member B under `D-023`. | `DONE` |
| `H-012` | Confirm the authoritative start gate for `WP-05` | `PROGRESS.md` and `dev_plan/01_work_breakdown.md` said `WP-05` waits for `G3`, but `dev_plan/02_dependencies_and_gates.md` said `G2`; `G3` itself requires `WP-05`, so the records could not all be correct. Starting Member C work without a decision would violate the gate rules. | Human decided on 2026-11-08: do not start `WP-05` until `WP-03` and `WP-04` are merged; `D-022` records the rule and `G3` remains the acceptance gate after both packages. | `DONE` |
| `H-013` | Approve the `WP-07` derived-fact thresholds and the `algorithm_version` value | `WP-07` cannot start without an approved close-encounter horizontal/vertical threshold, occupancy rule, and algorithm version; inventing them would be a business decision. | `G4` is recorded. Approved thresholds: severe horizontal < 0.5 nm and vertical < 500 ft; proximity horizontal < 1.0 nm and vertical < 1,000 ft (per `docs/04_data_model.md`). Approved `algorithm_version`: `wp07-v1` (per `dev_plan/01_work_breakdown.md`). No secret or console action is required. | `DONE` 2026-11-11; unblocks `WP-07` (Member E) |
| `H-014` | Upload the pinned real Tartan sample to `aerogrid-raw` | The bucket was confirmed empty on 2026-11-10, so `WP-06` cannot fetch `samples/kbtp/01-01-22/1.csv`; the seed fix alone is not sufficient for the acceptance run. | In the Neon Console, select the branch used by the `warehouse` secrets, open **Object storage** -> `aerogrid-raw`, and upload the extracted CSV as `samples/kbtp/01-01-22/1.csv` (4,325,376 bytes; SHA-256 `86342d09e5004102d765b82d04d16b43b6f15f2e7d829bfbde7909187d08a762`). Upload the extracted CSV, not the `2022.zip` archive. Neon CLI equivalent: `neon buckets object put aerogrid-raw/samples/kbtp/01-01-22/1.csv --file <local 1.csv> --content-type text/csv`. | `DONE` 2026-11-11; the WP-06 run fetched and verified the object |
| `H-015` | Review and merge the WP-11 ingestion PR, then dispatch the first approved apply run | The apply mode only runs on `main` inside the protected `warehouse` environment; no agent may write to the shared warehouse | After the WP-11 PR approval/merge: Actions -> **WP-11 Ingestion** -> Run workflow -> `mode=apply`, `confirm=APPROVE_WP11_APPLY`, sources `weather,uas,airspace`, stations `KBTP,KAGC`; record the run link and the per-source counts from the summary artifact. | `OPEN` |
| `H-016` | Create the repository variables that enable the weekly schedule | The `schedule` block is inert until a human enables it; unattended writes require a second explicit approval | GitHub repo Settings -> Secrets and variables -> Actions -> Variables: add `WP11_SCHEDULE_ENABLED=true` after the first apply run passes. Add `WP11_SCHEDULE_APPLY_ENABLED=true` only if unattended weekly writes are approved; without it, scheduled runs execute read-only `validate`. | `OPEN` |
| `H-017` | Members B–E run the read-only access check | `WP-11` acceptance and the G7 caveat both require member-read proof; `H-009` proved the role, not each member's own credentials | Each member sets their private read-only connection string in `READONLY_DATABASE_URL` and runs `python .github/scripts/platform_probe.py --mode reader` from the repo root (installs `psycopg[binary]` and `boto3` only in their own environment). Report pass/fail and the SQLSTATE of the rejected write per member. Never post the connection string in chat, a PR, or a workflow file. | `OPEN` |

`H-002` remains `BLOCKED` until Members B-E choose roles and provide real names.
`H-008` is resolved by `D-017`; the legacy samples are retained as demo-only artifacts
and are never loaded into Phase 2.

No human action may be simulated, inferred, or performed by an agent.

## Accepted data limitations (canonical register)

`G5`–`G7` acceptance did not resolve the data limitations; it accepted them. They are
tracked with stable IDs, observed values, and the condition that turns each one into
required work in
[`docs/13_accepted_data_limitations.md`](docs/13_accepted_data_limitations.md)
(`D-028`). `WP-11` must surface the linked DQ results and `WP-12` must report every
open entry. No entry may be closed by changing DQ severity or by omitting it from a
report.

| ID | Limitation | Observed 2026-11-13 | Trigger summary | Status |
|---|---|---|---|---|
| `L-001` | No weather linkage on tracking facts | 27,479 rows with `weather_key = -1`; not a METAR reading | Any weather-attributed metric, or a joinable 2022 METAR window | `OPEN` |
| `L-002` | Ground state unobserved | `on_ground` `NULL` on 27,479 rows; 7,433 inferred airborne | Any ground/air separation requirement | `OPEN` |
| `L-003` | Occupancy is 2D, 60-second cap | 3,658 real cells, 1,754 facts, no altitude bands | Any 3D/altitude-band or sub-60-second requirement | `OPEN` |
| `L-004` | Encounter predicate needs identical timestamps | 0 production facts; exploratory 20 s window: 22 pairs, 0 within limits | Any encounter count, rate, or "no conflicts" claim | `OPEN` |
| `L-005` | No historical restriction snapshot | 0 activation facts; 2026 FAA check found 0 KBTP features | Any restriction-compliance metric | `OPEN` |
| `L-006` | Reject ledger spans ETL runs | 418 events (416 invalid ID, 2 invalid timestamp) | Any single-run yield or rejection metric | `OPEN` |
| `L-007` | Corridor views are screening only | 808 rows in each corridor view | Any use as a validated corridor or capacity input | `OPEN` |
| `L-008` | UAS sources validated but never ingested | `stg_uas_position` 0 rows; Nightjar 12,448 and DJI 10,314 samples only tested | Any UAS traffic, UAS-to-manned separation, or combined airspace metric | `OPEN` |
| `L-009` | Airspace zones never staged; OpenSky unused | `stg_airspace_zone` 0 rows despite 12,849 approved FAA features; no OpenSky loader | Any zone membership/proximity metric, or any OpenSky-derived metric | `OPEN` |
| `L-010` | Fetched raw files are not archived to object storage | Every WP-11 run downloads to a transient runner directory; no raw object in `aerogrid-raw`, no manifest-linked archive | Any provenance audit needing the original bytes, or an offline re-run reproduction | `OPEN` |

The live DQ `WARN`s map exactly to this register: `L-001` (`DQ-C-003`), `L-002`
(`DQ-C-008`), `L-005` (`DQ-T-003`), `L-001` (`DQ-G-002`), `L-008` (`DQ-G-003`), and
`L-009` (`DQ-G-004`). `DQ-G-001` is the opposite guard: a primary source with zero
accepted rows becomes a `CRITICAL` failure, so an empty load can never be reported as
a measured zero. `L-010` has no DQ check; every WP-11 run summary states that fetched
raw files are transient. The "when is each table actually filled, and with how much data"
plan is the coverage completion plan in
[`docs/13_accepted_data_limitations.md`](docs/13_accepted_data_limitations.md#coverage-completion-plan):
five staging tables will fill through `WP-11`, restrictions stay conditional on a
real historical snapshot, OpenSky is deliberately not planned, and the planned initial
load is ~632,000 rows / ~130–320 MB (under the 1 GiB free-tier limit). The same
section records why each volume is limited, so no reduction is undocumented.

## 2026-11-13 live warehouse verification

Read-only verification dispatched on `main` after the local sync, to confirm the
deployed warehouse matches the accepted state. Both passing runs explicitly
`ROLLBACK`; no warehouse data changed.

| Run | Workflow | Result | Evidence |
|---|---|---|---|
| [43471609483](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43471609483) | `wp08-dq-verify.yml` (`mode=verify`) | `PASS` — 29 PASS, 3 WARN, 0 FAIL of 32; `DQ READ-ONLY PASS; ROLLBACK` | `DQ-C-003` 27,479; `DQ-C-008` 27,479; `DQ-T-003` 1; all critical checks 0 |
| [43471616729](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43471616729) | `wp10-views-verify.yml` (`mode=verify`) | `PASS` — 10 views present; `WP10 PASS; ROLLBACK - no persisted view changes` | Occupancy 1,754; traffic density 6,658; monthly 1; peak site hours 20; weather 1; corridor inputs 808; candidate cells 808; encounter and restriction views 0 |
| [43471623351](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43471623351) | `wp07-derived-facts-verify.yml` | `FAIL` before warehouse access — `ModuleNotFoundError: reportlab` in the unit-test job (2 failed, 105 passed) | `B-012` opened; superseded by run `43473293723` |
| [43473293723](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43473293723) | `wp07-derived-facts-verify.yml` (fixed in `bcf6777`) | `PASS` — 105 unit tests passed; `WP07 PASS; ROLLBACK (no persistent DDL or fact writes)` | 27,479 tracking inputs; 7,433 inferred airborne; 20,046 unknown airborne state; occupancy 1,754 candidates all already present; pass 2 inserted 0 rows; all 7 integrity checks 0; `accepted_snapshot_rows` 0 |
| [43478821521](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43478821521) | `wp08-dq-verify.yml` (`mode=verify`, branch `docs/wp11-accepted-limitation-register`) | `PASS` — 109 unit tests; 30 PASS, 6 WARN, 0 FAIL of 36; `DQ READ-ONLY PASS; ROLLBACK` | `DQ-G-001` 0; `DQ-G-002` 1; `DQ-G-003` 1; `DQ-G-004` 1; the original three warnings unchanged |
| [43478947023](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43478947023) | `wp09-reports.yml` | `PASS` — both PDFs generated and uploaded as artifacts | Both PDFs contain the source-coverage table: Tartan `LOADED`, five sources `NO DATA LOADED`, plus the coverage note |

Verdict: the deployed data is consistent with the accepted state — every critical
integrity check is 0, the six warnings are the accepted coverage and method
limitations, and WP-07 re-derivation is idempotent. `B-012` is resolved. `DQ-G-001`
proves the primary source is still loaded; `DQ-G-002`–`DQ-G-004` state explicitly
that weather, UAS, and airspace are not yet ingested rather than measured as zero.
The persisted audit run (`etl_run_id=7`) still holds the original 32 results; the
four coverage checks are recorded in `dq_result` only by the next approved
`mode=apply` run, which is a warehouse write and was not performed here.

## 2026-11-14 WP-11 ingestion implementation

`WP-11` adds the recurring ingestion path under `D-030`. No warehouse write was
performed; the only live evidence is a read-only `validate` run.

| Element | Delivered |
|---|---|
| Orchestrator | `Phase2/etl/run.py` — fetch, per-file manifest with SHA-256, staging with rejects, dimension refresh, DQ, run summary; `validate` opens no database connection |
| Source clients | `Phase2/etl/fetch.py` — IEM/AWC METAR, Nightjar, three nominal-io DJI flights, three approved FAA airspace services with pagination |
| Config | `Phase2/etl/config.py` — source URLs, site anchors, stations, licences, `LIMITATIONS` (`L-001`–`L-010`), 7-day default window |
| Dimension refresh | `Phase2/etl/dimension_loaders.py` — `dim_time`, `dim_vehicle`, `dim_weather`, `dim_airspace_zone` from accepted staging rows only |
| Workflow | `.github/workflows/wp11-ingest.yml` — `validate`/`apply` dispatch, Monday 06:00 UTC schedule gated by `WP11_SCHEDULE_ENABLED`, manual reader-check job, summary artifact |
| Tests | `Phase2/tests/test_wp11_run.py` — 20 tests: parsers, windows, apply guard, pagination, preview totals, dimension SQL, both summary modes, apply path |
| Safety | `--apply` requires `--confirm APPROVE_WP11_APPLY` plus `GITHUB_ACTIONS=true` and `WAREHOUSE_CI_APPROVED=true`; dispatch apply only on `main`; one transaction; `CRITICAL` DQ rolls back ingestion and records a separate `FAILED` run |

Read-only validate run, 2026-11-14, default window 2026-11-07..2026-11-14,
stations `KBTP`,`KAGC`: **23,414 rows read, 23,254 accepted, 160 rejected**
(`INVALID_TIMESTAMP=1`, `ZERO_COORDINATE=159`). Per source: METAR 400/400; Nightjar
12,448/12,447; Colorado 2,781/2,622; Palos Verdes 4,260/4,260; Offshore 3,273/3,273;
Class airspace 82/82; Special Use 0/0 (service answered; no feature intersects the
five documented study boxes, 1,545 nationally); Route airspace 170/170. A first
combined attempt failed once with a transient upstream API error and the immediate
retry passed; the workflow fails loudly rather than loading a partial source set.

The same validate run prints the accepted-limitation table for `L-001`–`L-010` with
`not evaluated` for checks that require warehouse data, and states that a `PASS`
proves staging coverage only. None of this closes `L-001`, `L-008`, or `L-009`: the
weather keys on existing facts are not backfilled and no UAS/restriction fact loader
exists.

Local checks: `python -m pytest -q Phase2/tests/test_wp11_run.py` → 19 passed; full
suite → 127 passed, 2 failed (`reportlab` not installed locally; CI installs it);
`python -m compileall -q Phase2/etl Phase2/tests` OK; `git diff --check` clean; YAML
parsed.

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
| `B-009` | `aerogrid_etl` lacks `project_staging` DDL rights for WP-04 acceptance | Staging DDL cannot be applied; real-sample load/reconciliation evidence cannot be collected | `H-011` | `RESOLVED` 2026-11-08: owner grants applied, DDL verified twice (runs `42474788058`/`42477720902`), and the 15-row self-check returns `true` for ETL, reader, and table-level access |
| `B-010` | `WP-05` start gate conflicts across canonical documents | Member C work cannot start without violating either the gate record or the dependency table; `G3` also requires `WP-05` | `H-012`, `D-022` | `RESOLVED` (Human directed no `WP-05` start until `WP-03`/`WP-04` merge; `D-022`) |
| `B-011` | `WP-04` sample evidence used the legacy synthetic demo CSV (`data/sample/tartan_trajectory_sample.csv`), so no real row was accepted in staging | The `G3` criterion "staging loaders work on real samples" is not proven by accepted rows; the demo file is excluded by `D-017` | `WP-06` real Tartan load + `H-014` raw upload | `RESOLVED` 2026-11-11: `H-014` uploaded the real sample and WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411) `PASS` on `phase2/wp06-tracking-facts` at `ecce8ec` (accepted staging rows `> 0`, tracking facts reconciled 1-to-1, zero duplicate inserts, zero FK orphans, reader `SELECT = true`). |
| `B-012` | `wp07-derived-facts-verify.yml` fails its unit-test job before touching the warehouse: the job installs `pytest` only, while `tests/test_reports.py` and `tests/test_report_improvements.py` import `reportlab` | The rollback-only WP-07 re-derivation and idempotency proof cannot run, so `WP-07` idempotency is unverified even though DQ integrity checks pass | Member A (`WP-11`): add `reportlab>=4,<5` to the unit-test install step in the workflow, then re-dispatch and record the run | `RESOLVED` 2026-11-13: fixed in `bcf6777` on `docs/wp11-accepted-limitation-register`; rerun [43473293723](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43473293723) `PASS` — 105 unit tests passed, `WP07 PASS; ROLLBACK`, all 7 integrity checks 0, second pass inserted 0 rows (idempotent) |

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

## WP-06 closeout evidence (closed 2026-11-11)

`WP-06` is `DONE` under `D-024`; `G4` is recorded and the `D-024` delegated window is
closed. The closeout used the real Tartan sample, not the excluded demo CSV:

- **Seed:** `Phase2/sql/02_dimensions/03_seed_real.sql` supplies 156 distinct real
  Tartan ICAO 24-bit `dim_vehicle` members from `samples/kbtp/01-01-22/1.csv`, with
  real first/last `event_ts`, `source_system='tartan'`, and no invented grid/weather
  rows. Both the WP-05 and WP-06 verifiers apply it before their checks.
- **Raw sample:** `H-014` uploaded the extracted CSV (4,325,376 bytes; SHA-256
  `86342d09e5004102d765b82d04d16b43b6f15f2e7d829bfbde7909187d08a762`) to
  `aerogrid-raw` at `samples/kbtp/01-01-22/1.csv`. The WP-06 run fetched and verified
  it.
- **Workflow evidence:** WP-05 run [42689267328](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42689267328)
  and WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411)
  both `PASS` on `phase2/wp06-tracking-facts` at `ecce8ec`. The WP-06 verifier asserts
  accepted staging rows `> 0`, `fact_vehicle_tracking + fact_flight_journey >= 10,000`,
  1-to-1 staging-to-tracking reconciliation, zero new inserts on Pass 2, zero FK
  orphans, zero `-1` rows on required dimensions, and `aerogrid_reader` `SELECT = true`.
  Exact counts are in the run summary.
- **Merge:** PR #12 merged the branch into `main` as `f29b099`.
- **Closed:** `B-011` `RESOLVED`; `WP-06` `DONE`; `G4` `DONE`; `D-024` window closed.
- **Next:** Member E starts `WP-07` derived facts now that `H-013` is approved; records `G5` evidence.

## Handoff log

| Date | From | To | Work package | Summary | Files | Checks | Next step |
|---|---|---|---|---|---|---|---|
| `2026-11-03` | Member A | Human | `WP-00` | Completed Phase 2 documentation, plan, templates, folder boundaries, and stale-doc updates. No implementation created. | `AGENTS.md`, `Phase2/**`, root `README.md`, `data/**`, `docs/LowAltitude_..._Guide.md`, `.gitignore`, `.github/workflows/README.md` | 213 links checked; no implementation/secret files; DBML balanced; `git diff --check` clean | Human reviews `H-001` to `H-008` |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | Documented the demo-only retention of legacy samples and saved the remaining G1 human actions. No implementation created. | `data/sample/README.md`, `.gitignore`, `Phase2/PROGRESS.md`, `Phase2/DECISIONS.md`, `Phase2/README.md`, `Phase2/docs/01`, `03`, `06`, `07`, `08`, `09`, `10`, `11`, `Phase2/dev_plan/01`, `02`, root `README.md`, `data/all_data_summary.md` | Link/grep checks and `git diff --check`; no secrets/raw data added | Complete `H-004` to `H-007`; `H-002` remains blocked |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | Recorded `H-003` Neon resources; `H-003` done. | `Phase2/PROGRESS.md`, `Phase2/docs/07`, `Phase2/docs/10` | `git diff --check`; no secrets recorded | Complete `H-004` |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | `H-004` and `G-01` done: `warehouse` environment, six required secrets, and `main` protection confirmed. `H-005` is next; `H-002` remains blocked. | `Phase2/PROGRESS.md`, `Phase2/docs/10` | `git diff --check`; no secrets recorded | Complete `H-005` |
| `2026-11-06` | HassanNawaz14 | Team | `WP-01` closeout | Reconciled `G1`/authorization status across the board and canonical docs; recorded `aerogrid_reader` confirmation; left `H-002` deferred. No implementation created. | `Phase2/PROGRESS.md`, `Phase2/README.md`, `Phase2/AGENTS.md`, `Phase2/docs/01`-`12`, `Phase2/dev_plan/README.md` and `01`-`05`, root `README.md`, root `AGENTS.md`, `data/all_data_summary.md`, `Phase2/sql/README.md`, `Phase2/etl/README.md`, `Phase2/tests/README.md`, `Phase2/reports/README.md`, `.github/workflows/README.md` | Stale-status grep and `git diff --check`; no secrets or raw data added | Start `WP-02` (Member A) and `WP-03` (Member B) |
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
| `2026-11-08` | Member B (Hamid4325) | Reviewers C/D | `WP-04` | Collected real-sample Neon evidence via `Phase2/etl/verify_wp04_staging.py --tartan-sample data/sample/tartan_trajectory_sample.csv`: connected as `aerogrid_etl` to `neondb` (PostgreSQL 18.6); preflight OK; DDL applied twice (idempotent); 11 staging tables present; sample pass1/pass2 each read 4 rows, 0 accepted, 4 rejected (`INVALID_VEHICLE_ID`), reconciled=True; rows rolled back, no data persisted; WP-04 verification PASS. Marked `WP-04` `DONE` under `D-023`. | `Phase2/etl/verify_wp04_staging.py`, `Phase2/PROGRESS.md` | Verifier output (non-secret): `WP-04 verification PASS`; `python -m pytest -q`: 38 passed | `WP-05` remains READY; Member C may start under `D-022`; `G3` after WP-05 acceptance. |
| `2026-11-08` | Member C | Reviewers A/D | `WP-05` | Implemented all WP-05 deliverables on branch `phase2/wp05-dimensions`: `Phase2/sql/02_dimensions/01_dimensions.sql` (six dimensions, identity surrogate keys, natural-key uniqueness, `-1` unknown members, `dim_site` FKs, idempotent), `02_seed.sql` (derived `dim_time` hourly spine 2022-01-01..2022-01-07 = 168 rows >= 100 floor; real site codes KBTP/KAGC/NIGHTJAR_PA/DJI_CO from WP-03; DJI unresolved site maps to -1), `Phase2/etl/verify_wp05_dimensions.py` (applies 00_schemas.sql + DDL + seed twice; asserts six tables, `-1` row each, no duplicate natural keys, FK targets exist, reader SELECT = true), `.github/workflows/wp05-dimensions-verify.yml` (15-min warehouse env, DATABASE_URL secret), `Phase2/etl/dimensions.py` + `Phase2/tests/test_dimensions.py` (key normalization/seed logic), `data/data_dictionary.md` and `data/diagrams/aerogrid_schema.dbml` synchronized to DDL. Local `python -m pytest -q Phase2/tests`: 43 passed; `compileall` OK; `git diff --check` clean. Grant path: DDL runs as `aerogrid_etl`; `00_schemas.sql` grants reader SELECT on ETL-owned tables and sets defaults (never run owner-only `00_grants.sql`). Neon DB verifier run and CI dispatch pending Member C dispatch with `DATABASE_URL` (set in your shell, never in chat). | `Phase2/sql/02_dimensions/*`, `Phase2/etl/verify_wp05_dimensions.py`, `Phase2/etl/dimensions.py`, `.github/workflows/wp05-dimensions-verify.yml`, `Phase2/tests/test_dimensions.py`, `data/data_dictionary.md`, `data/diagrams/aerogrid_schema.dbml`, `Phase2/PROGRESS.md` | pytest 43 passed; compileall OK; git diff --check clean | Mark `WP-05` `DONE` after the Neon verifier run; `G3` stays `IN_PROGRESS` for the human. |
| `2026-11-08` | HassanNawaz14 | Team | `WP-03` closeout / `G2` | Reviewed and merged PR #5 as `f9087f4`; recorded `WP-03` `DONE` and `G2` `DONE`, and started `WP-05` under `D-022`. Added the owner-run `Phase2/sql/00_grants.sql`, reader default privileges in the staging bootstrap, and a fast-fail privilege preflight in the WP-04 verifier for `H-011`. | `Phase2/PROGRESS.md`, `Phase2/sql/00_grants.sql`, `Phase2/sql/00_schemas.sql`, `Phase2/etl/verify_wp04_staging.py`, `AGENTS.md`, `Phase2/AGENTS.md`, `README.md`, `Phase2/README.md`, `Phase2/dev_plan/01`-`02`, `Phase2/dev_plan/README.md`, `Phase2/docs/01`, `05`, `07`, `09`, `10`, `Phase2/sql/README.md` | `pytest` 38 passed; `compileall`; stale-status grep; relative-link check; `git diff --check` | Member C starts `WP-05`; human runs `00_grants.sql` (`H-011`); HassanNawaz14 records `G3` after `WP-04`/`WP-05` acceptance. |
| `2026-11-08` | HassanNawaz14 | Human | `WP-04` | Recorded DDL evidence from run [42474788058](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42474788058): `aerogrid_etl` applied the three SQL files twice with no privilege error and created the 11 expected `project_staging` tables (all empty); the sample load was skipped. Because those tables were created after the first grants run, extended `00_grants.sql` with table-level self-checks and gave `00_schemas.sql` reader defaults for all three schemas. | `Phase2/sql/00_grants.sql`, `Phase2/sql/00_schemas.sql`, `Phase2/docs/07_operations_access_and_security.md`, `Phase2/PROGRESS.md` | `python -m pytest -q Phase2/tests`: **38 passed**; `python -m compileall -q Phase2\etl`: **OK**; `git diff --check`: **clean** | Human reruns the updated `00_grants.sql` (15 rows); Member B produces real-sample load/rerun evidence for `WP-04` |
| `2026-11-08` | HassanNawaz14 | Team | `D-023` closeout window | Documented the delegated closeout window so Member B and Member C agents can finish without human input: decision `D-023`, agent briefs in `dev_plan/01`, role and review mapping in `docs/08`, operating-rule exceptions in `docs/09`, and a hands-off window with a one-time environment setup and return checklist in `docs/10`. No code or data changed. | `Phase2/DECISIONS.md`, `AGENTS.md`, `Phase2/AGENTS.md`, `Phase2/PROGRESS.md`, `Phase2/README.md`, `README.md`, `Phase2/dev_plan/01_work_breakdown.md`, `Phase2/dev_plan/02_dependencies_and_gates.md`, `Phase2/dev_plan/README.md`, `Phase2/docs/01`, `Phase2/docs/05`, `Phase2/docs/07`, `Phase2/docs/08`, `Phase2/docs/09`, `Phase2/docs/10`, `data/data_dictionary.md`, `.github/workflows/README.md` | `pytest` 38 passed; `git diff --check`; stale-status and table-format checks | `HassanNawaz14` does the one-time `warehouse` reviewer setup, then Member B closes `WP-04` and Member C closes `WP-05`; the human returns at `G3` |
| `2026-11-09` | HassanNawaz14 | Team | `G3` / `D-024` | Recorded `G3` `DONE` on HassanNawaz14's explicit instruction and opened `D-024`: Member D owns `WP-06`; Member C completes real `dim_vehicle` (and grid) members and verifies the fact load before recording `G4`. Flagged `B-011`: the prior `WP-04` sample proof used the legacy demo CSV, so `WP-06` must load real Tartan rows, show accepted rows > 0, and reconcile tracking facts to staging. No application code changed. | `Phase2/PROGRESS.md`, `Phase2/DECISIONS.md`, `AGENTS.md`, `Phase2/AGENTS.md`, `Phase2/README.md`, `README.md`, `Phase2/dev_plan/01_work_breakdown.md`, `Phase2/dev_plan/02_dependencies_and_gates.md`, `Phase2/dev_plan/README.md`, `Phase2/docs/01`, `Phase2/docs/03`, `Phase2/docs/05`, `Phase2/docs/07`, `Phase2/docs/08`, `Phase2/docs/09`, `Phase2/docs/10`, `.github/workflows/README.md` | `pytest` 43 passed; `git diff --check`; status and link checks | PR #9 needs one approving review to merge; then Member C extends dimensions; Member D loads real Tartan staging + facts and closes `WP-06`; Member C records `G4` |
| `2026-11-09` | Member D (`ahmadazad-dev`) | Member C (`HarveyWebbs`) / Team | `WP-06` | Implemented `WP-06` core movement facts on branch `phase2/wp06-tracking-facts`: idempotent `fact_vehicle_tracking` and `fact_flight_journey` DDL (`01_facts.sql`), bulk dimension lookup/mapping (`-1` only for unresolved optional grid/weather; fail-closed required dims), deterministic gap-split (`300s`, `wp06-v1`) journey segmentation skipping single-point tracks, chunked staging/fact batching (`batch_size=500` opt-in, preserving `batch_size=1` default), Neon/S3 SHA-256 verifier, workflow (temp branch `push` trigger while open), 10 new unit tests, and dictionary/DBML/doc sync (`altitude_source VARCHAR(32)`). No Neon write run executed yet; `B-011` remains open until Member C lands `03_seed_real.sql` and uploads `samples/kbtp/01-01-22/1.csv` into `aerogrid-raw`. | `Phase2/sql/03_facts/01_facts.sql`, `Phase2/etl/facts.py`, `Phase2/etl/verify_wp06_facts.py`, `Phase2/etl/staging_writer.py`, `Phase2/etl/loaders.py`, `.github/workflows/wp06-facts-verify.yml`, `Phase2/tests/test_facts.py`, `data/data_dictionary.md`, `data/diagrams/aerogrid_schema.dbml`, `Phase2/docs/05_etl_pipeline.md`, `Phase2/sql/README.md`, `Phase2/etl/README.md`, `Phase2/tests/README.md`, `.github/workflows/README.md`, `Phase2/README.md`, `Phase2/PROGRESS.md` | `python -m compileall -q Phase2/etl Phase2/tests` OK; local Python 3.12 scratch test runner (`53 passed, 0 failed`; real `pytest` runs in CI); `git diff --check` clean; YAML/DBML/SQL/link checks OK | Member C uploads `samples/kbtp/01-01-22/1.csv` to `aerogrid-raw` and merges `03_seed_real.sql`; Member D rebases onto `main`, runs `wp06-facts-verify.yml` persistently (Member C/B approves `warehouse` run), removes temp `push` trigger, closes `B-011`, and opens PR for peer review (`D-024`). |
| `2026-11-09` | Member D (`ahmadazad-dev`) | Member C (`HarveyWebbs`) | `WP-06` PR handoff | Documented Member C's collaborator workflow and remaining `WP-06` execution checklist inside `Phase2/PROGRESS.md` (`03_seed_real.sql`, `aerogrid-raw` upload, shared-branch CI persistence on `phase2/wp06-tracking-facts`, temp trigger removal, `B-011`/`WP-06` closeout, peer review, merge, and `G4`) ahead of pushing `phase2/wp06-tracking-facts`. | `Phase2/PROGRESS.md`, `Phase2/README.md` | `git diff --check` clean; Markdown links/tables verified | Push `phase2/wp06-tracking-facts`, open Draft PR on `HassanNawaz14/AeroGrid` allowing collaborator edits, and hand execution of remaining checklist items to Member C (`HarveyWebbs`). |
| `2026-11-09` | Member D (`ahmadazad-dev`) | Member C (`HarveyWebbs`) | `WP-06` audit & hardening | Confirmed CI run `42670911235` `Run Phase 2 unit tests` passed while `Verify WP-06 tracking and journey facts` stopped at expected preflight `exit code 3` (`project_dw.dim_vehicle` has 0 real Tartan rows pending `03_seed_real.sql`). Fixed audit findings: aligned `data/data_dictionary.md` relationship summary (`grid` optional `-1`), added unambiguous SQL `to_hex()` unpadded vehicle ID fallback + `bisect` grid lookup in `facts.py`, enforced PostgreSQL 65,535 bind-param chunking and `160`-char NUL-safe reject ID clamping in `staging_writer.py`/`facts.py`, added `redact_secrets` + CLI param validation in `verify_wp06_facts.py`, and added 7 regression tests in `tests/test_facts.py`. | `Phase2/etl/facts.py`, `Phase2/etl/staging_writer.py`, `Phase2/etl/verify_wp06_facts.py`, `Phase2/tests/test_facts.py`, `Phase2/tests/README.md`, `data/data_dictionary.md`, `Phase2/PROGRESS.md` | `compileall` OK; local Python 3.12 test-function run `60 passed, 0 failed`; `static_audit_wp06.py` PASS (16 files); `git diff --check` clean | Commit/push fixes to `phase2/wp06-tracking-facts`, open Draft PR, and hand remaining `03_seed_real.sql`/`aerogrid-raw` + Neon verification checklist to Member C (`HarveyWebbs`). |
| `2026-11-10` | Member C | Member D / Team | `WP-06` seed fix | Fixed the merged `WP-06` CI preflight failure: extracted the real `samples/kbtp/01-01-22/1.csv` member from the public Tartan archive, verified SHA-256 `86342d09...a762`, and added `Phase2/sql/02_dimensions/03_seed_real.sql` with 156 distinct real Tartan ICAO 24-bit vehicle members (first/last seen from real rows; no invented weather/grid rows; idempotent, no deletes). WP-05 and WP-06 verifiers now apply the seed, and the temporary WP-06 `push` trigger was removed. | `Phase2/sql/02_dimensions/03_seed_real.sql`, `Phase2/etl/verify_wp05_dimensions.py`, `Phase2/etl/verify_wp06_facts.py`, `.github/workflows/wp06-facts-verify.yml`, `Phase2/tests/test_dimensions.py`, `Phase2/tests/test_facts.py`, `Phase2/sql/README.md`, `Phase2/etl/README.md`, `Phase2/README.md`, `data/data_dictionary.md`, `Phase2/PROGRESS.md` | `python -m pytest -q Phase2/tests`; `python -m compileall -q Phase2/etl Phase2/tests`; `git diff --check`; seed unit test asserts 156 unique real IDs and no invented rows | Run `wp05-dimensions-verify.yml` to apply/validate the seed, then dispatch `wp06-facts-verify.yml` from `main` (`dry_run=false`), record the run link and counts, close `B-011`/`WP-06`, and record `G4`. |
| `2026-11-10` | Member C | Member D / Team | `WP-06` raw-sample blocker | Confirmed `aerogrid-raw` is empty, so the WP-06 verifier cannot fetch `samples/kbtp/01-01-22/1.csv`; the seed fix is necessary but not sufficient. Recorded `H-014` with the exact object key, size, SHA-256, and upload path. | `Phase2/PROGRESS.md`, `Phase2/README.md` | Neon Console check (bucket empty); local extracted sample SHA-256 `86342d09...a762` and size `4,325,376` bytes; `pytest` 62 passed | Upload the extracted CSV to `aerogrid-raw` (`H-014`), then run `wp05-dimensions-verify.yml` and dispatch `wp06-facts-verify.yml`. |
| `2026-11-11` | Member C | Member E / Team | `WP-06` / `G4` closeout | Recorded the real Tartan `WP-05`/`WP-06` run evidence, resolved `B-011`/`H-014`, marked `WP-06`/`G4` `DONE`, closed the `D-024` window, and set `WP-07` `BLOCKED_ON_HUMAN` on `H-013`. Documentation only; no code, SQL, workflow, or test changes. | `Phase2/PROGRESS.md`, `Phase2/README.md`, `AGENTS.md`, `Phase2/AGENTS.md`, `Phase2/dev_plan/01`, `02`, `README.md`, `Phase2/DECISIONS.md`, `Phase2/docs/01`, `05`, `08`, `09`, `10`, `11`, `data/data_dictionary.md`, `.github/workflows/README.md`, root `README.md` | Markdown/link/status grep; `git diff --check`; no secrets or raw data | Human approves `H-013`; then Member E starts `WP-07` and records `G5` evidence |
| `2026-11-13` | Member A | Team / `WP-11` | Limitation register + live verification | Synced local `main` to `f0c2e51`; created the canonical accepted-limitation register `L-001`–`L-007` with implementation triggers; ran the read-only warehouse verifiers. DQ `PASS` (29/3/0), WP-10 `PASS` (10 views), WP-07 verification blocked by CI dependency defect `B-012`. Documentation only; no warehouse writes. | `Phase2/docs/13_accepted_data_limitations.md`, `Phase2/docs/00_documentation_map.md`, `Phase2/DECISIONS.md`, `Phase2/PROGRESS.md`, `Phase2/README.md`, `Phase2/dev_plan/01_work_breakdown.md` | WP-08 run `43471609483` `PASS`; WP-10 run `43471616729` `PASS`; WP-07 run `43471623351` `FAIL` (CI dependency); relative links checked; `git diff --check` | Member A adds `reportlab` to the WP-07 unit-test install, re-runs the rollback verifier (`B-012`), then starts `WP-11` |
| `2026-11-13` | Member A | Team / `WP-11` | `B-012` closeout | Fixed the WP-07 verifier's missing `reportlab` dependency (`bcf6777`), pushed `docs/wp11-accepted-limitation-register`, and re-dispatched: run `43473293723` `PASS` with 105 unit tests, all 7 integrity checks 0, second derivation pass inserting 0 rows, and an explicit rollback. No warehouse writes. | `.github/workflows/wp07-derived-facts-verify.yml`, `Phase2/PROGRESS.md`, `Phase2/README.md` | WP-07 run `43473293723` `PASS`; YAML parse; `git diff --check` | Start `WP-11`: weekly/manual orchestration, reader-access proof, and limitation lines in the run summary |
| `2026-11-13` | Member A | Team / `WP-11` | Coverage guards and `L-008`/`L-009` | Added `DQ-G-001`–`DQ-G-004` so an approved source with no accepted rows is reported as missing coverage instead of a measured zero; added the per-source coverage table to both PDFs; recorded `L-008` (UAS never ingested) and `L-009` (airspace never staged, OpenSky unused) with a coverage completion plan; decision `D-029`. Read-only runs only. | `Phase2/etl/dq.py`, `Phase2/etl/reports.py`, `Phase2/tests/test_dq.py`, `Phase2/tests/test_report_improvements.py`, `Phase2/docs/13_accepted_data_limitations.md`, `Phase2/DECISIONS.md`, `Phase2/dev_plan/01_work_breakdown.md`, `Phase2/PROGRESS.md` | WP-08 run `43478821521` `PASS` (109 tests, 30 PASS / 6 WARN / 0 FAIL of 36); WP-09 run `43478947023` `PASS` with the coverage table in both PDFs; `python -m compileall`; `git diff --check`; local pytest 107 passed, 2 skipped-by-missing-`reportlab` failures that pass in CI | `WP-11`: wire the existing loaders into the scheduled ingestion job so weather, UAS, and airspace staging stop being empty |
| `2026-11-14` | Member A | Reviewers B–E / Human | `WP-11` ingestion pipeline | Implemented the ingestion path under `D-030` on `phase2/wp11-ingestion`: fetch clients, source config, dimension refresh from accepted staging rows, transactional orchestrator with validate/apply split, and the `wp11-ingest.yml` workflow (dispatch, gated Monday schedule, manual reader-check, summary artifact). Recorded `L-010` (raw files not archived) and the read-only validate evidence (23,414 read / 23,254 accepted / 160 rejected). No warehouse write. | `Phase2/etl/run.py`, `Phase2/etl/fetch.py`, `Phase2/etl/config.py`, `Phase2/etl/dimension_loaders.py`, `Phase2/etl/loaders.py`, `Phase2/tests/test_wp11_run.py`, `.github/workflows/wp11-ingest.yml`, `Phase2/DECISIONS.md`, `Phase2/docs/13_accepted_data_limitations.md`, `Phase2/docs/05_etl_pipeline.md`, `Phase2/dev_plan/01_work_breakdown.md`, `Phase2/PROGRESS.md` | WP-11 tests 20 passed; full local suite 127 passed, 2 environmental `reportlab` failures; `compileall` OK; `git diff --check`; YAML parse; read-only validate run | Human: review/merge the WP-11 PR, dispatch the first `mode=apply` run (`H-015`), then create the schedule variables (`H-016`); Members B–E run the reader check (`H-017`) |

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
| `2026-11-08` | Merged PR #6; run `42477720902` applied the ETL bootstrap on `main`. Reader `SELECT` is restored and the 15-row self-check returns `true` on every row; `B-009` closed. Real-sample evidence is the only remaining `WP-04` item. | HassanNawaz14 | `WP-04`, `H-011`, `B-009` |
| `2026-11-08` | Reviewed and merged PR #5; `WP-03` `DONE`, `G2` `DONE`, `WP-05` `READY`. Added `00_grants.sql` (ETL + reader grants, default privileges, self-check) and a verifier preflight so missing privileges fail fast with a fix. | HassanNawaz14 | `WP-03`, `G2`, `H-011`, `B-009` |
| `2026-11-08` | Recorded `D-023`, the delegated closeout window: Members B and C may self-approve their `warehouse` runs, peer-review each other, merge their own package PRs, and mark `WP-04`/`WP-05` `DONE`. Gates, secrets, roles, repository settings, and destructive SQL stay human-only. The human returns only at `G3`. | HassanNawaz14 | `D-023`, `WP-04`, `WP-05`, `G3` |
| `2026-11-09` | Recorded `G3` `DONE` on explicit human instruction; opened `WP-06` for Member D with Member C completing dimension members and recording `G4` under `D-024`; tracked `B-011` for the demo-CSV sample proof | HassanNawaz14 | `G3`, `WP-06`, `D-024`, `B-011` |
| `2026-11-09` | Implemented `WP-06` core movement facts DDL, mapping/journey ETL, S3/Neon verifier, workflow, batched staging writer optimization, unit tests, and doc/dictionary/DBML alignment on `phase2/wp06-tracking-facts`; Neon acceptance load awaits Member C's `03_seed_real.sql` and raw S3 upload | Member D (`ahmadazad-dev`) | `WP-06`, `D-024`, `B-011` |
| `2026-11-09` | Documented `WP-06` Member C collaborator execution checklist on `phase2/wp06-tracking-facts` so Member C can finish `03_seed_real.sql`/S3, run/approve CI persistence in this PR, close `B-011`/`WP-06`, and record `G4` | Member D (`ahmadazad-dev`) | `WP-06`, `D-024`, `B-011` |
| `2026-11-09` | Hardened `WP-06` ETL/verifier/tests/dictionary after CI run `42670911235` audit (unpadded `to_hex` fallback, `bisect` grid index, 65,535 param chunking, `160`-char reject ID cleanup, secret redaction, optional `grid` doc sync, and 7 regression tests) | Member D (`ahmadazad-dev`) | `WP-06`, `D-024`, `B-011` |
| `2026-11-10` | Added the real `dim_vehicle` seed (156 real Tartan ICAO addresses) from the pinned `samples/kbtp/01-01-22/1.csv`, applied it in the WP-05 and WP-06 verifiers before preflight, and removed the merged WP-06 temporary `push` trigger | Member C | `WP-06`, `D-024`, `B-011` |
| `2026-11-10` | Confirmed `aerogrid-raw` is empty and opened `H-014` to upload the extracted real Tartan sample (`samples/kbtp/01-01-22/1.csv`, 4,325,376 bytes, SHA-256 `86342d09...a762`) before the WP-06 acceptance run; set `WP-06`/`B-011` to `BLOCKED_ON_HUMAN` | Member C | `WP-06`, `D-024`, `B-011`, `H-014` |
| `2026-11-11` | Uploaded the pinned real Tartan sample and ran both workflows: WP-05 run [42689267328](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42689267328) and WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411) `PASS` on `phase2/wp06-tracking-facts` at `ecce8ec`; accepted staging rows `> 0`, facts reconciled, `B-011` resolved | Member C | `WP-06`, `B-011`, `H-014` |
| `2026-11-11` | Merged PR #12 into `main` as `f29b099`; recorded `WP-06` `DONE` and `G4` `DONE` under `D-024`, closed the `D-024` window, and set `WP-07` `BLOCKED_ON_HUMAN` on `H-013` | Member C | `WP-06`, `G4`, `D-024`, `WP-07`, `H-013` |
| `2026-11-11` | Documentation-only closeout: synchronized the status board, contracts, plan, manuals, ETL/dictionary notes, and workflow notes to the completed `WP-06`/`G4` state and the `WP-07` handoff; no code, SQL, workflow, or test changes | Member C | `WP-06`, `G4`, `WP-07`, `H-013` |
| `2026-11-13` | Created the accepted-limitation register `L-001`–`L-007` with implementation triggers and audit hooks, verified the live warehouse read-only (DQ and WP-10 `PASS`), and opened `B-012` for the WP-07 verifier's missing `reportlab` dependency | Member A | `D-028`, `L-001`–`L-007`, `B-012` |
| `2026-11-13` | Fixed the WP-07 verifier dependency and recorded the passing rollback run `43473293723`: idempotent re-derivation, 7/7 integrity checks 0, 105 unit tests; `B-012` `RESOLVED` | Member A | `B-012`, `WP-07` |
| `2026-11-13` | Added source-coverage guards `DQ-G-001`–`DQ-G-004`, a coverage table in both PDFs, and register entries `L-008`/`L-009` with a coverage completion plan; read-only WP-08 run `43478821521` (36 checks, 30 PASS / 6 WARN / 0 FAIL) and WP-09 run `43478947023` both `PASS` | Member A | `D-029`, `L-008`, `L-009`, `WP-08`, `WP-09` |
| `2026-11-14` | Implemented the WP-11 ingestion job and workflow with a validate/apply split, transactional apply and rollback-on-`CRITICAL`, gated weekly schedule, and per-source coverage plus `L-001`–`L-010` lines in the run summary; recorded `L-010`; live validate 23,414 read / 23,254 accepted / 160 rejected with no database access | Member A | `D-030`, `L-010`, `WP-11` |

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
| Authorized scope | Phase 2 implementation under gated work packages; `WP-02`–`WP-10` accepted (`D-023`/`D-024` windows closed); `WP-11` implementation authorized 2026-11-14 (`D-030`) |
| Next gate to clear | None open for coding; `WP-11` acceptance and `WP-12` release evidence remain with the human (`H-015`–`H-017`) |

### Package acceptance

| Package | Accepted by | Date | Evidence |
|---|---|---|---|
| `WP-02` | `HassanNawaz14` | `2026-11-07` | Run [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288) `PASS`; PR #3 merged as `b6b76b9`. The agent marked it `DONE` on HassanNawaz14's explicit instruction. |
| `WP-03` | `HassanNawaz14` | `2026-11-08` | Reviewed and merged via PR #5 (`f9087f4`). Source records in [`docs/source_validation/`](docs/source_validation/): Tartan, Nightjar, DJI, FAA, and METAR all `PASS` (IEM `PASS WITH LIMITATION`), capacity estimate recorded. The agent marked it `DONE` on HassanNawaz14's explicit instruction. |
| `WP-04` | `HassanNawaz14` / Member B | `2026-11-08` | DDL runs [42474788058](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42474788058) and [42477720902](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42477720902); 15/15 access self-check. Accepted under `D-023`; the real accepted-row proof moved to `WP-06` (`B-011`, now resolved). |
| `WP-05` | Member C | `2026-11-08` | Six dimensions, `-1` members, unique natural keys, FK targets, and reader `SELECT` verified on Neon; 169 `dim_time` rows; dictionary/DBML synced. Accepted under `D-023`. |
| `WP-06` | Member D | `2026-11-11` | WP-05 run [42689267328](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42689267328) and WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411) `PASS` on `phase2/wp06-tracking-facts` at `ecce8ec`; PR #12 merged as `f29b099`. Accepted under `D-024`; `B-011` resolved. |

### Gate acceptance

| Gate | Accepted by | Date | Evidence |
|---|---|---|---|
| `G2` | `HassanNawaz14` | `2026-11-08` | `WP-02` access proof (run `42276737288`) and `WP-03` source validation merged in PR #5. A later privilege gap is tracked separately as `H-011`/`B-009` and does not reopen `G2`. |
| `G3` | `HassanNawaz14` (recorded by the Member A agent on explicit instruction) | `2026-11-09` | `WP-04` DDL runs `42474788058`/`42477720902`, `WP-05` Neon verifier PASS (six dimensions, `-1` members, unique natural keys, FK targets, reader SELECT), 169 `dim_time` rows, dictionary/DBML synced. Caveat `B-011`: the `WP-04` sample came from the legacy demo CSV, so real accepted-row proof is required in `WP-06` before `G4`. |
| `G4` | Member C (recorded under `D-024`) | `2026-11-11` | Real Tartan sample loaded; WP-05 run [42689267328](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42689267328) and WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411) `PASS`; PR #12 merged as `f29b099`; `B-011` resolved. |


## 2026-11-13 Member E completion and admin gate decision

The current requester, stating they hold project-administrator authority, has expressly accepted **G5, G6 and G7**, including the documented method and source limitations. This is an **administrative decision**, not an invented independent execution result. WP-07–WP-10 are accepted as complete. WP-11/WP-12 and missing independent reader/end-to-end evidence stay visible as technical follow-up. See [gate sign-off record](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

| Package | Admin acceptance | Deployed evidence |
|---|---|---|
| WP-07 | DONE | Persisted 27,479 mapped tracking records, 3,658 real 2D grid cells, 1,754 occupancy records; documented zero encounters/restrictions |
| WP-08 | DONE | Audit run 7, 32 checks: 29 PASS, 3 WARN, 0 FAIL |
| WP-09 | DONE | Both improved PDFs on main |
| WP-10 | DONE | Ten real reporting views in Neon |
| G5 / G6 / G7 | DONE by requester-admin declaration | Independent G7 replay, second-member reader proof and WP-11 automation not independently observed; follow-up explicitly documented |
