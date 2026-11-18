# Phase 3 Agent Operating Manual

**Status:** baseline. The binding contract is [`../AGENTS.md`](../AGENTS.md); this
manual adds Phase 3-specific operating detail.

## Session protocol

1. Ask the human for their member name and role (A–E); if unselected, they choose
   first.
2. Read, in order: root `AGENTS.md`, Phase 2 `README`/`AGENTS`/`PROGRESS`, Phase 3
   `README`, Phase 3 `AGENTS`, Phase 3 `PROGRESS`, this map's canonical table, the
   assigned WP in `dev_plan/01`.
3. Restate: WP ID, gate state, files to change, acceptance evidence, human-only
   actions.
4. Claim exactly one WP in `PROGRESS.md`. Never claim a second until the first is
   `DONE` or handed off.

## Phase 3-specific rules

- Analytics work is read-only against the warehouse. Agents never run writes
  outside the approved CI jobs, and Phase 3 CI jobs only create/replace views and
  indexes.
- Before authoring any analytics content, check the KPI dictionary in
  [04_data_model.md](04_data_model.md). A KPI not listed there needs a decision row
  first.
- Never invent numbers for dashboards, screenshots, or reports. If the data does not
  support a chart, the chart does not exist.
- Respect BI ownership: agents working for Members A–D must not author BI artifacts;
  agents working for Member E author BI artifacts only inside E's WPs.
- Keep the brief-name mapping (`D3-004`) intact: brief view names map to AeroGrid
  names; do not create retail-named views.

## Stop conditions (Phase 3 additions)

Stop and ask the human when:

- A requested KPI/metric would require data the warehouse does not have.
- A view or index would exceed a capacity guard.
- A BI artifact requires Power BI Service, a paid connector, or an account.
- The evaluator-facing wording would overclaim (zero as "no events", observed as
  certified, etc.).

## Handoff

End every session with a `PROGRESS.md` handoff: WP status, files changed, checks
run with results, evidence locations, blockers, next step, and reviewer. Use the
Phase 2 handoff template (`Phase2/templates/AGENT_HANDOFF.md`) unless Phase 3 gains
its own.
