# GitHub Actions Workflows

Automation is added only by an authorized work package. `WP-02` owns the platform
validation workflow; `WP-04` owns the staging verification workflow; `WP-05` owns the
dimension verification workflow; `WP-06` delivered the fact verification workflow;
`WP-11` owns the production workflow and CI checks. The Phase 3 workflows
(`wp-p3-*`) are listed below; `WP-P3-09` owns the packaging workflow.

## Current workflows

| File | Trigger | Purpose |
|---|---|---|
| `platform-validation.yml` | Manual dispatch | `WP-02` proof of database, raw-bucket, and read-only role access |
| `wp04-staging-verify.yml` | Manual dispatch | `WP-04` proof of idempotent staging DDL, row counts, and an optional real-sample load/rerun inside a rolled-back transaction |
| `wp05-dimensions-verify.yml` | Manual dispatch | `WP-05` proof of the six dimensions, `-1` unknown rows, seeds, and reader SELECT |
| `wp06-facts-verify.yml` | Manual dispatch | `WP-06` proof of the real dimension seed + `01_facts.sql` DDL, real Tartan S3 fetch + SHA-256 check, staging-to-tracking reconciliation, journey segmentation, zero orphans, and idempotent persistence |
| `wp11-ingest.yml` | Manual dispatch + Monday schedule | `WP-11` recurring ingestion: read-only `validate`, protected transactional `apply`, run summary artifact, and reader check (details below) |
| `ci.yml` | Pull request, push to `main`, manual | Unit tests and `compileall`; no `warehouse` environment and no secrets |
| `wp-p3-analytics-verify.yml` | Manual dispatch | `WP-P3-02/03` read-only run of the committed analytics and OLAP SQL through `aerogrid_reader`; uploads Markdown evidence |
| `wp-p3-gold-views.yml` | Manual dispatch | `WP-P3-04` gold views: `verify` rolls back; `apply` is `main`-only with `APPROVE_WP3_GOLD_VIEWS` in the `warehouse` environment |
| `wp-p3-05-indexes.yml` | Manual dispatch | `WP-P3-05` index measurement: `verify` rolls back; `apply` is `main`-only with `APPROVE_WP3_INDEXES` in the `warehouse` environment |
| `wp-p3-h3-scd2-eval.yml` | Manual dispatch | `WP-P3-H3` read-only SCD Type 2 evaluation probes through `aerogrid_reader` in the `warehouse` environment; uploads Markdown evidence; creates nothing |
| `wp-p3-09-package.yml` | Manual dispatch | `WP-P3-09` packages Phase 3 deliverables under `D3-008`; no database, no secrets, no `warehouse` environment (details below) |

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

## `WP-11` ingestion workflow

`wp11-ingest.yml` is the recurring ingestion path (`D-030`):

| Trigger | Mode | Notes |
|---|---|---|
| `workflow_dispatch` with `mode=verify` | Read-only fetch + parse | No secret, no database connection, no `environment` secret use |
| `workflow_dispatch` with `mode=apply` and `confirm=APPROVE_WP11_APPLY` | Transactional write | Only on `main`, `warehouse` environment, 35-minute timeout; a `CRITICAL` DQ failure rolls back |
| `schedule` (`0 6 * * 1`) | `verify` unless `WP11_SCHEDULE_APPLY_ENABLED=true` | Inert until the repository variable `WP11_SCHEDULE_ENABLED=true` exists |

The run summary is uploaded as the `wp11-summary` artifact on every run. A separate
`reader-check` job runs `platform_probe.py --mode reader` after a manual apply run.
Both schedule variables are repository variables, not secrets, and only a human can
create them.

## `WP-P3-09` packaging workflow

`wp-p3-09-package.yml` runs `Phase3/tests`, then
[`../../Phase3/scripts/package_artifacts.py`](../../Phase3/scripts/package_artifacts.py)
(`D3-015`). It reads committed files only and uploads two artifacts per run:

| Artifact | Contents |
|---|---|
| `phase3-release-bundle-<run_id>` | Deliverables under 10 MiB, `MANIFEST.json`, and the packaging record (`.md` and `.json`) |
| `phase3-release-oversize-<run_id>` | Deliverables of 10 MiB or more (never committed); absent when there are none |

The `strict` input makes the run fail while a required deliverable is missing; leave it
off until the BI files exist and turn it on for the final release run. A secret-pattern
hit, or an oversized file tracked by Git, always fails the run. The workflow file must
be on `main` before it can be dispatched (`H3-008`).

## Remaining planned workflow

None. `ci.yml` covers pull-request tests and compile checks; SQL checks run inside the
package verifiers because they need the `warehouse` environment.

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
