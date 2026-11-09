# AeroGrid Phase 2 - Physical Data Warehouse and ETL

Phase 2 turns the Phase 1 dimensional design into a shared, reproducible PostgreSQL
data warehouse loaded from real public data. This directory is the control point for
Phase 2 documentation, planning, status, and future implementation.

**Implementation status: AUTHORIZED (2026-11-04, `H-007`).** `G0`-`G3` are closed.
`WP-02` (run `42276737288`, PR #3 `b6b76b9`), `WP-03` (PR #5 `f9087f4`), `WP-04` (PR
#7), and `WP-05` (PR #8) are `DONE`. `G3` was recorded on 2026-11-09 with `B-011`
open, so accepted real staging rows are proven by `WP-06`. `WP-06` is `IN_PROGRESS`
under the delegated window `D-024`: the fact DDL, ETL, verifier, workflow, and unit
tests are merged, and `02_dimensions/03_seed_real.sql` now seeds the real Tartan
`dim_vehicle` members from the pinned sample. Remaining work is the live
`warehouse` verification that closes `B-011`/`WP-06` and records `G4`; the checklist
is in [PROGRESS.md](PROGRESS.md). Human input is zero until `G4`.

## Quick links

| Audience | Start here |
|---|---|
| Human reviewer | [docs/10_human_operating_manual.md](docs/10_human_operating_manual.md) |
| Coding agent | [AGENTS.md](AGENTS.md), then [docs/09_agent_operating_manual.md](docs/09_agent_operating_manual.md) |
| Status and blockers | [PROGRESS.md](PROGRESS.md) |
| Work packages | [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md) |
| Team division | [docs/08_team_work_division.md](docs/08_team_work_division.md) |
| Decisions | [DECISIONS.md](DECISIONS.md) |
| Full documentation map | [docs/00_documentation_map.md](docs/00_documentation_map.md) |

## Phase 2 objective

Implement the Phase 2 deliverables required by
[`DWBI Lab Phase 2.pdf`](DWBI%20Lab%20Phase%202.pdf):

- PostgreSQL schemas named `project_staging`, `project_dw`, and
  `project_reporting`.
- A staging layer with real source acquisition and cleaning.
- Dimension and fact tables with surrogate keys.
- Fact loading through natural-key to surrogate-key mapping.
- Data-quality validation and reports.
- At least 100 dimension rows and 10,000 fact rows.
- SQL scripts, ETL scripts, Data Cleaning Report PDF, Data Quality Report PDF, and a
  GitHub repository link.

## Constraint summary

- **Real data only.** No synthetic flights, weather, vehicles, restrictions, or
  encounters.
- **Legacy samples are demo-only.** The small synthetic files under `data/sample/` are
  retained for offline user/evaluator viewing and are never loaded into Phase 2.
- **Cloud-only shared warehouse.** Neon Free PostgreSQL is the current proposal.
- **No Docker** and no local PostgreSQL dependency.
- **Free tiers only.** No credit card, paid plan, trial, or billing account.
- **Weekly or manual refresh.** No five-minute polling.
- **Five-member read access** to one shared warehouse.
- **Raw data in object storage.** Raw archives are not committed to Git.
- **No secrets in the repository.** Humans add them through the GitHub/Neon UI.

## Accepted architecture at a glance

| Layer | Proposed choice | Purpose |
|---|---|---|
| Warehouse | Neon Free PostgreSQL, `aws-us-east-2` | Shared `project_staging`, `project_dw`, `project_reporting` |
| Raw archive | Neon Object Storage, 5 GB/project | Source zip/CSV/JSON snapshots with manifest |
| Automation | GitHub Actions, weekly + manual | Ingest, stage, load, validate, publish reports |
| ETL runtime | Python 3.11, psycopg2, pandas, boto3, shapely | No Docker, no local database |
| Reports | ReportLab | Data Cleaning and Data Quality PDFs |
| Team access | Neon organization + read-only SQL role | All five members query the same warehouse |

These are accepted decisions in [DECISIONS.md](DECISIONS.md) (`D-001`-`D-019`).
Reconfirm free-tier limits before any capacity change.

## Accepted data scope

The accepted scope is multi-site so that every fact has real supporting data:

- **KBTP / Pittsburgh-Butler:** TartanAviation ADS-B, METAR, FAA airspace.
- **KAGC / Pittsburgh-Allegheny:** METAR and airspace context; Tartan KAGC only if
  georeferencing is validated.
- **Nightjar PA field site:** real 10 Hz DJI flight telemetry from Hugging Face.
- **Nominal-io DJI sites:** real Colorado/Palos Verdes flight CSVs from Hugging Face.

The canonical source list, licenses, URLs, caveats, and validation status are in
[docs/03_data_sources_and_licensing.md](docs/03_data_sources_and_licensing.md).

## Progress dashboard

Statuses use the vocabulary in [AGENTS.md](AGENTS.md). Detail is in
[PROGRESS.md](PROGRESS.md).

| Gate | Meaning | Status |
|---|---|---|
| `G0` | Documentation baseline complete and links valid | `DONE` (`H-001`) |
| `G1` | Human prerequisites and approvals | `DONE` (`H-007`; `H-002` deferred) |
| `G2` | Platform and source readiness validated | `DONE` 2026-11-08 (`WP-02`/`WP-03`; PR #5 `f9087f4`) |
| `G3` | Staging, dimensional schema, and keys validated | `DONE` 2026-11-09 (`WP-04`/`WP-05`; `B-011` open) |
| `G4` | Core tracking and journey facts loaded | `IN_PROGRESS` (`WP-06` under `D-024`; Member C records) |
| `G5` | Derived facts and thresholds validated | `NOT_STARTED` |
| `G6` | DQ, reports, views, and automation complete | `NOT_STARTED` |
| `G7` | End-to-end run and team access demonstrated | `NOT_STARTED` |

| Work package | Owner | Status |
|---|---|---|
| `WP-00` Documentation and folder baseline | Member A | `DONE` |
| `WP-01` Human prerequisites and shared platform | Member A + human | `DONE` |
| `WP-02` Platform validation and access proof | Member A | `DONE` |
| `WP-03` Source validation and georeferencing | Member B | `DONE` |
| `WP-04` Staging DDL and loaders | Member B | `DONE` (PR #7; sample caveat `B-011`) |
| `WP-05` Dimensions, keys, and dictionary | Member C | `DONE` (PR #8) |
| `WP-06` Tracking and journey facts | Member D | `IN_PROGRESS` (branch code ready; awaits Member C dims/S3; owner-closable under `D-024`) |
| `WP-07` Derived facts | Member E | `NOT_STARTED` |
| `WP-08` Data-quality framework | Member E | `NOT_STARTED` |
| `WP-09` PDF reports | Member E | `NOT_STARTED` |
| `WP-10` Reporting views and corridor metrics | Member E | `NOT_STARTED` |
| `WP-11` CI, access, and deployment | Member A | `NOT_STARTED` |
| `WP-12` Integration, acceptance, and release | Member A + all | `NOT_STARTED` |

## Current blockers and next action

**`G3` is recorded and `WP-06` is `IN_PROGRESS`.** `WP-02`-`WP-05` are `DONE`; platform
validation passed on 2026-11-07 (22 pass, 1 warn, 0 fail), source validation merged
in PR #5 (`f9087f4`), and the staging and dimension packages merged in PR #7 and PR
#8. `H-002` remains deferred by the human; the Member B-E names are recorded in
[docs/08_team_work_division.md](docs/08_team_work_division.md). `B-011` records that
the `WP-04` sample run used the excluded legacy demo CSV, so `WP-06` must show
accepted real staging rows and reconcile the tracking facts to them.

**Next actions:** `aerogrid-raw` was confirmed empty, so the human must upload the
extracted real sample as `samples/kbtp/01-01-22/1.csv` (`H-014`; 4,325,376 bytes,
SHA-256 `86342d09...a762`) before the acceptance run. Then run
`wp05-dimensions-verify.yml` to apply and validate `03_seed_real.sql`, and dispatch
`wp06-facts-verify.yml` from `main` to prove accepted real staging rows, fact counts,
reconciliation, idempotency, and zero orphans. Follow the `WP-06` collaborator
checklist in [PROGRESS.md](PROGRESS.md) to close `B-011`/`WP-06` and record `G4`.
Agent briefs are in [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md).
HassanNawaz14 returns after `G4` for `H-013` (WP-07 thresholds), the environment
restoration, and the main-branch protection check. Human-only actions still require
the human (secrets, Neon roles, repository and environment settings, destructive SQL,
gate acceptance after `G4`).

## Directory map

```text
Phase2/
├── README.md                 # This dashboard
├── AGENTS.md                 # Phase-specific agent contract
├── PROGRESS.md               # Status, gates, human action queue, handoffs
├── DECISIONS.md              # Decision log
├── DWBI Lab Phase 2.pdf      # Course brief (historical input)
├── docs/                     # Architecture, sources, model, ETL, DQ, manuals
├── dev_plan/                 # Work packages, gates, acceptance, handoffs
├── templates/                # Work package, handoff, validation, PR templates
├── sql/                      # Schema, staging, dimension DDL, seeds, grants
├── etl/                      # Python loaders, verifiers, and transforms
├── tests/                    # Parser, SQL, and DQ tests
└── reports/                  # Generated PDF reports (not built yet)
```

The `sql/`, `etl/`, and `tests/` folders hold work delivered by authorized packages
(`WP-04` staging, `WP-05` dimensions, `WP-06` core facts on feature branch). Later
packages add their own files when their gate is recorded.

## Documentation rules

- The documents in `docs/` are canonical for their subject.
- `PROGRESS.md` is the only canonical status board.
- `DECISIONS.md` is the only canonical decision log.
- `dev_plan/01_work_breakdown.md` is the only canonical work-package list.
- Update the canonical document when a decision, interface, source, or model changes.
- If documentation and implementation disagree, stop and ask the human.

## Phase 1 relationship

Phase 1 remains the historical design baseline. Its PDFs and `.tex` sources are
frozen. Phase 2 keeps the five business processes and five facts, but refines the
model for real multi-site data:

- Add `dim_site`.
- Add exact fact timestamps while keeping an hourly `dim_time`.
- Add source provenance and ETL run lineage.
- Add altitude datum, weather keys, journey endpoints, and restriction windows.
- Add reporting views and quality evidence required by Phase 2.

The full delta is in [docs/04_data_model.md](docs/04_data_model.md). The updated
logical dictionary is [`../data/data_dictionary.md`](../data/data_dictionary.md).
