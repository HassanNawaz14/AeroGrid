-- Phase 2 role grants (owner-run: neondb_owner, in the Neon SQL Editor)
--
-- Run once, and again after any change that adds a schema or a new object class.
-- Re-running after a work package creates tables is also what grants the reader role
-- SELECT on those tables: default privileges only affect objects created afterwards.
-- This script only adds or tightens privileges; it creates no tables and touches no
-- data. It never grants write access to aerogrid_reader.
--
-- The final SELECT lists every check with a boolean `ok` column. Every row must be
-- true. A false row means a grant below failed or the role carries a platform
-- membership that overrides grants; see Phase2/docs/07.

BEGIN;

-- Roles can connect and see the database --------------------------------------
GRANT CONNECT ON DATABASE neondb TO aerogrid_etl, aerogrid_reader;

-- Schemas ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS project_staging;
CREATE SCHEMA IF NOT EXISTS project_dw;
CREATE SCHEMA IF NOT EXISTS project_reporting;

GRANT USAGE, CREATE ON SCHEMA project_staging TO aerogrid_etl;
GRANT USAGE, CREATE ON SCHEMA project_dw TO aerogrid_etl;
GRANT USAGE, CREATE ON SCHEMA project_reporting TO aerogrid_etl;

GRANT USAGE ON SCHEMA project_staging TO aerogrid_reader;
GRANT USAGE ON SCHEMA project_dw TO aerogrid_reader;
GRANT USAGE ON SCHEMA project_reporting TO aerogrid_reader;

REVOKE CREATE ON SCHEMA project_staging FROM aerogrid_reader;
REVOKE CREATE ON SCHEMA project_dw FROM aerogrid_reader;
REVOKE CREATE ON SCHEMA project_reporting FROM aerogrid_reader;

-- Existing objects ------------------------------------------------------------
-- These grants cover objects owned by the role running this script (neondb_owner).
-- Tables owned by aerogrid_etl are granted by aerogrid_etl in 00_schemas.sql; the
-- owner cannot grant on another role's tables, so the table-level self-check below
-- stays false until that ETL bootstrap has run.
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA project_staging TO aerogrid_etl;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA project_dw TO aerogrid_etl;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA project_reporting TO aerogrid_etl;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA project_staging TO aerogrid_etl;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA project_dw TO aerogrid_etl;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA project_reporting TO aerogrid_etl;

GRANT SELECT ON ALL TABLES IN SCHEMA project_staging TO aerogrid_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA project_dw TO aerogrid_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA project_reporting TO aerogrid_reader;

REVOKE INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA project_staging FROM aerogrid_reader;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA project_dw FROM aerogrid_reader;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA project_reporting FROM aerogrid_reader;

-- Objects created later by the owner ------------------------------------------
ALTER DEFAULT PRIVILEGES IN SCHEMA project_staging
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO aerogrid_etl;
ALTER DEFAULT PRIVILEGES IN SCHEMA project_dw
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO aerogrid_etl;
ALTER DEFAULT PRIVILEGES IN SCHEMA project_reporting
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO aerogrid_etl;

ALTER DEFAULT PRIVILEGES IN SCHEMA project_staging
    GRANT USAGE, SELECT ON SEQUENCES TO aerogrid_etl;
ALTER DEFAULT PRIVILEGES IN SCHEMA project_dw
    GRANT USAGE, SELECT ON SEQUENCES TO aerogrid_etl;
ALTER DEFAULT PRIVILEGES IN SCHEMA project_reporting
    GRANT USAGE, SELECT ON SEQUENCES TO aerogrid_etl;

ALTER DEFAULT PRIVILEGES IN SCHEMA project_staging
    GRANT SELECT ON TABLES TO aerogrid_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA project_dw
    GRANT SELECT ON TABLES TO aerogrid_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA project_reporting
    GRANT SELECT ON TABLES TO aerogrid_reader;

-- Self-check: every row must be true ------------------------------------------
SELECT 'etl usage staging' AS check,
       has_schema_privilege('aerogrid_etl', 'project_staging', 'USAGE') AS ok
UNION ALL SELECT 'etl create staging',
       has_schema_privilege('aerogrid_etl', 'project_staging', 'CREATE')
UNION ALL SELECT 'etl usage dw',
       has_schema_privilege('aerogrid_etl', 'project_dw', 'USAGE')
UNION ALL SELECT 'etl create dw',
       has_schema_privilege('aerogrid_etl', 'project_dw', 'CREATE')
UNION ALL SELECT 'etl usage reporting',
       has_schema_privilege('aerogrid_etl', 'project_reporting', 'USAGE')
UNION ALL SELECT 'etl create reporting',
       has_schema_privilege('aerogrid_etl', 'project_reporting', 'CREATE')
UNION ALL SELECT 'reader usage staging',
       has_schema_privilege('aerogrid_reader', 'project_staging', 'USAGE')
UNION ALL SELECT 'reader usage dw',
       has_schema_privilege('aerogrid_reader', 'project_dw', 'USAGE')
UNION ALL SELECT 'reader usage reporting',
       has_schema_privilege('aerogrid_reader', 'project_reporting', 'USAGE')
UNION ALL SELECT 'reader cannot create staging',
       NOT has_schema_privilege('aerogrid_reader', 'project_staging', 'CREATE')
UNION ALL SELECT 'reader cannot create dw',
       NOT has_schema_privilege('aerogrid_reader', 'project_dw', 'CREATE')
UNION ALL SELECT 'reader cannot create reporting',
       NOT has_schema_privilege('aerogrid_reader', 'project_reporting', 'CREATE')
UNION ALL SELECT 'reader has no neon_superuser membership',
       NOT EXISTS (
           SELECT 1
           FROM pg_auth_members am
           JOIN pg_roles member_role ON member_role.oid = am.member
           JOIN pg_roles granted_role ON granted_role.oid = am.roleid
           WHERE member_role.rolname = 'aerogrid_reader'
             AND granted_role.rolname = 'neon_superuser'
       )
UNION ALL SELECT 'reader can select every existing table',
       NOT EXISTS (
           SELECT 1
           FROM pg_class c
           JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname IN ('project_staging', 'project_dw', 'project_reporting')
             AND c.relkind IN ('r', 'p')
             AND NOT has_table_privilege('aerogrid_reader', c.oid, 'SELECT')
       )
UNION ALL SELECT 'reader cannot write any existing table',
       NOT EXISTS (
           SELECT 1
           FROM pg_class c
           JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname IN ('project_staging', 'project_dw', 'project_reporting')
             AND c.relkind IN ('r', 'p')
             AND (has_table_privilege('aerogrid_reader', c.oid, 'INSERT')
                  OR has_table_privilege('aerogrid_reader', c.oid, 'UPDATE')
                  OR has_table_privilege('aerogrid_reader', c.oid, 'DELETE')
                  OR has_table_privilege('aerogrid_reader', c.oid, 'TRUNCATE'))
       );

COMMIT;
