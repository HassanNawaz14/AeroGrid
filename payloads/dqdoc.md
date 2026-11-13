## WP-08 / WP-09 delivered evidence (2026-11-13)

The previously planned quality framework is now implemented at `Phase2/etl/dq.py`; results persist in `project_staging.dq_result` through `.github/workflows/wp08-dq-verify.yml`. A confirmed read from Neon shows the latest saved audit run `etl_run_id=7` contains **32 checks: 29 PASS, 3 WARN, 0 FAIL**. Warning details:

| Check | Observed | Explanation |
|---|---:|---|
| `DQ-C-003` | 27,479 | Unknown optional weather key: no matched observed METAR row. |
| `DQ-C-008` | 27,479 | Original source `on_ground` NULL: inferred airborne status is not a stored observation. |
| `DQ-T-003` | 1 | Single *warning indicator* for unavailable restriction snapshots, not one absent aircraft event. |

The two delivered, evidence-backed PDFs are `Phase2/reports/Data_Cleaning_Report.pdf` and `Phase2/reports/Data_Quality_Report.pdf`, built from Neon with `Phase2/etl/reports.py` and `.github/workflows/wp09-reports.yml`. The improved Cleaning PDF includes **run-scoped** reconciliation and rejects by reason; the improved Quality PDF explains the warnings, shows unknown dimension members separately and lists real stored fact/dimension counts. A successful local test or PDF generation alone is **not** gate acceptance; critical DQ failure must still block trusted publication.

**Source caveat:** The Tartan KBTP observations are January 2022. The 2026 FAA TFR service check returned no current features in the selected study box, but cannot establish absence of 2022 TFRs. The physical grid is 2D, not altitude-band 3D.
