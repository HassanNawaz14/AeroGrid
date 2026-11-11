# Phase 2 ETL

Current `WP-04` through `WP-06` ETL modules. `WP-06` applies the real dimension seed
before preflight; the real Tartan WP-05/WP-06 runs passed on 2026-11-11 and `G4` is
recorded.

## Modules

- `sources/`: strict normalizers for Tartan, Nightjar, nominal-io DJI, FAA, AWC,
  and IEM. Invalid numeric, timestamp, identity, coordinate, and range values are
  rejected rather than silently nulled.
- `dimensions.py` (`WP-05`): pure normalization helpers for dimension natural keys and
  hourly spine validation.
- `facts.py` (`WP-06`): surrogate-key lookups, missing-required-dimension rejects,
  batched tracking fact loader, Haversine geodesic distance (`nm`), and deterministic
  per-vehicle journey segmentation (`DEFAULT_GAP_SPLIT_SEC = 300`, `ALGORITHM_VERSION = "wp06-v1"`).
- `loaders.py`: raw CSV/JSON iterators plus staging mappings and `load_*` helpers
  for `stg_adsb_position`, `stg_uas_position`, `stg_weather_metar`, and
  `stg_airspace_zone` (optional `batch_size` forwarding on `load_tartan`).
- `staging_writer.py`: per-row/chunked savepoint writes, `ON CONFLICT DO NOTHING`
  idempotency, reject capture, reconciliation counts, run-log lifecycle, and
  SHA-256 source-manifest writes.
- `verify_wp04_staging.py`: applies idempotent staging DDL and optionally proves a
  real Tartan sample load/rerun inside a rolled-back transaction.
- `verify_wp05_dimensions.py`: applies idempotent dimension DDL/seeds and checks
  `-1` unknown members, uniqueness, FKs, and reader `SELECT`.
- `verify_wp06_facts.py`: downloads real `samples/kbtp/01-01-22/1.csv` from `aerogrid-raw`
  (SHA-256 verified), applies fact DDL twice, runs staging + tracking + journey loads
  twice for reconciliation/idempotency/orphan/reader checks (`--dry-run` rolls back;
  persistent acceptance commits when all checks pass).
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
