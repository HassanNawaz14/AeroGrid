# Operations, Access, and Security

<!-- AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->
**Current administrator-declared acceptance (2026-11-13):** The requester states they hold project-administrator authority and explicitly accepts G5, G6, and G7. This documents their decision, **not** independent confirmation of a full G7 end-to-end replay, all five members testing reader access, or finished WP-11/WP-12 technical evidence. Those proof items remain listed separately in the [Final gate record](FINAL_ACCEPTANCE_G5_G6_G7_2026-11-13.md).

**Member E deployment facts:** WP-07 through WP-10 are merged: 27,479 source-linked tracking facts, 178 journeys, 3,658 real 2D grid cells, 1,754 occupancy facts; 32 persisted DQ results (29 PASS, 3 WARN, 0 FAIL); 10 reporting views; both improved PDFs. The deployed encounter and restriction fact counts are zero, with documented coverage and algorithm limitations.
<!-- /AEROGRID_ADMIN_CLOSEOUT_2026_11_13 -->

## Status

This document defines the accepted operating model. The Neon project, database,
bucket, `aerogrid_etl` and `aerogrid_reader` roles, GitHub `warehouse` environment,
and required secrets exist. `WP-02` proved CI writer, storage, and read-only access
(run `42276737288`), and `WP-03` source validation merged in PR #5 (`f9087f4`); `G2`
closed on 2026-11-08. Role privileges are centralized in
[`../sql/00_grants.sql`](../sql/00_grants.sql); the owner run is tracked as `H-011`.
The production workflow remains pending. The human owns all account and secret
actions.

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
- `aerogrid_etl` and `aerogrid_reader` roles: created; the reader was recreated from SQL
  on 2026-11-07 without `neon_superuser`. All schema/table/sequence grants and their
  default privileges live in [`../sql/00_grants.sql`](../sql/00_grants.sql); the owner
  run is `H-011`.
- GitHub `warehouse` environment and six required secrets: created.
- `main` protection: confirmed.
- Member invitations: sent.
- Platform validation workflow `.github/workflows/platform-validation.yml` and probe
  script `.github/scripts/platform_probe.py`: executed 2026-11-07 with `PASS`; result
  recorded in [`../PROGRESS.md`](../PROGRESS.md).
- Production workflow YAML: not created.

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
`H-007`. On 2026-11-09 the repository ruleset `main-protection` (id `26542485`) is
active: it requires one approving review and blocks non-fast-forward pushes. The
classic branch-protection API still returns `Branch not protected`, so check
**Settings → Rules** rather than **Settings → Branches**.

1. Create or join the Neon organization.
2. Create a project named `AeroGrid-DW` in `aws-us-east-2` with Object storage enabled.
3. Confirm or create the database and a private raw bucket named `aerogrid-raw` on the
   `production` branch.
4. Create the `aerogrid_etl` role early enough to build `DATABASE_URL`; create
   `aerogrid_reader` for members. Run `Phase2/sql/00_grants.sql` once as the owner,
   and again after any schema or object-class change.
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

## Role privileges and grants

Grant changes are human-only. The single source of truth is
[`../sql/00_grants.sql`](../sql/00_grants.sql), run whole as `neondb_owner` in the
Neon SQL Editor. It is idempotent, a grants-only script: it creates no tables, changes
no rows, and contains an explicit `REVOKE` so `aerogrid_reader` can never write.

| Role | Database | Schemas | Tables and views | Sequences |
|---|---|---|---|---|
| `aerogrid_etl` | `CONNECT` | `USAGE, CREATE` on `project_staging`, `project_dw`, `project_reporting` | `SELECT, INSERT, UPDATE, DELETE, TRUNCATE` (current and future) | `USAGE, SELECT` (current and future) |
| `aerogrid_reader` | `CONNECT` | `USAGE` only | `SELECT` only (current and future) | none |

Run it again when any of these changes:

- A work package adds a schema or a new object class.
- A verifier or workflow reports a missing privilege.
- A member reports a read error.

The self-check ends with a table-level pair: `reader can select every existing table`
and `reader cannot write any existing table`. A `false` on the first row means the
reader cannot read a table that exists right now.

Ownership decides who can fix that. `neondb_owner` can grant only on objects it owns, so
a table created by `aerogrid_etl` is not covered by this script — confirmed on
2026-11-08, when all 10 staging tables showed `reader_select = false` after the owner
script ran. The repair path is the ETL bootstrap
[`../sql/00_schemas.sql`](../sql/00_schemas.sql), which runs as `aerogrid_etl` and, for
all three schemas:

1. grants `SELECT` on every table it owns that already exists;
2. sets `ALTER DEFAULT PRIVILEGES ... GRANT SELECT ON TABLES TO aerogrid_reader` so
   later ETL-created tables are readable without another manual step.

Run the WP-04 verifier after any ETL-applied DDL, then rerun `00_grants.sql` to confirm
the table-level row flips to `true`. If a future package applies DDL as a third role,
that package's bootstrap must grant the reader itself.

The WP-04 verifier now checks `USAGE` and `CREATE` on `project_staging` immediately
after connecting and exits with the exact missing privilege and this remediation
instead of a raw `InsufficientPrivilege` deep in the DDL step.

### Member read-access check

Connect with the shared read-only string (or open a Neon SQL Editor session using the
read-only role) and run:

```sql
SELECT current_user;                                                    -- aerogrid_reader
SELECT has_schema_privilege('project_staging', 'USAGE');                -- true
SELECT has_schema_privilege('project_dw', 'USAGE');                     -- true
SELECT count(*) FROM information_schema.tables
WHERE table_schema IN ('project_staging', 'project_dw', 'project_reporting');
```

Then confirm write access is refused, using any staging table that exists (for example
`project_staging.source_manifest` after the WP-04 DDL is applied):

```sql
SELECT has_table_privilege('project_staging.source_manifest', 'INSERT'); -- false
```

If the probe table exists in staging, `SELECT count(*) FROM
project_staging.wp02_read_probe;` proves real read access. A `false` where `true` is
expected, or an error, is an access defect: report the message text (never the
connection string) to Member A.

| Symptom | Cause | Fix |
|---|---|---|
| `permission denied for schema project_staging` as `aerogrid_etl` | `00_grants.sql` not run, or run before the schema existed | Rerun the script as owner; confirm every self-check row is `true` |
| `reader can select every existing table` is `false` | The tables are owned by `aerogrid_etl`; `neondb_owner` cannot grant on another role's tables | Run the WP-04 verifier or any ETL bootstrap run of `00_schemas.sql`, then rerun `00_grants.sql` to confirm |
| `permission denied for table ...` as `aerogrid_etl` | Object created by another role and no default privilege covers it | Rerun `00_grants.sql`; add the matching `ALTER DEFAULT PRIVILEGES` to that work package's bootstrap |
| Reader `INSERT` succeeds | The role holds `neon_superuser`, which overrides grants | Follow [the reader remediation](#if-the-reader-check-reports-that-insert-succeeded); grants alone cannot fix it |
| `password authentication failed` | Role password rotated or mistyped | Human resets it in the Neon Console and re-shares the string privately; do not paste it |
| `relation ... does not exist` | The object belongs to a later work package | Not an access defect; wait for that package |
| `SSL connection is required` | Connection string lacks TLS | Append `sslmode=require`; never disable TLS |

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

Current workflow:

| Workflow | Trigger | Purpose |
|---|---|---|
| `platform-validation.yml` | Manual dispatch only | `WP-02` proof of database, raw-bucket, and read-only access |

Planned workflows:

| Workflow | Trigger | Purpose |
|---|---|---|
| `warehouse.yml` | Weekly schedule + manual dispatch | Full/incremental ETL, DQ, reports |
| `ci.yml` | Pull request / push to feature branch | Lint, unit tests, SQL static checks |
| `docs.yml` (optional) | Documentation change | Link and formatting checks |

Planned workflow properties:

- `runs-on: ubuntu-latest`
- Python 3.12
- No Docker or service containers
- `timeout-minutes` bounded
- `concurrency` prevents overlapping warehouse runs
- Secrets from the `warehouse` environment
- Upload reports as artifacts
- Fail on critical DQ

Only the `WP-02` validation workflow exists so far; production workflows remain
planned.

## Runbook: WP-02 platform validation

The workflow `.github/workflows/platform-validation.yml` runs
`.github/scripts/platform_probe.py` on manual dispatch. It uses the `warehouse`
environment and prints only pass/fail evidence; connection strings and credentials
are redacted.

What it proves:

| Check | Proof |
|---|---|
| Writer connection | CI connects as `aerogrid_etl` over TLS; server, database, and search path recorded |
| Cold start | First and warm connection timings recorded |
| Database write | Temporary table create, insert, select, and drop |
| Statement timeout | A slow query is cancelled by a 1 s timeout |
| Schemas | Presence of `project_staging`, `project_dw`, `project_reporting` and writer privileges |
| Raw bucket | Small marker written, read back by hash, then deleted; bucket object count and size |
| Read-only role | Optional; runs only when `READONLY_DATABASE_URL` is set |

The read-only role is **not** added to GitHub secrets by default because member
credentials are shared privately. If the run reports `reader connection: SKIP`, prove
it manually.

### Recorded result

Run [42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288)
on 2026-11-07 returned `PASS`: 22 pass, 1 warn, 0 fail, 0 skip. It proved the writer
connection over TLS, temporary-table write, statement timeout, database size, bucket
put/head/read-back/delete, warm connection, free-tier headroom, and that
`aerogrid_reader` is rejected with SQLSTATE `42501` on insert, update, delete, create
table, and create schema while still selecting. The one warning is the absent
`project_dw` and `project_reporting` schemas, which `WP-04`/`WP-05` create. Neon
terminates client TLS at its proxy, so `pg_stat_ssl` cannot show TLS on the compute; an
established `sslmode=require` connection is the accepted encryption proof.

Earlier runs on 2026-11-06 were `PARTIAL` and then `FAIL`; the failure exposed
`aerogrid_reader` inheriting `neon_superuser` (see `B-007` in
[`../PROGRESS.md`](../PROGRESS.md)). The role was replaced and the rerun passed.

### Manual read-only proof

The writer needs a readable object. If the run reports that
`project_staging.wp02_read_probe` is absent, a human runs this once in the Neon SQL
Editor as the project owner:

```sql
CREATE SCHEMA IF NOT EXISTS project_staging;

CREATE TABLE IF NOT EXISTS project_staging.wp02_read_probe (
    probe_id integer PRIMARY KEY,
    note text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO project_staging.wp02_read_probe (probe_id, note)
VALUES (1, 'WP-02 read-only access proof')
ON CONFLICT (probe_id) DO NOTHING;

GRANT USAGE ON SCHEMA project_staging TO aerogrid_reader;
GRANT SELECT ON project_staging.wp02_read_probe TO aerogrid_reader;
```

If you are already connected as the project owner, you do not need a second
connection: assume the role for the checks instead. Role membership is required the
first time; `REVOKE` it afterwards if you want the owner to stop being a member.

```sql
GRANT aerogrid_reader TO neondb_owner;  -- owner only; one-time, reversible
SET ROLE aerogrid_reader;
SELECT current_user;                    -- must print aerogrid_reader
```

Then run each block, and finish with `RESET ROLE;`. Otherwise connect with the
`aerogrid_reader` connection string and run the same blocks:

```sql
-- Expected: one row with count 1.
SELECT count(*) FROM project_staging.wp02_read_probe;

-- Expected: ERROR: permission denied for table wp02_read_probe (SQLSTATE 42501).
INSERT INTO project_staging.wp02_read_probe (probe_id, note)
VALUES (999, 'should fail');

-- Expected: ERROR: permission denied for schema project_staging (SQLSTATE 42501).
CREATE TABLE project_staging.wp02_reader_should_fail (probe_id integer);
```

Record only the pass/fail result in `PROGRESS.md`. Never paste the connection string,
host password, or query output containing credentials.

### If the reader check reports that `INSERT` succeeded

`aerogrid_reader` must hold `SELECT` only; a write privilege means the shared warehouse
is not read-only for the team. Inspect the grants and memberships first:

```sql
SELECT pg_get_userbyid(relowner) AS table_owner, relacl
FROM pg_class WHERE oid = 'project_staging.wp02_read_probe'::regclass;

SELECT pg_get_userbyid(nspowner) AS schema_owner, nspacl
FROM pg_namespace WHERE nspname = 'project_staging';

SELECT m.rolname AS member_of
FROM pg_auth_members am
JOIN pg_roles m ON m.oid = am.roleid
WHERE am.member = 'aerogrid_reader'::regrole;
```

A correct table ACL shows only `aerogrid_reader=r/...`. If the membership query lists
`neon_superuser`, the role inherits `pg_write_all_data` across the whole project, and no
object-level grant can override it. That membership cannot be removed by
`neondb_owner`: it lacks ADMIN on `neon_superuser`, and PostgreSQL also refuses
`DROP ROLE` and `ALTER ROLE` on a role the platform created. In that case the role must
be replaced:

1. Neon Console → **Roles** → `aerogrid_reader` → **Delete**.
2. Recreate it from SQL. Roles created by SQL in this project carry no memberships,
   unlike platform-created roles:

```sql
DELETE FROM project_staging.wp02_read_probe WHERE probe_id = 999;
CREATE ROLE aerogrid_reader WITH LOGIN;
GRANT USAGE ON SCHEMA project_staging TO aerogrid_reader;
GRANT SELECT ON project_staging.wp02_read_probe TO aerogrid_reader;
```

3. Reset the role password in the console and update the `READONLY_DATABASE_URL`
   environment secret.

If the membership query is empty and the reader is neither the table nor schema owner,
the write instead comes from a grant; reduce it to the intended minimum:

```sql
REVOKE ALL ON project_staging.wp02_read_probe FROM aerogrid_reader;
GRANT SELECT ON project_staging.wp02_read_probe TO aerogrid_reader;
REVOKE ALL ON SCHEMA project_staging FROM aerogrid_reader;
GRANT USAGE ON SCHEMA project_staging TO aerogrid_reader;
```

Rerun the validation workflow afterwards; the insert must be rejected with SQLSTATE
`42501`.

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
- The `00_grants.sql` self-check returns `ok = true` for every role row, including
  `reader can select every existing table` and `reader cannot write any existing table`.
- A reporting view returns rows for a known real period.
- No secret appears in the repository or logs.
