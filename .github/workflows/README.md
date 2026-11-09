# GitHub Actions Workflows

Automation is added only by an authorized work package. `WP-02` owns the platform
validation workflow; `WP-04` owns the staging verification workflow; `WP-05` owns the
dimension verification workflow; `WP-06` adds the fact verification workflow (in its
package PR); `WP-11` owns the production workflow and CI checks.

## Current workflows

| File | Trigger | Purpose |
|---|---|---|
| `platform-validation.yml` | Manual dispatch | `WP-02` proof of database, raw-bucket, and read-only role access |
| `wp04-staging-verify.yml` | Manual dispatch | `WP-04` proof of idempotent staging DDL, row counts, and an optional real-sample load/rerun inside a rolled-back transaction |
| `wp05-dimensions-verify.yml` | Manual dispatch | `WP-05` proof of the six dimensions, `-1` unknown rows, seeds, and reader SELECT |

The probe script lives in [`../scripts/platform_probe.py`](../scripts/platform_probe.py).
It prints only non-secret evidence and redacts connection strings. The verifiers live
in [`../../Phase2/etl/verify_wp04_staging.py`](../../Phase2/etl/verify_wp04_staging.py)
and [`../../Phase2/etl/verify_wp05_dimensions.py`](../../Phase2/etl/verify_wp05_dimensions.py).

## `WP-06` workflow note

GitHub does not let anyone manually dispatch a `workflow_dispatch` workflow until the
file exists on the default branch. `WP-06` therefore adds a temporary branch-scoped
`push` trigger while the package branch is open, removes it before merge, and runs the
manual workflow from `main` afterwards. The `WP-06` verification must run in the
protected `warehouse` environment and must leave no rows behind on failure.

## Approval during the `D-024` window

These workflows run in the protected `warehouse` environment and need an approval.
During the delegated window (`D-024`, `2026-11-09` → `G4`), Member C (`HarveyWebbs`)
approves the dimension and fact verification runs. Member D (`ahmadazad-dev`) is not
on the reviewer list, because the human has not changed the environment and `D-024`
does not require it; Member C or Member B (`Hamid4325`) dispatches and approves the
`WP-06` runs instead. Member D still owns the `WP-06` code. Writes stay CI-only and
rollback-only. The human restores the reviewer list and re-enables *Prevent
self-review* after `G4`; see
[`../../Phase2/docs/10_human_operating_manual.md`](../../Phase2/docs/10_human_operating_manual.md).

## Planned workflows

| File | Trigger | Purpose |
|---|---|---|
| `warehouse.yml` | Weekly schedule + manual dispatch | ETL, DQ, reports |
| `ci.yml` | Pull request / feature branch | Lint, tests, SQL checks |
| `docs.yml` (optional) | Documentation change | Link/format checks |

## Rules

- Weekly or manual only; no five-minute polling.
- No Docker or service containers.
- Use the protected `warehouse` environment for secrets.
- Do not print secrets, connection strings, or raw data.
- Fail the job on critical DQ.
- Upload PDFs as artifacts.
- Keep `concurrency` and `timeout-minutes` bounded.
- Free-tier usage only.
- Do not create workflow YAML outside an authorized work package.
- Keep verifier loads inside a transaction that is rolled back; CI must not leave
  rows behind.
