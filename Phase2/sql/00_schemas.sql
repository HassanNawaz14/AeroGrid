-- Phase 2 schema bootstrap (WP-04 / staging-owned bootstrap for CI verification)
-- Creates schemas used by staging DDL. Dimension/fact/reporting schemas are owned by
-- later work packages; project_staging is required now.

CREATE SCHEMA IF NOT EXISTS project_staging;

-- Tables created here by aerogrid_etl stay readable to the shared read-only role.
-- The owner-run grants in 00_grants.sql cover objects created by neondb_owner.
ALTER DEFAULT PRIVILEGES IN SCHEMA project_staging
    GRANT SELECT ON TABLES TO aerogrid_reader;
