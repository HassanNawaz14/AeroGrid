# Phase 2 Tests

Current `WP-03`/`WP-04` unit tests run without a database or Docker.

## Coverage

- `test_tartan.py`, `test_uas.py`, `test_faa.py`, `test_weather.py`,
  `test_transforms.py`: source normalizers, units, rejects, and bounds.
- `test_staging_writer.py`: reconciliation, rejects, savepoint rollback, staging
  mapping, run-log lifecycle, and manifest hashing using `tests/fakes.py`.
- `test_loaders.py`: raw iterators, row-number provenance, logical source files,
  loader reject isolation, and normalized-to-staging mappings.

## Commands

From `Phase2/`:

```text
python -m pytest -q
```

From the repository root:

```text
python -m pytest -q Phase2/tests
```

## Rules

- Tests must not require a local PostgreSQL server or Docker.
- Use real, small, public licensed fixtures where possible.
- Clearly mark any parser fixture as test-only; never load it into `project_dw`.
- Never create synthetic production rows to satisfy a count.
- Test idempotency, key mapping, reconciliation, and critical DQ failures.
- Do not commit secrets, raw archives, or database dumps.
- Record the test command and result in `PROGRESS.md`.

## Owners

- Member B: source/staging tests.
- Member C: schema/key/data-dictionary tests.
- Member D: tracking/journey tests.
- Member E: derived fact/DQ/report tests.
- Member A: CI enforcement.
