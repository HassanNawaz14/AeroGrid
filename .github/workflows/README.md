# GitHub Actions Workflows

Automation is added only by an authorized work package. `WP-02` owns the platform
validation workflow; `WP-04` owns the staging verification workflow; `WP-11` owns
the production workflow and CI checks.

## Current workflows

| File | Trigger | Purpose |
|---|---|---|
| `platform-validation.yml` | Manual dispatch | `WP-02` proof of database, raw-bucket, and read-only role access |
| `wp04-staging-verify.yml` | Manual dispatch | `WP-04` proof of idempotent staging DDL, row counts, and an optional real-sample load/rerun inside a rolled-back transaction |

The probe script lives in [`../scripts/platform_probe.py`](../scripts/platform_probe.py).
It prints only non-secret evidence and redacts connection strings. The `WP-04`
verifier lives in [`../../Phase2/etl/verify_wp04_staging.py`](../../Phase2/etl/verify_wp04_staging.py).

## Approval during the `D-023` window

`wp04-staging-verify.yml` runs in the protected `warehouse` environment and needs
an approval. During the delegated closeout window (`D-023`, `2026-11-08` → `G3`),
Member B (`Hamid4325`) and Member C (`HarveyWebbs`) are added as required reviewers
and may approve their own runs. Writes stay CI-only and rollback-only. The human
restores the reviewer list and re-enables *Prevent self-review* at `G3`; see
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
