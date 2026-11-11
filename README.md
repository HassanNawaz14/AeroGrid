# AeroGrid: Low-Altitude Airspace Intelligence Warehouse

AeroGrid is a data-warehousing project for low-altitude airspace intelligence. It
combines real public flight telemetry, weather, and airspace-restriction data to study
mixed manned/UAS traffic, close encounters, restriction compliance, and corridor
capacity.

## Current status

| Phase | State |
|---|---|
| Phase 1 | Complete and frozen as the historical design baseline |
| Phase 2 | Documentation baseline accepted (`G0`/`H-001`) |
| Phase 2 implementation | **Authorized** 2026-11-04 (`H-007`) |
| Current human gate | `G5 - Derived facts and approved thresholds` |
| Current work packages | `WP-02`-`WP-06`, `DONE`; `WP-07` (Member E), `BLOCKED_ON_HUMAN` on `H-013` |

Nothing in `Phase1/` should be edited. Phase 2 work is controlled from
[`Phase2/`](Phase2/README.md), and the current status, blockers, and human action queue
are in [`Phase2/PROGRESS.md`](Phase2/PROGRESS.md).

## Start here

| Audience | Read |
|---|---|
| Human reviewer | [`Phase2/README.md`](Phase2/README.md), then [`Phase2/docs/10_human_operating_manual.md`](Phase2/docs/10_human_operating_manual.md) |
| Coding agent | [`AGENTS.md`](AGENTS.md), then [`Phase2/AGENTS.md`](Phase2/AGENTS.md), then [`Phase2/docs/09_agent_operating_manual.md`](Phase2/docs/09_agent_operating_manual.md) |
| New team member | [`Phase2/docs/08_team_work_division.md`](Phase2/docs/08_team_work_division.md) |
| Architecture | [`Phase2/docs/02_architecture_and_platform.md`](Phase2/docs/02_architecture_and_platform.md) |
| Sources and licenses | [`Phase2/docs/03_data_sources_and_licensing.md`](Phase2/docs/03_data_sources_and_licensing.md) |
| Data model | [`Phase2/docs/04_data_model.md`](Phase2/docs/04_data_model.md) |
| Work packages | [`Phase2/dev_plan/01_work_breakdown.md`](Phase2/dev_plan/01_work_breakdown.md) |
| Decisions | [`Phase2/DECISIONS.md`](Phase2/DECISIONS.md) |

## Phase 2 objective

Build a shared, cloud-hosted PostgreSQL warehouse with:

- `project_staging`, `project_dw`, and `project_reporting` schemas.
- Real source acquisition, cleaning, rejects, and provenance.
- Six dimensions and five facts with surrogate keys.
- At least 100 dimension rows and 10,000 fact rows from real data.
- Data-quality checks and two PDF reports.
- SQL and Python ETL scripts in a public GitHub repository.
- Read access for all five team members.
- Weekly or manual scheduled automation.

The Phase 2 course brief is
[`Phase2/DWBI Lab Phase 2.pdf`](Phase2/DWBI%20Lab%20Phase%202.pdf).

## Non-negotiable constraints

- **Real public data only.** No synthetic flights, weather, vehicles, restrictions, or
  encounters.
- **No local PostgreSQL dependency.** The warehouse is cloud-hosted and shared.
- **No Docker**, dev containers, or local service containers.
- **Free tiers only.** No credit card, paid plan, trial conversion, or billing account.
- **Weekly or manual refresh.** No five-minute polling.
- **All five members can read** the shared warehouse.
- **Raw data stays out of Git** and in cloud object storage with a provenance manifest.
- **No secrets in the repository.** Humans add them through GitHub/Neon UI.
- **Phase 1 is frozen.** Do not edit its `.tex` or PDF files.
- **Implementation is authorized by work package.** `WP-02`-`WP-06` are `DONE`
  (PR #3 `b6b76b9`, #5 `f9087f4`, #7, #8, #12 `f29b099`). `G2` closed 2026-11-08,
  `G3` on 2026-11-09, and `G4` on 2026-11-11 after the real Tartan WP-05/WP-06 runs
  passed and `B-011` was resolved. The `D-024` window is closed. `WP-07` is
  `BLOCKED_ON_HUMAN` on `H-013`; later packages wait for their gate.

## Accepted Phase 2 architecture

| Layer | Accepted choice | Purpose |
|---|---|---|
| Warehouse | Neon Free PostgreSQL, `aws-us-east-2` | Shared staging, warehouse, reporting schemas |
| Raw archive | Neon Object Storage | Source archives with URL/license/hash manifest |
| Automation | GitHub Actions, weekly + manual | Ingest, stage, load, validate, publish reports |
| ETL | Python 3.11, psycopg2, pandas, boto3, shapely | No Docker, no local database |
| Reports | ReportLab | Data Cleaning and Data Quality PDFs |
| Access | Neon organization + read-only SQL role | Five-member shared read access |

These are accepted decisions in [`Phase2/DECISIONS.md`](Phase2/DECISIONS.md)
(`D-001`-`D-019`). The Neon project and raw bucket exist; application schemas, ETL, and
workflows do not yet.

## Accepted real-data scope

- **TartanAviation KBTP ADS-B:** primary historical manned traffic, CC BY 4.0.
- **Nightjar PA UAS flights:** real 10 Hz DJI telemetry, CC BY 4.0.
- **Nominal-io DJI:** real Colorado/Palos Verdes flight CSVs, MIT.
- **FAA UDDS:** airspace, UAS facility maps, and restrictions, public data.
- **NOAA AWC / IEM ASOS:** current and historical METAR, public data.
- **OpenSky:** optional only; historical Trino access is not assumed.

The full source list, URLs, caveats, and validation status is in
[`Phase2/docs/03_data_sources_and_licensing.md`](Phase2/docs/03_data_sources_and_licensing.md).

## Model at a glance

Dimensions:

`dim_time`, `dim_site`, `dim_vehicle`, `dim_spatial_grid`, `dim_weather`,
`dim_airspace_zone`

Facts:

`fact_vehicle_tracking`, `fact_flight_journey`, `fact_close_encounter`,
`fact_restriction_activation`, `fact_airspace_occupancy`

Phase 2 keeps the five Phase 1 business processes and adds a site dimension, exact
fact timestamps, provenance, altitude datums, weather keys, journey endpoints,
restriction windows, and reporting views. See
[`Phase2/docs/04_data_model.md`](Phase2/docs/04_data_model.md).

## Team division

| Member | Scope |
|---|---|
| Member A | Platform, CI, access, integration, release |
| Member B | Sources, raw archive, staging, cleaning |
| Member C | Schema, dimensions, keys, data dictionary |
| Member D | Tracking and journey facts |
| Member E | Derived facts, data quality, reporting views, PDFs |

Member A is HassanNawaz14; Members B-E are recorded in
[`Phase2/docs/08_team_work_division.md`](Phase2/docs/08_team_work_division.md).
`H-002` remains deferred by the human.

## Repository map

```text
AeroGrid/
├── AGENTS.md                 # Repository-wide agent contract
├── Phase1/                   # Frozen historical design artifacts
├── Phase2/                   # Phase 2 control point
│   ├── AGENTS.md             # Phase-specific agent contract
│   ├── README.md             # Phase 2 dashboard
│   ├── PROGRESS.md           # Status, gates, human actions, handoffs
│   ├── DECISIONS.md          # Decision log
│   ├── docs/                 # Canonical Phase 2 documentation
│   ├── dev_plan/             # Work packages, dependencies, acceptance
│   ├── templates/            # Work package and review templates
│   ├── sql/                  # Schema, staging, dimension DDL and grants
│   ├── etl/                  # Python loaders, verifiers, and tests
│   ├── tests/                # Parser, SQL, and DQ tests
│   └── reports/              # Generated PDF reports (not built yet)
├── data/                     # Phase 1 data documentation and legacy samples
├── docs/                     # Phase 1 guide and overview PDFs
└── .github/workflows/        # Validation, staging, and dimension workflows
```

## Data status

- The data documentation under `data/` has been synchronized with the Phase 2 model.
- The legacy `data/sample/` files are synthetic demo artifacts retained intentionally
  for offline user/evaluator viewing. They are excluded from Phase 2, are never loaded
  or cited as real data, and are documented in
  [`data/sample/README.md`](data/sample/README.md) (`D-017`).
- Raw Phase 2 archives belong in object storage, not in Git.

## What happens next

`G4` is recorded and `WP-06` is `DONE`. The next actions are:

1. HassanNawaz14: approve `H-013` (severe: horizontal `< 0.5 nm` and vertical
   `< 500 ft`; proximity: horizontal `< 1.0 nm` and vertical `< 1,000 ft`; plus
   `algorithm_version`), restore the `warehouse` environment reviewers, and confirm
   the main-branch protection ruleset in
   [`Phase2/docs/10_human_operating_manual.md`](Phase2/docs/10_human_operating_manual.md).
2. Member E: start `WP-07` derived facts immediately after `H-013` is approved, using
   the brief in
   [`Phase2/dev_plan/01_work_breakdown.md`](Phase2/dev_plan/01_work_breakdown.md#wp-07-derived-facts).

Human-only actions still apply: secrets, Neon roles, repository and environment
settings, destructive SQL, thresholds, and gate acceptance. Later work packages wait
until their gate is recorded.
