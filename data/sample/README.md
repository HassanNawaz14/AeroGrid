# Legacy Sample Files

The files in this directory are small synthetic demo artifacts created before the
Phase 2 real-data-only rule was adopted. They are retained intentionally so users and
evaluators can inspect representative file shapes without accessing the shared Neon
warehouse.

They are **not** Phase 2 source data. They must never be loaded into
`project_staging`, `project_dw`, or `project_reporting`, cited as extraction evidence,
or presented as real observations. All Phase 2 facts come from the real public sources
in [`../../Phase2/docs/03_data_sources_and_licensing.md`](../../Phase2/docs/03_data_sources_and_licensing.md).

## Files

- `drone_telemetry_sample.csv`
- `faa_restrictions_sample.geojson`
- `opensky_sample.json`
- `tartan_trajectory_sample.csv`
- `weather_metar_sample.json`

## Handling

- Retained in Git for offline demonstration and evaluator review only (`D-017`).
- Excluded from every ETL, staging, warehouse, reporting, and DQ load.
- Never cite them in reports or use them as evidence.
- Label them as synthetic if shown in a demo.
- `.gitignore` intentionally keeps these files tracked; other files under
  `data/sample/` remain ignored.
- Do not add new synthetic files; Phase 2 uses real public data only.
- `H-008` is resolved and `B-006` is closed.
