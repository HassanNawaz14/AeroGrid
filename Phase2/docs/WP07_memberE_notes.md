# WP-07 Member E implementation and review notes

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

This **starter implementation** is not a claim of G5 acceptance. It depends on the actual
`Phase2/sql/03_facts/02_derived_facts.sql` that Member E has already pushed. Do not overwrite
that file when copying this kit. A `main` baseline passing 62 pytest tests does not
verify these new algorithms or the new DDL.

## Verified contracts

- Warehouse: `project_dw.fact_vehicle_tracking` joins to
  `project_staging.stg_adsb_position` on `(source_system, source_record_id)` for
  real WGS84 latitude/longitude; the tracking fact has no coordinates.
- H-013, `algorithm_version=wp07-v1`: `SEVERE` if horizontal `<0.5 nm` **and**
  vertical `<500 ft`; `PROXIMITY` if horizontal `<1.0 nm` **and** vertical `<1000 ft`
  and not severe. Strict `<` comparisons.
- **Remediation included in this ZIP:** `etl/wp07_data_readiness.py` offers a scope-limited and auditable `INFERRED_AIRBORNE` assessment for real Tartan KBTP positions using barometric MSL altitude, surveyed KBTP elevation, speed, and distance criteria. It **does not** modify the source `on_ground=NULL` flag. See `docs/WP07_readiness_remediation.md` for decision criteria, limitations and approval needs.
- Real `dim_spatial_grid` cells are inserted only from accepted real Tartan source positions through `sql/03_facts/05_wp07_seed_grid_and_backfill.sql`; the same approved transaction backfills existing unknown tracking grid keys. The optional targeted `facts.py` patch makes future tracking maps use exact grid IDs.
- No source dataset asserts observed ground state for Tartan. Always distinguish observed vs inferred airborne status. Inference is analytical only; it must not be described as a definitive aircraft safety classification.
- Exclude ground observations, unknown/unqualified states, unknown vehicle/site/time, invalid coordinates and incompatible altitude datums. Same site and **exact same timestamp** only for encounter candidates.
- Current code **does not interpolate** asynchronous positions; its encounter rows
  represent observed instant conflicts with duration 0. If the assessor requires
  multi-sample episodes/duration or asynchronous matching, Members C/D and the
  owner must approve matching/segmentation rules; update the code, DQ, and docs
  before the G5 acceptance run.
- Occupancy is per `(time_key, grid_key, algorithm_version)` and counts distinct
  airborne vehicles from accepted Tartan tracking input. `total_occupancy_minutes`
  is a conservative *observed-sample* estimate: add consecutive intervals per
  vehicle only when the gap is `<=60 sec`. Do not imply that a lone ping proves
  one minute of presence. The `60 sec` gap cap needs reviewer confirmation.
- Restriction facts require real `stg_restriction_snapshot` evidence, a matching
  `dim_airspace_zone`, and a matching UTC hour in `dim_time`. No snapshot -> zero
  new rows, not dummy activations. `affected_traffic_count`, `compliant_count`,
  and `compliance_rate_pct` remain NULL until geospatial coverage and altitude
  compliance are validated. This is **not complete compliance analytics**.
- No raw data, passwords, generated encounters, or test fixture rows are written
  into production. Test-only fixtures exist strictly inside pytest.

## Run locally in Windows CMD, from repository root

```bat
cd /d "D:\University docs\5th Semester\Data Warehousing\DW_Project\AeroGrid"
git status -sb
python -m pytest -q Phase2/tests
python -m pytest -q Phase2/tests/test_derived_facts.py
python -m compileall -q Phase2/etl
python -m compileall -q Phase2/tests
python -m pytest -q Phase2/tests
git diff --check
```

Read-only readiness diagnostics: `Phase2/sql/03_facts/04_wp07_preflight.sql` (run first).
Read-only post-load evidence: `Phase2/sql/03_facts/03_wp07_evidence_queries.sql`.
Do not run loaders from a laptop. The default `verify_wp07_facts` mode performs
DDL and fact writes inside a single rollback-only transaction *in approved CI*.
A persistent `--apply` needs owner approval and the protected `warehouse`
GitHub environment; coordinate workflow changes with Member A.

## Operational sequence

1. Extract the new remediation ZIP and read `README_FIRST.md`; it includes the earlier
   kit files plus `wp07_data_readiness.py`, the deterministic grid SQL, new tests,
   and a targeted patch for the prior Member D tracking lookup. The workflow proposal under `.github/workflows/` is optional
   and needs Member A approval before you stage it.
2. Run tests and ensure the existing suite remains green.
3. Have Member C review deterministic grid keys and the controlled backfill;
   have Member D review new airborne inference, input provenance, altitude assumptions,
   temporal pairing, and minute calculations.
4. Ask Member A to review and install the supplied optional WP-07 GitHub Action.
   GitHub requires a `workflow_dispatch` workflow to be registered on the default
   branch before it appears in Actions. Coordinate that safe workflow-only PR
   first, then dispatch the verifier against your WP-07 branch. It must use
   the existing protected `warehouse` environment and `DATABASE_URL` secret. It should
   run unit tests first and `cd Phase2 && python -m etl.verify_wp07_facts`
   for a rollback-only verification. No credentials in the repository or logs.
5. Review live counts and DQ output. Zero encounters, occupancy, or restrictions
   can be truthful; diagnose staging coverage rather than fabricating rows.
6. After explicit human authorization, re-run the protected workflow with
   `--apply`; capture run URL, SHA, exact counts, pass-2 zero inserts,
   orphans, duplicate checks, and a read-only SELECT proof.
7. Update `Phase2/PROGRESS.md` to `READY_FOR_REVIEW`, not `DONE`; link the
   verification run and document missing metrics/limitations. Update dictionary,
   data-model narrative and DBML with Member C if their contracts change.
8. Open a PR targeting `main`; request Members C and D. **G5 closure is a
   human-owned gate**, not a self-declared success.

## Additional acceptance work before G5

The code is a *conservative first increment*, not a complete replacement for the
WP-07 acceptance plan. In particular, the reviewers must decide and document:

- Whether exact-timestamp observations satisfy the required encounter **episode**
  grain, and if not the matching tolerance, pair-state transitions, and duration.
- How to handle timestamp skew, mixed altitude datums, and coordinate quality.
- Whether sample-gap occupancy is acceptable; how to handle missing intervals,
  hourly boundary splitting, and unmapped (`-1`) grid cells.
- Which real FAA zone sources are available and how to compute **affected** and
  **compliant** traffic with verified polygons and altitude ceilings. Until then
  null compliance metrics must stay explicitly incomplete.
- Sample proof for one source record, one key mapping, first-run counts,
  second-run duplicates 0, replay behavior, and reader access.

## Following packages

- **WP-08:** `Phase2/etl/dq.py`, DQ catalog, persisted
  `project_staging.dq_result`, tests including deliberate critical failures;
  coordinate reviewer check IDs with `docs/06_data_quality_and_reports.md`.
- **WP-09:** `Phase2/etl/reports.py`, regenerate two readable PDFs from stored
  counts and DQ rows, use reportlab, include source license attribution and
  run/hash metadata. Never invent totals or hard-code pass values.
- **WP-10:** `Phase2/sql/04_reporting/*.sql`, ten read-only SQL views, grains and
  example SELECTs, validate no join multiplication, reader SELECT permissions.
- Each package gets **its own PR**, reviews, and gate evidence. Do not bypass G5.
