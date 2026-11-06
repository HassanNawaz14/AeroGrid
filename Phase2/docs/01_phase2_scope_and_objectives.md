# Phase 2 Scope and Objectives

## Purpose

Phase 2 implements the physical AeroGrid data warehouse and ETL pipeline. It converts
the Phase 1 dimensional design into PostgreSQL schemas, real-data ingestion, staging
cleaning, dimension and fact loads, data-quality evidence, and reporting views.

The deliverable is a reproducible analytical warehouse, not a live air-traffic
system. The refresh cadence is weekly or manual.

## Course requirements

From [`DWBI Lab Phase 2.pdf`](../DWBI%20Lab%20Phase%202.pdf):

- PostgreSQL database SQL scripts.
- Staging schema SQL.
- Data warehouse schema SQL.
- ETL scripts in SQL or Python.
- Dimension load scripts.
- Fact load scripts.
- Data Cleaning Report PDF.
- Data Quality Report PDF.
- A GitHub repository link.
- At least **100 dimension records** and **10,000 fact records**.

Required schemas:

- `project_staging`
- `project_dw`
- `project_reporting`

Required techniques:

- Staging transformations: deduplication, null handling, text standardization, type
  conversion.
- Surrogate keys for dimensions.
- Fact loading through business-key to surrogate-key mapping.
- Data-quality checks for completeness, accuracy, and integrity.

## Objectives

1. Build a clean, documented logical and physical model from real data.
2. Preserve the five Phase 1 business processes and fact grains.
3. Add `dim_site` so real multi-site data can coexist without synthetic records.
4. Load and reconcile real manned, UAS, weather, and airspace data.
5. Make surrogate-key generation and fact mapping explicit and testable.
6. Prove data quality with stored check results and generated PDF reports.
7. Provide one shared warehouse readable by all five members.
8. Automate the pipeline with a weekly/manual GitHub Actions workflow.
9. Keep the design within free tiers and without local databases or Docker.

## In scope

- Phase 2 documentation and planning baseline (complete).
- Future SQL DDL for the three schemas.
- Future Python ETL package and tests.
- Real source acquisition from the approved public sources.
- Raw archival in cloud object storage with a provenance manifest.
- Dimension and fact loads.
- Data cleaning and data-quality reports.
- Reporting views aligned with the ten business questions.
- Read-only access for all team members.
- GitHub Actions weekly/manual automation after authorization.

## Out of scope

- Editing Phase 1 `.tex` files or PDFs.
- Synthetic data generation.
- Local PostgreSQL, Docker, or dev containers.
- Paid infrastructure, paid data, or card-gated storage.
- Five-minute polling or a real-time streaming claim.
- A production service-level agreement.
- Power BI dashboard implementation; that belongs to Phase 3.
- Member-local warehouses.
- Statistical or machine-learning claims not supported by the real data.

## Deliverable outcomes

| Outcome | Evidence |
|---|---|
| Reproducible schema | Idempotent SQL scripts create all three schemas from scratch |
| Real ingestion | Source manifest with URLs, licenses, hashes, and timestamps |
| Clean staging | Accepted/rejected counts and documented rules |
| Dimensions | 100+ rows; natural keys; surrogate keys; unknown members |
| Facts | 10,000+ rows; no orphan foreign keys; source lineage |
| Data quality | Stored checks and a generated Data Quality Report PDF |
| Data cleaning | Generated Data Cleaning Report PDF |
| Shared access | All five members can query read-only without local PostgreSQL |
| Automation | Weekly/manual GitHub Actions workflow completes end to end |

## Success criteria

Phase 2 is successful when:

- The course deliverables exist and are reproducible.
- A clean run creates the warehouse, loads real data, and passes critical checks.
- No fact row lacks provenance.
- No orphan foreign keys exist.
- The warehouse remains below the free-tier 1 GB database budget.
- Raw archives remain below the 5 GB object-storage budget.
- All five members can read the shared warehouse.
- The documentation makes the next action unambiguous for a human or agent.

## Constraints and assumptions

### Fixed constraints

- Real public data only.
- No synthetic records. Pre-existing synthetic demo files under `data/sample/` are
  retained only for offline illustration and are never loaded into Phase 2 (`D-017`).
- No local database or Docker.
- Free tools and free tiers only.
- Weekly or manual refresh.
- Shared five-member read access.
- Raw data outside Git.
- Phase 1 artifacts frozen.

### Confirmed assumptions

These were confirmed by the human at `G1` and are recorded in
[DECISIONS.md](../DECISIONS.md):

- Neon Free is the shared PostgreSQL platform (`D-001`).
- Neon Object Storage is the raw archive (`D-003`).
- The study scope is multi-site with `dim_site` (`D-010`).
- TartanAviation KBTP is the primary historical manned source (`D-012`).
- Nightjar and nominal-io DJI are the UAS sources (`D-011`).
- OpenSky is optional (`D-013`).

## Stakeholders

| Stakeholder | Interest |
|---|---|
| Course evaluator | Complete, reproducible Phase 2 deliverables |
| Team members A-E | Clear ownership and shared query access |
| Human project owner | Scope, accounts, secrets, and final approval |
| Coding agents | Exact contracts, boundaries, and stop conditions |
| Future maintainers | Decisions, provenance, and reproducible operations |

## Scope-change rule

Any change to sources, sites, facts, dimensions, grains, cadence, platform, or
access requires a human decision recorded in [DECISIONS.md](../DECISIONS.md). An
agent may propose a change but must not implement it silently.

## Definition of ready for implementation

Implementation may begin only when:

- `G1` is cleared (done 2026-11-04).
- Member names are recorded (done in `docs/08`; `H-002` deferred).
- The platform and source decisions are accepted (done, `D-001`-`D-019`).
- The assigned work package is `READY`.
- The human explicitly authorizes the work package.

`WP-02` and `WP-03` are currently authorized. `WP-02` is `BLOCKED_ON_HUMAN` on
`H-009`; `WP-03` is `READY`. Later packages start only after their gate is recorded in
`PROGRESS.md`.
