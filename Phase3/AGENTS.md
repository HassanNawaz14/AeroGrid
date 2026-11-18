# Phase 3 AGENTS.md — agent operating contract

This is the Phase 3 contract for coding agents. The repository-wide contract is
[../AGENTS.md](../AGENTS.md); the Phase 2 contract is
[../Phase2/AGENTS.md](../Phase2/AGENTS.md). Read both. Where they conflict, the
order is: direct human instruction → ../AGENTS.md → this file → canonical Phase 3
documents → work package details. Unresolved conflicts stop the work; ask the human.

## Precedence and authority

- Phase 1 stays frozen. Phase 2 is accepted; its schemas, pipeline, and gates are
  reused as-is. Phase 3 must not "improve" Phase 2 artifacts outside an approved
  Phase 3 work package.
- A change to the shared warehouse model, fact grains, sources, or cadence is a
  scope change: stop, record a decision in [DECISIONS.md](DECISIONS.md), and ask.

## First-interaction protocol

At the start of every session, always ask the human: "What is your team member name,
and have you selected your team role (A through E)?" If no role is selected, ask them
to choose one first. Then give a concise status report from
[PROGRESS.md](PROGRESS.md) and list the exact tasks awaiting that member.

## Required reading before any Phase 3 task

1. [../AGENTS.md](../AGENTS.md)
2. [Phase 2 README](../Phase2/README.md) and [Phase 2 PROGRESS](../Phase2/PROGRESS.md)
3. [../Phase2/AGENTS.md](../Phase2/AGENTS.md)
4. [README.md](README.md) (this folder)
5. This file
6. [PROGRESS.md](PROGRESS.md)
7. [docs/00_documentation_map.md](docs/00_documentation_map.md)
8. The canonical document for the area being changed
9. The assigned work package in [dev_plan/01_work_breakdown.md](dev_plan/01_work_breakdown.md)

If the work package is not `READY`, stop. If it needs a human-only action, use the
human action protocol below.

## Assignment protocol

The first response after receiving a Phase 3 task must state:

1. Work package ID and title.
2. Which gate(s) it satisfies and their current state.
3. Files expected to change.
4. The acceptance evidence that will be produced.
5. Any human-only actions required.

## Non-negotiable constraints

- Real public data only. Never fabricate analytics, KPI values, screenshots, or
  dashboard numbers.
- Phase 3 analytics read from `project_dw` and `project_reporting` only. New views
  must be built on the Phase 2 star schema; no new base tables without a decision.
- The pipeline rules of Phase 2 remain in force: fail closed, reconcile counts,
  idempotent reruns, no silent DQ downgrades, empty-means-missing-coverage.
- Free tools and free tiers only; no credit card, no paid connectors, no Power BI
  Service workspaces unless a human creates the account.
- No local PostgreSQL, no Docker, no machine-local dependencies.
- All five members must keep read access through `aerogrid_reader`.
- Never commit secrets, connection strings, `.env` files, or raw data. Never ask a
  human to paste secrets into chat.
- Do not edit `Phase1/`, Phase 1 PDFs, or accepted Phase 2 deliverables except
  through an approved Phase 3 work package.

## BI ownership rule

All BI deliverables — the Power BI dashboard (`.pbix`), dashboard screenshots,
business insights report, and final presentation — belong to **one owner**
(Member E; see [docs/08_team_work_division.md](docs/08_team_work_division.md)).
Other members review; only Member E authors BI artifacts. Member A owns CI plumbing
(workflows, artifact packaging), not BI content.

## Work discipline

- One work package at a time; one accountable owner per work package.
- Status vocabulary is exactly: `NOT_STARTED`, `READY`, `IN_PROGRESS`,
  `BLOCKED_ON_HUMAN`, `BLOCKED`, `READY_FOR_REVIEW`, `DONE`, `CANCELLED`.
  "Almost done" is forbidden. Agents may set `READY_FOR_REVIEW` at most; `DONE`
  requires the owner or human with recorded evidence.
- Prefer read-only inspection before edits. Keep changes inside the assigned
  package; no opportunistic refactors.
- Update canonical documentation in the same package when a decision, interface,
  or artifact changes. Record material decisions in [DECISIONS.md](DECISIONS.md).

## Git rules

- Never commit directly to `main`. Use short-lived branches
  (`phase3/wp-p3-XX-short-name`).
- Before any requested commit, inspect `git status`, `git diff`, and recent
  history. Verify no secrets, raw data, or large binaries are staged. PBIX/PDF
  artifacts follow the size guard in
  [docs/07_operations_access_and_security.md](docs/07_operations_access_and_security.md).
- Do not push, open pull requests, merge, or create tags unless the human
  explicitly asks. Reviewers cannot approve their own change.
- Never force-push, rewrite history, delete protected branches, or change the
  default branch.

## Human-only actions

Stop and request through the human action queue in [PROGRESS.md](PROGRESS.md):

- Creating accounts, accepting terms, or installing/licensing software that needs
  an account (including Power BI Service publishing).
- Creating or deleting Neon projects, branches, buckets, credentials, or roles.
- Adding, reading, or rotating GitHub or Neon secrets.
- Inviting members, changing repository visibility, or changing branch protection.
- Running destructive SQL, dropping objects, or any production write outside CI.
- Approving scope, source, model, cadence, or threshold changes.
- Presenting the final deck or submitting the course deliverables.

## Stop-and-ask triggers

Stop immediately, record the blocker in [PROGRESS.md](PROGRESS.md), and ask when:

- A human-only action is needed (see above).
- Analytics would require data Phase 2 does not have (a new source, a new fact, or
  a grain change).
- A requested change alters the Phase 2 model, sources, cadence, or thresholds.
- Documentation and the dev plan disagree.
- A KPI definition would make an unmeasured claim (for example, treating missing
  coverage as zero activity).
- The free-tier budget is at risk (database ≥ 700 MB, object storage ≥ 3.5 GB).
- Two reasonable fixes have failed.
- The task is outside an authorized `READY` work package.

## Completion rules

A package is complete only when: acceptance criteria pass with recorded evidence;
checks are recorded; canonical docs and [DECISIONS.md](DECISIONS.md) are synced;
[PROGRESS.md](PROGRESS.md) carries the handoff (status, files, checks, blockers,
next step); a reviewer sign-off exists; and no secrets, raw data, or unrelated
changes are included.
