# Phase 2 Agent Contract

This document is the phase-specific operating contract for coding agents working on
AeroGrid Phase 2. It is subordinate to the repository-wide
[AGENTS.md](../AGENTS.md) and to direct human instructions.

## Current state

- Phase 1 is frozen and must not be edited.
- Phase 2 documentation and planning baseline is ready for human review.
- **No Phase 2 implementation is authorized.**
- Do not create or modify SQL, ETL code, workflows, database objects, cloud
  resources, or test fixtures that imply implementation until the human clears
  gate `G1`.
- The current gate and next human action are recorded in
  [PROGRESS.md](PROGRESS.md).
- The current authorization status is `implementation_authorized: NO`.

## Mission

Build a reproducible, cloud-hosted PostgreSQL data warehouse and ETL pipeline for
real low-altitude airspace data. The warehouse must be usable by all five team
members and must satisfy the Phase 2 requirements in
[`DWBI Lab Phase 2.pdf`](DWBI%20Lab%20Phase%202.pdf).

The design is documented in [docs/00_documentation_map.md](docs/00_documentation_map.md).
Do not implement from memory or from a chat summary. Implement from the canonical
documents and the assigned work package.

## Precedence

When instructions conflict, use this order:

1. Direct instruction from the current human user.
2. [`../AGENTS.md`](../AGENTS.md).
3. This file.
4. Canonical Phase 2 documents in [docs/00_documentation_map.md](docs/00_documentation_map.md).
5. Work package details in [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md).
6. Other documentation.

If a conflict remains, stop and ask the human.

## Required reading before work

Read, in order:

1. [`../AGENTS.md`](../AGENTS.md).
2. [README.md](README.md).
3. This file.
4. [PROGRESS.md](PROGRESS.md).
5. [docs/00_documentation_map.md](docs/00_documentation_map.md).
6. The canonical document for the area being changed.
7. The assigned work package in
   [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md).
8. The relevant template in [templates/](templates/).

If the assigned work package is not in `READY` state, stop. Do not start dependent
work early.

## Assignment protocol

When a human assigns a work package, your first response must state:

- The work package ID and title.
- Whether its dependencies and gate are satisfied.
- The files you expect to read and change.
- The acceptance evidence you will produce.
- Any human-only action or secret that appears necessary.

Do not begin implementation if the work package is `NOT_STARTED`, `BLOCKED`, or
`BLOCKED_ON_HUMAN` without human confirmation that the state has changed.

## Non-negotiable constraints

- Real, public data only. Never generate synthetic flights, weather, vehicles,
  restrictions, or encounters. Derived metrics must be traceable to real source rows.
- No local PostgreSQL, Docker, dev containers, or local service containers.
- Free tools and free tiers only. No card-gated service, trial conversion, or paid
  quota.
- Weekly or manual refresh only. Do not add five-minute polling.
- All five members must be able to read the shared warehouse.
- Raw data stays out of Git and belongs in cloud object storage with provenance.
- Never handle or print secrets. A human adds secrets through the GitHub or Neon UI.
- Do not edit `Phase1/` or Phase 1 PDFs.
- Do not add a tool or dependency without checking its license and free-tier terms.
- Do not change the study sites, source set, cadence, or data model without a human
  decision recorded in [DECISIONS.md](DECISIONS.md).

## Work package rules

- Work on exactly one work package at a time.
- One owner is accountable per work package. Other members may review or support.
- Do not mix unrelated refactors with the assigned package.
- Keep implementation changes on a short-lived branch.
- Do not commit, push, or open a PR unless the human explicitly asks.
- If implementation is authorized, use the acceptance evidence in
  [dev_plan/04_acceptance_and_definition_of_done.md](dev_plan/04_acceptance_and_definition_of_done.md).
- Update [PROGRESS.md](PROGRESS.md) before ending a session. Include status, files
  changed, checks run, blockers, and handoff.
- Update the canonical document and [DECISIONS.md](DECISIONS.md) when a decision or
  interface changes.
- Never mark work `DONE` based on intent. Use evidence.

## Status vocabulary

Use only these statuses in `PROGRESS.md`:

| Status | Meaning |
|---|---|
| `NOT_STARTED` | No work has begun. |
| `READY` | Dependencies and gates are satisfied; work may begin. |
| `IN_PROGRESS` | An authorized owner is actively working. |
| `BLOCKED` | A technical or dependency issue prevents progress. |
| `BLOCKED_ON_HUMAN` | A human-only action is required. |
| `READY_FOR_REVIEW` | Work and evidence are complete; review is pending. |
| `DONE` | Accepted against the work package's acceptance criteria. |
| `CANCELLED` | Human-approved removal from scope. |

Only the human or the work package owner with human confirmation may mark work
`DONE`.

## Stop-and-ask register

Stop immediately and ask the human when any of the following is true. When stopping,
add an `H-###` item to the human action queue in `PROGRESS.md` if human action is
needed.

### Accounts, secrets, and access

- Creating a Neon project, branch, bucket, credential, database role, or API key.
- Adding, reading, rotating, or revealing a GitHub or Neon secret.
- Inviting a member, changing repository visibility, changing branch protection, or
  changing organization settings.
- Accepting data-use terms or applying for OpenSky historical/Trino access.

### Data and licensing

- A source's license, redistribution terms, or attribution requirement is unclear.
- A source is unavailable, changed schema, or requires credentials.
- You need to add a new source or remove an agreed source.
- You need to commit or redistribute raw data.
- A quality issue needs a business decision (for example, what counts as a close
  encounter or how to handle out-of-range positions).

### Scope and design

- The task would change the agreed data model, sites, fact grains, dimensions,
  cadence, or deliverables.
- Documentation and implementation disagree.
- A needed change would break the Phase 2 rubric or the team's ability to read data.
- The requested work depends on an unapproved or paid tool.

### Database and production safety

- You need to run destructive SQL, drop or truncate tables, or delete a schema.
- You need to change the shared database outside the CI pipeline.
- You need to load a large volume that risks the 1 GB database limit.
- You need to delete or overwrite raw archives in object storage.
- You need to force-push, rewrite Git history, or delete a branch.

### Blocked progress

- You have tried two reasonable fixes and are still blocked.
- You cannot verify a critical data-quality result.
- You cannot determine which document is authoritative.

Do not work around a human-only block. State the exact action needed and stop.

## Human action protocol

If human action is required:

1. Set the work package to `BLOCKED_ON_HUMAN`.
2. Add a stable `H-###` entry to the human action queue in `PROGRESS.md`.
3. Include the action, why it is needed, the safest path, and what you already checked.
4. Do not ask the human to paste secret values into chat. Point to the correct UI.
5. End the session with a clear next step for the human.

## File ownership and review

| Area | Accountable member | Required review |
|---|---|---|
| Platform, CI, cloud access, progress | Member A | Member C or D for schema/CI impact |
| Source ingestion and staging | Member B | Member C for field mapping |
| SQL schema and dimensions | Member C | Member A for CI and Member B for sources |
| Core facts and key mapping | Member D | Member C for surrogate keys |
| Derived facts, DQ, reports, reporting views | Member E | Member D for fact inputs and Member A for CI |
| Phase 2 docs and decisions | Member A | All affected owners |

Names are placeholders until the human assigns real names in
[docs/08_team_work_division.md](docs/08_team_work_division.md).

Cross-cutting files such as `PROGRESS.md`, `DECISIONS.md`, and the root `README.md`
require the accountable owner to coordinate with affected members.

## Documentation synchronization

Update documentation in the same work package as the change when the change affects:

- Architecture or platform.
- Data model, grain, keys, or units.
- Source set, cadence, or license.
- ETL stages or quality rules.
- Work packages, gates, or acceptance criteria.
- Team access or security.

Canonical sources:

- Architecture: [docs/02_architecture_and_platform.md](docs/02_architecture_and_platform.md)
- Sources: [docs/03_data_sources_and_licensing.md](docs/03_data_sources_and_licensing.md)
- Data model: [docs/04_data_model.md](docs/04_data_model.md) and
  [`../data/data_dictionary.md`](../data/data_dictionary.md)
- ETL: [docs/05_etl_pipeline.md](docs/05_etl_pipeline.md)
- DQ: [docs/06_data_quality_and_reports.md](docs/06_data_quality_and_reports.md)
- Work packages: [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md)
- Status: [PROGRESS.md](PROGRESS.md)
- Decisions: [DECISIONS.md](DECISIONS.md)

## Git and repository safety

- **Branching policy:** Never commit directly to `main`. Always use short-lived feature branches for any implementation or change work.
- **Pre-commit verification:** Before any requested commit, inspect `git status`, `git diff`, and recent history. Verify that no secrets, API keys, `.env` files, raw data, database dumps, or large binaries are staged.
- **Commit scope:** Keep commits strictly scoped to one work package with a concise message. Do not mix documentation and implementation in the same commit unless required.
- Do not push, open pull requests, or create tags unless explicitly asked by the human.

- Never commit secrets, connection strings, `.env` files, raw data, database dumps,
  or large binaries.
- Do not add raw data under `Phase2/` or `data/`; use the approved object-storage
  bucket after `G1`.
- Do not edit `Phase1/` or the historical course PDFs.
- Do not change the default branch, repository visibility, or branch protection.
- Use scoped commits only when the human explicitly requests a commit.
- Before any requested commit, inspect `git status`, `git diff`, and recent history.

## Completion evidence

A work package is not complete until:

- All acceptance criteria in the work package pass.
- Relevant checks or tests have been run and their output is recorded.
- Documentation and decision records are synchronized.
- `PROGRESS.md` contains the handoff and any remaining blockers.
- A reviewer has checked the artifacts if the package requires review.
- No secrets, raw data, or unrelated changes are included.

## Immediate stop conditions for this session

This session is documentation-only. If asked to do any of the following now, refuse
and point to the current gate:

- Create SQL tables or schemas.
- Write ETL code.
- Add GitHub Actions YAML workflows.
- Create a Neon project or bucket.
- Add secrets or invite members.
- Load data into the shared database.
- Mark `G1` as complete.

The next required action is human review of the baseline and completion of the
human prerequisites in `PROGRESS.md`.
