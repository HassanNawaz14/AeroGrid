-- WP-P3-03 / OLAP query 02 (QW-P3-03-02)
-- Business question: what are all marginal combinations of site and source system for
--   observed traffic, including site-only, source-only, and grand totals?
-- Grain: every row is an aggregate produced by CUBE; aggregation_level names the level.
-- Source system comes from the tracking fact and is normalized to uppercase.
-- Coverage (D3-009): a zero group carries a coverage label; an absent combination is
--   missing coverage, not proof of no activity.
-- Sources: project_dw.fact_vehicle_tracking, dim_site.
-- Check linkage: DQ3-A-004; reconciliation in 03_grand_total_reconciliation.sql.
-- Read-only: SELECT only.

WITH base AS (
    SELECT
        s.site_code,
        UPPER(TRIM(f.source_system)) AS source_system,
        f.vehicle_key,
        f.altitude_msl_ft,
        f.ground_speed_kts
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site s ON s.site_key = f.site_key
    WHERE f.site_key > 0
      AND f.vehicle_key > 0
)
SELECT
    b.site_code,
    b.source_system,
    CASE
        WHEN GROUPING(b.site_code) = 1 AND GROUPING(b.source_system) = 1 THEN 'GRAND_TOTAL'
        WHEN GROUPING(b.site_code) = 1 THEN 'SOURCE_SYSTEM_TOTAL'
        WHEN GROUPING(b.source_system) = 1 THEN 'SITE_TOTAL'
        ELSE 'DETAIL'
    END AS aggregation_level,
    COUNT(*)::bigint AS tracking_positions,
    COUNT(DISTINCT b.vehicle_key)::bigint AS distinct_vehicles,
    ROUND(AVG(b.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
    ROUND(AVG(b.ground_speed_kts), 2) AS avg_ground_speed_kts,
    CASE
        WHEN COUNT(*) = 0 THEN 'ZERO - missing coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS coverage_status
FROM base b
GROUP BY CUBE (b.site_code, b.source_system)
ORDER BY
    GROUPING(b.site_code), b.site_code,
    GROUPING(b.source_system), b.source_system;
