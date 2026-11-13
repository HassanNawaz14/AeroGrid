# AeroGrid: Low-Altitude Airspace Intelligence Warehouse

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](Phase2/docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

AeroGrid is a data-warehousing project for low-altitude airspace intelligence. It
combines real public flight telemetry, weather, and airspace-restriction data to study
mixed manned/UAS traffic, close encounters, restriction compliance, and corridor
capacity.

## Current status

| Phase | Current status |
|---|---|
| Phase 1 | Complete and frozen |
| Phase 2 | Shared Neon warehouse, DQ, views, and PDFs deployed |
| WP-07 to WP-10 | DONE by requester-admin acceptance (2026-11-13) |
| G5 / G6 / G7 | DONE by requester-admin declaration; missing independent G7 proof is disclosed |
| WP-11 / WP-12 | Member A/team technical evidence follow-up pending separate verification |

See [Phase 2 progress](Phase2/PROGRESS.md) and [the final acceptance record](Phase2/docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

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
│   └── reports/              # Generated Data Cleaning and Data Quality PDFs
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

The user-authorized administrator has declared G5/G6/G7 accepted as of 2026-11-13. WP-07–WP-10 implementation, two improved reports and ten views are merged into main. Independently obtain the full G7 replay, second-member read-only access evidence and WP-11/12 automation proof before claiming those particular technical checks succeeded.

