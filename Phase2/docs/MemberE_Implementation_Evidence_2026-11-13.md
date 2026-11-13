# Member E — WP-07 to WP-10 implementation evidence (2026-11-13)

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

> **Technical handoff, not a gate-acceptance certificate.** The canonical phase status is [`../PROGRESS.md`](../PROGRESS.md). Material business-rule approvals belong in [`../DECISIONS.md`](../DECISIONS.md). Do not mark work packages or gates `DONE` without the accountable human's confirmation.

## What is deployed

| Work package | Evidence from verified work | Current handoff |
|---|---|---|
| WP-07 — derived facts | PRs [#15](https://github.com/HassanNawaz14/AeroGrid/pull/15) and [#16](https://github.com/HassanNawaz14/AeroGrid/pull/16) merged. Protected WP-07 persistent workflow succeeded. 27,479 tracking records mapped; 3,658 *real* 2D grid cells; 1,754 `wp07-v1` occupancy records; zero encounter/restriction records. | `READY_FOR_REVIEW` — G5 acceptance of inference, grain and source limitations pending. |
| WP-08 — data quality | PR [#17](https://github.com/HassanNawaz14/AeroGrid/pull/17) merged. 32 `project_staging.dq_result` rows for audit run 7: 29 PASS, 3 WARN, 0 FAIL. Reported 96 passing Phase 2 tests at WP-08 stage. | `READY_FOR_REVIEW` — confirm severity policy and failure-path evidence. |
| WP-09 — PDF reports | Generator PR [#19](https://github.com/HassanNawaz14/AeroGrid/pull/19) and improvement PR [#20](https://github.com/HassanNawaz14/AeroGrid/pull/20) merged; both improved PDFs stored in `Phase2/reports/` on `main`. | `READY_FOR_REVIEW` — PDFs reviewed for readability and evidence; final gate decision pending. |
| WP-10 — reporting views | PR [#18](https://github.com/HassanNawaz14/AeroGrid/pull/18) merged. WP-10 GitHub Actions run #2 succeeded; 10 reporting views confirmed in `project_reporting` using Neon SQL. | `READY_FOR_REVIEW` — final reader-role, performance and scope acceptance outstanding. |

## Warehouse evidence and reconciliation

- `project_dw.fact_vehicle_tracking`: **27,479** real source-linked facts; `grid_key=-1`: **0** after WP-07 persistence.
- `project_dw.fact_flight_journey`: **178** records.
- `project_dw.dim_spatial_grid`: **3,659** rows, including one `-1` unknown member; **3,658 real grid cells**.
- `project_dw.fact_airspace_occupancy`: **1,754** stored `wp07-v1` facts.
- `project_dw.fact_close_encounter`: **0**; `project_dw.fact_restriction_activation`: **0**.
- `project_staging.stg_adsb_position`: **27,479 accepted** rows (`reject_reason IS NULL`).
- `project_staging.stg_reject`: **418** stored rejection events: 416 `INVALID_VEHICLE_ID`, 2 `INVALID_TIMESTAMP`. These may span different ETL runs; **do not add them to staging rows to claim a single-run source input total**.
- Cleaning-report ETL ledger: run 6 read/accepted 27,479/27,479; run 4 read/rejected/duplicates 27,688/209/27,479; run 3 read/accepted/rejected 27,688/27,479/209. Each of these runs balances internally.
- QA report database size: **52,781,056 bytes** at report snapshot; object-storage usage not measured via PostgreSQL.

## Data-quality exceptions — visible, not hidden

| Check | Status | Observed | Meaning |
|---|---|---:|---|
| `DQ-C-003` | WARN | 27,479 | Tracking weather keys are unknown; `dim_weather`'s `-1` member is not an observed METAR row. |
| `DQ-C-008` | WARN | 27,479 | Original `on_ground` is unknown; WP07-AIR-01 is an inference, not an observed field replacement. |
| `DQ-T-003` | WARN | 1 | An indicator of no real accepted restriction snapshots, **not one missing flight**. |

**0 stored critical DQ failures** in run 7. There is no basis to weaken these warnings to make the report appear complete.

## Important scientific and scope limitations

1. Tartan KBTP observations used in the warehouse are from **January 2022**. A read-only check of one FAA TFR service for the selected KBTP study box on **2026-11-12** returned no current features; this is not a historical TFR audit. Do not join a modern restriction to 2022 movements.
2. `wp07-v1` close-encounter matching uses **identical timestamps**. Diagnostic ±20-second observation comparisons found 22 geographically prefiltered pairs, none meeting both approved proximity limits. That does **not** prove that no close encounter occurred in reality; ±20-second comparison was **not deployed** as the production algorithm.
3. The actual spatial grid is **2D 0.01-degree WGS84 bins**, not the conceptual 3D altitude-band design. Hourly occupancy is `(time_key, grid_key, algorithm_version)` and uses a 60-second adjacent-sample cap. Do not claim vertical corridor separation based on a nonexistent altitude-band dimension.
4. WP-10 corridor view outputs are **screening indicators for observed cells**, not complete, approved UAS flight corridors, and no fabricated corridor suggestions are allowed.
5. Source coverage is limited: the current sample provides manned Tartan tracking, not a fully populated multi-site manned/UAS/weather/restriction study. Disclose absent dimensions/snapshots in final evaluation.

## Final gate actions for Member A

- **G5:** Review WP07-AIR-01, WP07-GRID-01, 60-second occupancy cap, zero restriction coverage, exact-time encounter limitation, persisted-run log, zero duplicates and reader SELECT. Record acceptance or change requests. WP-07 implementation is deployed; gate sign-off is still separate.
- **G6:** Confirm WP-08's 32 persisted checks, failure-path test, WP-09's two reproducible reports, WP-10's 10 views and reader access, and WP-11's schedule/automation responsibilities. Record any missing rubric items; no auto-close.
- **G7:** Run an independent end-to-end CI/SQL acceptance on `main`, including read-only user permissions, source provenance, complete row reconciliation, automation and team access. Member A/whole team owns G7.

## Canonical artifact locations

- Verification workflows: `.github/workflows/wp07-persist-reviewed.yml`, `wp08-dq-verify.yml`, `wp09-reports.yml`, `wp10-views-verify.yml`.
- WP-07: `Phase2/etl/verify_wp07_facts.py`, `Phase2/sql/03_facts/02_derived_facts.sql`, and `Phase2/docs/WP07_G5_handoff.md`.
- WP-08: `Phase2/etl/dq.py`, `Phase2/docs/06_data_quality_and_reports.md`, `project_staging.dq_result` (latest run 7 at evidence time).
- WP-09: `Phase2/etl/reports.py`, `Phase2/reports/Data_Cleaning_Report.pdf`, `Phase2/reports/Data_Quality_Report.pdf`.
- WP-10: `Phase2/sql/05_reporting/01_reporting_views.sql` and `project_reporting` (10 views in Neon).
- Course deadline remains separately owned by the team; this handoff does not claim completion of `WP-11` or `WP-12`.
