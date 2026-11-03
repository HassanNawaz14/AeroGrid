# GitHub Actions Workflows

This directory is intentionally empty of workflow YAML. Automation will be added only
after `G1` is cleared and the CI work package is authorized.

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
- Do not create workflow YAML before authorization.
