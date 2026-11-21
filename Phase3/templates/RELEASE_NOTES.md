# AeroGrid Phase 3 Release Notes

Copy this file to `Phase3/RELEASE_NOTES.md` at release time and fill every field.
Replace each `<...>` with a real value. Leave nothing as a placeholder: an item that
is not done is written as `NOT DONE` with its reason, never left blank.
Do not paste secrets, connection strings or raw data here.

## Release identity

| Field | Value |
|---|---|
| Release tag or branch | `<tag or branch>` |
| Repository link | `<https://github.com/HassanNawaz14/AeroGrid/tree/<tag-or-branch>>` |
| Commit | `<full commit SHA>` |
| Release date (UTC) | `<YYYY-MM-DD>` |
| Prepared by | Member A (platform / release) |
| Packaging run | `<GitHub Actions run URL or ID of wp-p3-09-package.yml>` |

## Deliverables

One row per course deliverable (see `Phase3/dev_plan/03_deliverables_matrix.md`).

| # | Deliverable | WP | Owner | Location | Size (MiB) | Route | SHA-256 |
|---|---|---|---|---|---:|---|---|
| 1 | Analytical SQL queries | WP-P3-02 | E | `Phase3/sql/analytical/` | n/a | committed | n/a |
| 2 | OLAP queries | WP-P3-03 | E | `Phase3/sql/olap/` | n/a | committed | n/a |
| 3 | Reporting views | WP-P3-04 | E | `Phase3/sql/views/01_gold_views.sql` | n/a | committed | n/a |
| 4 | Indexing report (PDF) | WP-P3-05 | D | `Phase3/reports/Indexing_Report.pdf` | `<>` | `<committed / Actions artifact>` | `<>` |
| 5 | Power BI dashboard (PBIX) | WP-P3-06 | E | `<path>` | `<>` | `<committed / Actions artifact>` | `<>` |
| 6 | Dashboard screenshots (PDF) | WP-P3-06 | E | `<path>` | `<>` | `<committed / Actions artifact>` | `<>` |
| 7 | Business insights report (PDF) | WP-P3-07 | E | `Phase3/reports/Business_Insights_Report.pdf` | `<>` | `<committed / Actions artifact>` | `<>` |
| 8 | Final presentation (PPTX) | WP-P3-08 | E | `Phase3/deliverables/Final_Presentation.pptx` | `<>` | `<committed / Actions artifact>` | `<>` |
| 9 | Repository link | WP-P3-09/10 | A | this file | n/a | committed | n/a |

Copy the size, route and SHA-256 values from the packaging manifest
(`Phase3/evidence/packaging_<mode>_<UTC>.md`). Never type them by hand.

## Size guard (D3-008)

- Rule: `.pbix`, PDF and PPTX files are committed only when each is under 10 MiB;
  larger files are published as GitHub Actions artifacts instead.
- Oversize artifacts in this release: `<none / list with Actions artifact name and run ID>`.
- Packaging result: `<PASS / PASS_WITH_PENDING / FAIL>` (strict run: `<yes / no>`).

## Evidence and checks

| Check | Result | Evidence |
|---|---|---|
| Phase 3 tests (`python -m pytest -q Phase3/tests`) | `<n passed>` | `<CI run URL>` |
| Analytics evidence (`DQ3-A-004`) | `<PASS>` | `Phase3/evidence/analytics_run_<UTC>.md` |
| Gold views (`DQ3-A-001`) | `<PASS>` | `Phase3/evidence/gold_views_<UTC>.md` |
| Indexing report (`DQ3-A-006`) | `<PASS>` | `Phase3/reports/Indexing_Report.pdf` |
| Dashboard KPI traceability (`DQ3-A-002`, `DQ3-A-003`) | `<PASS>` | `<link>` |
| Secret scan of packaged files | `<PASS>` | packaging manifest |
| Reader role can read all new objects | `<yes / no>` | `<link>` |

## Known limitations

List the accepted limitations that the release carries (see
`Phase3/docs/13_accepted_data_limitations.md`), for example single observed month,
single tracked site, and zero-coverage rows labelled as missing coverage.

- `<limitation and its ID>`

## Human acceptance

| Field | Value |
|---|---|
| Deliverables matrix fully `DONE` | `<yes / no>` |
| P3-G5 closed by | `<human name>` on `<date>` |
| Submission made by | `<human name>` on `<date>` |
