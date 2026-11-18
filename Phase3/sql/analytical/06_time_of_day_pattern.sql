-- WP-P3-02 / analytical query 06 (QW-P3-02-06)
-- Business question: at which UTC hours does observed traffic concentrate at each site?
-- Grain: one row per real site per observed UTC hour-of-day.
-- KPI dictionary: observed traffic positions, distinct vehicles observed, avg altitude/speed.
-- Coverage (D3-009): only observed site-hour pairs appear. An absent hour is missing
--   coverage, not zero activity.
-- Sources: project_dw.fact_vehicle_tracking, dim_site.
-- Check linkage: DQ3-A-001, DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only.

SELECT
    s.site_code,
    EXTRACT(HOUR FROM f.event_ts AT TIME ZONE 'UTC')::int AS hour_utc,
    COUNT(*)::bigint AS tracking_positions,
    COUNT(DISTINCT f.vehicle_key)::bigint AS distinct_vehicles,
    ROUND(AVG(f.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
    ROUND(AVG(f.ground_speed_kts), 2) AS avg_ground_speed_kts
FROM project_dw.fact_vehicle_tracking f
JOIN project_dw.dim_site s ON s.site_key = f.site_key
WHERE f.site_key > 0
  AND f.vehicle_key > 0
GROUP BY s.site_code, 2
ORDER BY s.site_code, hour_utc;
