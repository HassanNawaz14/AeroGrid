# WP-07 / G5 — Member E handoff and real-data evidence

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

**Status:** READY FOR REVIEW — **not** G5 accepted or WP-07 DONE. The existing CI run was rollback-only; a persistent load and post-load verification remain pending explicit project approval.

**Development branch:** `phase2/wp-07-derived-facts`  
**Latest verified remote commit as of 2026-11-13:** `68d7f484ca68c40865a223b9cc4a3cd220bc3264` (`WP-07: add FAA restriction source validation and tests`)  
**Workflow:** `.github/workflows/wp07-derived-facts-verify.yml` (registered via merged PR #14)  
**CI:** GitHub Actions “WP-07 derived facts - rollback-only verification”, run #1 on WP-07 branch, successful. Add the **specific run URL** to this record during PR review.

## Evidence summary (from protected Neon rollback verification)

| Check | Result |
|---|---:|
| Accepted real Tartan tracking rows | 27,479 |
| Rows assigned real grid keys inside dry-run transaction | 27,479 |
| Eligible *inferred*, not directly observed, airborne positions | 7,433 |
| Positions with unknown airborne state under WP07-AIR-01 | 20,046 |
| Candidate hourly grid occupancy facts | 1,754 |
| Candidate exact-timestamp close-encounter facts | 0 |
| Candidate restriction activation facts | 0 |
| New rows on second identical derivation pass | 0 |
| Integrity check failures | 0 |

**CI final line:** `WP07 PASS; ROLLBACK (no persistent DDL or fact writes)`.
This demonstrates calculation and transaction-level verification, **not** persisted facts.

## Encounter evidence and limitations

- Exactly simultaneous distinct-vehicle timestamps in the existing tracking data: **0**.
- Near-time analysis of *observed* positions found **22 geographically prefiltered observation pairs** within a **diagnostic 20-second window** using the approved narrow geographic prefilter; none passed both approved separation thresholds.
- Minimum horizontal separation among these 22 pairs was **1.213 NM**; minimum vertical separation was **6,000 ft**. These minima may refer to different pairs.
- Approved `H-013` thresholds: **SEVERE** = horizontal `< 0.5 NM` and vertical `< 500 ft`; **PROXIMITY** = horizontal `< 1 NM` and vertical `< 1,000 ft`.
- **Important:** 20-second temporal matching was investigative **SQL only**; production `wp07-v1` still requires identical timestamps. Neither a 20-second detector nor interpolation has been implemented or approved. Do **not** claim universal absence of close encounters or that `wp07-v1` performs asynchronous matching.
- Diagnostic SQL scripts are uncommitted in the working tree unless specifically reviewed and staged. The reviewer should check final SQL conditions before citing them as authoritative.

## FAA restriction source evidence and limitations

- Neon inventory: **0** rows in `project_staging.stg_airspace_zone`, **0** in `project_staging.stg_restriction_snapshot`, **0** real `dim_airspace_zone` members, **168** 2022 time members, **0** 2026 time members.
- Read-only FAA TFR probe for the documented KBTP study box on **2026-11-12 ~22:01 UTC** reported `real_tfr_features_in_study_box=0`, `distinct_faa_ids=0`, `active_by_complete_window=0`.
- This probe checks **one specific FAA restriction service** and study box at the fetch time; it is not a full FAA restriction inventory or an historical audit.
- The warehouse's accepted Tartan sample is dated **January 2022**. Current/2026 FAA polygons must **not** be joined to 2022 flights as historical restrictions.
- Real zero restriction activations are acceptable as a *documented coverage limitation* only if the reviewer/gate owner accepts the shortfall against the original WP-07 acceptance scope. The current read-only FAA probe **does not** populate FAA staging, dimension, time, or activation facts.

## Methods to review

- **`WP07-AIR-01` proposed inference:** Tartan KBTP, barometric MSL altitude, ground speed >=120 knots, altitude >=2,248.4 ft MSL, within 10 NM of KBTP; retain source `on_ground=NULL`; label as inferred, never observed.
- **`WP07-GRID-01` proposed grid:** 0.01-degree site-specific WGS84 bins from actual accepted staging positions. This is a 2D grid, **not** a true altitude-band occupancy dimension.
- Occupancy time is an adjacent-observation estimate capped at 60 seconds; it does not infer duration from isolated pings. These additional analysis rules require reviewer acceptance.

## Local verification

- User ran `python -m pytest -q Phase2/tests`: **89 passed** after adding 11 FAA unit tests.
- `python -m compileall -q Phase2/etl`: no reported errors.
- `git diff --check`: no reported errors.
- FAA probe: completed successfully, read-only.

## Remaining acceptance actions — **do not skip**

1. Reviewer inspects code, DDL, data provenance, `WP07-AIR-01`, `WP07-GRID-01`, occupancy cap, and actual CI log; record decisions in `Phase2/DECISIONS.md` and reflect accepted changes in `Phase2/PROGRESS.md` / data dictionary as necessary.
2. Decide explicitly whether zero current TFR coverage satisfies the restriction-activation component or whether a future-only FAA ingestion is required. Do not mark it implemented when only a source preview exists.
3. With gate-owner authorization, add a separate **protected, explicitly approved GitHub Actions persist workflow** to run `python -m etl.verify_wp07_facts --apply` on the *reviewed* commit, with the `warehouse` environment. Existing workflow is deliberately rollback-only. Review exact changes, restore privileges and verify all invariants before allowing this workflow to run.
4. After approved persistence, independently query grid keys, occupancy fact counts, `algorithm_version`, source lineage, rerun idempotency, warehouse reader SELECT privilege, ETL log, and duplicate/orphan checks. Compare stored results with the dry-run expectations.
5. Only the gate owner may record `G5 DONE` after evidence and scope limitations are accepted. Then WP-08 may proceed.

**No secrets, raw telemetry, or database connection strings should be attached to the PR.**
