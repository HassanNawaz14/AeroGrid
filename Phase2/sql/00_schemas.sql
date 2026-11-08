-- Phase 2 schema bootstrap (WP-04 / staging-owned bootstrap for CI verification)
-- Creates schemas used by staging DDL. Dimension/fact/reporting schemas are owned by
-- later work packages; project_staging is required now.
--
-- This file runs as aerogrid_etl on purpose. Objects created by aerogrid_etl belong to
-- aerogrid_etl, and the owner-run 00_grants.sql cannot grant on another role's tables,
-- so the shared read-only role would silently lose access to every ETL-created table.
-- The block below grants what exists now and sets the defaults for what comes later.

CREATE SCHEMA IF NOT EXISTS project_staging;

DO $$
DECLARE
    schema_name text;
    target record;
BEGIN
    FOREACH schema_name IN ARRAY ARRAY['project_staging', 'project_dw', 'project_reporting']
    LOOP
        CONTINUE WHEN NOT EXISTS (
            SELECT 1 FROM pg_namespace WHERE nspname = schema_name
        );

        FOR target IN
            SELECT c.oid
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = schema_name
              AND c.relkind IN ('r', 'p')
              AND pg_get_userbyid(c.relowner) = current_user
        LOOP
            EXECUTE format('GRANT SELECT ON TABLE %s TO aerogrid_reader', target.oid::regclass);
        END LOOP;

        EXECUTE format(
            'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT ON TABLES TO aerogrid_reader',
            schema_name
        );
    END LOOP;
END
$$;
