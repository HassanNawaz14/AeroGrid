# AGENTS.md - AeroGrid repository instructions

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](Phase2/docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

This file is the repository-wide contract for coding agents. The phase-specific
contract is [Phase2/AGENTS.md](Phase2/AGENTS.md). Read both before changing files.

## Current state

- Phase 1 is frozen; Phase 2 implementation was authorized under H-007.
- G0–G4 are historically accepted. The requester states project-administrator authority and explicitly accepted G5, G6 and G7 on 2026-11-13.
- Member E WP-07–WP-10 have been merged, persisted and accepted; H-013 was already approved for `wp07-v1` and is no longer a start blocker.
- The final release record distinguishes administrative sign-off from unverified independent G7 run or reader-access checks. Preserve CI protection and no-synthetic-production requirements.

## Authority and precedence

Use this order when instructions conflict:

1. Explicit instruction from the current human user.
2. This file.
3. [Phase2/AGENTS.md](Phase2/AGENTS.md).
4. Canonical Phase 2 documents listed in
   [Phase2/docs/00_documentation_map.md](Phase2/docs/00_documentation_map.md).
5. Other documentation.

If two authoritative sources still conflict, stop and ask the human. Do not guess.

## First-interaction role and progress protocol

- At the start of every session, always ask the human: "What is your team member name, and have you selected your team role (A through E)?"
- If the human has not selected a role yet, ask them to choose one first.
- Once selected, present a concise progress report from [Phase2/PROGRESS.md](Phase2/PROGRESS.md) and list the exact tasks awaiting them.
- HassanNawaz14 is Member A (platform, integration, and release lead). Members B-E are recorded in [Phase2/docs/08_team_work_division.md](Phase2/docs/08_team_work_division.md); `H-002` remains deferred by the human.

## Git and repository safety

- **Branching policy:** Never commit directly to `main`. Always use short-lived feature branches for any implementation or change work.
- **Pre-commit verification:** Before any requested commit, inspect `git status`, `git diff`, and recent history. Verify that no secrets, API keys, `.env` files, raw data, database dumps, or large binaries are staged.
- **Commit scope:** Keep commits strictly scoped to one work package with a concise message. Do not mix documentation and implementation in the same commit unless required.
- Do not push, open pull requests, or create tags unless explicitly asked by the human.
  Exception: inside the delegated window `D-023`, the `WP-04`/`WP-05` owners may push
  their own package branch, open its PR, and merge it after one peer approval.

Before any Phase 2 task, read:

1. This file.
2. [Phase2/README.md](Phase2/README.md).
3. [Phase2/AGENTS.md](Phase2/AGENTS.md).
4. [Phase2/PROGRESS.md](Phase2/PROGRESS.md).
5. The canonical document for the area being changed.
6. The assigned work package in
   [Phase2/dev_plan/01_work_breakdown.md](Phase2/dev_plan/01_work_breakdown.md).

For a new session, start with [Phase2/docs/00_documentation_map.md](Phase2/docs/00_documentation_map.md).

## Non-negotiable project constraints

- Use **real, public data only**. Never generate synthetic flight, weather,
  vehicle, restriction, or encounter records. Derived metrics must come from real
  source records.
- Do not introduce a local PostgreSQL dependency. The shared warehouse is
  cloud-hosted; the current platform proposal is Neon Free.
- Do not use Docker, Docker Compose, dev containers, or local service containers.
- Use free tools and free tiers only. Do not add a tool that requires a credit
  card, paid plan, trial conversion, or billing account.
- The automated refresh cadence is **weekly or manual**, not five-minute polling.
- All five team members must be able to read the shared data. Do not design a
  member-local or machine-local warehouse.
- Keep raw data out of Git. Raw archives belong in cloud object storage with a
  provenance manifest.
- Never commit credentials, connection strings, API keys, tokens, or `.env` files.
- Never ask a human to paste secrets into chat. Direct them to the GitHub or Neon
  UI instead.
- Do not edit files under `Phase1/` or the Phase 1 PDFs. They are historical
  submissions. Phase 2 changes belong in Phase 2 documents or implementation
  paths.
- Do not add paid services, paid data, or card-gated storage. If the free tier is
  insufficient, stop and escalate as a capacity decision.

## Human-only actions

Agents must not perform these actions. Stop and request the action through the
human action queue in [Phase2/PROGRESS.md](Phase2/PROGRESS.md):

- Creating accounts, accepting terms, enabling billing, or opening a subscription.
- Creating or deleting a Neon project, branch, bucket, credential, or role.
- Adding, reading, or rotating GitHub secrets or environment secrets.
- Inviting team members, changing repository visibility, changing branch
  protection, or changing GitHub organization settings.
- Applying for OpenSky historical/Trino access or accepting data-use terms.
- Running destructive SQL, dropping schemas/tables, rewriting Git history,
  force-pushing, or deleting branches.
- Approving a scope, source, data-license, or capacity change.
- Any action that cannot be reversed safely or that affects the shared database.

## Stop-and-ask triggers

Stop immediately, record the blocker in `Phase2/PROGRESS.md`, and ask the human when:

- The task requires a human-only action.
- A source is unavailable, license terms are unclear, or credentials are needed.
- A requested change would alter the agreed scope, model, source set, or cadence.
- Documentation and the implementation plan disagree.
- A critical data-quality check fails and the correct business response is unclear.
- The free-tier quota, database size, object-storage size, or egress limit is at
  risk.
- You have tried two reasonable fixes and are still blocked.
- You are about to touch production data, secrets, repository settings, or Phase 1
  artifacts.
- The human asks for work outside an authorized `READY` work package.

When stopping, say exactly what is blocked, which human action is needed, what you
already checked, and the safest next step. Do not silently work around the block.

## Working rules

- Work on **one work package at a time**. Do not start a dependent package early.
- Read the current status before acting. Do not duplicate completed or in-progress
  work.
- Keep changes inside the assigned work package. Do not opportunistically refactor
  unrelated files.
- Prefer read-only inspection before edits. Preserve existing user changes.
- Update the canonical documentation when a decision or interface changes. Update
  [Phase2/DECISIONS.md](Phase2/DECISIONS.md) for material decisions.
- Before finishing, update [Phase2/PROGRESS.md](Phase2/PROGRESS.md) with status,
  files changed, checks run, blockers, and the next handoff.
- Do not mark work `DONE` without the acceptance evidence defined in
  [Phase2/dev_plan/04_acceptance_and_definition_of_done.md](Phase2/dev_plan/04_acceptance_and_definition_of_done.md).
- When a human action is required, mark the work package `BLOCKED_ON_HUMAN`, add a
  stable `H-###` entry to the human action queue, and stop.

## Git rules

- Do not commit, amend, push, open pull requests, or create tags unless the human
  explicitly asks.
- Never force-push, rewrite history, delete a protected branch, or change the
  default branch.
- Keep commits scoped to one work package. Do not mix documentation and
  implementation in the same commit unless the work package explicitly requires it.
- If a commit is requested, inspect `git status`, `git diff`, and recent history
  first. Never stage secrets or raw data.
- Use short-lived branches for implementation work. Do not implement directly on
  `main`.

## Documentation map

- Phase dashboard and progress: [Phase2/README.md](Phase2/README.md)
- Status and human action queue: [Phase2/PROGRESS.md](Phase2/PROGRESS.md)
- Phase agent contract: [Phase2/AGENTS.md](Phase2/AGENTS.md)
- Architecture: [Phase2/docs/02_architecture_and_platform.md](Phase2/docs/02_architecture_and_platform.md)
- Data sources and licenses: [Phase2/docs/03_data_sources_and_licensing.md](Phase2/docs/03_data_sources_and_licensing.md)
- Logical data model: [Phase2/docs/04_data_model.md](Phase2/docs/04_data_model.md)
- ETL plan: [Phase2/docs/05_etl_pipeline.md](Phase2/docs/05_etl_pipeline.md)
- Data quality: [Phase2/docs/06_data_quality_and_reports.md](Phase2/docs/06_data_quality_and_reports.md)
- Team division: [Phase2/docs/08_team_work_division.md](Phase2/docs/08_team_work_division.md)
- Agent operating manual: [Phase2/docs/09_agent_operating_manual.md](Phase2/docs/09_agent_operating_manual.md)
- Human operating manual: [Phase2/docs/10_human_operating_manual.md](Phase2/docs/10_human_operating_manual.md)

## Current instruction

WP-07–WP-10 have been merged and accepted by requester-admin declaration. Use the current `Phase2/PROGRESS.md`, `Phase2/DECISIONS.md` and the final gate record rather than earlier historical status paragraphs. Member A/team retain independent WP-11/12 integration and reader-access proof follow-up; do not fabricate technical evidence. Phase 1 stays frozen.

