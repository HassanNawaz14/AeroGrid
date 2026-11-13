-- AeroGrid WP-07: READ-ONLY near-time encounter screening.
-- Experimental temporal tolerance: 1 second (NOT YET an approved wp07-v1 behavior).
-- Existing H-013 thresholds: SEVERE <0.5 NM horizontal AND <500 ft vertical;
-- PROXIMITY <1.0 NM horizontal AND <1000 ft vertical.
-- One aircraft-pair position observation != one continuous encounter episode.
-- No INSERT/UPDATE/DELETE; safe to run using aerogrid_reader.

WITH preliminary AS MATERIALIZED (
    SELECT f.tracking_id, f.site_key, f.vehicle_key, f.event_ts,
           s.latitude AS lat, s.longitude AS lon,
           f.altitude_msl_ft AS altitude_ft,
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
    SELECT tracking_id, site_key, vehicle_key, event_ts,
           lat, lon, altitude_ft
    FROM preliminary
    WHERE airport_distance_nm <= 10
      AND vehicle_key > 0
),
nearby AS (
    SELECT a.vehicle_key AS vehicle_a, b.vehicle_key AS vehicle_b,
           ABS(EXTRACT(EPOCH FROM (b.event_ts - a.event_ts))) AS gap_sec,
           ABS(a.altitude_ft - b.altitude_ft) AS vertical_ft,
           2.0 * 3440.065 * ASIN(SQRT(LEAST(1.0, GREATEST(0.0,
               POWER(SIN(RADIANS(b.lat - a.lat) / 2.0), 2)
               + COS(RADIANS(a.lat)) * COS(RADIANS(b.lat))
                 * POWER(SIN(RADIANS(b.lon - a.lon) / 2.0), 2)
           )))) AS horizontal_nm
    FROM eligible a
    JOIN eligible b
      ON b.site_key = a.site_key
     AND b.tracking_id > a.tracking_id
     AND b.vehicle_key <> a.vehicle_key
     AND b.event_ts BETWEEN a.event_ts - INTERVAL '5 second'
                        AND a.event_ts + INTERVAL '5 second'
     -- Conservative prefilter for <=1 NM near KBTP; exact Haversine below.
     AND ABS(b.lat - a.lat) <= 0.02
     AND ABS(b.lon - a.lon) <= 0.03
)
SELECT
    (SELECT COUNT(*) FROM eligible) AS eligible_airborne_positions,
    COUNT(*) AS near_time_nearby_observation_pairs,
    COUNT(*) FILTER (
        WHERE horizontal_nm < 0.5 AND vertical_ft < 500
    ) AS severe_observation_pairs,
    COUNT(*) FILTER (
        WHERE horizontal_nm < 1.0 AND vertical_ft < 1000
          AND NOT (horizontal_nm < 0.5 AND vertical_ft < 500)
    ) AS proximity_only_observation_pairs,
    COUNT(DISTINCT (LEAST(vehicle_a, vehicle_b), GREATEST(vehicle_a, vehicle_b)))
      FILTER (WHERE horizontal_nm < 1.0 AND vertical_ft < 1000)
      AS distinct_vehicle_pairs_within_proximity
FROM nearby;
