# Phase 3 Work Breakdown

Course track WP-P3-00 … WP-P3-10, then the optional hardening track. Each WP lists
owner, reviewers, prerequisites, gate, scope, deliverables, and acceptance.

## WP-P3-00 — Documentation baseline

- **Owner:** A. **Reviewers:** B, E. **Prerequisites:** none. **Gate:** P3-G0.
- **Scope:** docs 00–13 + dev_plan; no implementation, no secrets, no raw data.
- **Deliverables:** this dev_plan; docs 00–13.
- **Acceptance:** map covers every canonical subject; WPs have owners/reviewers;
  PROGRESS board initialized; zero implementation files.

## WP-P3-01 — Human prerequisites

- **Owner:** Human (A supports). **Reviewers:** —. **Prerequisites:** P3-G0. **Gate:** P3-G1.
- **Scope:** authorize Phase 3; confirm Power BI Desktop path; pick presenter.
- **Acceptance:** H3-001/002/003 closed in PROGRESS; approval recorded.

## WP-P3-02 — Analytical SQL layer

- **Owner:** E. **Reviewers:** C, D. **Prerequisites:** P3-G1. **Gate:** P3-G2.
- **Scope:** aggregation queries (SUM/AVG/COUNT) incl. monthly traffic with
  month-over-month growth; stored under `Phase3/sql/analytical/` with run evidence.
- **Out of scope:** retail-named outputs; revenue framing.
- **Acceptance:** queries run read-only against real data; results recorded
  (counts + capture date); each query reproducible; coverage labels where zeros.

## WP-P3-03 — OLAP queries (ROLLUP / CUBE)

- **Owner:** E. **Reviewers:** C, D. **Prerequisites:** P3-G1 (may overlap WP-P3-02). **Gate:** P3-G2.
- **Scope:** ROLLUP over site → source category → vehicle type; CUBE over site ×
  source system; `Phase3/sql/olap/`.
- **Acceptance:** grand totals equal plain aggregations (DQ3-A-004); run evidence
  recorded; queries reproducible.

## WP-P3-04 — Phase 3 reporting views

- **Owner:** E. **Reviewers:** C, D. **Prerequisites:** P3-G2. **Gate:** P3-G3.
- **Scope:** `vw_monthly_traffic_growth`, `vw_vehicle_analysis`,
  `vw_source_performance` in `project_reporting` (`D3-004`); idempotent DDL;
  documented grain per view.
- **Acceptance:** views created via CI; row counts reconcile to facts (DQ3-A-001);
  reader role can select; no synthetic rows.

## WP-P3-05 — Query optimization + indexing report

- **Owner:** D. **Reviewers:** C, A. **Prerequisites:** P3-G2. **Gate:** P3-G3.
- **Scope:** identify dashboard-critical queries; EXPLAIN ANALYZE before/after;
  idempotent index DDL with size impact; indexing report PDF.
- **Acceptance:** before/after pairs for every claimed index (DQ3-A-006); execution
  time and cost comparison table; storage delta within guard; report PDF in repo or
  artifact per `D3-008`.

## WP-P3-06 — Power BI dashboard

- **Owner:** E (sole author). **Reviewers:** A, D. **Prerequisites:** P3-G3, H3-002. **Gate:** P3-G4.
- **Scope:** Power BI Desktop file over the reader connection; page 1 executive
  overview (KPIs from the KPI dictionary + trend), page 2 detailed analysis
  (source/site/vehicle segmentation), page 3 decision page; screenshots PDF.
- **Acceptance:** every visual traces to a stored query (DQ3-A-002); zeros labeled;
  no credentials visible; PBIX + screenshots delivered under `D3-008`.

## WP-P3-07 — Business insights report

- **Owner:** E. **Reviewers:** B, A. **Prerequisites:** WP-P3-06. **Gate:** P3-G4.
- **Scope:** decision narrative answering "based on the dashboard, what should
  management do?"; every claim cites its query and check ID.
- **Acceptance:** DQ3-A-005 passes (dashboard numbers match cited queries at capture
  time); coverage labels present; PDF delivered.

## WP-P3-08 — Final presentation

- **Owner:** E (authors); presenter chosen by human (H3-003). **Reviewers:** all. **Prerequisites:** P3-G4. **Gate:** P3-G4.
- **Scope:** PPTX covering architecture, pipeline strength, analytics, dashboard,
  decision; consistent with all evidence documents.
- **Acceptance:** no number in the deck lacks a citation; reviewers approve.

## WP-P3-09 — CI packaging + artifacts

- **Owner:** A. **Reviewers:** D, E. **Prerequisites:** P3-G3. **Gate:** P3-G5.
- **Scope:** Phase 3 workflows (views apply + verification, optimization check,
  artifact packaging); artifact directory layout; release notes template.
- **Acceptance:** workflows green on main; artifacts packaged per `D3-008`; no
  secrets in logs.
- **Status:** `DONE` (2026-11-21, Member A; run 44871649279 green on `main`; D and E reviews recorded). The views and optimization
  workflows were delivered with WP-P3-04/05; this package adds the packaging workflow.
- **Delivered:** `Phase3/scripts/package_artifacts.py`,
  `.github/workflows/wp-p3-09-package.yml`, `Phase3/tests/test_package_artifacts.py`,
  `Phase3/templates/RELEASE_NOTES.md`, layout READMEs in `Phase3/deliverables/` and
  `Phase3/reports/`, dry-run evidence in `Phase3/evidence/`.
- **Still open (outside this package):** the final `--strict` run and
  `Phase3/RELEASE_NOTES.md` once the BI files exist (`H3-009`).

## WP-P3-10 — Release + acceptance

- **Owner:** Human (A supports). **Reviewers:** —. **Prerequisites:** P3-G4, WP-P3-09. **Gate:** P3-G5.
- **Scope:** final submission package; repo link; human acceptance recorded.
- **Acceptance:** deliverables matrix fully DONE; human closes P3-G5.

## Optional hardening track

| WP | Title | Owner | Prerequisite |
|---|---|---|---|
| WP-P3-H1 | Raw archive closure (`L-010`) | A | Decision + human priority |
| WP-P3-H2 | FAA quota mitigation | B (HarveyWebbs) | Repeated scheduled-run failures (implemented under D3-016) |
| WP-P3-H3 | SCD Type 2 evaluation | C | Decision; Phase 3+ need |
| WP-P3-H4 | Materialized marts + refresh | D | `D3-007` EXPLAIN evidence |

### WP-P3-H2 — FAA ArcGIS quota mitigation

- **Owner:** B (`HarveyWebbs` / Abdullah Zia). **Track:** Hardening. **Decision:** `D3-016`.
- **Scope:** Airspace GeoJSON FeatureServer caching (`ArcGisCache`), exponential backoff with jitter and retry budget (`BackoffBudget`), and optional-airspace graceful fallback (`AEROGRID_OPTIONAL_AIRSPACE=1`).
- **Acceptance:** Tests pass in `Phase3/tests/test_faa_quota_mitigation.py`; caching eliminates redundant REST queries; quota errors retry gracefully.
- **Status:** `DONE` (2026-11-21; review closed).
