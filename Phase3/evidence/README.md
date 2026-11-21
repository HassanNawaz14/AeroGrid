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

`gold_views_<UTC timestamp>.md` is written by
[`../scripts/verify_gold_views.py`](../scripts/verify_gold_views.py). Each file
records the DDL SHA-256, writer mode (`ROLLBACK` or `apply`), the fact baseline,
the view row/measure reconciliation (`DQ3-A-001`), and the separate
`aerogrid_reader` proof in apply mode. A verify-mode file proves the DDL and
reconciliation without persisting the views; only an apply-mode file with a
passing reader section is apply evidence.

`index_optimization_<mode>_<UTC timestamp>.json` and `.md` are written by
[`../scripts/measure_indexes.py`](../scripts/measure_indexes.py). Each file records
the capture time, role/database/version (never the connection string), the fact
baseline, every `OQ-P3-05-xx` query SHA-256, and one
`EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` before/after pair per candidate index plus
its measured size. Verify-mode files are rollback evidence: the DDL was created and
discarded in the same transaction. Only an apply-mode file with
`"persisted": true` proves the indexes exist. When `D3-011` declines the apply,
the verify-mode PDF is the final deliverable and stays labelled `verify`. The PDF
in `Phase3/reports/` is built from this JSON by
[`../scripts/generate_index_report.py`](../scripts/generate_index_report.py); never
hand-edit a pair or copy a number into the report.

`packaging_<mode>_<UTC timestamp>.md` and `.json` are written by
[`../scripts/package_artifacts.py`](../scripts/package_artifacts.py). Each file records
the capture time, environment (`local` or `github-actions`), commit, the `D3-008`
limit, which deliverables are present or `MISSING`, and for every file its size,
route (`bundle` under 10 MiB, `oversize` otherwise), secret-scan result and SHA-256.
They need no warehouse access. A `dryrun` file reports without copying anything. A
`PASS_WITH_PENDING` result means required deliverables are still missing; only a
`--strict` run with result `PASS` supports the release notes. Never hand-edit one.

`scd2_evaluation_<UTC timestamp>.md` is written by
[`../scripts/evaluate_scd2.py`](../scripts/evaluate_scd2.py) (`WP-P3-H3`, read-only through
`aerogrid_reader`). It records the four probe results and the derived verdict
(`DEFER_SCD2`, `REVIEW_SCD2` or `INCONCLUSIVE_NO_DATA`). The first run file,
`scd2_evaluation_20261121T200340Z.md`, has a header line "Probes: 28 of 4 executed"; that is a
counting bug since fixed in the harness. All four probes ran and the file is not hand-edited.

A run file is evidence only when it was produced against the shared warehouse through
`aerogrid_reader` (or a read-only transaction) and the capture date is visible. Never
hand-edit a generated run file or copy numbers into it.

## Rules

- Never store connection strings, passwords, tokens, raw data, or screenshots of them.
- Do not commit a failed run as a passing evidence file; keep the failure visible.
- Do not commit a run file that contains unlabeled zeros or retail-named metrics.
