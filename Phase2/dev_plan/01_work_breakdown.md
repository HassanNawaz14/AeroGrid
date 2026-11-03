# Work Breakdown

## Status summary

| WP | Name | Owner | Reviewer | Status |
|---|---|---|---|---|
| `WP-00` | Documentation and folder baseline | A | B + C | READY_FOR_REVIEW |
| `WP-01` | Human prerequisites and approvals | A | Human | BLOCKED_ON_HUMAN |
| `WP-02` | Platform validation and access proof | A | B + C | NOT_STARTED |
| `WP-03` | Source validation and georeferencing spike | B | D + E | NOT_STARTED |
| `WP-04` | Staging DDL and loaders | B | C + D | NOT_STARTED |
| `WP-05` | Dimensions, keys, and data dictionary | C | A + D | NOT_STARTED |
| `WP-06` | Tracking and journey facts | D | C + E | NOT_STARTED |
| `WP-07` | Derived facts | E | C + D | NOT_STARTED |
| `WP-08` | Data-quality framework | E | B + D | NOT_STARTED |
| `WP-09` | PDF reports | E | B + A | NOT_STARTED |
| `WP-10` | Reporting views and corridor metrics | E | C + D | NOT_STARTED |
| `WP-11` | CI, access, and deployment | A | B + C | NOT_STARTED |
| `WP-12` | Integration, acceptance, and release | A | B-E | NOT_STARTED |

Members A-E are placeholders. The human assigns real names before implementation.

---

## WP-00: Documentation and folder baseline

**Status:** READY_FOR_REVIEW
**Owner:** Member A
**Reviewers:** Members B and C
**Prerequisites:** None
**Gate:** G0

### Objective

Create a complete, internally consistent Phase 2 documentation and folder baseline
that the human can review and that agents can follow without inventing scope.

### Scope

- Root and Phase 2 agent contracts.
- Phase 2 dashboard, progress board, and decision log.
- Canonical docs `00`-`12`.
- Development plan and templates.
- Folder README placeholders.
- Updated previous documentation.
- Link and status consistency.

### Out of scope

- SQL, ETL code, workflows, database objects, cloud resources, secrets.
- Any Phase 1 edit.

### Deliverables

- `AGENTS.md`
- `Phase2/AGENTS.md`
- `Phase2/README.md`
- `Phase2/PROGRESS.md`
- `Phase2/DECISIONS.md`
- `Phase2/docs/00` through `12`
- `Phase2/dev_plan/` plan files
- `Phase2/templates/` templates
- Folder READMEs and `.gitignore`
- Updated root README and existing data docs
- Updated DBML or historical pointer
- Phase 1 guide supersession note

### Acceptance evidence

- All links resolve.
- No implementation files or resources exist.
- Status, WPs, gates, sources, model, and actions are consistent.
- Human can identify the exact next action: review and clear `G1`.
- `PROGRESS.md` records files changed and checks run.

### Verification

- Run a relative-link check.
- Search for stale claims such as `synthetic`, `5-minute`, `Docker`, `local PostgreSQL`.
- Confirm Phase 1 files are unmodified.
- Confirm no secrets or raw data.

---

## WP-01: Human prerequisites and approvals

**Status:** BLOCKED_ON_HUMAN
**Owner:** Member A (coordinator)
**Reviewer:** Human
**Prerequisites:** WP-00 accepted
**Gate:** G1

### Objective

Obtain the accounts, approvals, resource names, and authorization required before
implementation.

### Scope

- Human reads and approves the baseline.
- Real names replace Members A-E.
- Neon project and raw bucket created.
- GitHub `warehouse` environment and secrets created.
- Member invitations and read-only access planned.
- Licenses and optional OpenSky terms confirmed.
- Implementation authorization recorded.

### Out of scope

- Agents creating accounts, accepting terms, creating resources, adding secrets, or
  inviting members.

### Deliverables

- Human action queue `H-001` through `H-008` resolved.
- `implementation_authorized: YES`.
- G1 approval recorded with approver and date.

### Acceptance evidence

- G1 checklist complete.
- Resource existence confirmed without values.
- Secret names confirmed, not values.
- Member access plan confirmed.
- Human approval recorded in `PROGRESS.md`.

---

## WP-02: Platform validation and access proof

**Status:** NOT_STARTED
**Owner:** Member A
**Reviewers:** Members B and C
**Prerequisites:** WP-01, G1 cleared
**Gate:** G2 input

### Objective

Prove that CI, object storage, and read-only member access work before loading real
data.

### Scope

- Test write connection from CI.
- Test object-storage read/write with a small non-sensitive marker.
- Test read-only role connection.
- Confirm schemas and search path.
- Confirm TLS and connection pooling behavior.
- Record cold-start and timeout behavior.
- Confirm quota warning thresholds.

### Out of scope

- Loading production facts.
- Creating the full schema.
- Sharing credentials in the repository.
- Changing account settings.

### Deliverables

- Access proof notes in `Phase2/PROGRESS.md`.
- Row/object counts from the proof.
- Role permission matrix confirmed.
- CI connectivity evidence.

### Acceptance evidence

- CI can connect and write a scratch object.
- Read-only role can `SELECT` a known object and cannot write.
- No secret is printed.
- Quotas and timeouts are recorded.
- No production data exists.

---

## WP-03: Source validation and georeferencing spike

**Status:** NOT_STARTED
**Owner:** Member B
**Reviewers:** Members D and E
**Prerequisites:** WP-01, G1 cleared
**Gate:** G2

### Objective

Validate every required source's schema, license, units, time base, coordinates, and
volume using real samples before building the pipeline.

### Scope

- Tartan sample and georeferencing.
- Nightjar CSV/GeoJSON validation.
- Nominal-io DJI CSV validation.
- FAA layer/geometry validation.
- METAR/IEM validation.
- Optional OpenSky smoke test.
- Capacity estimate.

### Out of scope

- Full raw download beyond the approved load window.
- Synthetic test data.
- Production loads.
- Video/audio ingestion.

### Deliverables

- Completed `SOURCE_VALIDATION.md` records.
- Row counts, sizes, hashes, and sample evidence.
- Georeferencing notes and comparison.
- Unit/time-base mapping.
- Capacity estimate.
- Pass/fail recommendation per source.

### Acceptance evidence

- Each required source is marked PASS with evidence.
- Any FAIL has a documented blocker and human action.
- Tartan coordinates are plausibly inside KBTP.
- Nightjar/DJI time basis and altitude datum are known.
- Full-load estimate is below the approved database budget.
- No raw data is committed.

---

## WP-04: Staging DDL and loaders

**Status:** NOT_STARTED
**Owner:** Member B
**Reviewers:** Members C and D
**Prerequisites:** WP-03, G2 cleared
**Gate:** G2/G3

### Objective

Create the staging schema and reproducible source-to-staging loaders.

### Scope

- `project_staging` DDL.
- Source manifest, run log, rejects, DQ result.
- Source-shaped staging tables.
- Loaders for approved sources.
- Cleaning, deduplication, unit conversion, rejects.
- Idempotent reruns.

### Out of scope

- Warehouse dimensions/facts.
- Derived metrics.
- Report generation.
- Full production load unless separately authorized.

### Deliverables

- Staging SQL migration(s).
- Loader clients and tests.
- Reject reason catalog.
- Counts and reconciliation.
- Data dictionary staging additions.
- Source manifest evidence.

### Acceptance evidence

- Staging tables accept real samples.
- Exact read/accepted/rejected/duplicate reconciliation.
- Rerun of the same sample creates no duplicates.
- Every reject has a reason and source identifier.
- No raw payload is committed to Git.
- Critical staging checks pass.

---

## WP-05: Dimensions, keys, and data dictionary

**Status:** NOT_STARTED
**Owner:** Member C
**Reviewers:** Members A and D
**Prerequisites:** WP-02, model approved
**Gate:** G3

### Objective

Create the six dimensions, surrogate keys, unknown members, constraints, and
authoritative data dictionary.

### Scope

- `project_dw` schema and dimensions.
- `dim_time`, `dim_site`, `dim_vehicle`, `dim_spatial_grid`, `dim_weather`,
  `dim_airspace_zone`.
- Identity surrogate keys.
- `-1` unknown member seeding.
- Natural-key uniqueness.
- FK/index design for facts.
- Data dictionary and DBML consistency.

### Out of scope

- Fact loading.
- Derived metrics.
- Reporting views.
- Guessing identities or sites.

### Deliverables

- Dimension DDL and seed SQL.
- Data dictionary.
- Updated DBML.
- Dimension row counts.
- Key-map/reconciliation query.
- Model review notes.

### Acceptance evidence

- All six dimensions exist with PK/FK/unique constraints.
- Unknown member exists in every dimension.
- Dimension row count is at least 100 using real data.
- Data dictionary matches DDL.
- DBML matches DDL.
- No orphan or duplicate natural keys.

---

## WP-06: Tracking and journey facts

**Status:** NOT_STARTED
**Owner:** Member D
**Reviewers:** Members C and E
**Prerequisites:** WP-04, WP-05
**Gate:** G4

### Objective

Load the two core movement facts from real tracking data with correct keys and grain.

### Scope

- `fact_vehicle_tracking`.
- `fact_flight_journey`.
- Natural-key-to-surrogate mapping.
- Exact timestamps and hourly time key.
- Journey segmentation.
- Idempotent loads.
- Reconciliation and tests.

### Out of scope

- Close encounters, occupancy, restrictions.
- Reporting views.
- Synthetic tracks or journeys.

### Deliverables

- Fact DDL and loaders.
- Journey algorithm and version.
- Tracking/journey counts.
- Reconciliation evidence.
- Tests for duplicates, gaps, and endpoint handling.

### Acceptance evidence

- Facts total at least 10,000 rows.
- Tracking uniqueness holds.
- Journey grain is documented and valid.
- Rerun creates no duplicates.
- Orphans are zero.
- Tracking facts reconcile to accepted staging.
- All timestamps and units are documented.

---

## WP-07: Derived facts

**Status:** NOT_STARTED
**Owner:** Member E
**Reviewers:** Members C and D
**Prerequisites:** WP-06, thresholds approved
**Gate:** G5

### Objective

Build the derived facts from real tracking rows with approved, versioned algorithms.

### Scope

- `fact_close_encounter`.
- `fact_airspace_occupancy`.
- `fact_restriction_activation`.
- Thresholds and algorithm versioning.
- Tests and evidence.

### Out of scope

- Fabricating encounters to reach a count.
- Reporting views.
- Final PDFs.

### Deliverables

- Derived-fact DDL and loaders.
- Algorithm documentation.
- Threshold decision record.
- Counts and sample evidence.
- Reconciliation to tracking.

### Acceptance evidence

- Every derived row traces to real tracking/restriction evidence.
- Thresholds are approved and unchanged after results review.
- Encounter vehicles are distinct and same-site/time.
- Occupancy uniqueness holds.
- Restriction activation has a real window/snapshot.
- No synthetic derived rows.
- Tests pass.

---

## WP-08: Data-quality framework

**Status:** NOT_STARTED
**Owner:** Member E
**Reviewers:** Members B and D
**Prerequisites:** WP-04 through WP-07
**Gate:** G6 input

### Objective

Implement the check catalog, persist results, and make critical failures block trusted
publication.

### Scope

- `dq_result` writes.
- Completeness, uniqueness, accuracy, integrity, reconciliation, timeliness,
  business-rule checks.
- Severity and CI behavior.
- Evidence queries.

### Out of scope

- Changing thresholds to make a run pass.
- Hiding failures.
- Report design.

### Deliverables

- DQ SQL/Python.
- Check catalog with IDs.
- Stored results from a real run.
- Failure-path test.
- Evidence for the report.

### Acceptance evidence

- Every run stores pass/fail results.
- Critical failures fail the run.
- Orphan and duplicate checks are zero on a valid run.
- Reconciliation is exact or explicitly explained.
- A deliberate failure is detected in a test.
- No synthetic data used to pass.

---

## WP-09: PDF reports

**Status:** NOT_STARTED
**Owner:** Member E
**Reviewers:** Members B and A
**Prerequisites:** WP-08
**Gate:** G6

### Objective

Generate the required Data Cleaning and Data Quality PDFs from stored evidence.

### Scope

- `Data_Cleaning_Report.pdf`.
- `Data_Quality_Report.pdf`.
- Run metadata, counts, rules, rejects, DQ table, capacity, limitations,
  attribution.
- Reproducible generation.

### Out of scope

- Writing unverifiable claims.
- Omitting critical failures.
- Embedding secrets or raw personal data.

### Deliverables

- PDF files in `Phase2/reports/`.
- Report source/template.
- Stored data backing each claim.
- Screenshot/verification of PDF readability.

### Acceptance evidence

- Both PDFs exist and open.
- Counts match the database.
- Critical failures are visible.
- Source licenses/attribution appear.
- "No synthetic data" statement is supported.
- Report can be regenerated from stored evidence.

---

## WP-10: Reporting views and corridor metrics

**Status:** NOT_STARTED
**Owner:** Member E
**Reviewers:** Members C and D
**Prerequisites:** WP-06, WP-07
**Gate:** G6

### Objective

Create stable `project_reporting` views that answer the Phase 2 analytics and corridor
questions.

### Scope

- Ten planned views.
- Density, occupancy, encounters, restrictions, weather, corridors.
- Grain/documentation for each view.
- Query performance review.

### Out of scope

- New facts not authorized.
- Synthetic corridor recommendations.
- Paid visualization tools.

### Deliverables

- `project_reporting` DDL/views.
- View catalog with grain and use.
- Example read-only queries.
- Performance evidence.

### Acceptance evidence

- All required views exist.
- Each view returns real data for the chosen period.
- Read-only role can select them.
- No row multiplication from role-playing joins.
- Corridor metrics state their assumptions.
- View definitions are documented.

---

## WP-11: CI, access, and deployment

**Status:** NOT_STARTED
**Owner:** Member A
**Reviewers:** Members B and C
**Prerequisites:** WP-01, WP-02, WP-04 through WP-10
**Gate:** G6/G7

### Objective

Automate weekly/manual execution and enforce critical DQ without local credentials.

### Scope

- GitHub Actions workflows.
- Environment secret references.
- Weekly schedule and manual dispatch.
- Concurrency and timeout.
- Report artifacts.
- Read-only access test.
- Run summary.

### Out of scope

- Five-minute polling.
- Secrets in repository files.
- Local database.
- Auto-upgrading paid plans.

### Deliverables

- Workflow YAML.
- CI check workflow.
- Access proof.
- Runbook update.
- Artifact links.

### Acceptance evidence

- Manual run succeeds on a controlled real window.
- Scheduled cadence is weekly, not minutes.
- Critical DQ fails the job.
- Reports upload as artifacts.
- No secret appears in logs.
- Read-only role cannot write.
- Run summary has counts.

---

## WP-12: Integration, acceptance, and release

**Status:** NOT_STARTED
**Owner:** Member A
**Reviewers:** Members B-E
**Prerequisites:** WP-02 through WP-11
**Gate:** G7

### Objective

Prove the full Phase 2 deliverable is integrated, reproducible, documented, and ready
for submission/demo.

### Scope

- End-to-end run.
- Rubric audit.
- Report audit.
- Access audit.
- Documentation and link audit.
- Demo script.
- Final status.

### Out of scope

- Late scope additions.
- Destructive cleanup.
- Unapproved source changes.

### Deliverables

- Final acceptance checklist.
- Reproducible run evidence.
- Final PDFs.
- Demo script.
- Repository link.
- Updated `PROGRESS.md` and decisions.

### Acceptance evidence

- All rubric items have evidence.
- 100+ dimension rows and 10,000+ fact rows are demonstrated.
- Both PDFs are final.
- Read-only access works for members.
- No critical DQ failures.
- No secrets/raw data in Git.
- A fresh authorized run reproduces the result.
- Human accepts the release.
