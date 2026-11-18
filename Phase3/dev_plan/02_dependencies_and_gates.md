# Phase 3 Dependencies and Gates

## Dependency order

```text
WP-P3-00 → WP-P3-01 → {WP-P3-02, WP-P3-03} → WP-P3-04 → {WP-P3-05, WP-P3-06}
          → WP-P3-07 → WP-P3-08 → WP-P3-09 → WP-P3-10
```

- WP-P3-02 and WP-P3-03 may run in parallel; both feed P3-G2.
- WP-P3-05 (optimization) and WP-P3-06 (dashboard) both need P3-G3 views.
- WP-P3-07 needs the dashboard (WP-P3-06); WP-P3-08 needs everything graded.
- Hardening WPs are independent of the course critical path and start only via a
  decision.

Critical path: WP-P3-01 → WP-P3-02 → WP-P3-04 → WP-P3-06 → WP-P3-07 → WP-P3-09 →
WP-P3-10.

## Gates

| Gate | Required WPs | Closer | Exit criteria |
|---|---|---|---|
| P3-G0 Documentation baseline | WP-P3-00 | Owner + reviewer | docs 00–13 + dev_plan complete; no implementation/secrets/raw data; map resolves every subject |
| P3-G1 Human prerequisites | WP-P3-01 | **Human only** | Phase 3 authorized; Power BI path confirmed; presenter chosen (H3-001…003 closed) |
| P3-G2 Analytics layer | WP-P3-02, WP-P3-03 | Owner | analytical + OLAP SQL stored; run evidence recorded; DQ3-A-004 passes; queries reproducible read-only |
| P3-G3 Reporting & performance | WP-P3-04, WP-P3-05 | Owner | three gold views live and reconciled (DQ3-A-001); indexing report PDF with before/after pairs; storage within guard |
| P3-G4 BI delivery | WP-P3-06, WP-P3-07, WP-P3-08 | Owner | PBIX + screenshots + insights report delivered; every KPI traced (DQ3-A-002); decision narrative evidence-cited; deck approved by all reviewers |
| P3-G5 Release | WP-P3-09, WP-P3-10 | **Human only** | deliverables matrix all DONE; artifacts packaged; repo link ready; human accepts |

## Gate rules

- Gates close in order; a later gate never reopens an earlier one silently.
- Every gate close updates [../PROGRESS.md](../PROGRESS.md) with evidence pointers.
- If gate evidence and documentation disagree, stop and reconcile before closing.
