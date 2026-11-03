# Phase 2 Tests

This directory is intentionally empty. It will hold parser, transformation, key, DQ,
and reporting tests after `G1` is cleared and the relevant work package is authorized.

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
