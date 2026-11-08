# Phase 2 ETL

Current `WP-04` package for source-shaped staging.

## Modules

- `sources/`: strict normalizers for Tartan, Nightjar, nominal-io DJI, FAA, AWC,
  and IEM. Invalid numeric, timestamp, identity, coordinate, and range values are
  rejected rather than silently nulled.
- `loaders.py`: raw CSV/JSON iterators plus staging mappings and `load_*` helpers
  for `stg_adsb_position`, `stg_uas_position`, `stg_weather_metar`, and
  `stg_airspace_zone`.
- `staging_writer.py`: per-row savepoint writes, `ON CONFLICT DO NOTHING`
  idempotency, reject capture, reconciliation counts, run-log lifecycle, and
  SHA-256 source-manifest writes.
- `verify_wp04_staging.py`: applies idempotent DDL and optionally proves a real
  Tartan sample load/rerun inside a rolled-back transaction.
- `transforms.py`: unit, visibility, ceiling, and flight-category helpers.

## Local checks

From `Phase2/`:

```text
python -m pytest -q
python -m compileall -q etl
```

DB verification requires `DATABASE_URL` supplied by the approved CI/human path:

```text
python -m etl.verify_wp04_staging
python -m etl.verify_wp04_staging --tartan-sample /path/to/real/1.csv
```

The sample run writes staging rows, rejects, and run-log rows inside a transaction
that is always rolled back. Do not use synthetic flight rows.

## Rules

- Real public data only; never generate synthetic business rows.
- No local PostgreSQL, Docker, or dev containers.
- Use environment variables/secrets; never hard-code credentials.
- Archive raw data in object storage with a manifest.
- Use idempotent loads and preserve provenance.
- Fail closed on critical DQ.
- Do not add a dependency without checking its license and free-tier terms.
- Do not commit raw data or generated credentials.

## Owners

- Member B: source clients, raw archive, staging, cleaning.
- Member D: tracking and journey facts.
- Member E: derived facts, DQ, reporting views, PDFs.
- Member A: CI integration and deployment.
