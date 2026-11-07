# Phase 2 Decision Log

This file records material decisions for AeroGrid Phase 2. A decision that changes
scope, sources, model, cadence, platform, access, or capacity requires a human
decision. Use the template in [templates/DECISION_RECORD.md](templates/DECISION_RECORD.md).

## Decision status

| Status | Meaning |
|---|---|
| `ACCEPTED` | Explicitly accepted by the human or fixed by the project brief. |
| `PROPOSED` | Recommended baseline; not yet safe to provision or implement. |
| `SUPERSEDED` | Replaced by a later decision. |
| `REJECTED` | Evaluated and not selected. |

## Decision register

| ID | Decision | Status | Human confirmation |
|---|---|---|---|
| `D-001` | Use Neon Free PostgreSQL as the shared warehouse | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-002` | Use GitHub Actions for weekly and manual ETL | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-003` | Use Neon Object Storage for raw archives | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-004` | Use real data only; never synthetic data | `ACCEPTED` | Explicit user constraint |
| `D-005` | Do not use local PostgreSQL, Docker, or local service containers | `ACCEPTED` | Explicit user constraint |
| `D-006` | Use free tools and free tiers only; no card-gated service | `ACCEPTED` | Explicit user constraint |
| `D-007` | Refresh weekly or manually; no five-minute polling | `ACCEPTED` | Explicit user constraint |
| `D-008` | All five members read the same shared warehouse | `ACCEPTED` | Explicit user constraint |
| `D-009` | Keep raw data out of Git and archive it with provenance | `ACCEPTED` | Required by constraints |
| `D-010` | Use a multi-site scope and add `dim_site` | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-011` | Use Nightjar and nominal-io DJI as the real UAS sources | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-012` | Use TartanAviation KBTP as the primary historical manned source | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-013` | Treat OpenSky historical/Trino as optional, not a dependency | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-014` | Use the Phase 1 five facts and add one site dimension | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-015` | Freeze Phase 1 artifacts; Phase 2 documents are canonical for Phase 2 | `ACCEPTED` | Documentation baseline |
| `D-016` | Work in gated work packages with named owners A-E | `ACCEPTED` | Documentation baseline |
| `D-017` | Retain legacy synthetic samples in `data/sample/` as documented demo-only artifacts | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-018` | Keep GitHub Actions scheduled workflow as the Phase 2 scheduler; no external Python/OS cron host | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-019` | Weekly Monday 06:00 UTC schedule; artifact report mode | `ACCEPTED` | Accepted by HassanNawaz14 |
| `D-020` | Use FAA granular airspace services instead of `Airspace (DEMO)` | `ACCEPTED` | Accepted in session by the human, 2026-11-07 |
| `D-021` | Start `WP-04` before `G2` is recorded and review `WP-03`/`WP-04` together | `ACCEPTED` | Approved in session by the human, 2026-11-07 |

## D-001: Neon Free PostgreSQL

**Status:** `ACCEPTED`

**Context:** The team needs one cloud-hosted PostgreSQL warehouse that all five
members can read, with no local database and no credit card.

**Proposed decision:** Use Neon Free PostgreSQL in `aws-us-east-2` (Ohio) for the
shared warehouse.

**Rationale:**

- Free plan requires no credit card.
- Unlimited organization members.
- 1 GB PostgreSQL storage per project and 20 GB account total.
- 100 CU-hours per project per month.
- Scale-to-zero after inactivity; no weekly inactivity shutdown.
- Object storage is available in the same project and region.

**Consequences:**

- The curated warehouse must stay under 1 GB.
- Raw data must stay in object storage, not in PostgreSQL.
- A weekly CI run keeps the project active and within the intended cadence.
- The human creates and owns the project and credentials.

**Alternatives considered:**

- Aiven Free: powers off after inactivity; unsuitable for shared availability.
- Supabase Free: 500 MB and pauses after one week; insufficient.
- Local PostgreSQL: explicitly prohibited.
- Paid plans: excluded by the no-card constraint.

**Confirm before:** `WP-01` provisioning.

## D-002: GitHub Actions weekly and manual ETL

**Status:** `ACCEPTED`

**Context:** The team needs reproducible automation without local services or paid
orchestration.

**Proposed decision:** Use GitHub Actions on the existing public repository for a
weekly scheduled run and a manual `workflow_dispatch` run.

**Rationale:**

- Free standard runners for public repositories.
- No Docker or local PostgreSQL is required.
- The workflow is reproducible and visible to all members.
- Weekly/manual cadence is explicitly acceptable.

**Consequences:**

- The repository must remain public unless the human accepts minute limits.
- CI writes to the shared warehouse; members only read.
- The workflow must be idempotent and safe to rerun.
- Secrets must be stored in a protected GitHub environment.

**Confirm before:** `WP-11`.

## D-003: Neon Object Storage for raw archives

**Status:** `ACCEPTED`

**Context:** Raw ADS-B, UAS, FAA, and weather files can exceed 1 GB and must not be
committed to Git.

**Proposed decision:** Store raw archives and source snapshots in a private Neon
Object Storage bucket with a manifest of URL, license, SHA-256, size, and fetch time.

**Rationale:**

- 5 GB object storage per project on the free plan.
- S3-compatible access from GitHub Actions.
- Keeps raw data out of PostgreSQL and Git.
- The original public URLs remain the primary provenance source.

**Consequences:**

- The human creates the bucket and credentials.
- CI needs a storage write credential; members may receive a read-only credential.
- Raw archives are not directly queryable; curated tables are in PostgreSQL.
- Capacity must stay below 5 GB; the selected sources are currently below that.

**Confirm before:** `WP-01`.

## D-004: Real data only

**Status:** `ACCEPTED`

**Decision:** Every flight, weather, vehicle, restriction, and encounter record must
come from real public source data. Derived measures must be computed from real source
rows and documented. No synthetic fallback is permitted.

**Consequences:** A source outage produces a documented gap or a blocked human
action, not synthetic filler. Data quality reports must state gaps honestly.

## D-005: No local database or Docker

**Status:** `ACCEPTED`

**Decision:** Do not use local PostgreSQL, Docker, Docker Compose, dev containers, or
local service containers. The shared Neon warehouse and GitHub Actions are the
execution environment.

**Consequences:** Local checks are limited to unit tests and static analysis. Database
integration is demonstrated through CI and the shared warehouse.

## D-006: Free tools only

**Status:** `ACCEPTED`

**Decision:** Use only free tools, free tiers, and public data. No credit card, paid
plan, trial conversion, or billing account.

**Consequences:** If a free limit is exceeded, stop and ask the human for a capacity
decision. Do not silently upgrade or add a paid dependency.

## D-007: Weekly or manual refresh

**Status:** `ACCEPTED`

**Decision:** Use a weekly schedule and manual dispatch. Do not poll every five
minutes.

**Consequences:** The warehouse is an analytical snapshot, not a live tracking
system. Documentation must not claim real-time freshness.

## D-008: Shared five-member read access

**Status:** `ACCEPTED`

**Decision:** All five members query one shared warehouse through a read-only SQL
role. Do not create member-local warehouses or machine-local copies.

**Consequences:** The human provisions membership and credentials. CI is the only
writer.

## D-009: Raw data outside Git

**Status:** `ACCEPTED`

**Decision:** Raw archives, large source files, and database dumps are never
committed. They belong in approved cloud object storage with provenance metadata.

**Consequences:** The repository contains documentation, SQL, ETL, tests, and small
fixtures only. `.gitignore` must be maintained.

## D-010: Multi-site scope with `dim_site`

**Status:** `ACCEPTED`

**Context:** The real UAS data is not co-located with the Pittsburgh ADS-B data.
Restricting the warehouse to Pittsburgh would either lose the UAS facts or require
synthetic data.

**Proposed decision:** Use a multi-site analytical scope and add `dim_site` as a
sixth dimension. Sites:

- KBTP Pittsburgh-Butler.
- KAGC Pittsburgh-Allegheny (weather/airspace; ADS-B only if validated).
- Nightjar PA field site.
- Nominal-io DJI Colorado and California sites.

**Consequences:**

- Site-level comparisons become a first-class analytical capability.
- Grid cells, weather observations, and airspace zones carry a `site_key` where
  applicable.
- The Phase 1 five-dimension diagram is refined, not discarded.
- The human must confirm this scope before `G2`.

## D-011: Real UAS sources

**Status:** `ACCEPTED`

**Decision:** Use Nightjar (CC BY 4.0) and nominal-io DJI (MIT) CSV/GeoJSON data for
real UAS tracking and journey facts. Do not use video or synthetic paths.

**Rationale:**

- Nightjar provides 10 Hz GPS, altitude, and multiple real flights at a PA site.
- Nominal-io provides real DJI FlightRecord data in Colorado and California.
- Both are free and do not require credentials.
- The datasets expose realistic parsing and quality problems.

**Consequences:**

- Add `dim_site` and site-specific weather mapping.
- Do not pair UAS flights with unrelated manned traffic in close-encounter facts.
- Document that close encounters are primarily derived from Tartan ADS-B.

## D-012: TartanAviation KBTP as primary historical manned source

**Status:** `ACCEPTED`

**Decision:** Use TartanAviation KBTP ADS-B as the primary manned tracking source.
Archive raw data and load a documented high-traffic window that fits the 1 GB
warehouse limit.

**Caveat:** Tartan raw positions are range/bearing/local-frame records. The parser
must georeference them to WGS84 and validate against known KBTP geometry before the
data is used for spatial facts. If validation fails, stop and ask the human; do not
invent coordinates.

## D-013: OpenSky is optional

**Status:** `ACCEPTED`

**Decision:** OpenSky REST may provide recent manned snapshots, but it is not a
dependency for the initial load. Historical Trino access is optional and requires a
human application.

**Consequences:**

- A failed OpenSky call does not block the core warehouse.
- No agent may apply for OpenSky access or accept terms.
- The data-quality report must distinguish optional-source gaps from required-source
  failures.

## D-014: Phase 1 facts plus one dimension

**Status:** `ACCEPTED`

**Decision:** Keep `FactVehicleTracking`, `FactFlightJourney`,
`FactCloseEncounter`, `FactRestrictionActivation`, and `FactAirspaceOccupancy`.
Add `dim_site`; refine columns and keys as documented in
[docs/04_data_model.md](docs/04_data_model.md).

**Consequences:** The final model has six dimensions and five facts. This is a
Phase 2 refinement, not a replacement of the Phase 1 business processes.

## D-015: Phase 1 is frozen

**Status:** `ACCEPTED`

**Decision:** Do not edit `Phase1/` or Phase 1 PDFs. Phase 2 documents supersede
their implementation details where the real-data/cloud plan differs.

## D-016: Gated work packages

**Status:** `ACCEPTED`

**Decision:** Work is organized into gated work packages with named owners A-E,
explicit dependencies, acceptance evidence, and stop conditions.

**Consequences:** Agents work on one package at a time. Human-only actions block the
package rather than being improvised.

## D-017: Retain legacy synthetic samples as demo-only artifacts

**Status:** `ACCEPTED`

**Context:** `data/sample/` contains five small synthetic files from Phase 1. Phase 2
uses real data only, but users and evaluators may want offline sample files without
accessing the shared Neon warehouse.

**Decision:** Keep the five files tracked in Git under `data/sample/` as clearly
labeled demonstration artifacts. They are not a Phase 2 source, are excluded from all
ETL, staging, warehouse, reporting, and DQ loads, and must never be cited as evidence
or presented as real data.

**Rationale:** Provides an offline sample for reviewers and evaluators without
introducing synthetic records into the shared warehouse. Clear labeling prevents the
files from being mistaken for real observations.

**Consequences:**
- `data/sample/README.md` states the demo-only status and handling rules.
- `.gitignore` intentionally keeps the five sample files tracked; other files under
  `data/sample/` remain ignored.
- Every load, DQ check, report, and evidence path excludes them.
- Any demo use must label the files as synthetic.
- `H-008` is resolved and `B-006` is closed.

**Alternatives considered:** Delete the files from Git or quarantine them outside the
repository. Rejected because the human wants offline samples available to users and
evaluators.

## D-018: Keep GitHub Actions as the scheduler

**Status:** `ACCEPTED`

**Context:** A suggestion was made to consider Python cron jobs for the weekly
ingestion instead of GitHub Actions.

**Decision:** Keep the accepted GitHub Actions workflow with `on.schedule.cron` as the
scheduler and `workflow_dispatch` for manual runs. The Python ETL remains a CLI entry
point (`python -m etl.run --mode weekly`) and is scheduler-agnostic.

**Rationale:** No always-on host, no card, no second writer, protected secrets, audit
logs, artifacts, and reproducibility. An external cron host would add hosting,
secret-management, and operational burden and conflict with `D-002`, `D-005`, `D-006`,
and `D-008`.

**Consequences:** `warehouse.yml` uses a weekly cron schedule; no five-minute polling.
A future requirement for an external cron host needs a new human decision.

## D-019: Weekly Monday 06:00 UTC schedule; artifact report mode

**Status:** `ACCEPTED`

**Context:** The project requires a reproducible, low-maintenance weekly ingestion and reporting cadence.

**Decision:**
- **Schedule:** Monday 06:00 UTC.
- **Manual inputs:** defaults to the last 7 days, `publish_reports: true`, sites `KBTP`, `KAGC`.
- **Report mode:** `artifact`.

**Rationale:** Captures the full weekend, ensures availability for the team, and avoids expensive serverless hosting. `artifact` mode keeps reports in Git-accessible Action run artifacts rather than polluting the commit history.

**Consequences:** `warehouse.yml` must be configured with this cron schedule. Reports are accessible via Action artifacts.

## D-020: Use FAA granular airspace services instead of `Airspace (DEMO)`

**Status:** `ACCEPTED`

**Context:** The FAA `Airspace` ArcGIS item `a044dd8afb3a46a0a49d0b9ec66cad55`
is titled `Airspace (DEMO)` and has no `licenseInfo` or `accessInformation`. The
same FAA org publishes granular `Class_Airspace`, `Special_Use_Airspace`, and
`Route_Airspace` services with explicit public-use license text and FAA
attribution.

**Decision:** Use the granular FAA airspace services for `dim_airspace_zone` and
airspace-occupancy work. Do not load the `Airspace (DEMO)` layer. Preserve the FAA
attribution, service item IDs, and `GLOBAL_ID` natural keys.

**Rationale:** The granular items have clear provenance, publisher ownership
(`AeronauticalInformationServices_FAA`), eight-week effective dates, and explicit
public-use terms. They avoid relying on a layer whose title and missing terms make
its status ambiguous.

**Consequences:** Validate and load `Class_Airspace`, `Special_Use_Airspace`, and
`Route_Airspace` separately, deduplicate by `GLOBAL_ID`, and request `outSR=4326`
from their native EPSG:4269 geometry. `Boundary_Airspace`, `Airspace_Schedule`, and
the DEMO layer remain unapproved unless a later decision adds them. The combined
granular national count is 12,849 features, not the DEMO layer's 16,789.

## D-021: Start WP-04 before G2 and review WP-03/WP-04 together

**Status:** `ACCEPTED`

**Context:** `WP-03` is `READY_FOR_REVIEW`; reviewers D/E have not signed off and
`G2` is therefore still `IN_PROGRESS`. The human directed that `WP-04` begin and that
the two packages be reviewed together.

**Decision:** Start `WP-04` staging DDL and loaders before `G2` is recorded. Keep
`WP-03` evidence available for reviewers D/E and prepare `WP-04` for reviewers C/D.
Do not mark either package `DONE` or close `G2` without the required review and human
acceptance.

**Rationale:** The two packages are closely coupled: staging must reflect the source
contracts validated in `WP-03`. A combined review reduces waiting time while keeping
the evidence separate.

**Consequences:**

- `G2` remains open until reviewers sign off on `WP-03` and Member A records the gate.
- If `WP-03` review changes a source contract, affected `WP-04` staging columns or
  transformations must be revised before `WP-04` acceptance.
- `WP-04` implementation and tests may proceed, but database acceptance evidence still
  requires the approved CI path or human-run verification.
- `WP-04` and `WP-03` changes must remain separable for review and any eventual commit.

## Change process

1. Create a decision record in [templates/DECISION_RECORD.md](templates/DECISION_RECORD.md).
2. Add or update a row in this register.
3. Update all affected canonical documents.
4. Update [PROGRESS.md](PROGRESS.md) and the human action queue if approval is needed.
5. Do not provision or implement a `PROPOSED` decision before human confirmation.
