# Phase 3 Team Work Division

**Status:** baseline; effective once P3-G1 authorizes Phase 3 (`D3-002`).

## Members

Roles are fixed; names for Members A–D are decided by the team and recorded here
when assigned. Member E is assigned.

| Member | Account | Phase 3 role |
|---|---|---|
| A | (unassigned) | platform / integration / release lead — CI workflows, artifact packaging, release, hardening track lead |
| B | HarveyWebbs (Abdullah Zia) | sources & staging — source/licence reviews, hardening H2 |
| C | (unassigned) | schema & dimensions — model reviews, hardening H3 |
| D | (unassigned) | facts & performance — query optimization + indexing report, hardening H4 |
| E | HassanNawaz14 | analytics & BI — **all BI deliverables** (see below) |

## BI ownership rule (`D3-002`)

**Member E owns and authors every BI deliverable.** One accountable owner, no split
responsibility:

| Deliverable | Owner | Reviewers |
|---|---|---|
| Analytical SQL queries (WP-P3-02) | E | C, D |
| OLAP queries (WP-P3-03) | E | C, D |
| Phase 3 reporting views (WP-P3-04) | E | C, D |
| Power BI dashboard `.pbix` (WP-P3-06) | E | A, D |
| Dashboard screenshots PDF (WP-P3-06) | E | A, D |
| Business insights report PDF (WP-P3-07) | E | B, A |
| Final presentation PPTX (WP-P3-08) | E | All members |

Other members may **review** BI artifacts but must not author or edit them. Member A
owns the CI plumbing that packages BI artifacts, not their content. The indexing
report (WP-P3-05) is a performance engineering report owned by D, not a BI artifact.

## Division of labour outside BI

| Area | Owner | Support |
|---|---|---|
| Documentation baseline (P3-G0) | A | All |
| Human prerequisites (P3-G1) | Human | A |
| Query optimization + indexing report | D | C |
| CI workflows + artifact packaging | A | D |
| Release + acceptance (P3-G5) | Human | A |
| Hardening track (optional) | A (H1), B (H2), C (H3), D (H4) | E reviews analytics impact |

## Review protocol

- Every WP names two reviewers in [dev_plan/01](../dev_plan/01_work_breakdown.md).
- Reviewers check evidence, not summaries: re-runnable queries, stored results,
  coverage labels.
- The author cannot approve their own change; Member E cannot merge BI PRs alone.
