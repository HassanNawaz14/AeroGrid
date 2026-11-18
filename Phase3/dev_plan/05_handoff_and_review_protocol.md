# Phase 3 Handoff and Review Protocol

## Session start

1. Read root `AGENTS.md` → Phase 2 `README`/`AGENTS` → Phase 3 `README` → Phase 3
   `AGENTS` → Phase 3 `PROGRESS` → canonical doc for the area → the WP → `git status`.
2. Stop if the WP is `NOT_STARTED`/`BLOCKED`/`BLOCKED_ON_HUMAN`, or if its
   prerequisites/gate are not met.
3. Restate WP ID, gate state, files, acceptance evidence, human-only actions.

## Claiming work

- Claim exactly one WP: set `IN_PROGRESS` with your name and date in
  `Phase3/PROGRESS.md`. Never hold two.
- Branch: `phase3/wp-p3-XX-short-name` from `main`. Never work directly on `main`.
- Scope: only the WP's files. No opportunistic refactors.

## Pre-commit checks

1. `git status` / `git diff` — confirm scope.
2. Secret/raw-data/oversized-binary scan on staged files (PBIX/PDF/PPT per `D3-008`).
3. Run the WP's checks; record commands and results.
4. Commit only when the human explicitly asks; keep the commit scoped to one WP.

## Pull request requirements

Every PR states:

1. WP ID and title.
2. Files changed and why.
3. Evidence: commands run, results, counts, capture dates.
4. Capacity impact, if any.
5. Limitations touched (coverage labels), if any.
6. Reviewers requested (the WP's two named reviewers).

## Review standards

Reviewers verify, not summarize:

- Re-run the recorded queries; compare with the artifact's numbers.
- Check zero labels, KPI dictionary conformance, and citation maps.
- Check idempotency where applicable (views, indexes, workflows).
- Confirm documentation sync and PROGRESS update.
- Outcomes: **Approved / Approved with comments / Changes requested / Blocked /
  Rejected**. The author cannot approve their own PR.

## Session end handoff

Update `Phase3/PROGRESS.md` (or reference the PR): WP status, files changed, checks
run with results, evidence locations, blockers with `H3-###` IDs if human action is
needed, and the next concrete step. Use the Phase 2 handoff template
(`Phase2/templates/AGENT_HANDOFF.md`) unless Phase 3 introduces its own.

## Conflict handling

Re-read the authority order in `Phase3/AGENTS.md`. If two authoritative sources
still conflict, stop, record both, and ask the human; do not guess. Record the
resolution in `Phase3/DECISIONS.md`.
