# Phase 3 Acceptance and Definition of Done

## Universal definition of done

A work package is `DONE` only when all of the following hold:

1. Scope matches the WP; nothing outside it changed.
2. Every acceptance criterion in [01_work_breakdown.md](01_work_breakdown.md) passes.
3. Two named reviewers approved; the author did not self-approve.
4. Commands and results are recorded so a reviewer can reproduce them.
5. Canonical documents and `Phase3/DECISIONS.md` are synced in the same PR.
6. `Phase3/PROGRESS.md` carries the handoff (status, files, checks, evidence, next step).
7. No secrets, raw data, oversized binaries, or unrelated changes.
8. No synthetic data or fabricated KPI values anywhere.
9. The work is reproducible on a clean machine with the recorded steps.
10. A reviewer can find every claim's evidence without asking the author.

## Evidence rules

- A number in any artifact must also be reproducible by a stored query run against
  the warehouse, with the capture date recorded.
- A "pass" shows observed value, expected value, and check ID.
- Screenshots are supporting evidence, never the only evidence.
- Optimization claims need EXPLAIN ANALYZE before/after pairs (DQ3-A-006).
- Coverage gaps are labeled; an unlabeled zero fails DQ3-A-003 and blocks the gate.
- BI artifacts cite the KPI dictionary entry they implement ([04](../docs/04_data_model.md)).

## "Not done if" list

- Works only on the author's machine or requires local services.
- Any secret appeared in chat, logs, screenshots, or the repo.
- A KPI appears that is not in the KPI dictionary without a decision row.
- Zero coverage is presented as "no events".
- Retail brief names are used as real view names (mapping rule `D3-004` broken).
- A claim in the insights report or deck cannot be re-run from its citation.
- Documentation disagrees with the artifact and no decision reconciles them.

## Capacity rule

No WP is `DONE` if its storage delta (indexes, materialized objects, artifacts)
would push the database past 700 MB or object storage past 3.5 GB, unless a human
approved a capacity decision in writing.
