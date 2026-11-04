# Phase 2 Progress and Handoff Board

This is the canonical status board for AeroGrid Phase 2. Every agent and human must
read it before acting. Update it at the end of every work session.

| Field | Value |
|---|---|
| Last updated | `2026-11-04` |
| Phase state | `BASELINE_ACCEPTED_GATE_G1_IN_PROGRESS` |
| Implementation authorized | `NO` |
| Current gate | `G1 - Human prerequisites` |
| Current gate status | `BLOCKED_ON_HUMAN` |
| Active work package | `WP-01` human prerequisites and shared platform |
| Active work package status | `BLOCKED_ON_HUMAN` |
| Next work package | `WP-02` after `G1` clearance |
| Next action owner | HassanNawaz14 (Member A) |

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
| `G1` | Human approvals, named owners, Neon/GitHub access, and secrets ready | `BLOCKED_ON_HUMAN` | HassanNawaz14 |
| `G2` | Platform access and source validation spikes pass | `NOT_STARTED` | HassanNawaz14 / Member B |
| `G3` | Staging, physical schema, constraints, indexes, keys, and seeds validated | `NOT_STARTED` | Members B/C |
| `G4` | Core tracking and journey facts loaded and reconciled | `NOT_STARTED` | Member D |
| `G5` | Derived facts and approved thresholds validated | `NOT_STARTED` | Member E |
| `G6` | DQ, reports, reporting views, and automation validated | `NOT_STARTED` | Member E / HassanNawaz14 |
| `G7` | A clean end-to-end run and team read access are demonstrated | `NOT_STARTED` | HassanNawaz14 |

`G0` documentation baseline has been reviewed and accepted by HassanNawaz14 (`H-001`). The substantive implementation gate remains `G1`.

## Work package status

| WP | Title | Owner | Depends on | Status | Next action |
|---|---|---|---|---|---|
| `WP-00` | Documentation and folder baseline | HassanNawaz14 | none | `DONE` | Accepted via `H-001` |
| `WP-01` | Human prerequisites and shared platform | HassanNawaz14 | `WP-00` | `BLOCKED_ON_HUMAN` | HassanNawaz14 executes `H-004` to `H-007` (`H-002` blocked; `H-003` and `H-008` resolved) |
| `WP-02` | Platform validation and access proof | HassanNawaz14 | `WP-01` | `NOT_STARTED` | Wait for `G1` |
| `WP-03` | Source validation and georeferencing | Member B | `WP-01` | `NOT_STARTED` | Wait for `G1`; can prepare read-only checks |
| `WP-04` | Staging DDL and loaders | Member B | `WP-03` | `NOT_STARTED` | Wait for `G2` |
| `WP-05` | Dimensions, keys, and dictionary | Member C | `WP-02`, model approval | `NOT_STARTED` | Wait for `G2` |
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
| `H-002` | Assign real names to Members B-E | Work packages need accountable owners | Edit placeholder table in [docs/08_team_work_division.md](docs/08_team_work_division.md) once other team members choose roles | `BLOCKED` |
| `H-003` | Create the Neon project, database, and object-storage bucket | The shared warehouse and raw archive are human-owned resources | Recorded in the Neon resource record: project `AeroGrid-DW`, branch `production`, database `neondb`, bucket `aerogrid-raw`, ETL role `aerogrid_etl` | `DONE` |
| `H-004` | Add GitHub environment secrets for the warehouse | CI cannot connect to Neon without secrets | HassanNawaz14 creates `warehouse` environment in GitHub settings and adds secrets | `OPEN` |
| `H-005` | Invite the other members and create read-only access | All five members must read the shared warehouse | HassanNawaz14 invites members through Neon/GitHub and provisions read-only SQL role | `OPEN` |
| `H-006` | Confirm data licenses, attribution, and optional OpenSky access | Redistribution and source-use terms must be confirmed | HassanNawaz14 reviews [docs/03_data_sources_and_licensing.md](docs/03_data_sources_and_licensing.md) | `OPEN` |
| `H-007` | Explicitly authorize Phase 2 implementation | Opens the implementation phase | After `H-002` to `H-006` complete (`H-008` resolved), HassanNawaz14 sets `implementation_authorized: YES` and assigns `WP-02`/`WP-03` | `OPEN` |
| `H-008` | Confirm handling of the tracked legacy synthetic samples under `data/sample/` | Prevents synthetic demo files from being mistaken for real Phase 2 data | HassanNawaz14 confirmed the five files are intentionally retained as demo-only artifacts for offline user/evaluator viewing; excluded from all Phase 2 loads and reports; `D-017` | `DONE` |

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
| `H-004` | Configure the GitHub `warehouse` environment and secrets | Confirm the repo is public (or accept the private-repo Actions budget); create the `warehouse` environment; add `DATABASE_URL` from the `aerogrid_etl` role (not `neondb_owner`), `NEON_S3_ENDPOINT`, `NEON_S3_REGION` (`us-east-2`), `NEON_S3_BUCKET` (`aerogrid-raw`), `NEON_S3_ACCESS_KEY_ID`, `NEON_S3_SECRET_ACCESS_KEY`; optional `OPENSKY_CLIENT_ID`, `OPENSKY_CLIENT_SECRET`, `SOURCE_TIMEZONE`, `REPORT_PUBLISH_MODE`; enable required reviewers if available; never paste values into chat or repository files. | Environment and secret names exist; no values in Git/chat; `H-004` `DONE` |
| `H-005` | Invite members and establish read-only access | Invite Members B-E to the Neon organization and GitHub as needed; create `aerogrid_reader`; grant `CONNECT`, `USAGE`, and `SELECT` after the schema/views exist; test one `SELECT` per reporting view; share the read-only connection string privately. At `G1`, invitations sent plus a recorded read-only plan is sufficient; actual grants follow `WP-04`/`WP-05`/`WP-10`. | Invitations sent; role/plan recorded; `H-005` `DONE` |
| `H-006` | Confirm licenses, attribution, and optional OpenSky access | Review [docs/03_data_sources_and_licensing.md](docs/03_data_sources_and_licensing.md); confirm Tartan (CC BY 4.0), Nightjar (CC BY 4.0), nominal-io DJI (MIT), FAA/NOAA open data, and IEM terms; confirm or explicitly defer OpenSky; record the decision. | Recorded in [DECISIONS.md](DECISIONS.md)/this file; `H-006` `DONE` |
| `H-007` | Explicitly authorize Phase 2 implementation | Confirm `H-002` to `H-006` are resolved (`H-008` is resolved by `D-017`); set `implementation_authorized: YES`; mark `G1` `DONE` with date and approver; record the authorization scope; assign `WP-02` and `WP-03`. | `G1` `DONE`; `WP-02`/`WP-03` assigned |
| `G-01` | Protect `main` and confirm repository settings | Settings > Branches: require pull requests, one approval, status checks when workflows exist, and disallow direct pushes; confirm the `warehouse` environment reviewers; confirm repository visibility. | Settings confirmed |
| `G-02` | Confirm schedule and report parameters | Choose the weekly cron time (for example Monday 06:00 UTC); confirm manual dispatch inputs (`start_date`, `end_date`, `publish_reports`, `sites`); choose `REPORT_PUBLISH_MODE` (`artifact` or `commit`); record the choices. | Choices recorded in [DECISIONS.md](DECISIONS.md)/this file |

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
| `B-001` | Phase 2 implementation is not authorized | No SQL, ETL, CI, or cloud resource work can begin | `H-007` | `OPEN` |
| `B-002` | CI secrets and member access are incomplete | Cannot run CI or give members read access | `H-004`, `H-005` | `OPEN` |
| `B-003` | Proposed platform and source decisions need confirmation | Cannot freeze architecture or source contracts | `H-001`, `H-006` | `RESOLVED` (Accepted by HassanNawaz14 via `H-001`) |
| `B-004` | TartanAviation georeferencing is not yet validated | Spatial facts may need a fallback design | Authorize `WP-03` source spike | `OPEN` |
| `B-005` | Documentation baseline is awaiting human acceptance | `G0`/`G1` cannot close | `H-001` | `RESOLVED` (Accepted by HassanNawaz14) |
| `B-006` | Legacy synthetic files remain tracked under `data/sample/` | They are intentionally retained for offline demo/evaluator viewing and must not be mistaken for real data | `H-008`, `D-017` | `RESOLVED` (Retained as documented demo-only samples via `D-017`) |

## Documentation baseline evidence

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

## Handoff log

| Date | From | To | Work package | Summary | Files | Checks | Next step |
|---|---|---|---|---|---|---|---|
| `2026-11-03` | Member A | Human | `WP-00` | Completed Phase 2 documentation, plan, templates, folder boundaries, and stale-doc updates. No implementation created. | `AGENTS.md`, `Phase2/**`, root `README.md`, `data/**`, `docs/LowAltitude_..._Guide.md`, `.gitignore`, `.github/workflows/README.md` | 213 links checked; no implementation/secret files; DBML balanced; `git diff --check` clean | Human reviews `H-001` to `H-008` |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | Documented the demo-only retention of legacy samples and saved the remaining G1 human actions. No implementation created. | `data/sample/README.md`, `.gitignore`, `Phase2/PROGRESS.md`, `Phase2/DECISIONS.md`, `Phase2/README.md`, `Phase2/docs/01`, `03`, `06`, `07`, `08`, `09`, `10`, `11`, `Phase2/dev_plan/01`, `02`, root `README.md`, `data/all_data_summary.md` | Link/grep checks and `git diff --check`; no secrets/raw data added | Complete `H-004` to `H-007`; `H-002` remains blocked |
| `2026-11-04` | HassanNawaz14 | Human/team | `WP-01` | Recorded `H-003` Neon resources; `H-003` done; `H-004` is next. | `Phase2/PROGRESS.md`, `Phase2/docs/07`, `Phase2/docs/10` | `git diff --check`; no secrets recorded | Complete `H-004` |

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
| Authorized by | not yet authorized |
| Authorization date | not applicable |
| Authorized scope | documentation only |
| Next gate to clear | `G1` |
