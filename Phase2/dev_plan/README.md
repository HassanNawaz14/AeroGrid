# Phase 2 Development Plan

## Purpose

This directory turns the Phase 2 scope into sequenced, reviewable work packages. It
is the canonical plan for Members A-E and their agents. The status dashboard remains
[`../PROGRESS.md`](../PROGRESS.md).

## Authorization status

- Phase 2 implementation is **authorized** (`H-007`, 2026-11-04).
- `G2`, `G3`, and `G4` are closed; the current gate is `G5`.
- `WP-02`-`WP-06` are `DONE` (PR #3 `b6b76b9`, PR #5 `f9087f4`, PR #7, PR #8, PR
  #12 `f29b099`). `G4` was recorded 2026-11-11 after the real Tartan WP-05/WP-06 runs
  passed and `B-011` was resolved. `WP-07` is `BLOCKED_ON_HUMAN` on `H-013`; Member E
  starts after the human approves the thresholds and `algorithm_version`. The `WP-07`
  brief is in [`01_work_breakdown.md`](01_work_breakdown.md).
- Later work packages begin only after their gate and authorization are recorded in
  [`../PROGRESS.md`](../PROGRESS.md).
- Do not create resources or data outside the assigned work package.

## How to use this plan

1. Read the canonical design document for the work package.
2. Read the work package in `01_work_breakdown.md`.
3. Confirm prerequisites and gate status.
4. Claim one package in `PROGRESS.md`.
5. Implement only that package.
6. Produce the acceptance evidence.
7. Request peer review.
8. Update the handoff and status.

## Plan files

| File | Purpose |
|---|---|
| `01_work_breakdown.md` | Work packages, owners, deliverables, acceptance |
| `02_dependencies_and_gates.md` | Dependency graph and gate criteria |
| `03_deliverables_matrix.md` | Rubric and artifact traceability |
| `04_acceptance_and_definition_of_done.md` | Global and per-package DoD |
| `05_handoff_and_review_protocol.md` | Branches, PRs, reviews, handoffs |

## Work package sequence

```text
WP-00 docs baseline
  -> WP-01 human prerequisites (G1)
  -> WP-02 platform validation
  -> WP-03 source validation (G2)
  -> WP-04 staging
  -> WP-05 dimensions (G3)
  -> WP-06 core facts (G4)
  -> WP-07 derived facts (G5)
  -> WP-08 data quality
  -> WP-09 reports
  -> WP-10 reporting views (G6)
  -> WP-11 CI and access
  -> WP-12 integration and release (G7)
```

`WP-02`-`WP-06` are complete and `G4` is recorded. `WP-07` waits for `H-013`
(thresholds and `algorithm_version`) before Member E starts; later packages wait for
`G5` and their own authorization. `WP-11` can prepare documentation early but must
not create workflows until it is authorized.

## Team ownership

Members B-E are recorded in [`../docs/08_team_work_division.md`](../docs/08_team_work_division.md);
`H-002` remains deferred by the human.

| Member | Scope |
|---|---|
| A | Platform, CI, access, integration, release |
| B | Source clients, raw archive, staging, cleaning |
| C | Schema, dimensions, keys, data dictionary |
| D | Tracking and journey facts |
| E | Derived facts, DQ, reporting views, PDFs |

## Status language

Use exactly:

- `NOT_STARTED`
- `READY`
- `IN_PROGRESS`
- `BLOCKED_ON_HUMAN`
- `BLOCKED`
- `READY_FOR_REVIEW`
- `DONE`
- `CANCELLED`

Do not use "almost done" as a status.

## Change control

A change to scope, source set, cadence, model grain, thresholds, or capacity requires:

1. A decision entry in `../DECISIONS.md`.
2. A `PROGRESS.md` update.
3. Human approval when it changes the agreed baseline.

Do not edit the plan silently to match an implementation shortcut.
