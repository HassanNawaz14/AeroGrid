-- AeroGrid / WP-07 / READ-ONLY diagnostic for zero near-time encounters.
-- Keep H-013 separation thresholds unchanged. No INSERT/UPDATE/DELETE.
-- Query A checks whether the *approved-for-experiment* 10-NM subset contains
-- two distinct vehicles in the same hour, 10-second window, or spatial box.
-- This is a diagnostic of observed telemetry, NOT an encounter count.

WITH preliminary AS MATERIALIZED (
    SELECT f.tracking_id, f.site_key, f.vehicle_key, f.event_ts,
           s.latitude AS lat, s.longitude AS lon,
           2.0 * 3440.065 * ASIN(SQRT(LEAST(1.0, GREATEST(0.0,
               POWER(SIN(RADIANS(s.latitude - 40.7765833) / 2.0), 2)
               + COS(RADIANS(s.latitude)) * COS(RADIANS(40.7765833))
                 * POWER(SIN(RADIANS(s.longitude + 79.9510833) / 2.0), 2)
           )))) AS airport_distance_nm
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site ds ON ds.site_key = f.site_key
    JOIN project_staging.stg_adsb_position s
      ON s.source_system = f.source_system
     AND s.source_record_id = f.source_record_id
    WHERE UPPER(f.source_system) = 'TARTAN'
      AND ds.site_code = 'KBTP'
      AND s.reject_reason IS NULL
      AND f.on_ground IS NULL
      AND f.altitude_source = 'TARTAN_ALTISGNSS_FALSE'
      AND f.ground_speed_kts >= 120
      AND f.altitude_msl_ft >= 2248.4
      AND s.latitude > -90 AND s.latitude < 90
      AND s.longitude >= -180 AND s.longitude < 180
),
eligible AS MATERIALIZED (
    SELECT * FROM preliminary
    WHERE airport_distance_nm <= 10 AND vehicle_key > 0
),
time_pairs AS MATERIALIZED (
    SELECT ABS(EXTRACT(EPOCH FROM b.event_ts - a.event_ts)) AS time_gap_sec,
           ABS(a.lat - b.lat) AS lat_diff,
           ABS(a.lon - b.lon) AS lon_diff
    FROM eligible a
    JOIN eligible b
      ON b.site_key = a.site_key
     AND b.vehicle_key <> a.vehicle_key
     AND b.tracking_id > a.tracking_id
     AND b.event_ts BETWEEN a.event_ts - INTERVAL '10 seconds'
                        AND a.event_ts + INTERVAL '10 seconds'
)
SELECT
    (SELECT COUNT(*) FROM preliminary) AS candidates_before_radius,
    (SELECT COUNT(*) FROM eligible) AS eligible_within_10nm,
    (SELECT COUNT(*) FROM (
        SELECT site_key, date_trunc('hour', event_ts)
        FROM eligible
        GROUP BY site_key, date_trunc('hour', event_ts)
        HAVING COUNT(DISTINCT vehicle_key) >= 2
    ) h) AS hours_with_multiple_vehicles,
    COUNT(*) FILTER (WHERE time_gap_sec <= 1) AS pairs_time_only_1s,
    COUNT(*) FILTER (WHERE time_gap_sec <= 5) AS pairs_time_only_5s,
    COUNT(*) AS pairs_time_only_10s,
    COUNT(*) FILTER (
        WHERE lat_diff <= 0.02 AND lon_diff <= 0.03
    ) AS pairs_10s_and_spatial_box
FROM time_pairs;

-- Query B: use ONLY IF Query A says pairs_time_only_10s = 0.
-- Removes the optional 10-NM geographic screening rule, but keeps the
-- same speed, altitude-datum and altitude criteria. This does not change
-- production policy, and these pairs are not automatically encounters.
WITH preliminary AS MATERIALIZED (
    SELECT f.tracking_id, f.site_key, f.vehicle_key, f.event_ts
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site ds ON ds.site_key = f.site_key
    JOIN project_staging.stg_adsb_position s
      ON s.source_system = f.source_system
     AND s.source_record_id = f.source_record_id
    WHERE UPPER(f.source_system) = 'TARTAN'
      AND ds.site_code = 'KBTP'
      AND s.reject_reason IS NULL
      AND f.on_ground IS NULL
      AND f.altitude_source = 'TARTAN_ALTISGNSS_FALSE'
      AND f.ground_speed_kts >= 120
      AND f.altitude_msl_ft >= 2248.4
      AND s.latitude > -90 AND s.latitude < 90
      AND s.longitude >= -180 AND s.longitude < 180
      AND f.vehicle_key > 0
)
SELECT
    (SELECT COUNT(*) FROM preliminary) AS candidates_without_radius,
    COUNT(*) AS different_vehicle_pairs_within_10s_without_radius
FROM preliminary a
JOIN preliminary b
  ON b.site_key = a.site_key
 AND b.vehicle_key <> a.vehicle_key
 AND b.tracking_id > a.tracking_id
 AND b.event_ts BETWEEN a.event_ts - INTERVAL '10 seconds'
                    AND a.event_ts + INTERVAL '10 seconds';
