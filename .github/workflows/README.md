# GitHub Actions Workflows

Automation is added only by an authorized work package. `WP-02` owns the platform
validation workflow; `WP-04` owns the staging verification workflow; `WP-05` owns the
dimension verification workflow; `WP-06` delivered the fact verification workflow;
`WP-11` owns the production workflow and CI checks.

## Current workflows

| File | Trigger | Purpose |
|---|---|---|
| `platform-validation.yml` | Manual dispatch | `WP-02` proof of database, raw-bucket, and read-only role access |
| `wp04-staging-verify.yml` | Manual dispatch | `WP-04` proof of idempotent staging DDL, row counts, and an optional real-sample load/rerun inside a rolled-back transaction |
| `wp05-dimensions-verify.yml` | Manual dispatch | `WP-05` proof of the six dimensions, `-1` unknown rows, seeds, and reader SELECT |
| `wp06-facts-verify.yml` | Manual dispatch | `WP-06` proof of the real dimension seed + `01_facts.sql` DDL, real Tartan S3 fetch + SHA-256 check, staging-to-tracking reconciliation, journey segmentation, zero orphans, and idempotent persistence |

The probe script lives in [`../scripts/platform_probe.py`](../scripts/platform_probe.py).
It prints only non-secret evidence and redacts connection strings. The verifiers live
in [`../../Phase2/etl/verify_wp04_staging.py`](../../Phase2/etl/verify_wp04_staging.py),
[`../../Phase2/etl/verify_wp05_dimensions.py`](../../Phase2/etl/verify_wp05_dimensions.py),
and [`../../Phase2/etl/verify_wp06_facts.py`](../../Phase2/etl/verify_wp06_facts.py).

## `WP-06` workflow note

GitHub does not let anyone manually dispatch a `workflow_dispatch` workflow until the
file exists on the default branch. The merged `WP-06` workflow is now manual-dispatch
only; the temporary branch-scoped `push` trigger used during the package PR has been
removed. Run it from `main` (or dispatch it against a branch ref) in the protected
`warehouse` environment. The `WP-06` verification must leave no rows behind on
failure.

## Approval after the `D-024` window

These workflows run in the protected `warehouse` environment and need an approval.
The `D-024` delegated window closed when `G4` was recorded on 2026-11-11. WP-05 run
[42689267328](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42689267328) and
WP-06 run [42887782411](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42887782411)
both passed; the temporary reviewer arrangement should now be restored to the normal
protected-environment settings (*Prevent self-review* re-enabled) as described in
[`../../Phase2/docs/10_human_operating_manual.md`](../../Phase2/docs/10_human_operating_manual.md).
Writes stay CI-only and rollback-only.

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
- Keep non-acceptance verifier runs (`WP-04`, `--dry-run`) and failed `WP-06` runs inside transactions that roll back; `WP-06` commits persistent facts only after all assertions pass.
