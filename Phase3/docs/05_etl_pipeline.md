# Phase 3 ETL and Refresh Pipeline

**Status:** target design. The Phase 2 pipeline is the only write path to the
warehouse and is unchanged (`D3-001`). Phase 3 adds a **read-only analytics refresh
layer** and an optional hardening track.

## What Phase 3 changes

Nothing about ingestion. Sources, staging, dimensions, facts, DQ, and cadence stay
exactly as Phase 2 defined them. Phase 3 workflows:

1. Apply gold views (`CREATE OR REPLACE VIEW`) idempotently — safe to rerun.
2. Run analytics verification: every gold view returns a reconciled row count;
   zero rows are labeled missing coverage, never "no events" (`D3-009`).
3. Run optimization checks: `EXPLAIN ANALYZE` before/after for the queries the
   dashboard uses; index DDL is idempotent (`CREATE INDEX IF NOT EXISTS`). The
   measurement harness is `Phase3/scripts/measure_indexes.py`; it always rolls back
   in verify mode and only the protected `.github/workflows/wp-p3-05-indexes.yml`
   apply mode persists `Phase3/sql/indexes/01_indexes.sql` (`D3-010`).
4. Package artifacts (SQL, PDFs, PBIX under the size guard) for the release.

All of the above are read-only with respect to base tables; the only writes Phase 3
ever performs are new views/indexes in `project_reporting` and `project_dw`
(respectively), applied through CI as `aerogrid_etl`.

## Pipeline principles carried forward (non-negotiable)

- Real data only; aggregates must come from keyed fact rows.
- Idempotent reruns; a re-applied view or index changes nothing.
- Reconciliation: gold-view totals must tie back to fact counts for the same scope.
- Fail closed: a broken view or failed reconciliation fails the workflow.
- No five-minute polling; weekly/manual cadence unchanged.

## Refresh and timing

| Artifact | Refresh trigger | Owner |
|---|---|---|
| Gold views | Phase 3 CI workflow; after any WP-11 apply | A (workflow), E (content) |
| Dashboard | Manual refresh in Power BI Desktop against current views | E |
| Materialized marts | Only if `D3-007` evidence approves them; refresh in the same transaction as view apply | D |

WP-P3-05 verify run 44397831286 measured three candidate indexes as `NEUTRAL`
(identical plans and costs), so none is applied (`D3-011`); the DDL stays
evaluated/deferred. That run says nothing in favor of materialized marts, so
`D3-007` remains unproven and `WP-P3-H4` stays optional.

## Optional hardening track (post-course or by decision)

| WP | Item | Trigger |
|---|---|---|
| WP-P3-H1 | Close `L-010`: archive raw files to `aerogrid-raw` with manifest linkage | Human prioritizes replayability |
| WP-P3-H2 | FAA ArcGIS quota mitigation (caching, backoff budget, optional-airspace runs) | Repeated scheduled-run failures |
| WP-P3-H3 | SCD Type 2 evaluation for `dim_vehicle` | A Phase 3+ question needs attribute history |
| WP-P3-H4 | Materialized marts + refresh orchestration | `EXPLAIN ANALYZE` evidence per `D3-007` |

Each hardening WP requires its own decision row and gate evidence; none may be
started "in passing."

## Failure behaviour

| Failure | Required behaviour |
|---|---|
| Gold view fails to create or reconcile | Fail the workflow; do not publish the artifact |
| Dashboard refresh fails | Fail the CI verification step; no warehouse writes occur |
| Index DDL exceeds capacity guard | Stop before apply; ask the human |
| Phase 2 pipeline failure | Unchanged: rollback, failure evidence run, red workflow |
