# Phase 3 Human Operating Manual

**Status:** baseline. For warehouse operations (roles, secrets, quotas), the
authoritative manual remains `Phase2/docs/10_human_operating_manual.md`.

## Human responsibilities unique to Phase 3

| Action | When | How |
|---|---|---|
| Authorize Phase 3 start | Before any WP beyond P3-G0 | Reply in chat; record approval (H3-001) |
| Confirm Power BI Desktop availability | Before WP-P3-06 | Free Desktop install; report back (H3-002) |
| Decide the presenter | Before WP-P3-08 | Team decision; record in DECISIONS.md (H3-003) |
| Optional: create a Power BI Service account/workspace | Only if cloud publishing is wanted | Human-owned account; then record a decision (`D3-005`) |
| Submit course deliverables | At P3-G5 | Human submits; agents prepare the package |

## Approvals and gates

- Gates P3-G1 and P3-G5 close only by the human. Owners close P3-G2 … P3-G4 with
  evidence per [dev_plan/02](../dev_plan/02_dependencies_and_gates.md).
- "Almost done" is not a status. If an agent reports a WP complete, ask for the
  acceptance evidence list from [dev_plan/04](../dev_plan/04_acceptance_and_definition_of_done.md).

## Verification checklist for humans

1. Re-run the recorded queries behind any number an artifact shows.
2. Check that zero-valued KPIs carry coverage labels.
3. Check the indexing report has before/after pairs, not just "indexes added".
4. Confirm BI artifacts came from Member E's branch and were reviewed.
5. Confirm no secrets, raw data, or >10 MB artifacts were committed.

## What humans should never do

- Paste secrets or connection strings into chat.
- Run destructive SQL on the shared warehouse outside approved CI.
- Let a non-E member author dashboard artifacts.
- Treat Phase 3 aggregates as new facts with independent lineage.
