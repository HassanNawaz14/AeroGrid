# WP-P3-H3: SCD Type 2 evaluation for `dim_vehicle`

Owner: Member C (schema and dimensions). Track: optional hardening. Decision:
`D3-017`. This is an evaluation, not an implementation: no Type 2 table is created, no
dimension changes and no loader changes.

## Question

Does any Phase 3 question need attribute history for a vehicle, and does the data hold an
attribute that changes? Type 2 only helps when both are true.

## What the code does today

| Fact | Where |
|---|---|
| `dim_vehicle` holds `vehicle_type`, `first_seen_ts` and `last_seen_ts` besides the keys | `Phase2/sql/02_dimensions/01_dimensions.sql` |
| The loader writes the constant `'UAS'` as `vehicle_type` for every vehicle | `VEHICLE_SQL` in `Phase2/etl/dimension_loaders.py` |
| The refresh is insert-only (`ON CONFLICT DO NOTHING`), so `last_seen_ts` is not advanced after first load | same file; `Phase2/docs/15_architecture_and_evaluation_guide.md` |
| `stg_uas_position` has a serial but no model, operator or registration column | `Phase2/sql/01_staging/02_source_tables.sql` |
| Identity is source-scoped (`source_system` + serial), not a global aircraft | `L3-003`, `Phase3/docs/13_accepted_data_limitations.md` |
| Type 1 is the recorded Phase 2 scope; Type 2 is listed as future work | `Phase2/docs/04_data_model.md` |

## Evidence probes

All probes are single `SELECT` statements in `Phase3/sql/scd2_evaluation/`, run read-only
through `Phase3/scripts/evaluate_scd2.py` (or the `WP-P3-H3 SCD2 evaluation evidence`
workflow, `H3-010`).

| ID | Measures |
|---|---|
| `QW-P3-H3-01` | Real members, distinct `vehicle_type` values, members with no or zero seen span |
| `QW-P3-H3-02` | Staged serials seen under several sources, on several days, or from several launch points (flight-level behaviour, not a dimension attribute) |
| `QW-P3-H3-03` | Members whose `last_seen_ts` is behind staged data, and the largest lag |
| `QW-P3-H3-04` | Tracking rows, tracked vehicles and observed months |

## Decision rules

The harness applies these rules to the probe numbers and writes the verdict into the
evidence file.

| Verdict | Condition | Meaning |
|---|---|---|
| `DEFER_SCD2` | At least one real member and at most one distinct `vehicle_type` | No descriptive attribute varies; Type 2 would version nothing. Keep Type 1 |
| `REVIEW_SCD2` | More than one distinct `vehicle_type` | A varying attribute exists; the team decides whether history is needed before any design work |
| `INCONCLUSIVE_NO_DATA` | No real members | The run cannot support a decision; the harness exits non-zero |

**Type 1 gap.** Members with `last_seen_ts` behind the staged data are reported
separately. That is a refresh defect in the insert-only loader, not a reason for Type 2.
Fixing it (advance `last_seen_ts` with `GREATEST` on each load) would change Phase 2
loader code and needs its own decision and tests; it is not part of this evaluation.

A single observed month is also reported. It is supporting context: even a varying
attribute could not show a version change inside one month.

## If the verdict is `REVIEW_SCD2`

Do not start building. The design questions to settle first:

- which attribute varies and which business question needs its history;
- whether facts keep pointing at one surrogate key per version, and what that does to
  `project_reporting` views and the dashboard (`D3-014` keeps the dashboard on
  aggregate views);
- how first-seen and last-seen map to `valid_from`, `valid_to` and `is_current`.

## Result (evidence run 2026-11-21)

Evidence: [`../evidence/scd2_evaluation_20261121T200340Z.md`](../evidence/scd2_evaluation_20261121T200340Z.md),
read-only through `aerogrid_reader`. Verdict: **`DEFER_SCD2`**.

| Probe | Result |
|---|---|
| `QW-P3-H3-01` | 158 real members from 3 source systems share a single `vehicle_type`; 1 member has a zero seen span |
| `QW-P3-H3-02` | Staging holds only 2 UAS serials; neither appears under more than one source; both have more than one launch point (flight-level behaviour) |
| `QW-P3-H3-03` | Only 2 of 158 members could be compared with staging; none has a stale `last_seen_ts` |
| `QW-P3-H3-04` | 27,479 tracking rows for 156 vehicles in one observed month (2022-01-01 08:09 to 2022-01-02 03:59 UTC, under one day) |

What this supports: no descriptive attribute varies, and the tracked history is far too
short to show a version change, so Type 2 would version nothing. Keep Type 1.

Limits of the evidence:

- The `last_seen_ts` check covers 2 of 158 members, because only UAS serials in
  `stg_uas_position` can be compared. "No stale members" says nothing about the other 156;
  the insert-only loader gap stays a separate, undecided Type 1 item.
- The evidence header reads "Probes: 28 of 4 executed". That is a counting bug in the
  harness (it counted report lines). All four probes ran and all four result tables are in
  the file. The harness is fixed; the committed run file is not hand-edited.

## Status

`READY_FOR_REVIEW`. The probes, harness, workflow, tests and evidence are in place and the
verdict is recorded in `Phase3/PROGRESS.md` and `D3-017`. `DONE` needs the hardening-track
review recorded.
