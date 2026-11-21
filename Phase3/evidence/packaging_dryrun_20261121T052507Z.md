# Phase 3 artifact packaging record

- Captured (UTC): `2026-11-21T05:25:07Z`
- Mode: `dry-run`; strict: `false`
- Environment: `local`; commit: `887fd7ec94c794ca87c5c95ba2c5207eb7e4f997`
- Rule: `D3-008` - commit only when < 10 MiB each; larger files are Actions artifacts
- Result: **PASS_WITH_PENDING**

## Deliverable coverage

| Key | WP | Owner | Kind | Required | Status | Files |
|---|---|---|---|---|---|---|
| `indexing_report` | WP-P3-05 | D | deliverable | yes | PRESENT | 1 |
| `dashboard_pbix` | WP-P3-06 | E | deliverable | yes | MISSING | 0 |
| `dashboard_screenshots` | WP-P3-06 | E | deliverable | yes | MISSING | 0 |
| `business_insights` | WP-P3-07 | E | deliverable | yes | MISSING | 0 |
| `final_presentation` | WP-P3-08 | E | deliverable | yes | MISSING | 0 |
| `release_notes` | WP-P3-09 | A | deliverable | yes | MISSING | 0 |
| `evidence_analytics` | WP-P3-02/03 | E | evidence | no | PRESENT | 1 |
| `evidence_gold_views` | WP-P3-04 | E | evidence | no | PRESENT | 1 |
| `evidence_indexes` | WP-P3-05 | D | evidence | no | MISSING | 0 |

## Files

| Path | Bytes | MiB | Route | Secret scan | SHA-256 |
|---|---:|---:|---|---|---|
| `Phase3/reports/Indexing_Report.pdf` | 6599 | 0.006 | bundle | PASS | `19a9a6f9bdb6200a2db4d2fdf927cea9f7d7279fa6deaf8d9817a516a2a0d119` |
| `Phase3/evidence/analytics_run_20261118T110136Z.md` | 56360 | 0.054 | bundle | PASS | `2de104fca711a2d39ba3ed5e245ba5808ed862e505686447860f7a979906818f` |
| `Phase3/evidence/gold_views_20261118T113454Z.md` | 1425 | 0.001 | bundle | PASS | `0d3c06baa179f8da9a5e3228ced4ee6eaddf19ac9637b651aa4d6937d0d3b9fd` |

## Findings

- No secret-pattern hits and no oversized tracked files.
- Required deliverables not yet present: `dashboard_pbix`, `dashboard_screenshots`, `business_insights`, `final_presentation`, `release_notes`. A missing file is reported, never created or simulated.

Secret scan limits: only uncompressed bytes are inspected, so compressed PDF streams are not decoded. Review screenshots and PDFs by eye before release.
