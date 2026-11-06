# Agent Operating Manual

## Purpose

This is the practical session manual for coding agents. It explains how to start,
what to read, how to work, when to stop, and how to hand off. The binding rules remain
[`../../AGENTS.md`](../../AGENTS.md) and [`../AGENTS.md`](../AGENTS.md). If this manual
conflicts with them, the higher-level file wins.

## Current authorization

- Phase 1 is frozen.
- Phase 2 documentation and planning baseline is accepted (`G0`/`H-001`).
- Phase 2 implementation is **authorized** (`H-007`, 2026-11-04).
- `G1` is closed; the current gate is `G2`.
- `WP-02` is `DONE` (accepted 2026-11-07; PR #3 merged); `WP-03` is `READY` and
  authorized.
- Later work packages begin only after their gate and authorization are recorded in
  [`../PROGRESS.md`](../PROGRESS.md).

## Session start checklist

1. Read `AGENTS.md`.
2. Read `Phase2/README.md`.
3. Read `Phase2/AGENTS.md`.
4. Read `Phase2/PROGRESS.md`.
5. Read `Phase2/docs/00_documentation_map.md`.
6. Read the canonical document for the area.
7. Read the assigned work package.
8. Check `git status` and recent history.
9. Confirm the work package is authorized and not already done.
10. State the intended change before editing.

Do not skip the status check. Do not duplicate completed work.

## Source authority order

1. Explicit instruction from the current human.
2. Root `AGENTS.md`.
3. `Phase2/AGENTS.md`.
4. Canonical Phase 2 documents.
5. Other documentation.

If two authoritative sources conflict, stop and ask. Do not guess.

## Non-negotiable constraints

- Real public data only. Never generate synthetic flight, weather, vehicle,
  restriction, or encounter data.
- No local PostgreSQL dependency.
- No Docker, dev containers, or service containers.
- Free tools and free tiers only; no card-gated service.
- Weekly or manual refresh; no five-minute polling.
- All five members read the shared warehouse.
- Raw data stays out of Git and in cloud object storage with a manifest.
- Never commit or reveal credentials, connection strings, tokens, or `.env` files.
- Never ask a human to paste a secret into chat.
- Do not edit Phase 1 artifacts.
- Do not alter scope, sources, cadence, or model without approval.

## Work package discipline

- Work on one work package at a time.
- Keep edits inside the assigned package.
- Do not opportunistically refactor unrelated files.
- Do not start a dependent package early.
- Do not mark `DONE` without acceptance evidence.
- Do not mix documentation and implementation in one commit unless the package
  requires it.
- Do not commit, push, open a PR, or create a tag unless explicitly asked.
- Do not implement directly on `main`.

## Before editing

- Locate the canonical file and its related interface.
- Read surrounding code and documentation.
- Check for existing work, TODOs, or conflicting decisions.
- Identify the exact acceptance evidence.
- Identify any human-only dependency.
- Prefer read-only inspection.

## While editing

- Preserve user changes.
- Follow existing style and libraries.
- Do not add comments unless requested.
- Do not invent dependencies.
- Do not add a secret, token, or real connection string.
- Do not add raw data or large binaries.
- Keep SQL and code parameterized.
- Use UTC for stored timestamps.
- Keep transformations reproducible.
- Record material decisions in `DECISIONS.md`.

## Stop-and-ask triggers

Stop immediately and record the blocker in `PROGRESS.md` when:

- A human-only action is required.
- A source is unavailable, has changed schema, or has unclear license terms.
- Credentials or account access are needed.
- The task changes scope, source set, model, cadence, or thresholds.
- Documentation and the plan disagree.
- A critical DQ check fails and the correct response is unclear.
- A free-tier quota or capacity limit is at risk.
- Two reasonable fixes have failed.
- You are about to touch production data, secrets, repository settings, or Phase 1
  artifacts.
- The human requests work outside an authorized `READY` work package.
- You cannot verify a claim with real evidence.

When stopping, state:

1. What is blocked.
2. Which human action is needed.
3. What you already checked.
4. The safest next step.

Do not silently work around the block.

## Human-only actions

Agents must not:

- Create accounts, accept terms, enable billing, or start a subscription.
- Create/delete a Neon project, branch, bucket, credential, or role.
- Add/read/rotate GitHub or environment secrets.
- Invite members or change repository visibility.
- Change branch protection or GitHub organization settings.
- Apply for OpenSky historical/Trino access or accept data-use terms.
- Run destructive SQL, drop schemas/tables, rewrite history, force-push, or delete
  branches.
- Approve scope, source, license, or capacity changes.
- Trigger a production ETL run unless explicitly authorized.
- Clear `G1` on their own.

## Secret handling

- Never print environment variables or connection strings.
- Never read `.env` files containing real secrets.
- Never commit a secret.
- If a secret is exposed, stop and tell the human to rotate it.
- Use placeholders such as `<DATABASE_URL>` in docs.
- Do not ask the human to paste a value into chat; direct them to the GitHub or Neon
  UI.

## Source handling

- Cite the exact source URL and license.
- Verify the file is real and public.
- Record size, hash, and fetch time in the manifest.
- Do not synthesize missing rows.
- Do not lower a DQ threshold to pass.
- Do not mix altitude datums silently.
- Do not treat a standing UAS facility map as a TFR.
- Do not assume historical TFR coverage that the source does not provide.
- Do not commit raw archives.

## Database handling

- All writes go through CI after authorization.
- Use the write role only from CI.
- Use idempotent upserts.
- Never run `DROP`, `TRUNCATE`, or unbounded `DELETE` without a human decision.
- Never disable TLS.
- Never create a local PostgreSQL server.
- Stop before exceeding the 1 GB database or 5 GB object-storage budget.
- Do not add indexes to production without a work package.

## Testing and validation

- Check the repository for the real test command before assuming one.
- Use real source fixtures only if they are small, public, and licensed.
- Do not create fake production data.
- Validate counts and keys.
- Verify links in documentation.
- Run lint/typecheck if configured.
- Record exact commands and results in the handoff.

## Git rules

- Inspect `git status`, `git diff`, and recent history before committing.
- Stage only intended files.
- Never stage secrets or raw data.
- Do not use `git add -A` blindly.
- Do not amend a failed commit; create a new one.
- Do not force-push.
- Do not commit unless asked.
- Keep commits scoped to one work package.
- Link the work package and evidence in the commit message if committing.

## Documentation rules

- Update the canonical document when an interface or decision changes.
- Update the data dictionary and DBML together.
- Update `PROGRESS.md` before finishing.
- Use relative links that work from the file's directory.
- Do not create new documentation files unless required.
- Do not edit Phase 1 PDFs or `.tex` submissions.
- Keep placeholders explicit; do not invent member names.

## Handoff requirements

Before ending a session:

1. Update `PROGRESS.md` with status, files changed, checks, blockers, and next step.
2. Add or update a `H-###` human action if blocked.
3. Record decisions in `DECISIONS.md`.
4. Leave the workspace in a readable state.
5. Do not commit unless asked.

Use `Phase2/templates/AGENT_HANDOFF.md`.

## Common failure modes

| Failure | Correct response |
|---|---|
| Implementing outside an authorized `READY` package | Stop; cite the gate; do not create files |
| Inventing data to fill a table | Stop; real data only |
| Lowering a threshold to pass DQ | Stop; ask the human |
| Requesting a secret in chat | Stop; direct to the UI |
| Creating a local database | Stop; use the shared cloud warehouse |
| Loading raw data into PostgreSQL | Stop; archive raw separately |
| Committing `.env` or a dump | Stop; remove and rotate if exposed |
| Duplicating another member's package | Stop; coordinate through `PROGRESS.md` |
| Claiming a report without evidence | Stop; produce counts and checks |

## Completion criteria

A task is complete only when:

- Acceptance criteria are met.
- Required checks pass.
- Documentation is updated.
- No secrets/raw data are staged.
- `PROGRESS.md` records evidence.
- The human is told the exact next action if a gate is next.

## Current next action

`WP-02` (platform validation and access proof) is `DONE`, accepted on 2026-11-07 with
validation run `42276737288` `PASS`. `WP-03` (source validation and georeferencing) is
the active Member B package and is authorized. Do not start a later package until its
gate is recorded in [`../PROGRESS.md`](../PROGRESS.md), and do not fabricate evidence.
The `DONE` marking for `WP-02` was made on HassanNawaz14's explicit instruction and is
recorded in the package acceptance table there.
