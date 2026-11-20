# Phase 3 Deliverables Matrix

Course deliverables (from `Phase3/DWBI Lab Phase 3.pdf`) mapped to WPs, owners, and
evidence. Statuses: `PLANNED` / `IN_PROGRESS` / `READY_FOR_REVIEW` / `DONE` /
`BLOCKED`.

| # | Course deliverable | Marks | Phase 3 artifact | WP | Owner | Evidence | Status |
|---|---|---|---|---|---|---|---|
| 1 | Analytical SQL queries | 10 | `Phase3/sql/analytical/*.sql` + run log | WP-P3-02 | E | recorded query outputs with capture date | DONE (PR #35, `761475b`; `Phase3/evidence/analytics_run_20261118T110136Z.md`) |
| 2 | OLAP queries | 5 | `Phase3/sql/olap/*.sql` + run log | WP-P3-03 | E | DQ3-A-004 grand-total reconciliation | DONE (PR #35, `761475b`; `DQ3-A-004` PASS) |
| 3 | Reporting views | — | `project_reporting.vw_monthly_traffic_growth`, `vw_vehicle_analysis`, `vw_source_performance` | WP-P3-04 | E | view DDL + row-count reconciliation | DONE (applied and reader-proofed via `H3-005`; `DQ3-A-001` PASS) |
| 4 | Indexing report (PDF) | — | `Phase3/reports/Indexing_Report.pdf` | WP-P3-05 | D | before/after EXPLAIN ANALYZE pairs | DONE (Reviewed; run 44397831286; all pairs NEUTRAL; no apply per `D3-011`) |
| 5 | Power BI dashboard (PBIX) | 10 | `Phase3/deliverables/AeroGrid_Dashboard.pbix` (or artifact if ≥ 10 MB) | WP-P3-06 | E | KPI traceability table (DQ3-A-002) | PLANNED |
| 6 | Dashboard screenshots (PDF) | — | `Phase3/reports/Dashboard_Screenshots.pdf` | WP-P3-06 | E | per-page captures with data-as-of | PLANNED |
| 7 | Business insights report (PDF) | 5 | `Phase3/reports/Business_Insights_Report.pdf` | WP-P3-07 | E | claim → query → check citation map | PLANNED |
| 8 | Final presentation (PPT) | — | `Phase3/deliverables/Final_Presentation.pptx` | WP-P3-08 | E | reviewer approvals; citation check | PLANNED |
| 9 | Repository link | — | repo URL at release tag/branch | WP-P3-09/10 | A | release notes | PLANNED |

## Marks guardrail

- Analytical SQL 10 + OLAP 5 + dashboard 10 + insights 5 = 30%. Every graded
  artifact is traceable to a WP with two named reviewers.
- The indexing report and views are unmarked deliverables but gate P3-G3; they are
  not optional.

## Final submission checklist

- [ ] All rows above `DONE` with evidence links
- [ ] Zero-valued KPIs labeled (DQ3-A-003 pass)
- [ ] No secrets, raw data, or oversized binaries committed
- [ ] Reader role can still read everything new
- [ ] Human closes P3-G5 and submits
