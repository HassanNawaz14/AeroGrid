# Handoff and Review Protocol

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](../docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Purpose

This protocol prevents lost state, duplicate work, unreviewed data changes, and
secret leaks. It applies to every Phase 2 work package.

## Session start

1. Read `AGENTS.md`.
2. Read `Phase2/README.md`.
3. Read `Phase2/AGENTS.md`.
4. Read `Phase2/PROGRESS.md`.
5. Read the canonical document for the area.
6. Read the assigned work package.
7. Run `git status` and inspect recent history.
8. Confirm the package is authorized and not already `DONE`.
9. Confirm prerequisites and gate status.
10. State the intended change and acceptance evidence.

If the package is `NOT_STARTED`, `BLOCKED`, or `BLOCKED_ON_HUMAN`, stop unless the
human has explicitly changed the state.

## Claiming a work package

Update `PROGRESS.md`:

- Set the package to `IN_PROGRESS`.
- Record the owner and start context.
- Keep the next action accurate.
- Do not claim two packages.

Coordinate with the reviewer before starting if the change affects their layer.

## Branching

- Branch from current `main`.
- Use `phase2/wp-XX-short-name`.
- Do not work directly on `main`.
- Do not rewrite history.
- Do not force-push.
- Keep one package per branch.

## Before a commit

1. Inspect `git status`.
2. Inspect `git diff`.
3. Check for secrets, `.env`, dumps, raw data, and large binaries.
4. Confirm only intended files are staged.
5. Confirm docs and dictionary changes are included when required.
6. Run the relevant checks.
7. Do not use `git add -A` blindly.

Do not commit unless the human explicitly asks.

## Pull request contents

A PR must state:

- Work package ID and title.
- What changed and why.
- Source/real-data evidence.
- Schema or interface changes.
- Commands/checks run and results.
- Row counts and DQ status.
- Capacity impact.
- Known limitations.
- Human actions or blockers.
- Reviewer requested.

Link the canonical docs and acceptance evidence.

## Review responsibilities

The reviewer must check:

- Scope is limited to the work package.
- No synthetic data or fabricated result.
- Real source URL/license/hash present.
- Natural and surrogate keys are correct.
- Counts reconcile.
- Critical DQ passes or is explicitly blocked.
- Rerun is idempotent.
- No secret/raw data is included.
- Docs and dictionary are synchronized.
- Tests cover the changed behavior.
- `PROGRESS.md` is accurate.
- The free-tier budget is respected.

The reviewer must not approve based on a summary alone. Inspect the diff and evidence.

## Required reviewer by change

| Change | Reviewer |
|---|---|
| Source client or staging | Member C; Member D for georeferencing |
| Schema or dimension | Member A; Member D for fact impact |
| Fact loader/key mapping | Member C; Member E for derived inputs |
| Derived fact/DQ | Member C or D |
| Report | Member B for cleaning claims; Member A for CI |
| CI/access | Member B or C |
| Docs/decisions | Affected owners |

The author cannot self-approve. The human approves scope and gates.

## Review outcomes

| Outcome | Meaning |
|---|---|
| Approved | Evidence is sufficient; merge allowed |
| Approved with comments | Merge after minor fixes; no new scope |
| Changes requested | Evidence or implementation incomplete |
| Blocked | Human/technical dependency prevents acceptance |
| Rejected | Wrong scope or invalid approach; stop and ask |

Do not merge with an unresolved critical DQ failure.

## Handoff at session end

Update `PROGRESS.md` with:

- Work package and status.
- Files changed.
- Commands/checks run and outcomes.
- Counts/evidence.
- Decisions and links.
- Blockers and human actions.
- Exact next step.
- Reviewer/owner.

Use `Phase2/templates/AGENT_HANDOFF.md`.

## Handoff quality bar

A handoff is insufficient if:

- It says "done" without evidence.
- It does not name the next step.
- It leaves an unrecorded decision.
- It hides a failed check.
- It requires the next member to rediscover the state.
- It includes a secret or raw data path that should not be shared.

## Conflict resolution

1. Re-read the authority order.
2. Compare the canonical docs.
3. If they still conflict, stop.
4. Record the conflict and the options in `PROGRESS.md`.
5. Ask the human to decide.
6. Record the decision in `DECISIONS.md`.

Do not resolve a scope conflict by choosing the easier implementation.

## Escalation

Escalate immediately for:

- Human-only actions.
- Unclear licenses or unavailable sources.
- Critical DQ failure with unclear business response.
- Capacity or quota risk.
- Secret exposure.
- Destructive SQL or production data changes.
- A request to skip a gate or review.

## Human approval

The human is required for:

- `H-###` actions.
- `G1` and `G7`.
- Scope/source/model/cadence changes.
- Threshold changes after results are known.
- Capacity decisions.
- Destructive operations.

The human does not need to approve routine code style or local refactors that stay
inside the package and do not change interfaces.

## Post-merge

- Confirm the package status is `DONE` only after acceptance.
- Update dependent packages to `READY` if appropriate.
- Record the gate if the package closed one.
- Keep the handoff log history.
- Start no more than one new package per member.
