# Deliverables Matrix

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](../docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md)..

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Purpose

This matrix maps every Phase 2 requirement and operating commitment to a concrete
artifact, evidence, work package, and owner. A requirement is not complete until the
evidence exists and is reviewable.

## Rubric and required deliverables

| ID | Requirement | Artifact / evidence | WP | Owner | Status |
|---|---|---|---|---|---|
| `D-01` | `project_staging` schema | Staging DDL and live schema inventory | `WP-04` | B | DONE (`WP-04`; runs `42474788058`/`42477720902`) |
| `D-02` | `project_dw` schema | Dimension/fact DDL and live schema inventory | `WP-05`, `WP-06` | C/D | DONE (requester-admin accepted 2026-11-13) |
| `D-03` | `project_reporting` schema | Reporting view DDL and view catalog | `WP-10` | E | DONE (requester-admin accepted 2026-11-13) |
| `D-04` | Real public data only | Source manifest, URL/license, validation records, no-synthetic audit | `WP-03`, `WP-08` | B/E | IN_PROGRESS (source validation `DONE`; no-synthetic audit pending `WP-08`) |
| `D-05` | Staging and cleaning | Staging loaders, rejects, cleaning counts | `WP-04` | B | DONE (`WP-04`) |
| `D-06` | Dimension tables | Six dimensions with constraints and seeds | `WP-05` | C | DONE (`WP-05`) |
| `D-07` | Fact tables | Five facts with documented grains | `WP-06`, `WP-07` | D/E | DONE (requester-admin accepted 2026-11-13) |
| `D-08` | Surrogate keys | Identity keys, `-1` unknown members, natural-key uniqueness | `WP-05` | C | DONE (`WP-05`) |
| `D-09` | Fact loading by key mapping | Mapping SQL/code and reconciliation evidence | `WP-06`, `WP-07` | D/E | DONE (requester-admin accepted 2026-11-13) |
| `D-10` | 100+ dimension rows | Count query and report evidence | `WP-05` | C | DONE (169 `dim_time`, 156 real Tartan vehicles) |
| `D-11` | 10,000+ fact rows | Count query and report evidence | `WP-06`, `WP-07` | D/E | DONE (requester-admin accepted 2026-11-13) |
| `D-12` | Data-quality checks | Check catalog, stored `dq_result`, pass/fail evidence | `WP-08` | E | DONE (requester-admin accepted 2026-11-13) |
| `D-13` | Data Cleaning Report PDF | `Phase2/reports/Data_Cleaning_Report.pdf` | `WP-09` | E | DONE (requester-admin accepted 2026-11-13) |
| `D-14` | Data Quality Report PDF | `Phase2/reports/Data_Quality_Report.pdf` | `WP-09` | E | DONE (requester-admin accepted 2026-11-13) |
| `D-15` | SQL scripts | Versioned SQL in `Phase2/sql/` | `WP-04`-`WP-10` | B/C/D/E | DONE (requester-admin accepted 2026-11-13) |
| `D-16` | ETL scripts | Python package in `Phase2/etl/` | `WP-03`-`WP-09` | B/D/E | DONE (requester-admin accepted 2026-11-13) |
| `D-17` | GitHub repository link | Public repository and final commit/code link | `WP-12` | A | PLANNED |
| `D-18` | Shared five-member read access | Read-only role proof from multiple members | `WP-02`, `WP-11` | A | IN_PROGRESS (reader `SELECT` proof exists; five-member demonstration pending `WP-11`) |

## Operating commitments

| ID | Commitment | Artifact / evidence | WP | Owner | Status |
|---|---|---|---|---|---|
| `O-01` | No local PostgreSQL | Architecture/access proof; no local DB dependency | `WP-02` | A | PLANNED |
| `O-02` | No Docker or containers | Workflow/package review | `WP-11` | A | PLANNED |
| `O-03` | Free tiers only | Neon/GitHub plan evidence; no card-gated service | `WP-01`, `WP-02` | Human/A | PLANNED |
| `O-04` | Weekly or manual refresh | Workflow schedule and manual dispatch | `WP-11` | A | PLANNED |
| `O-05` | Raw data outside Git | Object storage manifest; `.gitignore`; repo scan | `WP-03`, `WP-04` | B/A | PLANNED |
| `O-06` | No secrets in Git | Secret scan; environment-only references | `WP-11` | A | PLANNED |
| `O-07` | Source attribution | License section in docs and reports | `WP-09` | E | DONE (requester-admin accepted 2026-11-13) |
| `O-08` | Capacity guardrails | DB/object-storage usage and estimates | `WP-02`, `WP-12` | A | PLANNED |
| `O-09` | Reproducibility | Run ID, code version, source manifest, counts | `WP-11`, `WP-12` | A | PLANNED |
| `O-10` | Human gate discipline | `PROGRESS.md` gate/action evidence | `WP-01`, `WP-12` | A/Human | IN_PROGRESS |
| `O-11` | Documentation/agent contract | `AGENTS.md`, `Phase2/AGENTS.md`, manuals | `WP-00` | A | DONE (`H-001`) |
| `O-12` | Phase 1 preservation | Phase 1 files unmodified; supersession note | `WP-00` | A | DONE (`H-001`) |

## Evidence quality rules

- A count in a PDF must also exist as a stored DQ/result row.
- A source claim must include URL, license, and fetch/hash evidence.
- A generated row must show its real input rows.
- A "pass" must include the observed value, expected value, and check ID.
- A screenshot is supporting evidence, not the only evidence.
- A repository link must point to the final code and docs, not a local path.
- A read-only proof must show both a successful `SELECT` and a rejected write.

## Status definitions for this matrix

| Status | Meaning |
|---|---|
| `PLANNED` | Not implemented; acceptance evidence absent |
| `IN_PROGRESS` | Artifact exists but is not accepted |
| `READY_FOR_REVIEW` | Evidence exists; review pending |
| `DONE` | Accepted with evidence |
| `BLOCKED` | Dependency, human action, or validation failure |

Do not change a row to `DONE` based on intent. Point to the evidence.

## Final submission checklist

- [ ] `project_staging` exists and contains real cleaned source data.
- [ ] `project_dw` has six dimensions and five facts.
- [ ] `project_reporting` has the required views.
- [ ] 100+ dimension rows are demonstrated.
- [ ] 10,000+ fact rows are demonstrated.
- [ ] Surrogate-key mapping is demonstrated.
- [ ] Data-quality checks and stored results are demonstrated.
- [ ] Data Cleaning Report PDF is final.
- [ ] Data Quality Report PDF is final.
- [ ] SQL and ETL scripts are in Git.
- [ ] GitHub link is recorded.
- [ ] All five members can read the warehouse.
- [ ] No secrets or raw data are committed.
- [ ] No synthetic data exists.
- [ ] Weekly/manual automated run works.
- [ ] Human accepts `G7`.
