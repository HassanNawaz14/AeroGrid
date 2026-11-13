# Phase 2 Development Plan

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](../docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Purpose

This directory turns the Phase 2 scope into sequenced, reviewable work packages. It
is the canonical plan for Members A-E and their agents. The status dashboard remains
[`../PROGRESS.md`](../PROGRESS.md).

## Authorization status

- H-007 authorized Phase 2, and G0–G4 were previously accepted.
- The requester asserts administrator rights and expressly accepts G5, G6 and G7 on 2026-11-13 (D-025 through D-027).
- WP-07–WP-10 are deployed, merged and administratively accepted. The old H-013 blocker has been resolved.
- WP-11/12 and independent second-member read access / complete end-to-end evidence are still technical follow-up; never invent these runs.
- Canonical status: [PROGRESS.md](../PROGRESS.md) and [gate record](../docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

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
