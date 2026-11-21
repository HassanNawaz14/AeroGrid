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

## Status

The probes, harness, workflow and static tests are in place and pass. The evidence run
against the shared warehouse is a human action (`H3-010`); the work package stays
`IN_PROGRESS` until the evidence file is committed and the verdict is recorded in
`Phase3/PROGRESS.md` and `D3-017`.
