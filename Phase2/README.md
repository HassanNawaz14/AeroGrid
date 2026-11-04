# AeroGrid Phase 2 - Physical Data Warehouse and ETL

Phase 2 turns the Phase 1 dimensional design into a shared, reproducible PostgreSQL
data warehouse loaded from real public data. This directory is the control point for
Phase 2 documentation, planning, status, and future implementation.

**Implementation status: NOT AUTHORIZED.** The documentation and folder baseline is
ready for human review. No Phase 2 code, database object, or cloud resource exists.
The next human gate is `G1`.

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

## Proposed architecture at a glance

| Layer | Proposed choice | Purpose |
|---|---|---|
| Warehouse | Neon Free PostgreSQL, `aws-us-east-2` | Shared `project_staging`, `project_dw`, `project_reporting` |
| Raw archive | Neon Object Storage, 5 GB/project | Source zip/CSV/JSON snapshots with manifest |
| Automation | GitHub Actions, weekly + manual | Ingest, stage, load, validate, publish reports |
| ETL runtime | Python 3.11, psycopg2, pandas, boto3, shapely | No Docker, no local database |
| Reports | ReportLab | Data Cleaning and Data Quality PDFs |
| Team access | Neon organization + read-only SQL role | All five members query the same warehouse |

These are planning decisions proposed in [DECISIONS.md](DECISIONS.md). Confirm them
before provisioning any cloud resource.

## Planned data scope

The recommended scope is multi-site so that every fact has real supporting data:

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
| `G0` | Documentation baseline complete and links valid | `READY_FOR_REVIEW` |
| `G1` | Human prerequisites and approvals | **IN PROGRESS / BLOCKED_ON_HUMAN** |
| `G2` | Platform and source readiness validated | `NOT_STARTED` |
| `G3` | Staging, dimensional schema, and keys validated | `NOT_STARTED` |
| `G4` | Core tracking and journey facts loaded | `NOT_STARTED` |
| `G5` | Derived facts and thresholds validated | `NOT_STARTED` |
| `G6` | DQ, reports, views, and automation complete | `NOT_STARTED` |
| `G7` | End-to-end run and team access demonstrated | `NOT_STARTED` |

| Work package | Owner | Status |
|---|---|---|
| `WP-00` Documentation and folder baseline | Member A | `READY_FOR_REVIEW` |
| `WP-01` Human prerequisites and shared platform | Member A + human | `BLOCKED_ON_HUMAN` |
| `WP-02` Platform validation and access proof | Member A | `NOT_STARTED` |
| `WP-03` Source validation and georeferencing | Member B | `NOT_STARTED` |
| `WP-04` Staging DDL and loaders | Member B | `NOT_STARTED` |
| `WP-05` Dimensions, keys, and dictionary | Member C | `NOT_STARTED` |
| `WP-06` Tracking and journey facts | Member D | `NOT_STARTED` |
| `WP-07` Derived facts | Member E | `NOT_STARTED` |
| `WP-08` Data-quality framework | Member E | `NOT_STARTED` |
| `WP-09` PDF reports | Member E | `NOT_STARTED` |
| `WP-10` Reporting views and corridor metrics | Member E | `NOT_STARTED` |
| `WP-11` CI, access, and deployment | Member A | `NOT_STARTED` |
| `WP-12` Integration, acceptance, and release | Member A + all | `NOT_STARTED` |

## Current blockers and next action

**Blocker:** implementation is intentionally blocked until the human completes `G1`.

**Next human action:** review this documentation baseline, confirm or change the
proposed decisions, assign real names to Members B-E, and complete the human action
queue in [PROGRESS.md](PROGRESS.md). `H-002` remains blocked until Members B-E choose
roles and provide real names.

Do not create Neon, GitHub, or database resources from an agent session. The human
operating manual lists the exact prerequisites and safe order.

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
├── sql/                      # Future DDL and load scripts (empty by design)
├── etl/                      # Future Python ETL package (empty by design)
├── tests/                    # Future parser, SQL, and DQ tests (empty by design)
└── reports/                  # Future generated PDF reports (empty by design)
```

The `sql/`, `etl/`, `tests/`, and `reports/` folders contain README placeholders.
They exist to establish ownership and boundaries. They must remain free of
implementation until `G1` is cleared and the relevant work package is authorized.

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
