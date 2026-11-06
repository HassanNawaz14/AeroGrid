# Data Quality and Reports

## Purpose

Phase 2 requires demonstrable data cleaning and data-quality validation. This
document defines the rules, severity model, evidence, and report content. It is the
canonical quality plan until implementation changes it through a recorded decision.

## Quality principles

- Validate real data; never fabricate a passing result.
- The legacy synthetic files under `data/sample/` are demo-only and are excluded from
  every Phase 2 load, check, and report (`D-017`).
- Store every check result, including passes.
- Separate source gaps from pipeline defects.
- Fail closed on critical integrity issues.
- Never silently correct a business-significant value.
- Make every rejection traceable to a source row and reason.
- Reconcile staging counts to fact counts.
- Publish the same evidence to the database and the PDF reports.

## Data cleaning versus data quality

| Activity | Output |
|---|---|
| Data cleaning | Normalized staging rows, rejects with reasons, duplicate handling |
| Data quality | Independent checks against the cleaned warehouse, with pass/fail evidence |
| Reporting | Human-readable PDFs summarizing both |

Cleaning must not be used to hide a quality problem. If rows are rejected, the report
must show the count and reason.

## Check catalog

### Completeness

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-C-001` | Required tracking fields non-null: event time, site, vehicle, grid | Critical | 0 nulls in accepted facts |
| `DQ-C-002` | Required dimension fields non-null | Critical | 0 nulls |
| `DQ-C-003` | Weather key completeness for tracking rows | Warning | Report percentage; unknown allowed |
| `DQ-C-004` | Vehicle natural key completeness | Critical | 0 missing accepted keys |
| `DQ-C-005` | Source manifest completeness: URL, license, hash, fetched_at | Critical | 0 missing for used sources |
| `DQ-C-006` | Provenance completeness on facts | Critical | 0 fact rows without source/run lineage |

### Uniqueness

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-U-001` | Dimension natural key uniqueness | Critical | 0 duplicates |
| `DQ-U-002` | Fact source natural key uniqueness | Critical | 0 duplicates |
| `DQ-U-003` | Occupancy `(time_key, grid_key)` uniqueness | Critical | 0 duplicates |
| `DQ-U-004` | Encounter deterministic pair uniqueness | Critical | 0 duplicates |
| `DQ-U-005` | No duplicate raw object manifest entries for the same SHA-256 and source | Warning | Report count |

### Accuracy

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-A-001` | Latitude within [-90, 90] | Critical | 0 invalid accepted rows |
| `DQ-A-002` | Longitude within [-180, 180] | Critical | 0 invalid accepted rows |
| `DQ-A-003` | Position inside the assigned site bounding box with tolerance | Critical | 0 outside accepted rows |
| `DQ-A-004` | Altitude within a documented plausible range for the source | Critical | 0 outside accepted rows; rejected rows explained |
| `DQ-A-005` | Speed within a documented plausible range | Warning | Report outliers |
| `DQ-A-006` | Timestamp inside the source's valid range | Critical | 0 impossible accepted rows |
| `DQ-A-007` | Altitude datum is not mixed silently | Critical | 0 accepted rows without datum/source |
| `DQ-A-008` | Wind direction within [0, 360) or null/VRB | Warning | 0 invalid stored values |
| `DQ-A-009` | Visibility/ceiling units match the dictionary | Warning | 0 unit mismatches |

### Integrity

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-I-001` | Fact to time FK orphan count | Critical | 0 |
| `DQ-I-002` | Fact to site FK orphan count | Critical | 0 |
| `DQ-I-003` | Fact to vehicle FK orphan count | Critical | 0 |
| `DQ-I-004` | Fact to grid FK orphan count | Critical | 0 |
| `DQ-I-005` | Fact to weather FK orphan count | Critical | 0 (unknown `-1` allowed) |
| `DQ-I-006` | Fact to zone FK orphan count | Critical | 0 |
| `DQ-I-007` | Journey origin/destination grid belongs to the same site policy | Warning | 0 unexplained mismatches |
| `DQ-I-008` | Encounter vehicles are distinct | Critical | 0 same-key pairs |

### Reconciliation

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-R-001` | Staging accepted + rejected + duplicates = staging read (out-of-scope rows count as rejected) | Critical | Exact reconciliation |
| `DQ-R-002` | Tracking facts = accepted tracking source records for the load window | Critical | Exact, allowing documented unknown-dimension rejects |
| `DQ-R-003` | Journey facts match source journey/segment count | Warning | Report difference |
| `DQ-R-004` | Occupancy vehicles are a subset of tracking vehicles for the hour | Critical | 0 violations |
| `DQ-R-005` | Encounter rows have two valid tracking inputs | Critical | 0 violations |
| `DQ-R-006` | Restriction affected counts do not exceed valid tracking rows in the zone/time | Critical | 0 violations |

### Timeliness

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-T-001` | Latest successful ETL run within the expected weekly window | Warning | Report age; fail if stale beyond approved threshold |
| `DQ-T-002` | Required sources have a current snapshot or documented static status | Warning | Report per source |
| `DQ-T-003` | Optional source gap is visible | Warning | Report only |

### Business rules

| ID | Check | Severity | Proposed threshold |
|---|---|---|---|
| `DQ-B-001` | Close encounters use documented thresholds and airborne rows | Critical | 0 violations |
| `DQ-B-002` | UAS and manned data are not paired across unrelated sites/times | Critical | 0 violations |
| `DQ-B-003` | TFR activation has a real snapshot/effective window | Critical | 0 unsupported active rows |
| `DQ-B-004` | No synthetic or generated records | Critical | 0 provenance gaps |
| `DQ-B-005` | Fact rows do not use zero as a substitute for unknown | Warning | Report candidates |

Thresholds are proposals. The human must approve any threshold that changes the
business meaning, especially close-encounter separation.

## Severity model

| Severity | Meaning | CI behavior |
|---|---|---|
| `CRITICAL` | Trust or integrity is broken | Fail the run; do not mark data trusted |
| `WARNING` | Data is usable but incomplete or suspicious | Continue; publish in report; require review |
| `INFO` | Observation for context | Continue; publish in report |

A critical check may be temporarily accepted only by a human decision recorded in
`DECISIONS.md` and `PROGRESS.md`. Do not downgrade a critical check silently.

## DQ result storage

Table: `project_staging.dq_result`

Suggested columns:

- `dq_result_id`
- `etl_run_id`
- `check_id`
- `check_name`
- `severity`
- `table_name`
- `status` (`PASS`, `FAIL`, `WARN`, `SKIP`)
- `observed_value`
- `expected_value`
- `details`
- `checked_at`

Every run must record passes and failures. Empty results are not evidence.

## Data Cleaning Report

File: `Phase2/reports/Data_Cleaning_Report.pdf`

Required sections:

1. Run metadata: run ID, date, code version, source manifest IDs.
2. Source inventory: source, URL, license, fetch time, file size, SHA-256.
3. Before/after counts per source.
4. Cleaning rules applied: time, text, units, coordinates, duplicates, nulls.
5. Reject counts by source and reason.
6. Georeferencing and unit validation notes.
7. Duplicate handling.
8. Known gaps and limitations.
9. Attribution and license notices.
10. Reproduction instructions.

The report must state that no synthetic data was used.

## Data Quality Report

File: `Phase2/reports/Data_Quality_Report.pdf`

Required sections:

1. Run metadata and scope.
2. Executive summary: pass/fail by severity.
3. Check results table grouped by category.
4. Critical failures and their impact.
5. Dimension and fact row counts.
6. Foreign-key orphan counts.
7. Staging-to-fact reconciliation.
8. Close-encounter and restriction threshold notes.
9. Timeliness and source gaps.
10. Capacity usage: database size, object storage, row counts.
11. Recommended actions.
12. Evidence appendix with SQL/check identifiers.

## Required headline evidence

The report must include at least:

- Total dimension rows and whether the 100+ requirement is met.
- Total fact rows and whether the 10,000+ requirement is met.
- Orphan counts for every fact-to-dimension relationship.
- Duplicate natural-key counts.
- Staging read/accepted/rejected/duplicate counts.
- Latest successful run timestamp.
- Raw archive size and database size.
- Source licenses and attribution.

## DQ failure handling

If a critical check fails:

1. Mark `etl_run_log.status = FAILED`.
2. Keep the previous trusted warehouse state if possible.
3. Write the failure to `dq_result`.
4. Generate the DQ report with the failure visible.
5. Do not publish a "data trusted" claim.
6. If the correct fix needs a business decision, stop and ask the human.

If a warning fails:

1. Continue.
2. Include the warning in the report.
3. Record a follow-up in `PROGRESS.md` if it affects a deliverable.

## Quality ownership

| Area | Owner |
|---|---|
| Source validation and rejects | Member B |
| Dimension/key integrity | Member C |
| Tracking/journey reconciliation | Member D |
| Derived facts, checks, reports | Member E |
| CI enforcement and publication | Member A |

## Future automation

The DQ framework will be implemented in `WP-08`, with PDF generation in `WP-09`:

- SQL check library in `Phase2/sql/`.
- Python runner in `Phase2/etl/dq.py`.
- Results in `project_staging.dq_result`.
- PDF builder in `Phase2/etl/reports.py`.
- CI gate that fails on critical failures.

No quality code exists yet. `G1` is cleared; DQ implementation begins in `WP-08` after
`G5`.
