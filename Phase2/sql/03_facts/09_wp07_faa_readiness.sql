-- WP-07 FAA source readiness. SELECT only. No production mutations.
-- FAA TFR service in WP-03 is current/forward-looking; 2026 snapshot != 2022 flight.
SELECT 'accepted_faa_tfr_zones' AS metric, COUNT(*) AS count_value
FROM project_staging.stg_airspace_zone
WHERE UPPER(source_system)='FAA_TFR' AND reject_reason IS NULL
UNION ALL
SELECT 'accepted_real_restriction_snapshots', COUNT(*)
FROM project_staging.stg_restriction_snapshot
WHERE reject_reason IS NULL AND is_active IS NOT NULL
UNION ALL
SELECT 'real_airspace_zone_dimension', COUNT(*)
FROM project_dw.dim_airspace_zone WHERE zone_key > 0
UNION ALL
SELECT 'restriction_activation_facts', COUNT(*)
FROM project_dw.fact_restriction_activation
UNION ALL
SELECT '2026_utc_time_members', COUNT(*)
FROM project_dw.dim_time
WHERE hour_ts >= TIMESTAMPTZ '2026-01-01T00:00:00Z'
  AND hour_ts < TIMESTAMPTZ '2027-01-01T00:00:00Z';
