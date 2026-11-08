# Phase 2 SQL

Versioned DDL and checks for Phase 2. SQL is applied through the approved CI/human
path against the shared Neon warehouse (no local PostgreSQL, no Docker). No
credentials, dumps, or raw data are committed.

## Ownership

- Member C owns schema, dimensions, keys, and data dictionary SQL.
- Member B owns staging DDL and ingestion-adjacent SQL.
- Member D owns core fact SQL.
- Member E owns derived facts, DQ checks, and reporting views.

## Layout

```text
sql/
├── 00_grants.sql                           # owner-run grants: aerogrid_etl + aerogrid_reader
├── 00_schemas.sql                          # ETL bootstrap: staging schema + reader defaults
├── 01_staging/
│   ├── 01_source_manifest_run_reject_dq.sql # WP-04 manifest/run/reject/DQ tables
│   └── 02_source_tables.sql                # WP-04 source-shaped staging tables
├── 02_dimensions/                          # WP-05 (Member C)
├── 03_facts/                               # WP-06/WP-07 (Members D/E)
├── 04_reporting/                           # WP-10 (Member E)
├── 05_checks/                              # WP-08 (Member E)
└── seeds/                                  # dimension seeds, unknown members
```

## Rules

- Apply in filename order; DDL is idempotent (`IF NOT EXISTS`) where practical.
- `00_grants.sql` is owner-run (human-only), grants-only, and idempotent. Rerun it
  after any schema or object-class change. Its grants apply only to objects owned by
  the running owner role, so its final self-check must return `true` for every row,
  including the table-level reader rows.
- Bootstrap files applied by `aerogrid_etl` must grant the reader itself, because the
  owner cannot grant on another role's tables:
  `ALTER DEFAULT PRIVILEGES IN SCHEMA <schema> GRANT SELECT ON TABLES TO aerogrid_reader;`
  plus `GRANT SELECT` on tables that already exist. [`00_schemas.sql`](00_schemas.sql)
  does both for all three schemas on every run.
- Use explicit schema qualification (`project_staging.*`, etc.).
- Seed the `-1` unknown member for every dimension (`WP-05`).
- Keep destructive SQL out unless a human explicitly approves it.
- `etl_run_log` enforces `rows_read = rows_accepted + rows_rejected + rows_duplicate`;
  loaders must update run counts atomically at end-of-batch.
- Update `data/data_dictionary.md` when staging columns or constraints change.
