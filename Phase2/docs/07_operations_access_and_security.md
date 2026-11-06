# Operations, Access, and Security

## Status

This document defines the accepted operating model. The Neon project, database,
bucket, `aerogrid_etl` and `aerogrid_reader` roles, GitHub `warehouse` environment,
and required secrets exist. Schema grants, ETL, and workflow YAML remain pending. The
human owns all account and secret actions.

## Operating model

| Function | Owner | Channel |
|---|---|---|
| Cloud account and billing state | Human | Neon/GitHub UI |
| Warehouse provisioning | Human + Member A | Neon UI |
| Schema and data loads | GitHub Actions | CI with write secret |
| Team query access | Human + Member A | Read-only SQL role |
| Raw archive | GitHub Actions | Object storage with write credential |
| Progress and approvals | Member A | `PROGRESS.md` |
| Incident escalation | Any member | Human action queue |

## Access matrix

| Principal | Database | Object storage | GitHub | Notes |
|---|---|---|---|---|
| Human owner | Admin | Admin | Admin | Creates resources and secrets |
| Member A | Read; write only via CI | Read/write via CI | Write via PR | Platform coordinator |
| Members B-E | Read-only | Read-only if needed | Write via PR | Cannot modify shared data |
| CI workflow | Write | Read/write | Workflow token | Only automated writer |
| Public | None | None | Read code | Repo is public for free Actions |

## Required resources

### Neon

- One project named `AeroGrid-DW` in `aws-us-east-2` (Ohio).
- One primary database named `neondb` for the shared warehouse.
- One private object-storage bucket named `aerogrid-raw` for raw archives.
- One write credential for CI.
- One read-only storage credential for member access if needed.
- Database roles:
  - `aerogrid_etl`: schema/table write privileges for CI.
  - `aerogrid_reader`: `CONNECT`, schema `USAGE`, and `SELECT` only.
- No paid plan, branch, or add-on.

### GitHub

- Repository: `https://github.com/HassanNawaz14/AeroGrid`
- Public visibility required for free standard runners unless the human accepts the
  private-repository minute budget.
- Environment: `warehouse`.
- Protected `main` branch.
- Required reviewers for the `warehouse` environment if available.
- Short-lived feature branches and PRs.

### Provisioning status (2026-11-06)

- Neon project `AeroGrid-DW`, branch `production`, database `neondb`, bucket
  `aerogrid-raw`: created.
- `aerogrid_etl` and `aerogrid_reader` roles: created; schema/table grants follow
  `WP-04`/`WP-05`/`WP-10`.
- GitHub `warehouse` environment and six required secrets: created.
- `main` protection: confirmed.
- Member invitations: sent.
- Workflow YAML: not created.

## Secret and variable names

The human creates these in the GitHub `warehouse` environment. Agents must never ask
for the values or print them.

### Required secrets

| Name | Purpose |
|---|---|
| `DATABASE_URL` | Write connection string for `aerogrid_etl` |
| `NEON_S3_ENDPOINT` | S3-compatible endpoint for the project branch |
| `NEON_S3_REGION` | Storage region |
| `NEON_S3_BUCKET` | Raw archive bucket |
| `NEON_S3_ACCESS_KEY_ID` | CI storage credential access key |
| `NEON_S3_SECRET_ACCESS_KEY` | CI storage credential secret |

### Optional secrets/variables

| Name | Purpose |
|---|---|
| `OPENSKY_CLIENT_ID` | Optional authenticated OpenSky access |
| `OPENSKY_CLIENT_SECRET` | Optional authenticated OpenSky secret |
| `SOURCE_TIMEZONE` | Optional source timezone override; default UTC |
| `REPORT_PUBLISH_MODE` | `artifact` or `commit`; default `artifact` |

### Member-only values

Do not put these in GitHub:

- `READONLY_DATABASE_URL` for members.
- Read-only object-storage credentials, if raw access is required.

Share those through a private team channel approved by the human, never through Git or
chat with an agent.

## Human setup sequence

The human performs these steps. Member A may provide checklists but must not execute
account actions. Steps 1-10 were completed by 2026-11-04; step 11 was completed via
`H-007`.

1. Create or join the Neon organization.
2. Create a project named `AeroGrid-DW` in `aws-us-east-2` with Object storage enabled.
3. Confirm or create the database and a private raw bucket named `aerogrid-raw` on the
   `production` branch.
4. Create the `aerogrid_etl` role early enough to build `DATABASE_URL`; grant
   schema/table privileges after `WP-04`/`WP-05`. Create `aerogrid_reader` after the
   schema and reporting views exist.
5. Create the CI storage credential with `storage:read` and `storage:write`.
6. Create a member storage credential with `storage:read` only, if needed.
7. Invite the other four members to the Neon organization.
8. Create the GitHub `warehouse` environment and add the required secrets.
9. Enable branch protection on `main`.
10. Confirm data licenses and optional OpenSky terms.
11. Set `implementation_authorized: YES` in `PROGRESS.md` only after the above.

If a step requires a card, paid plan, or terms acceptance, stop and record the
decision. Do not proceed silently.

## Read-only member access

Member access is through a PostgreSQL connection string and any SQL client, such as
DBeaver, pgAdmin, or Python. No local PostgreSQL server is required.

The read-only role must:

- Have `CONNECT` on the database.
- Have `USAGE` on `project_dw` and `project_reporting`.
- Have `SELECT` on all current and future tables/views in those schemas.
- Have no write, create, delete, or role-management privileges.
- Be tested by one `SELECT` against each reporting view.

The human shares the connection string privately. Do not commit it, paste it into an
issue, or send it to an agent.

## Data handling

| Data | Storage | Git | Access |
|---|---|---|---|
| Raw ADS-B/UAS/weather/FAA archives | Object storage | Never | CI + read-only members |
| Staging rows | PostgreSQL | Never | CI writer; read-only role if needed |
| Warehouse facts/dimensions | PostgreSQL | Never | All members read-only |
| SQL, ETL, docs | Git | Yes | Public |
| Secrets | GitHub/Neon secret store | Never | Human/CI only |
| Reports | Git artifact or `Phase2/reports/` | Yes, if no sensitive data | Public |

No personal data is intentionally collected. Aircraft identifiers and UAS serials are
treated as public research data. If a source contains unexpected personal data, stop
and ask the human.

## License and attribution operations

- Keep source license metadata in the source manifest.
- Keep a human-readable attribution section in the repository and reports.
- Do not redistribute raw data if the terms prohibit it.
- Do not upload raw data to a public bucket.
- OpenSky raw payloads are not committed; use them only as permitted.
- If a license changes, stop and ask the human.

## Free-tier quota management

| Resource | Free limit | Warning threshold | Action |
|---|---|---|---|
| PostgreSQL storage | 1 GB/project | 700 MB | Reduce load window or move raw out; ask human |
| Object storage | 5 GB/project | 3.5 GB | Review retention; ask human |
| Compute | 100 CU-hours/month | 60 hours | Reduce runs or query load |
| Egress | 5 GB/project | 3.5 GB | Query DB; share original URLs |
| GitHub Actions | Free for public repo | - | No five-minute polling |

Do not upgrade a plan to solve a quota problem. Stop and escalate.

## Neon operational notes

- Scale-to-zero after inactivity is acceptable; cold start is not a failure.
- A weekly run keeps the project active and within the intended cadence.
- Free-plan retention and restore features are limited; do not treat Neon as a
  long-term backup.
- The raw archive is the durable source copy.
- Do not delete branches, projects, or buckets from an agent session.

## GitHub Actions operating model

Planned workflows:

| Workflow | Trigger | Purpose |
|---|---|---|
| `warehouse.yml` | Weekly schedule + manual dispatch | Full/incremental ETL, DQ, reports |
| `ci.yml` | Pull request / push to feature branch | Lint, unit tests, SQL static checks |
| `docs.yml` (optional) | Documentation change | Link and formatting checks |

Planned workflow properties:

- `runs-on: ubuntu-latest`
- Python 3.11
- No Docker or service containers
- `timeout-minutes` bounded
- `concurrency` prevents overlapping warehouse runs
- Secrets from the `warehouse` environment
- Upload reports as artifacts
- Fail on critical DQ

No workflow YAML is implemented in this session.

## Runbook: manual refresh

After authorization, a human or authorized maintainer:

1. Opens GitHub Actions.
2. Selects `warehouse`.
3. Chooses `Run workflow`.
4. Selects `mode = weekly` or `initial`.
5. Confirms the source window.
6. Reviews the run summary and DQ status.
7. Downloads the PDF artifacts.
8. Records any failure in `PROGRESS.md`.

Agents may prepare the workflow and documentation but must not trigger a production
run unless the human explicitly authorizes it.

## Runbook: read-only query

1. Connect with the member read-only connection string.
2. Set the session to read-only if the client supports it.
3. Query `project_reporting` views first.
4. Do not create tables or run DDL.
5. If a query is slow, report it; do not add indexes to production without a work
   package and human approval.

## Incident response

| Incident | Immediate action |
|---|---|
| Secret exposed | Human rotates the secret in Neon/GitHub; do not paste it in chat; record incident |
| CI fails on required source | Keep previous trusted data; inspect source; ask human if persistent |
| Critical DQ failure | Do not publish trusted data; review report; ask human if business rule unclear |
| Database near quota | Stop loads; ask human for retention/load-window decision |
| Object storage near quota | Stop uploads; ask human for retention decision |
| Accidental destructive SQL | Stop; do not rerun; ask human to use Neon restore if appropriate |
| Corrupt fact load | Stop; preserve logs; fix parser; reload idempotently after review |
| Repository visibility change needed | Human-only action; record decision |

## Rollback

- The pipeline must be idempotent.
- A failed run should not replace the last trusted data.
- For a bad load, prefer a scoped reload from raw after fixing the parser.
- Destructive rollback (drop/truncate) requires a human decision.
- Neon instant restore is limited on the free plan; do not assume unlimited recovery.

## Security rules for agents

- Never print, read, or request secret values.
- Never create `.env` files with real credentials.
- Never use `git add -A` without inspecting the diff.
- Never commit raw data, database dumps, or large binaries.
- Never disable TLS verification in production code.
- Never add an unlicensed dependency.
- Never make a repository private/public change.
- Never change branch protection or invite members.
- Never use a shared write credential from a local machine.

## Access acceptance checks

`WP-02` and `WP-11` must demonstrate:

- CI can connect with the write role.
- CI can read/write the raw bucket.
- A member can connect with the read-only role.
- The read-only role cannot insert, update, delete, create, or drop.
- A reporting view returns rows for a known real period.
- No secret appears in the repository or logs.
