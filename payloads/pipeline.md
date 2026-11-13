## Delivered WP-07–WP-10 execution evidence (2026-11-13)

The status paragraph above reflects the earlier WP-06 closeout; **current deployment** is: WP-07 persistent GitHub Actions workflow applied the 2D grid backfill, derived fact DDL and 1,754 occupancy rows; WP-08 CI persisted a 32-check DQ audit (run 7, 29 PASS / 3 WARN / 0 FAIL); WP-10 persisted 10 reporting views; WP-09 ran a read-only Neon report generator and published both improved PDFs. All package code is on `main` (see merged PRs #15–#20), but G5/G6 have not yet been formally signed off.

Pipeline order is accepted real Tartan staging -> core warehouse tracking/journey facts -> deterministic real 2D grid/derived occupancy -> DQ audit -> `project_reporting` views -> evidence-backed PDF reports. Follow `etl/verify_wp07_facts.py --apply`, `etl/dq.py --apply`, `etl/verify_wp10_views.py --apply` only in approved protected GitHub Actions jobs. The PDF generator `etl/reports.py` reads Neon and writes files, not database records.

No current accepted FAA restriction snapshots or matched METAR observation exist for the sample. Encounter matching in `wp07-v1` is exact-time, and all 27,479 recorded `on_ground` values remain NULL; the 7,433 eligible airborne observations are *inferred*. Do not interpret zero derived encounter/restriction rows as proof of universal absence, or claim altitude-band metrics from the 2D grid.
