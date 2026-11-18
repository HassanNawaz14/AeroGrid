# Phase 3 evidence

This folder holds generated, non-secret run evidence. It is not a source of truth for
KPI values: the stored SQL and the capture metadata in each run file are.

## Generated files

`analytics_run_<UTC timestamp>.md` is written by
[`../scripts/run_readonly_analytics.py`](../scripts/run_readonly_analytics.py). Each file
records:

- the capture time, connected role, database, server version, and `READ ONLY` mode;
- every SQL file, its query ID, SHA-256, columns, row count, and result rows;
- the `DQ3-A-004` grand-total reconciliation status;
- explicit labels for zero-row results (missing coverage, not zero activity).

A run file is evidence only when it was produced against the shared warehouse through
`aerogrid_reader` (or a read-only transaction) and the capture date is visible. Never
hand-edit a generated run file or copy numbers into it.

## Rules

- Never store connection strings, passwords, tokens, raw data, or screenshots of them.
- Do not commit a failed run as a passing evidence file; keep the failure visible.
- Do not commit a run file that contains unlabeled zeros or retail-named metrics.
