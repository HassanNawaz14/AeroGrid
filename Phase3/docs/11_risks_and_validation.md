# Phase 3 Risks and Validation

**Status:** baseline register. Probabilities and impacts are stated for the Phase 3
context (post-Phase 2 acceptance).

## Risk register

| ID | Risk | P | I | Mitigation | Owner |
|---|---|---|---|---|---|
| R3-01 | Dashboard shows zeros that read as "no activity" where coverage is missing | Med | High | Mandatory coverage labels (`D3-009`); DQ3-A-003; insights report wording review | E |
| R3-02 | Retail-brief mapping seen as not following the assignment | Med | Med | Mapping table in [01](01_phase3_scope_and_objectives.md); preserve brief view names in comments/commit messages | E |
| R3-03 | Optimization claims without evidence | Med | High | Before/after EXPLAIN ANALYZE pairs required (DQ3-A-006) | D |
| R3-04 | Indexes or materialized marts breach free-tier storage | Low | High | Capacity guard; size impact mandatory in WP-P3-05; materialization needs `D3-007` evidence | D / A |
| R3-05 | PBIX embeds credentials or exceeds repo norms | Low | High | Reader-role connection only; size guard `D3-008`; screenshot redaction rules | E / A |
| R3-06 | Gold views drift from fact data after a WP-11 apply | Med | Med | Post-apply analytics verification workflow re-runs DQ3-A-001/004 | A |
| R3-07 | Team availability for BI (single owner) | Med | Med | Early P3-G1 start of WP-P3-02/03; reviewers pre-assigned | A |
| R3-08 | Power BI Desktop version/format incompatibility at evaluation | Low | Med | Export screenshots PDF + keep `.pbix`; record Desktop version in the insights report | E |
| R3-09 | Overclaiming in the decision page | Med | High | Every decision cites a query + check; reviewers B/A sign off | E |
| R3-10 | Phase 2 limitations (L-001…L-010) silently treated as fixed | Low | Med | Hardening track owns them via decisions; limitations doc carried forward | A |

## Validation spikes before implementation

| Spike | Question | Method | Gate |
|---|---|---|---|
| V3-01 | Can Power BI Desktop reach Neon from the evaluation machine? | Manual test with reader credentials (human) | P3-G1 |
| V3-02 | Do the three gold views reconcile to fact counts? | Run draft queries read-only; compare totals | P3-G3 |
| V3-03 | Which dashboard queries need indexes? | EXPLAIN ANALYZE on draft queries before writing index DDL | P3-G3 |

## Standing rules

- Any risk rated High impact that materializes stops the affected WP and goes to the
  human queue.
- Risks are reviewed at each gate close; new risks get the next `R3-###` ID.
