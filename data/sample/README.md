# Legacy Sample Files

The files in this directory are legacy demo artifacts created before the Phase 2
real-data-only rule was adopted. They are **synthetic** and must never be loaded into
`project_staging`, `project_dw`, or `project_reporting`.

Phase 2 uses only real public sources documented in
[`../../Phase2/docs/03_data_sources_and_licensing.md`](../../Phase2/docs/03_data_sources_and_licensing.md).

## Handling

- Do not use these files as extraction evidence.
- Do not load them into the warehouse.
- Do not cite them in reports.
- They are excluded from Phase 2 by policy and ignored for future changes.
- They are currently tracked from the earlier repository state. `H-008` in
  [`../../Phase2/PROGRESS.md`](../../Phase2/PROGRESS.md) tracks their human review and
  removal or quarantine.
- A human may delete them after confirming they are not needed for historical context.

This notice exists to prevent accidental use of synthetic rows.
