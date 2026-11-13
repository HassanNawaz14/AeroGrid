# Phase 2 Documentation Map

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

This is the entry point for Phase 2 documentation. It explains which document is
canonical, who should read what, and how to keep the documentation usable.

## Start paths

### Human reviewer

1. [Phase 2 README](../README.md) - scope and current status.
2. [Human operating manual](10_human_operating_manual.md) - approvals, access, and
   verification.
3. [Progress board](../PROGRESS.md) - gates, blockers, and human action queue.
4. [Architecture](02_architecture_and_platform.md) - proposed platform.
5. [Data sources](03_data_sources_and_licensing.md) - real data and licenses.
6. [Team division](08_team_work_division.md) - Members A-E.

### Coding agent starting a session

1. [`../../AGENTS.md`](../../AGENTS.md) - repository-wide contract.
2. [Phase 2 AGENTS](../AGENTS.md) - phase-specific contract.
3. [Progress board](../PROGRESS.md) - current state and blockers.
4. This map.
5. The canonical document for the assigned area.
6. The assigned work package in
   [dev plan](../dev_plan/01_work_breakdown.md).
7. The relevant template in [templates](../templates/).

If the work package is not `READY`, stop. If the task needs a human-only action, use
the human action protocol in [AGENTS.md](../AGENTS.md).

## Canonical-source table

| Subject | Canonical document | Secondary reference |
|---|---|---|
| Phase status, gates, blockers, human actions | [PROGRESS.md](../PROGRESS.md) | [README.md](../README.md) |
| Material decisions | [DECISIONS.md](../DECISIONS.md) | Decision templates |
| Work packages and dependencies | [dev_plan/01_work_breakdown.md](../dev_plan/01_work_breakdown.md) | [dev_plan/02_dependencies_and_gates.md](../dev_plan/02_dependencies_and_gates.md) |
| Team ownership A-E | [08_team_work_division.md](08_team_work_division.md) | Work packages |
| Scope and objectives | [01_phase2_scope_and_objectives.md](01_phase2_scope_and_objectives.md) | Phase 2 brief |
| Architecture and platform | [02_architecture_and_platform.md](02_architecture_and_platform.md) | [DECISIONS.md](../DECISIONS.md) |
| Data sources, URLs, licenses, cadence | [03_data_sources_and_licensing.md](03_data_sources_and_licensing.md) | [`../../data/all_data_summary.md`](../../data/all_data_summary.md) |
| Logical data model, grain, keys | [04_data_model.md](04_data_model.md) | [`../../data/data_dictionary.md`](../../data/data_dictionary.md) |
| Column-level dictionary | [`../../data/data_dictionary.md`](../../data/data_dictionary.md) | [04_data_model.md](04_data_model.md) |
| ETL stages and idempotency | [05_etl_pipeline.md](05_etl_pipeline.md) | Work packages |
| Data quality and reports | [06_data_quality_and_reports.md](06_data_quality_and_reports.md) | [04_acceptance_and_definition_of_done.md](../dev_plan/04_acceptance_and_definition_of_done.md) |
| Access, security, quotas, operations | [07_operations_access_and_security.md](07_operations_access_and_security.md) | [10_human_operating_manual.md](10_human_operating_manual.md) |
| Agent rules and stop conditions | [09_agent_operating_manual.md](09_agent_operating_manual.md) | [AGENTS.md](../AGENTS.md) |
| Human actions and verification | [10_human_operating_manual.md](10_human_operating_manual.md) | [PROGRESS.md](../PROGRESS.md) |
| Risks and validation spikes | [11_risks_and_validation.md](11_risks_and_validation.md) | Source doc |
| Terms | [12_glossary.md](12_glossary.md) | - |

## Audience split

| Audience | Needs | Avoid |
|---|---|---|
| Human reviewer | Decisions, tradeoffs, approvals, access steps, verification evidence | Being asked to read raw parser details |
| Coding agent | Exact contracts, file ownership, allowed actions, stop triggers, acceptance evidence | Inferring missing requirements |
| Team member | Work package, inputs/outputs, dependencies, handoff state | Editing another owner's package |
| Course evaluator | Evidence that requirements are met | Unsupported claims of implementation |

## Document set

### Phase control

- [Phase 2 README](../README.md) - dashboard and directory map.
- [Phase 2 AGENTS](../AGENTS.md) - phase-specific agent contract.
- [Progress board](../PROGRESS.md) - canonical status.
- [Decision log](../DECISIONS.md) - canonical decisions.
- [Documentation map](00_documentation_map.md) - this file.

### Design and implementation plan

- [Scope and objectives](01_phase2_scope_and_objectives.md)
- [Architecture and platform](02_architecture_and_platform.md)
- [Data sources and licensing](03_data_sources_and_licensing.md)
- [Logical data model](04_data_model.md)
- [ETL pipeline](05_etl_pipeline.md)
- [Data quality and reports](06_data_quality_and_reports.md)
- [Operations, access, and security](07_operations_access_and_security.md)
- [Risks and validation](11_risks_and_validation.md)
- [Glossary](12_glossary.md)

### People and operations

- [Team work division](08_team_work_division.md)
- [Agent operating manual](09_agent_operating_manual.md)
- [Human operating manual](10_human_operating_manual.md)

### Development plan

- [Plan index](../dev_plan/README.md)
- [Work breakdown](../dev_plan/01_work_breakdown.md)
- [Dependencies and gates](../dev_plan/02_dependencies_and_gates.md)
- [Deliverables matrix](../dev_plan/03_deliverables_matrix.md)
- [Acceptance and definition of done](../dev_plan/04_acceptance_and_definition_of_done.md)
- [Handoff and review protocol](../dev_plan/05_handoff_and_review_protocol.md)

## Planned implementation paths

These paths do not contain implementation yet. They are reserved so that agents do
not invent competing structures.

| Path | Future content | Owner |
|---|---|---|
| `Phase2/sql/` | Schema, constraints, indexes, seed, dimension and fact loads | Member C / D |
| `Phase2/etl/` | Python source clients, staging, dimensions, facts, DQ, reports | Members B/D/E |
| `Phase2/tests/` | Parser fixtures, unit tests, SQL assertions, DQ tests | All owners |
| `Phase2/reports/` | Generated Data Cleaning and Data Quality PDFs | Member E |
| `.github/workflows/` | `warehouse.yml`, `ci.yml` | Member A |
| Neon object storage | Raw archives and source snapshots | Member A / B |

## Updating documentation

Use these rules to keep the set coherent:

1. Change the canonical document first.
2. Update `PROGRESS.md` with status, files, checks, blockers, and handoff.
3. Add a decision record if the change alters scope, sources, model, cadence,
   platform, access, or capacity.
4. Update the Phase 2 README if the change affects navigation or the dashboard.
5. Update the root README only for project-level state, not work-package detail.
6. Do not create a second "summary" document that competes with a canonical source.
7. Do not use dead relative links for planned files. Use backtick paths until the
   file exists.

## Freshness markers

Use a `Last reviewed` date in a document only when the review is meaningful. The
canonical changing documents are `PROGRESS.md` and `DECISIONS.md`; they carry dates.
Design documents should be updated when the design changes, not merely reformatted.

## Conflict handling

If two documents disagree:

1. Check the canonical-source table.
2. Check `DECISIONS.md` for a later decision.
3. Check `PROGRESS.md` for a recent handoff.
4. If the conflict remains, stop and ask the human. Do not choose silently.
