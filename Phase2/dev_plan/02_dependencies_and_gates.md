# Dependencies and Gates

## Purpose

This file defines the canonical work-package dependency graph and gate criteria. A
work package may not start until its prerequisites and gate are satisfied. When in
doubt, stop and ask the human.

## Canonical work-package sequence

```text
WP-00 Documentation baseline
  |
WP-01 Human prerequisites (G1)
  |
  +--> WP-02 Platform validation
  |
  +--> WP-03 Source validation (G2 with WP-02)
          |
          +--> WP-04 Staging
          |
          +--> WP-05 Dimensions
                  |
          WP-06 Core facts (needs WP-04 + WP-05; G3)
                  |
          WP-07 Derived facts (G4 then G5)
                  |
          +--> WP-08 Data quality
          +--> WP-10 Reporting views
                  |
          WP-09 PDF reports (after WP-08)
                  |
          WP-11 CI and access (after WP-02, WP-04 to WP-10)
                  |
          WP-12 Integration and release (G6 then G7)
```

The diagram is a dependency view, not a requirement to work in a single global order.
Members may work in parallel only where the explicit dependency table allows it.

## Dependency table

| WP | Depends on | May overlap with | Gate before start |
|---|---|---|---|
| `WP-00` | None | None | None |
| `WP-01` | `WP-00` accepted | None | G0 |
| `WP-02` | `WP-01` | `WP-03` | G1 |
| `WP-03` | `WP-01` | `WP-02` | G1 |
| `WP-04` | `WP-03` | `WP-05` | G2 |
| `WP-05` | `WP-02`, model approved | `WP-04` | `D-022` (`WP-03`/`WP-04` merged) |
| `WP-06` | `WP-04`, `WP-05` | None | G3 |
| `WP-07` | `WP-06`, thresholds approved | `WP-10` design | G4 |
| `WP-08` | `WP-04` to `WP-07` | `WP-09` design | G5 |
| `WP-09` | `WP-08` | `WP-10` | G6 input |
| `WP-10` | `WP-06`, `WP-07` | `WP-08`, `WP-09` | G5 |
| `WP-11` | `WP-02`, `WP-04` to `WP-10` | `WP-12` planning | G6 input |
| `WP-12` | `WP-11` | None | G6 |

## Critical path

```text
WP-01 -> WP-03 -> WP-04 -> WP-05 -> WP-06 -> WP-07 -> WP-08 -> WP-09 -> WP-11 -> WP-12
```

`WP-02` must also be complete before a real CI run. A delay in the platform proof can
block `WP-11` even if source work progresses.

## Gate definitions

### G0: Documentation baseline

**Status:** DONE (`H-001`, 2026-11-04).
**Owner:** Member A
**Approvers:** Members B and C; human review
**Required WPs:** `WP-00`

Exit criteria:

- Root and Phase 2 agent contracts exist.
- Phase 2 dashboard, progress board, and decision log exist.
- Docs `00`-`12` exist and links resolve.
- Dev plan, acceptance, and templates exist.
- Folder boundaries are documented.
- Previous docs are updated or marked historical.
- No implementation, secrets, or raw data exists.
- The human can identify the exact next action.

Evidence:

- Link check output in `PROGRESS.md`.
- File inventory.
- Handoff row.

### G1: Human prerequisites

**Status:** DONE (`H-007`, 2026-11-04; `H-002` deferred).
**Owner:** Human
**Coordinator:** Member A
**Required WPs:** `WP-01`

Exit criteria:

- Human approves scope, architecture, sources, licenses, and model.
- Member A is HassanNawaz14; Members B-E have real names, or the B-E placeholders are
  explicitly accepted for planning.
- Neon project, database, and raw bucket exist.
- GitHub `warehouse` environment and required secret names exist.
- Read-only access plan is approved.
- Optional OpenSky terms are confirmed or explicitly deferred.
- `implementation_authorized: YES` is recorded.
- All G1 checklist items are complete.

Evidence:

- `H-001` to `H-008` closed or explicitly deferred with scope impact.
- Authorization record in `PROGRESS.md`.
- No secret values in Git or chat.

### G2: Platform and source readiness

**Status:** DONE 2026-11-08; `WP-02` passed access validation (run `42276737288`) and
`WP-03` source validation merged in PR #5 (`f9087f4`). Accepted by HassanNawaz14.
**Owner:** Member A for platform; Member B for sources
**Reviewers:** Members C, D, E
**Required WPs:** `WP-02`, `WP-03`

Exit criteria:

- CI can connect with the write role and use object storage.
- Read-only role works and cannot write.
- Required sources are validated for schema, license, units, time base, and
  coordinates.
- Tartan georeferencing is validated.
- Nightjar/DJI time and altitude semantics are documented.
- FAA geometry and historical TFR limitation are documented.
- Weather station mapping is validated.
- Capacity estimate is below the approved database budget.
- Any source FAIL has a recorded decision and fallback.

Evidence:

- Access proof counts.
- Source validation records.
- Georeferencing comparison.
- Capacity estimate.
- Gate row in `PROGRESS.md`.

### G3: Staging and dimensional schema

**Status:** DONE 2026-11-09, recorded on HassanNawaz14's explicit instruction.
Staging DDL is applied and readable; the six dimensions, `-1` members, unique natural
keys, FK targets, and reader access are verified. Caveat `B-011` (now resolved): the
`WP-04` sample used the legacy demo CSV, so real accepted-row staging proof came from
`WP-06` before `G4`.
**Owner:** Member C for schema; Member B for staging
**Reviewers:** Members A, D
**Required WPs:** `WP-04`, `WP-05`

Exit criteria:

- `project_staging` exists with manifest, run log, rejects, and DQ result tables.
- Staging loaders work on real samples and rerun idempotently.
- `project_dw` exists with six dimensions and required constraints.
- Unknown members are seeded.
- Natural keys are unique.
- Dimension row count is at least 100 using real data.
- Data dictionary and DBML match the DDL.
- No raw data is in Git.

Evidence:

- DDL and seed commands.
- Staging reconciliation.
- Dimension counts.
- Constraint/orphan queries.
- Data dictionary diff.

### G4: Core movement facts

**Status:** DONE 2026-11-11, recorded under `D-024` after WP-05 run `42689267328` and
WP-06 run `42887782411` passed on `phase2/wp06-tracking-facts` at `ecce8ec`; PR #12
merged as `f29b099` and `B-011` is resolved. The `D-024` window is closed.
**Owner:** Member D
**Reviewers:** Members C, E
**Required WPs:** `WP-06`

Exit criteria:

- Tracking and journey facts load from real staging rows.
- Surrogate-key mapping is correct.
- Fact counts meet the 10,000-row requirement.
- Natural-key uniqueness holds.
- Tracking reconciles to accepted staging.
- Journeys have a documented grain and segmentation.
- Rerun is idempotent.
- No orphan facts.

Evidence:

- Fact counts.
- Reconciliation query.
- Duplicate/orphan checks.
- Rerun comparison.
- Journey sample review.

### G5: Derived facts and thresholds

**Status:** NOT_STARTED; `WP-07` is `BLOCKED_ON_HUMAN` until `H-013` approves the
thresholds and `algorithm_version`.
**Owner:** Member E
**Reviewers:** Members C, D
**Required WPs:** `WP-07`

Exit criteria:

- Close encounters, occupancy, and restriction activation are built only from real
  evidence.
- Thresholds are approved and versioned before results are interpreted.
- Every derived row traces to tracking/restriction rows.
- Encounter vehicles are distinct and same-site/time.
- Occupancy uniqueness holds.
- No threshold was changed silently to improve results.
- No synthetic derived rows.

Evidence:

- Derived-fact counts.
- Algorithm version and threshold record.
- Traceability queries.
- Failure-path tests.

### G6: Quality, reporting, and automation

**Owner:** Member E for DQ/reports; Member A for CI/access
**Reviewers:** All affected owners
**Required WPs:** `WP-08`, `WP-09`, `WP-10`, `WP-11`

Exit criteria:

- DQ results are stored for every run.
- Critical failures fail the run.
- Both PDFs exist and match stored evidence.
- Reporting views exist and are readable by the read-only role.
- Weekly/manual CI works with environment secrets.
- Reports upload as artifacts.
- No secret appears in logs.
- Capacity is within the free-tier budget.
- No critical DQ failures remain on the accepted run.

Evidence:

- DQ result counts.
- PDF links.
- View list and read-only query proof.
- Actions run URL/summary.
- Capacity report.

### G7: Integration and release

**Owner:** Member A
**Reviewers:** Members B-E; human acceptance
**Required WPs:** `WP-12`

Exit criteria:

- A clean authorized end-to-end run reproduces the accepted result.
- All rubric items have evidence.
- Final PDFs are present.
- All five members can query the shared warehouse read-only.
- No critical DQ failures.
- No secrets or raw data in Git.
- Documentation and status are final.
- Human accepts the release.

Evidence:

- Final acceptance checklist.
- Reproducible run ID.
- Access proof from a second member.
- Final repository link.
- Handoff record.

## Gate status rules

- A gate is `BLOCKED_ON_HUMAN` when a human action is the only missing item.
- A gate is `BLOCKED` for a technical dependency or failed validation.
- Only the human closes `G1` and `G7`.
- Technical gate owners close `G2`-`G6` with reviewer evidence and a `PROGRESS.md`
  row.
- Do not mark a gate done because the implementation "mostly works".
- Do not reopen a closed gate silently; record the reason and the human decision.

## Dependency stop rules

Stop and ask the human if:

- A dependency is missing but someone asks to start the dependent package anyway.
- A source validation fails and no fallback is approved.
- A work package would change the model, sites, grains, or thresholds.
- A gate is being skipped to meet a demo.
- A member is asked to approve their own high-risk change.
- The free-tier budget would be exceeded.
