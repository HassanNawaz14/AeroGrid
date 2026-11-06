# Phase 2 ETL

This directory is intentionally empty. It will hold the Python ETL package once the
relevant work package is authorized.

## Owners

- Member B: source clients, raw archive, staging, cleaning.
- Member D: tracking and journey facts.
- Member E: derived facts, DQ, reporting views, PDFs.
- Member A: CI integration and deployment.

## Planned modules

See [docs/05_etl_pipeline.md](../docs/05_etl_pipeline.md) for the canonical layout.

## Rules

- Real public data only; never generate synthetic business rows.
- No local PostgreSQL, Docker, or dev containers.
- Use environment variables/secrets; never hard-code credentials.
- Archive raw data in object storage with a manifest.
- Use idempotent loads and preserve provenance.
- Fail closed on critical DQ.
- Do not add a dependency without checking its license and free-tier terms.
- Do not commit raw data or generated credentials.
