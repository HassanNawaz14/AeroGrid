# Phase 2 Decision Log

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

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
| `D-022` | Keep `WP-05` not started until `WP-03` and `WP-04` are merged; record `G3` after `WP-04` and `WP-05` acceptance | `ACCEPTED` | Approved in session by the human, 2026-11-08 |
| `D-023` | Delegate `WP-04`/`WP-05` closeout to Members B and C through `G3`: self-approved CI runs, peer review, owner-marked `DONE`; gates stay human | `ACCEPTED` | Approved in session by the human, 2026-11-08 |
| `D-024` | Extend the delegated window through `G4`: Member D closes `WP-06`, Member C completes dimension members and records `G4`; `G3` recorded as instructed with `B-011` open | `ACCEPTED` (closed 2026-11-11 at `G4`) | Approved in session by the human, 2026-11-09 |

| `D-025` | G5 derived-fact acceptance | `ACCEPTED` (requester declaration) | 2026-11-13, requester states project-admin authority |
| `D-026` | G6 DQ, reports and views acceptance | `ACCEPTED` (requester declaration) | 2026-11-13, requester states project-admin authority |
| `D-027` | G7 administrative acceptance | `ACCEPTED` (requester declaration) | 2026-11-13, requester states project-admin authority |
| `D-028` | Track accepted data limitations as a register with explicit implementation triggers | `ACCEPTED` | Directed by HassanNawaz14, 2026-11-13 |
| `D-029` | Report empty sources as "no data loaded" (coverage guards `DQ-G-001`–`DQ-G-004`), never as measured zero | `ACCEPTED` | Directed by HassanNawaz14, 2026-11-13 |
| `D-030` | WP-11 ingestion is one transactional job with a separate read-only `validate` mode; schedule stays inert until a human sets `WP11_SCHEDULE_ENABLED` | `ACCEPTED` | Directed by HassanNawaz14, 2026-11-14 |
| `D-031` | WP-11 accepted; weekly Monday 06:00 UTC schedule enabled with standing approval for unattended `apply` and cited scope limits | `ACCEPTED` (requester declaration) | 2026-11-14, requester states project-admin authority |
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

## D-022: Keep WP-05 blocked until WP-03 and WP-04 are merged

**Status:** `ACCEPTED` (the `WP-05` start condition was later met; `D-023` governs
the closeout)

**Context:** `PROGRESS.md` and the work breakdown described `WP-05` as waiting for
`G3`, while the dependency table listed `G2`; `G3` itself requires both `WP-04` and
`WP-05`. The human resolved the operational question on 2026-11-08: do not start
`WP-05` until `WP-03` and `WP-04` are merged.

**Decision:** Keep `WP-05` `NOT_STARTED` until `WP-03` and `WP-04` are merged. Do not
start Member C work early. `G3` remains the gate that records acceptance of both
staging and dimensions, and is recorded after `WP-04` and `WP-05` are accepted.

**Rationale:** Starting dimensions before the staging contract and review are settled
risks rework and breaks the documented one-package-at-a-time rule. Waiting for both
merges keeps Member C's work aligned with the accepted source and staging model.

**Consequences:**

- The dependency table's `G2` entry no longer authorizes `WP-05` early; `D-022` is the
  operative start rule.
- `WP-05` remained `NOT_STARTED` while `WP-04` was `BLOCKED_ON_HUMAN` on `H-011`; the
  start condition is now met and `D-023` governs the closeout.
- `G3` is recorded only after `WP-04` and `WP-05` acceptance evidence exists.

## D-023: Delegated closeout window for `WP-04` and `WP-05`

**Date:** 2026-11-08
**Decider:** HassanNawaz14 (Member A, human owner)
**Status:** `ACCEPTED`

**Context:** The human wants no involvement until the remaining staging and dimension
work is complete. The standing rules require human confirmation before a work package
is marked `DONE`, and the `warehouse` environment listed the human as its only
reviewer, so every database run needed a human approval.

**Decision:** Open a delegated window that ends when `G3` is recorded.

1. Member B (Hamid4325) may mark `WP-04` `DONE`, and Member C (HarveyWebbs) may mark
   `WP-05` `DONE`, once the evidence in their agent briefs
   ([dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md)) is recorded in
   `PROGRESS.md`. No further human confirmation is needed for those two packages.
2. Hamid4325 and HarveyWebbs join the `warehouse` environment's required reviewers and
   may approve their own runs; `Prevent self-review` stays unchecked. All database
   writes remain CI-only; do not run loaders from a laptop.
3. Owners may commit, push their own package branch, open a PR, and merge it after one
   peer approval (Member C or D for `WP-04`; Member D for `WP-05`). No agent merges
   another package's PR.
4. These stay human-only: secrets, Neon roles/branches/databases, repository and
   environment settings, destructive SQL, `G3` acceptance, and any change to scope,
   sources, licenses, or capacity.
5. The human returns at `G3`: review both packages, rerun
   `Phase2/sql/00_grants.sql` as `neondb_owner` (all 15 rows `true`), record `G3`, then
   restore the `warehouse` reviewers to HassanNawaz14 only and re-enable
   `Prevent self-review`.

**Rationale:** The remaining work is well-defined and evidence-checked. Delegating the
closeout removes an approval bottleneck without lowering the evidence bar, and the
CI-only write rule keeps one audited path into the shared warehouse.

**Consequences:**

- `PROGRESS.md` treats `WP-04` and `WP-05` as owner-closable until `G3`.
- Every other work package still needs human confirmation to close.
- If a blocker needs a human-only action, the owner records `BLOCKED_ON_HUMAN`, adds a
  new `H-###` item, and stops. This window does not authorize that action.

## D-024: Extended delegated window through `G4` for `WP-06`

**Date:** 2026-11-09
**Decider:** HassanNawaz14 (Member A, human owner)
**Status:** `ACCEPTED`

**Context:** `WP-04` and `WP-05` closed under `D-023`, and the human instructed the
Member A agent to record `G3` and let Members D and C start and finish the next work
without further human input. The `WP-04` sample proof used the legacy synthetic demo
CSV (`B-011`), so the real accepted-row proof must come from `WP-06`'s real Tartan
load. The dimensions currently hold only their `-1` unknown members apart from
`dim_time` and `dim_site`, which blocks surrogate-key mapping for real tracking rows.

**Decision:** Extend the delegated window through `G4`:

1. Member D owns `WP-06` (tracking and journey facts). Member C completes the
   dimension members needed for key mapping (`dim_vehicle` from real observed
   `icao24` identities, and any real grid cells) and verifies the fact load. Member E
   stays a reviewer and does not start `WP-07`, which needs approved thresholds.
2. `G3` is recorded as instructed by the human on 2026-11-09, with `B-011` open: the
   real accepted-row staging proof is folded into `WP-06`.
3. D and C may commit, push their own package branches, open PRs, and merge after one
   peer approval (Member C or E for `WP-06`). No agent merges another package's PR.
4. D dispatches the `WP-06` workflow; Member C (or Member B) approves the `warehouse`
   run because D is not an environment reviewer. All database writes stay CI-only.
5. D marks `WP-06` `DONE` after recording counts, reconciliation, idempotency, and
   orphan evidence. Member C then records `G4`. This is the only gate an agent may
   record, and only for `G4` with the `WP-06` evidence present.
6. The human returns after `G4` to review the evidence, approve the `WP-07`
   thresholds, restore the environment reviewers, and re-enable
   `Prevent self-review`.

These stay human-only: secrets, Neon roles/branches/databases, repository and
environment settings, destructive SQL, thresholds, and any gate other than `G4`.

**Rationale:** The remaining work is well-defined, and the dimension gap is a
mechanical prerequisite for key mapping. Delegating the closeout and `G4` keeps the
project moving while preserving the evidence bar and the CI-only write rule.

**Consequences:**

- `PROGRESS.md` treats `WP-06` as owner-closable and `G4` as verifier-recordable.
- `WP-07` and every later package still need the human (thresholds and gates).
- `B-011` closes only when real Tartan rows are accepted in staging and reconcile to
  the tracking facts.

**Closure (2026-11-11):** The window is closed. `WP-06` is `DONE` and `G4` is
recorded after WP-05 run `42689267328` and WP-06 run `42887782411` passed on
`phase2/wp06-tracking-facts` at `ecce8ec`; PR #12 merged as `f29b099` and `B-011` is
resolved. `WP-07` remains `BLOCKED_ON_HUMAN` on `H-013`.

## D-025: G5 derived-fact acceptance

**Date:** 2026-11-13  
**Decider:** Current requester (states they are project administrator; independent GitHub admin permission not proved).  
**Status:** `ACCEPTED` at the requester's explicit direction.

WP-07 persisted; approve 2D grid, inferred airborne, 60-second occupancy cap, exact-timestamp encounter method and zero real FAA snapshots as explicitly documented limitations.

**Evidence:** [Member E evidence](docs/MemberE_Implementation_Evidence_2026-11-13.md); [final acceptance and caveats](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

## D-026: G6 DQ, reports and views acceptance

**Date:** 2026-11-13  
**Decider:** Current requester (states they are project administrator; independent GitHub admin permission not proved).  
**Status:** `ACCEPTED` at the requester's explicit direction.

Accept 32 stored DQ checks (29 PASS, 3 WARN, 0 FAIL), both improved PDFs and ten deployed reporting views. Additional WP-11 automation and reader evidence remains separately tracked.

**Evidence:** [Member E evidence](docs/MemberE_Implementation_Evidence_2026-11-13.md); [final acceptance and caveats](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

## D-027: G7 administrative acceptance

**Date:** 2026-11-13  
**Decider:** Current requester (states they are project administrator; independent GitHub admin permission not proved).  
**Status:** `ACCEPTED` at the requester's explicit direction.

The requester explicitly directs that G7 be recorded accepted. No independent clean end-to-end replay or full multi-member read test was supplied to this package; do not imply otherwise.

**Evidence:** [Member E evidence](docs/MemberE_Implementation_Evidence_2026-11-13.md); [final acceptance and caveats](docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

## D-028: Accepted limitations are tracked with implementation triggers

**Date:** 2026-11-13

**Decider:** HassanNawaz14

**Status:** `ACCEPTED`

Accepted data limitations are recorded in one canonical register,
[`docs/13_accepted_data_limitations.md`](docs/13_accepted_data_limitations.md), with a
stable `L-###` ID, the observed warehouse state, the condition that requires
implementation, the required work, and the linked DQ check. `WP-11` must surface the
linked DQ results and `WP-12` must report every open entry; neither package may close
an entry by changing DQ severity or by omitting it from a report.

**Rationale:** G5–G7 acceptance covered the limitations administratively. Without a
register they would survive only as prose in the gate record, with no trigger and no
audit owner. This makes each one implementable when its trigger occurs and makes
silent masking a review failure.

**Evidence:** Live verification 2026-11-13, WP-08 run `43471609483` (29 PASS, 3 WARN,
0 FAIL) and WP-10 run `43471616729` (10 views); [register](docs/13_accepted_data_limitations.md);
[PROGRESS.md](PROGRESS.md) verification section.

## D-029: Empty sources are reported as missing coverage, not as zero events

**Date:** 2026-11-13

**Decider:** HassanNawaz14

**Status:** `ACCEPTED`

An approved source that produced **no accepted staging rows** must be reported as
"no data loaded", never as a measured zero. Two mechanisms enforce this:

1. **Coverage DQ checks.** `DQ-G-001` (`CRITICAL`) fails the run when the primary
   Tartan source has zero accepted rows. `DQ-G-002`, `DQ-G-003`, and `DQ-G-004`
   (`WARNING`) flag the empty METAR/ASOS, UAS, and FAA airspace sources.
2. **Coverage reporting.** Both PDFs carry a per-source table with an explicit
   `LOADED` / `NO DATA LOADED` status and a note that "no data loaded" is a coverage
   gap, not proof of a zero-activity world.

Two limitations are recorded for sources that were validated but never wired into
ingestion: `L-008` (Nightjar / nominal-io DJI) and `L-009` (FAA granular airspace
services and the optional OpenSky path). The register also carries the coverage
completion plan that says which package fills each staging table, the expected
volume per table, the ingestion sequence, and the reason for each volume limit, so
no reduction is undocumented.

**Rationale:** `vw_daily_encounter_hotspots` and `vw_restriction_traffic_impact`
return 0 rows because the underlying sources were never ingested. Without an explicit
coverage signal, a reader could conclude that the airspace had no encounters and no
restrictions, which is a false safety claim. Severity stays `WARNING` for optional or
not-yet-wired sources and `CRITICAL` only for the primary source whose absence
invalidates the whole load.

**Not decided here:** adding a source, starting UAS/airspace ingestion, enabling
OpenSky, or changing project scope. Those remain human-gated per the register rules.

**Evidence:** [register](docs/13_accepted_data_limitations.md);
`Phase2/etl/dq.py` (`DQ-G-001`–`DQ-G-004`); `Phase2/etl/reports.py` (`coverage_rows`,
`COVERAGE_NOTE`); [PROGRESS.md](PROGRESS.md) limitation register.

## D-030: WP-11 ingestion is one transactional job with a separate read-only validate mode

**Date:** 2026-11-14

**Decider:** HassanNawaz14 (explicit instruction to complete WP-11 as planned)

**Status:** `ACCEPTED`

`Phase2/etl/run.py` and `.github/workflows/wp11-ingest.yml` are the recurring
ingestion path. They have two modes with different powers:

1. **`validate`** — fetches and parses the real approved sources, computes
   accepted/rejected counts, and refuses the run when any requested source yields no
   accepted rows. It opens no database connection and receives no secret.
2. **`apply`** — records one `etl_run_log` row, writes `source_manifest`, staging,
   rejects, dimension refresh, and `dq_result` inside a **single transaction**, then
   commits once. A `CRITICAL` DQ failure rolls back every ingestion write, then records
   a separate `FAILED` run with the captured DQ rows so the failure is auditable.

Apply also refuses an empty source **before the first write**. The persisted coverage
DQ checks are table-wide, so historical rows would keep `DQ-G-002`–`DQ-G-004` green
after a run that loaded nothing; the pre-write parse prevents that false PASS.

Apply is constrained three ways: `--apply` requires `--confirm APPROVE_WP11_APPLY`,
the process must see `GITHUB_ACTIONS=true` and `WAREHOUSE_CI_APPROVED=true`, and the
workflow allows dispatch apply only on `main` inside the `warehouse` environment. No
local run can write to the shared warehouse.

The weekly Monday 06:00 UTC schedule exists in the workflow but is inert until a human
creates the repository variable `WP11_SCHEDULE_ENABLED=true`. Scheduled runs execute
`validate` unless a second variable, `WP11_SCHEDULE_APPLY_ENABLED=true`, is also set;
that second variable is the standing human approval for unattended writes. This keeps
the cadence weekly/manual per `D-018`/`D-019` and keeps the first write human-gated.

Fetched raw files are transient: they are not archived to object storage, because no
object-storage integration exists in the repo and bucket credentials are human-only.
This gap is recorded as `L-010` rather than hidden; the run summary states it on every
run.

**Rationale:** the loaders and normalizers were already implemented and tested, but
validation alone never fills a staging table, so the accepted limitations `L-008` and
`L-009` could not start to close. A single-transaction apply makes a partially loaded
week impossible, and separating validate (no secret) from apply (protected job) means
the source contract can be checked at any time without risking the shared warehouse.

**Not decided here:** adding a source, enabling OpenSky, backfilling `weather_key` onto
existing facts, or changing thresholds. Staging coverage is not the same as closing a
limitation: `L-001` stays `OPEN` until facts are mapped to real weather keys, and
`L-008`/`L-009` stay `OPEN` until dependent facts are re-derived.

**Evidence:** `Phase2/etl/run.py`, `Phase2/etl/fetch.py`, `Phase2/etl/config.py`,
`Phase2/etl/dimension_loaders.py`, `.github/workflows/wp11-ingest.yml`,
`Phase2/tests/test_wp11_run.py`; [work breakdown](dev_plan/01_work_breakdown.md#wp-11-ci-access-and-deployment);
[PROGRESS.md](PROGRESS.md).

## D-031: WP-11 accepted; schedule enabled with standing approval for unattended apply

**Date:** 2026-11-14

**Decider:** HassanNawaz14 (explicit instruction: "you can accept WP-11"; statement
that both repository variables were created)

**Status:** `ACCEPTED` (requester declaration)

The requester records `WP-11` `DONE` on the strength of apply run
[`43502710978`](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43502710978):
`SUCCESS` on `main@165d59d`, `etl_run_id=11`, 23,254 accepted and 160 rejected rows,
0 duplicates, 8 manifests, 820 dimension rows, 36 DQ results (32 `PASS`, 4 `WARN`,
0 `FAIL`), and a passing reader-proof job.

The requester states that `WP11_SCHEDULE_ENABLED=true` and
`WP11_SCHEDULE_APPLY_ENABLED=true` were created, and this is the standing approval for
unattended Monday 06:00 UTC writes. That approval is bounded:

- one source set (`weather`, `uas`, `airspace`) and the documented stations;
- the default 7-day window;
- one transaction per run, rollback on any `CRITICAL` DQ failure, refusal of an empty
  source before the first write, and a summary artifact on every run;
- no new source, cadence change, threshold change, or `L-###` closure.

Both variables were created as **environment** variables on the `warehouse`
environment. The workflow's job-level `if` reads the `vars` context before the
environment is assigned, so the first scheduled run (Monday 2026-11-16 06:00 UTC) must
be checked. If it is skipped, create the same two variables at repository level
(Settings -> Secrets and variables -> Actions -> Variables) and leave the environment
copies in place. The run-mode step already reads the environment-scoped values.

**Residual follow-up:** Members B-E have not individually run the reader probe
(`H-017`); only the role-level proof in the apply dispatch exists. This acceptance is
an administrative declaration, not independent end-to-end evidence, matching `D-025` –
`D-027`.

**Evidence:** [PROGRESS.md](PROGRESS.md) WP-11 row and change log;
[accepted-limitations register](docs/13_accepted_data_limitations.md#wp-11-ingestion-status-2026-11-14);
[human operating manual](docs/10_human_operating_manual.md#first-action-for-every-team-member-reader-proof).

## Change process

1. Create a decision record in [templates/DECISION_RECORD.md](templates/DECISION_RECORD.md).
2. Add or update a row in this register.
3. Update all affected canonical documents.
4. Update [PROGRESS.md](PROGRESS.md) and the human action queue if approval is needed.
5. Do not provision or implement a `PROPOSED` decision before human confirmation.
