# Phase 3 Glossary

Extends `Phase2/docs/12_glossary.md`. Phase 2 terms keep their meaning.

## Analytics and OLAP

| Term | Meaning |
|---|---|
| Aggregation | Computing SUM/AVG/COUNT over grouped rows |
| ROLLUP | Multi-level grouping with subtotals and a grand total along one hierarchy |
| CUBE | Grouping across all combinations of two or more dimensions |
| Hierarchy | Ordered grouping levels; Phase 3 default: site → source category → vehicle type |
| Measure | A derived aggregate computed from fact rows; not a new fact |
| KPI | A dashboard number with a defined formula, source, and zero semantics |
| Month-over-month growth | (current − previous) / previous; null (not ±∞) when previous is 0 |
| Gold layer | The Phase 3 analytics views above the Phase 2 star schema |

## BI

| Term | Meaning |
|---|---|
| Power BI Desktop | Free Microsoft report-building tool; the Phase 3 BI client (`D3-005`) |
| PBIX | The Power BI Desktop project file; a binary deliverable under the size guard |
| Semantic model | The tables/relationships Power BI sees; here, the reporting views |
| Slicer | A dashboard filter (e.g. by site, month, source) |
| Decision page | The dashboard page stating the management decision with evidence |
| Coverage label | Visible text marking a zero as "missing coverage", not "no events" |

## Phase 3 process

| Term | Meaning |
|---|---|
| WP-P3-## | Phase 3 work package (see dev_plan/01) |
| WP-P3-H# | Optional hardening work package for Phase 2 limitations |
| P3-G# | Phase 3 gate (see dev_plan/02) |
| D3-### / H3-### | Phase 3 decision / human-action ID |
| Brief-name mapping | The retail→AeroGrid term mapping (`D3-003`, `D3-004`) |
