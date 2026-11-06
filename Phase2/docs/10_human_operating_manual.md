# Human Operating Manual

## Purpose

This guide is for the project owner and team members. It explains what the human must
do, what agents must not do, how to clear the gate, and how to operate the shared
warehouse without exposing secrets.

## How to use this repository

| Audience | Start here |
|---|---|
| New human reviewer | `Phase2/README.md`, then this file |
| New team member | `Phase2/README.md`, `08_team_work_division.md`, `07_operations_access_and_security.md` |
| Coding agent | `AGENTS.md`, `Phase2/AGENTS.md`, `09_agent_operating_manual.md` |
| Instructor/reviewer | `Phase2/README.md`, `Phase2/PROGRESS.md`, reports |

## Current state

- Phase 1 is complete and frozen.
- Phase 2 documentation and planning baseline is accepted (`G0`/`H-001`).
- Implementation is **authorized** (`H-007`, 2026-11-04).
- `G1` is closed; the current gate is `G2`.
- `WP-02` is `DONE` (accepted 2026-11-07; PR #3 merged); `WP-03` is `READY` and
  authorized.

## The one rule for secrets

Never paste a password, connection string, API key, token, or `.env` content into
chat. Put it directly in the GitHub `warehouse` environment or the Neon UI. If an
agent asks for a secret, refuse and correct the instruction.

## Human action queue

The canonical queue is in [`../PROGRESS.md`](../PROGRESS.md). Current status:

| ID | Action | Status |
|---|---|---|
| `H-001` | Review and approve the Phase 2 baseline documents | `DONE` |
| `H-002` | Record Members B-E names | Names recorded in [docs/08](08_team_work_division.md); formal closure deferred |
| `H-003` | Create Neon project `AeroGrid-DW` and raw bucket `aerogrid-raw` | `DONE` |
| `H-004` | Add GitHub environment secrets | `DONE` |
| `H-005` | Invite members and create read-only access | `DONE`; `aerogrid_reader` confirmed 2026-11-06 |
| `H-006` | Confirm licenses and optional OpenSky terms | `DONE` |
| `H-007` | Authorize implementation after G1 | `DONE` 2026-11-04 |
| `H-008` | Confirm handling of tracked legacy synthetic samples | `DONE` via `D-017` |
| `H-009` | Run the `WP-02` platform validation workflow and confirm read-only access | `DONE` 2026-11-07; run `42276737288` `PASS` after the reader role was replaced |

Project `AeroGrid-DW`, branch `br-royal-cherry-beij6hxw`, database `neondb`, bucket
`aerogrid-raw`, and the storage endpoint are recorded in
[`../PROGRESS.md`](../PROGRESS.md) → Neon resource record. The GitHub `warehouse`
environment and its six required secrets are in place; `main` is protected. `H-002`
remains deferred; the Member B-E names are recorded in
[docs/08_team_work_division.md](08_team_work_division.md).

`WP-02` and `WP-03` are authorized. `WP-02` is `DONE`; `WP-03` proceeds with Member B.
Do not start a later work package until its gate is recorded in `../PROGRESS.md`.

## Current action: `WP-03`, then close `G2`

`WP-02` is closed. Run
[42276737288](https://github.com/HassanNawaz14/AeroGrid/actions/runs/42276737288)
returned `PASS`: 22 pass, 1 warn, 0 fail, 0 skip, and PR #3 merged as `b6b76b9` on
2026-11-06. The writer connects over TLS and writes, the bucket round-trips a marker,
quotas and cold-start timings are recorded, and `aerogrid_reader` can select but is
rejected with SQLSTATE `42501` on insert, update, delete, create table, and create
schema. The one warning is the absent `project_dw` and `project_reporting` schemas,
which `WP-04`/`WP-05` create.

What remains on `G2` is `WP-03` source validation, owned by Member B (`B-004`,
TartanAviation georeferencing is the first task):

1. Member B runs `WP-03` and records its evidence in [`../PROGRESS.md`](../PROGRESS.md).
2. HassanNawaz14 closes `G2` once both `WP-02` and `WP-03` evidence is recorded, then
   authorizes the `WP-04`/`WP-05` work.

To re-run the platform validation later, dispatch **Actions → Platform validation
(WP-02) → Run workflow** and approve the `warehouse` environment when GitHub asks. The
run is bounded at 15 minutes.

If validation ever fails on a reader write check, follow the remediation section in
[docs/07](07_operations_access_and_security.md#if-the-reader-check-reports-that-insert-succeeded).

Never paste a secret, connection string, or full query output into chat or an issue.

## Gate G1 checklist (closed 2026-11-04)

`G1` was closed and implementation authorized via `H-007`. The checklist is retained
as the acceptance record:

- [x] The human has read the scope, architecture, sources, model, and plan.
- [x] The human accepts the free-tier platform and its limits.
- [x] The human accepts the source list and license posture (`H-006`).
- [x] The human accepts the multi-site model and `dim_site`.
- [x] Member A is HassanNawaz14; Members B-E have real names, or the B-E placeholders
      are explicitly accepted for planning only (H-002 deferred per human instruction).
- [x] The Neon project `AeroGrid-DW` and raw bucket `aerogrid-raw` exist.
- [x] The GitHub `warehouse` environment exists.
- [x] Required secrets are stored in GitHub, not in the repository.
- [x] `main` is protected with pull requests, review, and force-push/deletion blocks.
- [x] Members can be invited and read-only access is planned (`aerogrid_reader` exists).
- [x] Legacy synthetic samples are explicitly documented as demo-only and excluded
      from Phase 2 (`D-017`).
- [x] `implementation_authorized` is set to `YES` only after all of the above.

## Step 1: Review the baseline

Read, in order:

1. `AGENTS.md`
2. `Phase2/README.md`
3. `Phase2/AGENTS.md`
4. `Phase2/PROGRESS.md`
5. `Phase2/docs/00_documentation_map.md`
6. `01_phase2_scope_and_objectives.md`
7. `02_architecture_and_platform.md`
8. `03_data_sources_and_licensing.md`
9. `04_data_model.md`
10. `05_etl_pipeline.md`
11. `06_data_quality_and_reports.md`
12. `07_operations_access_and_security.md`
13. `08_team_work_division.md`
14. The dev plan and acceptance files.

Approve or request changes. The baseline was accepted via `H-001`; no further
authorization is needed for `WP-02`/`WP-03`.

## Step 2: Replace placeholders

Edit `Phase2/PROGRESS.md` and `Phase2/docs/08_team_work_division.md` to replace
Members B-E with real names. If names are not ready, keep the placeholders and mark
`H-002` blocked. Do not let an agent guess names.

## Step 3: Create the Neon project

In the Neon UI:

1. Create or join the organization.
2. Create a project named `AeroGrid-DW` in `aws-us-east-2`.
3. Under **Services**, keep Postgres enabled and enable **Object storage**, then
   create the project.
4. Neon creates branch `production` (main), database `neondb`, and role
   `neondb_owner`. Use `neondb` or create a dedicated database; record the database
   name.
5. Select the `production` branch, open **Object storage**, and create a private
   bucket named `aerogrid-raw`. Record the bucket name and storage endpoint.
6. Create the `aerogrid_etl` role early enough to build `DATABASE_URL`; grant
   schema/table privileges after `WP-04`/`WP-05`. Create `aerogrid_reader` after the
   schema and reporting views exist.
7. Store the write connection string in the GitHub `warehouse` environment, not in a
   file or chat.
8. Create a CI storage credential with read/write access (`storage:read`,
   `storage:write`).
9. Create a member storage credential with read-only access (`storage:read`) if
   needed.
10. Invite the other four members.

If Neon asks for a card or paid plan, stop and record a capacity decision. Do not
upgrade silently.

## Step 4: Configure GitHub

1. Confirm the repository is public, or accept the private-repo Actions budget.
2. Create an environment named `warehouse`.
3. Add these as **environment secrets**, not repository secrets:
   - `DATABASE_URL` — direct connection string for `aerogrid_etl`, never
     `neondb_owner`.
   - `NEON_S3_ENDPOINT` — `https://br-royal-cherry-beij6hxw.storage.c-9.us-east-2.aws.neon.tech`.
   - `NEON_S3_REGION` — `us-east-2`.
   - `NEON_S3_BUCKET` — `aerogrid-raw`.
   - `NEON_S3_ACCESS_KEY_ID`.
   - `NEON_S3_SECRET_ACCESS_KEY`.
   Neon's generated `.env` may use the generic AWS names `AWS_ACCESS_KEY_ID`,
   `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, and `AWS_REGION`. Map them to the
   `NEON_S3_*` GitHub secret names above; the values are the same. Do not rename the
   GitHub secrets or commit the `.env`.
4. Optional: add `OPENSKY_CLIENT_ID` and `OPENSKY_CLIENT_SECRET` as environment
   secrets only if OpenSky access is approved; add `SOURCE_TIMEZONE` and
   `REPORT_PUBLISH_MODE` as environment variables only if overriding the defaults.
5. Require approval for the environment if available.
6. Protect `main`:
   - Require pull requests.
   - Require at least one approval.
   - Require status checks after workflows exist.
   - Disallow direct pushes.
7. Do not put real values in repository variables or files. Delete the Neon-generated
   `.env` after transferring values through the GitHub UI.

## Step 5: Share read-only access

1. Create the `aerogrid_reader` role after the schema exists.
2. Grant only connection, schema usage, and select.
3. Test one query per reporting view.
4. Share the connection string privately with the four members.
5. Never commit or paste it into an issue.
6. Ask members to set their SQL client to read-only mode.

## Step 6: Confirm sources and licenses

Confirm:

- Tartan ADS-B terms permit the intended academic use.
- Nightjar datasets are CC BY 4.0 and require attribution.
- Nominal-io DJI is MIT and requires attribution.
- FAA data is public and usable with attribution.
- NOAA/IEM data is public and usable with attribution.
- OpenSky is optional; do not rely on historical access until approved.

If a license is unclear, stop and record `H-006`. Do not add the source.

## Step 7: Authorize implementation (completed 2026-11-04)

This step was completed via `H-007`: `implementation_authorized: YES`, `G1` marked
done with approver and date, and `WP-02`/`WP-03` assigned. The procedure below is
retained for a future gate:

Only after `H-001` through `H-006` and `H-008` are resolved:

1. Set `implementation_authorized: YES` in `Phase2/PROGRESS.md`.
2. Mark `G1` done with the date and approver.
3. Assign `WP-02` or the first authorized work package.
4. Tell the agent the exact work package and scope.

An agent must not self-clear `G1`.

## Running the pipeline later

After implementation and authorization:

1. Open GitHub Actions.
2. Select `warehouse`.
3. Choose `Run workflow`.
4. Select `weekly` or `initial`.
5. Wait for completion.
6. Read the job summary.
7. Download the Data Cleaning and Data Quality PDFs.
8. If a critical check fails, do not treat the data as trusted.
9. Record failures and decisions in `PROGRESS.md`.

Do not run five-minute polling.

## Reading the data

Members should:

- Use the read-only connection string.
- Query `project_reporting` first.
- Use `project_dw` only for documented analytical needs.
- Avoid full-table scans during shared demos.
- Report slow queries instead of adding indexes.

## Capacity decisions

The free tier is a hard boundary:

- 1 GB PostgreSQL per project.
- 5 GB object storage per project.
- 100 CU-hours/month.
- 5 GB egress/project.

If usage approaches a warning threshold:

1. Stop new loads.
2. Review the load window and retention.
3. Ask the human for a decision.
4. Do not upgrade, delete, or truncate without approval.

## What to ask an agent

Good requests:

- "Update the documentation to match the approved model."
- "Review this PR for key integrity."
- "Implement `WP-05` as assigned."
- "Run the checks and report evidence."
- "Explain this DQ failure."

Bad requests:

- "Add a quick table so the demo has data."
- "Make up sample flights."
- "Use my password in the script."
- "Create the database for me."
- "Push directly to main."
- "Lower the threshold so the report passes."

## What agents cannot do

Agents cannot create accounts, accept terms, enable billing, create or delete Neon
resources, manage secrets, invite members, change repository settings, apply for
OpenSky access, run destructive SQL, or approve scope changes. These remain human
actions.

## Reviewing agent work

Check:

- The work package and scope.
- Files changed.
- Real source evidence.
- Counts and key integrity.
- No secrets or raw data.
- Docs updated.
- `PROGRESS.md` handoff.
- Whether the agent stopped at a gate instead of working around it.

## Troubleshooting

| Problem | Human response |
|---|---|
| Neon project paused | It will resume on connection; this is expected |
| CI cannot connect | Check the `warehouse` environment secret and role grants |
| Member cannot read | Check the read-only role and reporting view grants |
| Source is down | Record the gap; do not synthesize |
| Critical DQ failure | Review the report; decide whether to fix the source/rule |
| Storage near limit | Stop loads; decide retention/load window |
| Secret exposed | Rotate it in GitHub/Neon immediately |
| Repository visibility needs change | Human-only action; record decision |

## Handoff to the team

When implementation starts, the human should:

1. Confirm the authorized work package.
2. Assign the accountable member and reviewer.
3. Point them to the plan and acceptance file.
4. Require a PR, not a direct commit.
5. Require `PROGRESS.md` evidence at the end.

No deadlines are implied by this plan. Completion is evidence-based.
