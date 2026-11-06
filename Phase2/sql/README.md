# Phase 2 SQL

This directory is intentionally empty. It will hold versioned DDL, seeds, checks, and
reporting views once the relevant work package is authorized.

## Ownership

- Member C owns schema, dimensions, keys, and data dictionary SQL.
- Member B owns staging DDL and ingestion-adjacent SQL.
- Member D owns core fact SQL.
- Member E owns derived facts, DQ checks, and reporting views.

## Planned layout

```text
sql/
├── 00_schemas.sql
├── 01_staging/
├── 02_dimensions/
├── 03_facts/
├── 04_reporting/
├── 05_checks/
└── seeds/
```

## Rules

- No SQL is authorized until `WP-04`/`WP-05` begin.
- No local PostgreSQL or Docker.
- Use explicit schema qualification.
- Use idempotent DDL where practical.
- Seed the `-1` unknown member for every dimension.
- Keep destructive SQL out unless a human explicitly approves it.
- Do not commit credentials, dumps, or raw data.
- Update `data/data_dictionary.md` and the DBML with model changes.
