# Phase 3 Data Quality and Reports

**Status:** target design. Phase 2's DQ framework is unchanged and continues to
gate every write. Phase 3 adds **analytics-level quality rules** and three new
evidence reports.

## Quality principles (carried forward)

- Validate real data; never fabricate a passing result or a KPI value.
- Store every check result, including passes (in `project_staging.dq_result` when
  run through CI).
- Fail closed on critical integrity issues; never silently correct a value.
- Empty means missing coverage, never "no events" (`D3-009`).

## Phase 3 analytics checks

| ID | Check | Severity | Threshold |
|---|---|---|---|
| DQ3-A-001 | Gold view row count reconciles to fact counts for the same scope | CRITICAL | Exact for deterministic views |
| DQ3-A-002 | Every published KPI traces to a stored query and check ID | CRITICAL | 0 untraced KPIs |
| DQ3-A-003 | Zero-valued KPIs carry a coverage label | WARNING | 0 unlabeled zeros |
| DQ3-A-004 | ROLLUP/CUBE grand totals equal the plain aggregation | CRITICAL | Exact |
| DQ3-A-005 | Dashboard numbers match the cited view/query at capture time | CRITICAL | Exact; recorded in the insights report |
| DQ3-A-006 | Index report shows before/after EXPLAIN ANALYZE for each claimed index | WARNING | 1 pair per index |

## Reports

| Report | Content requirements | WP |
|---|---|---|
| Indexing report (PDF) | Query, before plan + time/cost, index DDL, after plan + time/cost, conclusion; capacity note | WP-P3-05 |
| Dashboard screenshots (PDF) | One page per dashboard page, capture date, data-as-of timestamp | WP-P3-06 |
| Business insights report (PDF) | Decision narrative, each claim with its query citation and check ID, coverage labels, recommended actions | WP-P3-07 |

Reports are generated from stored results and recorded queries, never from
hard-coded claims. A number in a PDF must be reproducible by re-running its query.

## DQ failure handling (unchanged)

1. Mark the run failed in CI; keep previous artifacts.
2. Record observed vs expected in `dq_result` when running through CI.
3. Do not publish a "trusted" claim for the affected artifact.
4. If the correct fix needs a business decision, stop and ask the human.
