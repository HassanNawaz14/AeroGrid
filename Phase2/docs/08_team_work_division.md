# Team Work Division

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Purpose

Phase 2 is split by warehouse layer so all five members have independent, reviewable
work. Member A is HassanNawaz14. Members B-E are recorded below; `H-002` remains
deferred by the human, so agents must not invent or reassign identities.

## Ownership model

- One accountable member per work package.
- One peer reviewer per PR; the author cannot self-approve.
- Member A coordinates sequencing and human actions but does not unilaterally change
  scope.
- The human approves scope, source, license, capacity, and gate changes.
- Work is merged through short-lived branches and PRs, never directly to `main`.

## Delegated closeout windows (`D-023` → `G3`, `D-024` → `G4`)

Both delegated windows are closed. `D-023` handed off `WP-04`/`WP-05`; both packages
are `DONE` and `G3` was recorded on 2026-11-09. `D-024` handed off `WP-06` and `G4`;
the real Tartan WP-05/WP-06 runs passed and `G4` was recorded on 2026-11-11.

- Member D owns `WP-06` (now `DONE`); Member C completed the real `dim_vehicle`
  members and recorded `G4`.
- All database writes stay in CI; never run loaders from a laptop.
- Member E completed WP-07 through WP-10; the requester explicitly accepted G5/G6/G7 as a self-reported project administrator on 2026-11-13. H-013 is resolved.
- Human-only actions are unchanged: secrets, Neon roles and branches, repository and
  environment settings, destructive SQL, thresholds, and every gate after `G4`.

The exact step-by-step briefs are in
[dev_plan/01_work_breakdown.md](../dev_plan/01_work_breakdown.md). Any blocker that
needs a human action becomes a new `H-###` row and stops the package; the closed
windows do not authorize it.

## Member roles

| Name / Username | Role | Primary scope | Secondary scope |
|---|---|---|---|
| HassanNawaz14 (Member A) | Platform and integration lead | Cloud setup, CI, access, integration, release | Documentation, human action queue, demo |
| Hamid4325 (Member B) | Source and staging engineer | Source clients, raw archive, staging, cleaning | Source validation, reject analysis |
| HarveyWebbs (Member C) | Data model engineer | Schema, dimensions, keys, dictionary, ERD | Integrity checks, SQL review |
| ahmadazad-dev (Member D) | Flight analytics engineer | Tracking and journey facts | Reconciliation, trajectory logic |
| x-abdullah-saeed-x (Member E) | Derived analytics and quality engineer | Derived facts, DQ, reporting views, PDFs | Reporting demos, threshold analysis |

## Work package ownership

| WP | Work package | Accountable | Reviewer | Main paths |
|---|---|---|---|---|
| `WP-00` | Documentation and folder baseline | A | B + C | `AGENTS.md`, `Phase2/` docs |
| `WP-01` | Human prerequisites and approvals | A | Human | `PROGRESS.md`, action queue |
| `WP-02` | Platform validation and access proof | A | B + C | `Phase2/sql/`, CI config |
| `WP-03` | Source validation and georeferencing spike | B | D + E | `Phase2/etl/sources/`, validation notes |
| `WP-04` | Staging DDL and loaders | B | C + D | `Phase2/sql/01_staging/`, `Phase2/etl/loaders.py`, `Phase2/etl/staging_writer.py` |
| `WP-05` | Dimensions, keys, and data dictionary | C | A + D | `Phase2/sql/`, `data/data_dictionary.md` |
| `WP-06` | Tracking and journey facts | D | C + E | `Phase2/etl/facts.py` |
| `WP-07` | Derived facts | E | C + D | `Phase2/etl/facts.py`, tests |
| `WP-08` | Data-quality framework | E | B + D | `Phase2/etl/dq.py`, `Phase2/sql/` |
| `WP-09` | PDF reports | E | B + A | `Phase2/etl/reports.py`, `Phase2/reports/` |
| `WP-10` | Reporting views and corridor metrics | E | C + D | `Phase2/sql/`, `project_reporting` |
| `WP-11` | CI, access, and deployment | A | B + C | `.github/workflows/`, access docs |
| `WP-12` | Integration, acceptance, and release | A | B-E | All Phase 2 paths |

## Responsibilities by layer

### HassanNawaz14 (Member A): Platform and integration

- Maintain the human action queue and gate status.
- Validate Neon, object storage, and GitHub access.
- Own CI workflow structure and environment secret references.
- Coordinate the weekly/manual run and release checklist.
- Ensure no agent performs human-only actions.
- Own the final integration demo and repository links.
- Do not own business rules for encounters, restrictions, or DQ thresholds.

### Member B: Sources and staging

- Build source clients for Tartan, Nightjar, DJI, FAA, METAR, and optional OpenSky.
- Archive raw data and manifest provenance.
- Normalize types, units, coordinates, and timestamps.
- Implement duplicate and reject handling.
- Produce cleaning counts and reject reasons for the Data Cleaning Report.
- Validate georeferencing with Member D.
- Do not create warehouse dimensions or facts directly.

### Member C: Schema and dimensions

- Own schema DDL, constraints, indexes, and seed data.
- Own all six dimensions and surrogate-key mapping.
- Own the data dictionary and DBML consistency.
- Define unknown-member behavior.
- Review every fact join for key correctness.
- Do not embed source-specific parsing in dimension code.

### Member D: Tracking and journeys

- Implement tracking fact loading.
- Implement journey segmentation and journey facts.
- Validate coordinate, speed, altitude, and time ordering.
- Ensure idempotent fact loads.
- Reconcile tracking counts to accepted staging counts.
- Do not define close-encounter or occupancy thresholds alone.

### Member E: Derived facts, DQ, and reporting

- Implement close encounters, occupancy, and restriction activation.
- Implement the DQ check library and result persistence.
- Build reporting views and business metrics.
- Generate both PDF reports from real results.
- Document thresholds and limitations.
- Do not hide a failed check or lower a threshold without approval.

## Review matrix

| Author | Required peer reviewer | Extra reviewer for high-risk changes |
|---|---|---|
| A | B | C for schema/access changes |
| B | C | D for georeferencing; E for quality rules |
| C | A | D for fact joins |
| D | C | E for derived-fact inputs |
| E | D | C for SQL; B for source claims |

Reviewer checklist:

- Scope matches the work package.
- No synthetic data or fabricated results.
- Real source URL and license are recorded.
- Natural keys and surrogate keys are valid.
- Counts reconcile.
- Critical DQ passes or the blocker is explicit.
- No secret, raw data, or `.env` is committed.
- Docs updated if an interface or decision changed.
- Tests cover the changed transformation.
- `PROGRESS.md` has status, evidence, and next handoff.

## Working agreements

- **First action, before any other work:** run the read-only reader probe and report
  pass/fail plus the rejected-write SQLSTATE. Steps are in
  [10_human_operating_manual.md](10_human_operating_manual.md#first-action-for-every-team-member-reader-proof);
  tracked as `H-017`.
- One work package in progress per member.
- Do not start a dependent package before its prerequisite passes.
- Pull the latest `main` before branching.
- Use branch names like `phase2/wp-06-tracking-facts`.
- Keep PRs scoped; refactors go in a separate PR.
- Ask questions in the PR or issue, not in code comments.
- Record decisions in `DECISIONS.md`; do not rely on chat memory.
- Update `PROGRESS.md` before ending a work session.
- Prefer read-only inspection before edits.
- Do not commit raw data, database dumps, or reports containing secrets.
- No deadlines; sequence and evidence decide completion.

## Handoff protocol

Use `Phase2/templates/AGENT_HANDOFF.md`. A handoff must state:

1. Work package and status.
2. Files changed.
3. Checks run and results.
4. Decisions made.
5. Blockers and human actions.
6. Exact next step.
7. Evidence paths or counts.

A handoff is incomplete if the next member must rediscover the state.

## Coverage and substitution

- Every work package has a named reviewer, not a single point of failure.
- Member A can temporarily coordinate a blocked package.
- Schema changes require Member C even if another member writes the SQL.
- DQ and report claims require Member E even if another member supplies data.
- Source claims require Member B even if another member runs the query.
- A missing member does not authorize skipping review or changing scope.

## Workload balance

| Member | Primary load | Relative size |
|---|---|---|
| A | Platform, CI, access, integration | Medium |
| B | Multiple source clients and staging | High |
| C | Schema, dimensions, dictionary | Medium-high |
| D | Tracking and journeys | High |
| E | Derived facts, DQ, views, reports | High |

If one member is overloaded, rebalance by layer-adjacent tasks, not by inventing new
owners. Record the change in `PROGRESS.md`.

## Human touchpoints

The human is needed for:

- Confirming the recorded Member B-E names (`H-002` remains deferred).
- Creating Neon/GitHub resources and secrets.
- Approving sources, licenses, scope, and thresholds.
- Authorizing implementation after `G1`.
- Any destructive or capacity decision.

Do not route these through an agent.

## Definition of done

A member is done only when:

- The work package acceptance criteria are met.
- The PR is reviewed and merged.
- Required checks pass.
- Documentation and data dictionary are updated.
- `PROGRESS.md` records evidence and the next handoff.

See
[`../dev_plan/04_acceptance_and_definition_of_done.md`](../dev_plan/04_acceptance_and_definition_of_done.md).
