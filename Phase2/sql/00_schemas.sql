-- Phase 2 schema bootstrap (WP-04 / staging-owned bootstrap for CI verification)
-- Creates schemas used by staging DDL. Dimension/fact/reporting schemas are owned by
-- later work packages; project_staging is required now.

CREATE SCHEMA IF NOT EXISTS project_staging;
