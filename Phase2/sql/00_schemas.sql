-- Phase 2 schema bootstrap (WP-04 / staging-owned bootstrap for CI verification)
-- Creates schemas used by staging DDL. Dimension/fact/reporting schemas are owned by
-- later work packages; project_staging is required now.

CREATE SCHEMA IF NOT EXISTS project_staging;

-- Tables created by aerogrid_etl stay readable to the shared read-only role.
-- The owner-run grants in 00_grants.sql only cover owner-created objects, and only
-- those that existed when that script ran, so ETL-applied DDL needs its own defaults.
DO $$
DECLARE
    schema_name text;
BEGIN
    FOREACH schema_name IN ARRAY ARRAY['project_staging', 'project_dw', 'project_reporting']
    LOOP
        IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = schema_name) THEN
            EXECUTE format(
                'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT ON TABLES TO aerogrid_reader',
                schema_name
            );
        END IF;
    END LOOP;
END
$$;
