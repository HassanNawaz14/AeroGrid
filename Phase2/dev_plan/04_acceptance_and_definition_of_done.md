# Acceptance and Definition of Done

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](../docs/FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Purpose

This file defines the evidence required to call Phase 2 work complete. It applies to
humans, agents, and reviewers. A status of `DONE` without evidence is invalid.

## Universal Definition of Done

Every work package must satisfy all of the following:

1. Scope matches the assigned work package.
2. All package acceptance criteria pass.
3. The required peer review is complete.
4. Relevant tests/checks pass and the exact commands/results are recorded.
5. Documentation and data dictionary are updated where interfaces changed.
6. `PROGRESS.md` has status, files changed, checks, blockers, and next step.
7. No secret, raw data, database dump, or unrelated change is included.
8. No synthetic data was introduced.
9. The change is reproducible from the recorded inputs.
10. A reviewer can find the evidence without asking the author.

## Status language

| Status | Required evidence |
|---|---|
| `NOT_STARTED` | None |
| `READY` | Dependencies/gates satisfied |
| `IN_PROGRESS` | Active owner and scope recorded |
| `BLOCKED_ON_HUMAN` | `H-###` action and exact block |
| `BLOCKED` | Technical dependency and attempted fixes |
| `READY_FOR_REVIEW` | Deliverables and evidence complete |
| `DONE` | Reviewer/human acceptance recorded |
| `CANCELLED` | Human-approved reason |

Only the human or the accountable owner with explicit human confirmation may mark a
package `DONE`.

## Phase 2 global acceptance

Phase 2 is complete only when all are true:

- `project_staging`, `project_dw`, and `project_reporting` exist.
- Six dimensions and five facts exist with the documented grains.
- At least 100 dimension rows and 10,000 fact rows come from real sources.
- Fact rows use surrogate keys resolved from natural keys.
- Data-quality checks pass at the required severity.
- Both PDF reports exist and match stored evidence.
- SQL and ETL scripts are in Git.
- The GitHub repository link is recorded.
- All five members can read the shared warehouse.
- Weekly/manual automation works.
- No secrets or raw data are committed.
- No synthetic data exists.
- The human accepts `G7`.

## Documentation baseline acceptance (completed 2026-11-04)

**Status:** DONE via `H-001`. This checklist records the `G0` baseline at acceptance;
cloud resources were provisioned later under `G1` and are not part of the `G0`
checklist.

- [x] `AGENTS.md` and `Phase2/AGENTS.md` exist and agree.
- [x] `Phase2/README.md` and `Phase2/PROGRESS.md` are consistent.
- [x] Docs `00`-`12` exist and links resolve.
- [x] Dev plan files exist and agree on WP IDs.
- [x] Templates exist.
- [x] Folder README placeholders exist.
- [x] `.gitignore` blocks secrets, dumps, and raw data.
- [x] Root README and data docs reflect Phase 2.
- [x] DBML is updated or clearly marked historical.
- [x] Phase 1 guide has a supersession note.
- [x] No SQL, ETL code, workflow YAML, database object, or cloud resource existed at `G0`.
- [x] No secret or raw data is present.
- [x] The human can see the exact next action.

## Work-package acceptance summary

Detailed criteria are in `01_work_breakdown.md`. The summary below is the minimum
evidence set.

| WP | Minimum acceptance evidence |
|---|---|
| `WP-00` | Link check, file inventory, consistent status, no implementation |
| `WP-01` | G1 checklist, resource names (not secrets), authorization record |
| `WP-02` | CI write proof, storage read/write proof, read-only write rejection |
| `WP-03` | Source validation records, georeferencing proof, capacity estimate |
| `WP-04` | Staging DDL, real sample load, exact reconciliation, idempotent rerun |
| `WP-05` | Six dimensions, `-1` seeds, 100+ real rows, dictionary/DBML match |
| `WP-06` | Core facts, 10,000+ rows, key mapping, reconciliation, idempotency |
| `WP-07` | Derived facts trace to real rows, approved thresholds, no synthetic rows |
| `WP-08` | Stored pass/fail results, critical-failure test, orphan/duplicate checks |
| `WP-09` | Two readable PDFs, counts match DB, attribution, reproducibility |
| `WP-10` | Required views, real query results, read-only access, documented grain |
| `WP-11` | Weekly/manual workflow, DQ gate, artifacts, no secret in logs |
| `WP-12` | Fresh end-to-end run, rubric audit, team access, human acceptance |

## Evidence format

Record in `PROGRESS.md` or the PR:

```text
Work package:
Status:
Files changed:
Commands/checks run:
Results (counts, pass/fail):
Data/source evidence:
Decisions:
Blockers:
Next step:
Reviewer:
```

A claim without a command, stored result, or artifact is not evidence.

## Data and quality acceptance

### Real-data audit

- Every used source has a URL, license, fetch time, hash, and manifest row.
- No generator, fixture, or seed creates fake business rows.
- Small fixtures, if used for parser tests, are clearly marked test-only and are not
  loaded into `project_dw`.
- Derived facts trace to real input rows.
- An empty result is reported as empty, not filled with synthetic data.

### Key acceptance

- Natural-key uniqueness passes.
- Unknown members exist in every dimension.
- No fact orphan exists for a required dimension.
- Unknown `-1` usage is counted and explained.
- Role-playing keys are distinct where required.
- A rerun does not duplicate facts.

### Count acceptance

- `SELECT COUNT(*)` evidence for each dimension and fact.
- Dimension total >= 100.
- Fact total >= 10,000.
- Staging accepted/rejected/duplicate counts reconcile exactly.
- The report shows the same counts as the database.

### Quality acceptance

- Every `CRITICAL` check passes on the accepted run or has a human-approved exception.
- Every `WARNING` is visible in the report.
- Critical failure fails CI.
- No threshold change is hidden.
- The check catalog IDs match the report.

## Report acceptance

The Data Cleaning Report must include:

- Run metadata and sources.
- Before/after counts.
- Cleaning rules.
- Rejects and reasons.
- Georeferencing/unit notes.
- Gaps and limitations.
- Attribution.
- Reproduction steps.

The Data Quality Report must include:

- Executive summary by severity.
- Check table with observed/expected values.
- Dimension/fact counts.
- Orphan and duplicate results.
- Staging-to-fact reconciliation.
- Timeliness and source gaps.
- Capacity usage.
- Recommended actions.

A PDF that only contains screenshots or unsupported prose is not acceptable.

## Access acceptance

- The CI role can write.
- The read-only role can `SELECT`.
- The read-only role is rejected on `INSERT`, `UPDATE`, `DELETE`, `CREATE`, and
  `DROP`.
- A second member can query a reporting view with their own credentials.
- No connection string or password appears in the repository or logs.

## Automation acceptance

- Manual dispatch works.
- Weekly schedule is configured; no minutes-based polling.
- Concurrency prevents overlapping production runs.
- Timeout is bounded.
- Critical DQ fails the job.
- Reports upload as artifacts.
- The job summary contains counts and the run ID.
- A failed run leaves the previous trusted state intact.

## Capacity acceptance

- Database usage is below 700 MB at acceptance, with an explanation if higher.
- Object storage is below 3.5 GB, with an explanation if higher.
- Compute and egress remain within the free tier.
- The raw archive has a retention note.
- No paid upgrade was used to pass acceptance.

## Documentation acceptance

- Canonical docs agree on WP IDs, gates, sources, model, and cadence.
- Data dictionary matches DDL.
- DBML matches DDL or is marked historical.
- Root README points to Phase 2.
- Phase 1 guide marks superseded claims.
- Relative links resolve.
- No placeholder person is presented as a real assigned member.

## Not done if

A package is not done if any of these are true:

- It works only on the author's machine.
- It uses a local database or Docker.
- It needs a secret pasted in chat.
- It creates synthetic rows.
- It hides a critical DQ failure.
- It changes a threshold after seeing results without approval.
- It leaves duplicate facts after a rerun.
- It has no reconciliation.
- It has no data dictionary update.
- It reports a count not present in the database.
- It exceeds the free-tier budget.
- It edits Phase 1.
- It marks a gate done without human approval.

## Acceptance record

For each accepted package, record:

| Field | Value |
|---|---|
| Work package | |
| Accepted by | |
| Acceptance date | |
| Evidence link | |
| Gate closed | |
| Exceptions | |
| Next work package | |
