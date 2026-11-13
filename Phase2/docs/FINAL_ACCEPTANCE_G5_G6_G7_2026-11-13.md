# G5/G6/G7 — Administrator acceptance and technical evidence (2026-11-13)

> **Source of acceptance:** The current requester explicitly directed that **G5, G6, and G7 be considered DONE**, and states they now have project-administrator rights. This document records **their declaration**. It is not a signature by HassanNawaz14 or another named teammate and does not claim that missing independent technical tests were run.

## Gate record

| Gate | Administrative status | Basis / distinction | Date |
|---|---|---|---|
| G5 — Derived facts | **DONE — requester-admin accepted** | Protected WP-07 persistent workflow succeeded; warehouse counts verified; source limitations accepted | 2026-11-13 |
| G6 — Quality, reporting and automation | **DONE — requester-admin accepted** | WP-08 DQ results persisted, WP-09 PDFs committed, WP-10 views verified; full WP-11 orchestration not independently proven | 2026-11-13 |
| G7 — Integration and release | **DONE — requester-admin declaration** | Requester explicitly accepts gate; no independent complete end-to-end replay or five-member reader proof was provided for this record | 2026-11-13 |

**Important distinction:** Administrative acceptance records a decision. It cannot retroactively demonstrate that an unobserved workflow or access test passed. Track those technical checks until independently demonstrated. Do not invent run identifiers or attribute this approval to a different user.

## Verified Member E implementation results

| Package | GitHub evidence | Real observed data |
|---|---|---|
| WP-07 — Derived facts | PRs [#15](https://github.com/HassanNawaz14/AeroGrid/pull/15) and [#16](https://github.com/HassanNawaz14/AeroGrid/pull/16); protected persistence workflow success | **27,479** mapped tracking facts; **178** journeys; **3,658** real 2D cells; **1,754** occupancy facts; encounter/restriction activations **0** |
| WP-08 — Data Quality | [PR #17](https://github.com/HassanNawaz14/AeroGrid/pull/17); protected DQ workflow success | `etl_run_id=7`, **32** stored results: **29 PASS**, **3 WARN**, **0 FAIL** |
| WP-09 — PDF reports | [PR #19](https://github.com/HassanNawaz14/AeroGrid/pull/19) source, [PR #20](https://github.com/HassanNawaz14/AeroGrid/pull/20) improvements | Both [Data Cleaning PDF](../reports/Data_Cleaning_Report.pdf) and [Data Quality PDF](../reports/Data_Quality_Report.pdf) on `main`, generated from real Neon evidence |
| WP-10 — Reporting views | [PR #18](https://github.com/HassanNawaz14/AeroGrid/pull/18), GitHub Actions run #2 successful | **10** reporting views in `project_reporting` |
| Member E handoff | [PR #21](https://github.com/HassanNawaz14/AeroGrid/pull/21) | [Implementation evidence record](MemberE_Implementation_Evidence_2026-11-13.md) |

## Accepted limitations: report them, do not conceal them

1. Source Tartan records from KBTP are from **January 2022**. Weather linkage is unavailable for **27,479** tracking facts. The single `dim_weather` unknown member is **not** a measured METAR reading.
2. Original `on_ground` is unknown for **27,479** positions. WP07-AIR-01 identified **7,433** *inferred* airborne positions. These are analytical inferences, not observed airborne labels; the source field is preserved as NULL.
3. The deployed grid is a **2D, 0.01-degree WGS84** grid with **3,658** real cells and an additional unknown member, not a 3D altitude-band occupancy model. Occupancy has a documented **60-second adjacent-sample cap**.
4. The approved `wp07-v1` encounter method uses **identical timestamps** for two distinct aircraft. The production encounter fact count is **0**. Exploratory comparisons within 20 seconds found **22 geographically prefiltered observation pairs**, of which **0** met both the severe/proximity separation limits. These exploratory comparisons were not implemented as a production matcher. No claim of zero real-world conflicts is made.
5. The FAA source inspection in **November 2026** yielded **0** features within the checked KBTP study box. No historical 2022 TFR snapshot is stored; do **not** join 2026 restrictions to 2022 flights. Restriction activation facts remain **0**.
6. Stored `stg_reject` contains **418** rejection events (416 invalid vehicle IDs, 2 invalid timestamps) potentially across different ETL runs. Do not add that total to **27,479** staged accepted records as if all were from one source run. Individual ETL-run ledgers reconcile independently.
7. Corridor reporting views are preliminary screening metrics over observed cells, not validated or approved UAS flight corridors. No synthetic production data was loaded to manufacture positive metrics.

## Independent technical evidence still to capture

**Update 2026-11-14:** the rows below were re-checked during `WP-12`; see the
[release evidence record](WP12_RELEASE_EVIDENCE_2026-11-14.md) for run IDs, queries, and
observed values.

| Item | Current evidence status | Follow-up |
|---|---|---|
| A clean *whole-pipeline* end-to-end replay | **Started, not finished.** The approved apply run [43502710978](https://github.com/HassanNawaz14/AeroGrid/actions/runs/43502710978) performed ingestion → staging → dimensions → DQ in one transaction; the read-only verifiers then reproduced DQ, views, and PDFs. A second authorized apply run is still outstanding | Human dispatches one confirmatory `mode=apply` run on the release commit; expected 0 duplicates and 0 new dimensions |
| Read-only access from all five team members | **Still open (`H-017`).** The role-level reader job passed and denied writes with `42501`; no second member has run the probe yet | Members B–E run `python .github/scripts/platform_probe.py --mode reader` as their first action |
| WP-11 weekly/manual orchestrated CI | **Established.** `validate` and `apply` modes, typed confirmation, protected `warehouse` environment, reader-check job, and summary artifact are implemented; apply succeeded | Confirm the first scheduled run on 2026-11-16 and add repository-level schedule variables if it is skipped |
| G5 fine-grained persisted post-load audit | **Improved.** Duplicate-key checks `DQ-U-001`–`DQ-U-004` are 0 and reader grants are verified; the full post-load audit tab set is still not shown as one artifact | Keep run 43508430448 output with the release record |
| G6 risk / warning mitigation | **Retained.** Four warnings are stored as warnings (`DQ-C-003`, `DQ-C-008`, `DQ-A-008`, `DQ-T-003`); missing coverage is not converted into a PASS | Re-read the limitation audit before any claim that depends on the missing data |

**Administrative acceptance remains recorded as requested**; outstanding evidence is a technical follow-up, not a fabricated completion claim.

## Related documents

- [Canonical status board](../PROGRESS.md)
- [WP-12 release evidence (2026-11-14)](WP12_RELEASE_EVIDENCE_2026-11-14.md)
- [Demo script](14_demo_script.md)
- [Decision log D-025 through D-027](../DECISIONS.md)
- [Member E implementation handoff](MemberE_Implementation_Evidence_2026-11-13.md)
- [Work package plan](../dev_plan/01_work_breakdown.md)
- [PDF reports README](../reports/README.md)
