# AeroGrid Phase 2 - Physical Data Warehouse and ETL

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

Phase 2 turns the Phase 1 dimensional design into a shared, reproducible PostgreSQL
data warehouse loaded from real public data. This directory is the control point for
Phase 2 documentation, planning, status, and future implementation.

**Current status (2026-11-13):** WP-07 through WP-10 have been merged and deployed. The requester, who states they hold project-administrator authority, explicitly accepted G5/G6/G7. The independent end-to-end replay, full reader-access checks and WP-11/12 automation proof have not been independently supplied and remain documented follow-ups. G0–G4 retain their original historical evidence.

## Quick links

| Audience | Start here |
|---|---|
| Human reviewer | [docs/10_human_operating_manual.md](docs/10_human_operating_manual.md) |
| Coding agent | [AGENTS.md](AGENTS.md), then [docs/09_agent_operating_manual.md](docs/09_agent_operating_manual.md) |
| Status and blockers | [PROGRESS.md](PROGRESS.md) |
| Work packages | [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md) |
| Accepted data limitations | [docs/13_accepted_data_limitations.md](docs/13_accepted_data_limitations.md) |
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

| Gate | Current status |
|---|---|
| G0–G4 | DONE (historical accepted evidence) |
| G5 | DONE — requester-admin acceptance (D-025) |
| G6 | DONE — requester-admin acceptance (D-026) |
| G7 | DONE — requester-admin declaration (D-027; independent proof outstanding) |

| Work package | Status | Evidence |
|---|---|---|
| WP-07 | DONE (admin accepted) | 27,479 mapped, 3,658 real cells, 1,754 occupancy |
| WP-08 | DONE (admin accepted) | 32 stored DQ results (29 PASS, 3 WARN, 0 FAIL) |
| WP-09 | DONE (admin accepted) | Two improved live-source PDF reports on main |
| WP-10 | DONE (admin accepted) | Ten deployed reporting views |
| WP-11 / WP-12 | Technical follow-up | Independent G7 run, readers, and automation checks not independently observed |

## Current blockers and next action

H-013 is historically resolved. The requester has accepted G5/G6/G7 and the Member E packages. The remaining action is to archive independent WP-11/12 evidence rather than repeat already persisted WP-07–WP-10 implementation. See [final acceptance](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

The seven accepted data limitations are tracked with implementation triggers in
[docs/13_accepted_data_limitations.md](docs/13_accepted_data_limitations.md); they are
audit obligations for `WP-11` and `WP-12`, not closed items. `B-012` (WP-07 verifier
missing `reportlab`) was fixed and the rollback verification now passes.

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
(`WP-04` staging, `WP-05` dimensions, `WP-06` core facts merged on `main`). Later
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
