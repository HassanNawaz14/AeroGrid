-- Query ID: OQ-P3-05-01
-- WP-P3-05 dashboard-critical query: observed monthly tracking volume per source.
-- Mirrors the monthly CTE of project_reporting.vw_source_performance so the
-- EXPLAIN ANALYZE before/after pair measures the real dashboard access path.
-- Read-only. Grain: one row per source system per observed UTC month. A missing
-- month is missing coverage, never zero activity (D3-009).
SELECT
    UPPER(TRIM(f.source_system)) AS source_system,
    date_trunc('month', f.event_ts AT TIME ZONE 'UTC')::date AS month_utc,
    COUNT(*)::bigint AS tracking_positions,
    COUNT(DISTINCT f.vehicle_key)::bigint AS distinct_vehicles,
    COUNT(DISTINCT f.site_key)::bigint AS sites_covered,
    ROUND(AVG(f.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
    ROUND(AVG(f.ground_speed_kts), 2) AS avg_ground_speed_kts,
    CASE
        WHEN COUNT(*) = 0 THEN 'ZERO - missing coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS coverage_status
FROM project_dw.fact_vehicle_tracking f
WHERE f.site_key > 0
  AND f.vehicle_key > 0
GROUP BY 1, 2
ORDER BY 1, 2;
