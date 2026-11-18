-- WP-P3-02 / analytical query 03 (QW-P3-02-03)
-- Business question: how much observed traffic, journey activity, and 2D occupancy does
--   each real study site have?
-- Grain: one row per real site in dim_site (coverage rows are explicit).
-- KPI dictionary: observed traffic positions, distinct vehicles observed, journeys
--   observed, occupied cell-hours.
-- Coverage (D3-009): sites with no fact rows keep zero-valued measures with a
--   NO_*_COVERAGE label instead of disappearing or implying no activity.
-- Sources: project_dw.fact_vehicle_tracking, fact_flight_journey,
--   fact_airspace_occupancy, dim_site.
-- Check linkage: DQ3-A-001, DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only. Independent CTEs prevent join multiplication.

WITH traffic AS (
    SELECT
        f.site_key,
        COUNT(*)::bigint AS tracking_positions,
        COUNT(DISTINCT f.vehicle_key)::bigint AS distinct_vehicles,
        ROUND(AVG(f.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
        ROUND(AVG(f.ground_speed_kts), 2) AS avg_ground_speed_kts,
        MIN(f.event_ts) AS first_event_ts,
        MAX(f.event_ts) AS last_event_ts,
        COUNT(DISTINCT (f.event_ts AT TIME ZONE 'UTC')::date)::bigint AS active_days_utc
    FROM project_dw.fact_vehicle_tracking f
    WHERE f.site_key > 0
      AND f.vehicle_key > 0
    GROUP BY f.site_key
),
journeys AS (
    SELECT
        j.site_key,
        COUNT(*)::bigint AS journeys_observed,
        ROUND(AVG(j.flight_duration_sec), 2) AS avg_journey_duration_sec,
        ROUND(SUM(j.total_distance_nm), 3) AS observed_journey_distance_nm,
        ROUND(AVG(j.avg_speed_kts), 2) AS avg_journey_speed_kts
    FROM project_dw.fact_flight_journey j
    WHERE j.site_key > 0
      AND j.vehicle_key > 0
    GROUP BY j.site_key
),
occupancy AS (
    SELECT
        o.site_key,
        COUNT(*)::bigint AS occupied_cell_hours,
        ROUND(SUM(o.total_occupancy_minutes), 2) AS observed_occupancy_minutes,
        ROUND(AVG(o.active_vehicle_count), 2) AS avg_active_vehicles_per_cell_hour,
        MAX(o.active_vehicle_count) AS peak_active_vehicles_in_a_cell_hour
    FROM project_dw.fact_airspace_occupancy o
    WHERE o.site_key > 0
    GROUP BY o.site_key
)
SELECT
    s.site_key,
    s.site_code,
    s.site_name,
    COALESCE(t.tracking_positions, 0)::bigint AS tracking_positions,
    COALESCE(t.distinct_vehicles, 0)::bigint AS distinct_vehicles,
    t.avg_altitude_msl_ft,
    t.avg_ground_speed_kts,
    t.first_event_ts,
    t.last_event_ts,
    COALESCE(t.active_days_utc, 0)::bigint AS active_days_utc,
    COALESCE(j.journeys_observed, 0)::bigint AS journeys_observed,
    j.avg_journey_duration_sec,
    j.observed_journey_distance_nm,
    j.avg_journey_speed_kts,
    COALESCE(o.occupied_cell_hours, 0)::bigint AS occupied_cell_hours,
    COALESCE(o.observed_occupancy_minutes, 0) AS observed_occupancy_minutes,
    o.avg_active_vehicles_per_cell_hour,
    o.peak_active_vehicles_in_a_cell_hour,
    CASE
        WHEN COALESCE(t.tracking_positions, 0) = 0 THEN 'NO_TRACKING_COVERAGE - not proof of no activity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN COALESCE(j.journeys_observed, 0) = 0 THEN 'NO_JOURNEY_COVERAGE - not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage,
    CASE
        WHEN COALESCE(o.occupied_cell_hours, 0) = 0 THEN 'NO_OCCUPANCY_COVERAGE - not proof of no activity'
        ELSE 'OBSERVED (2D grid; 60 s sample cap, L-003)'
    END AS occupancy_coverage
FROM project_dw.dim_site s
LEFT JOIN traffic t ON t.site_key = s.site_key
LEFT JOIN journeys j ON j.site_key = s.site_key
LEFT JOIN occupancy o ON o.site_key = s.site_key
WHERE s.site_key > 0
ORDER BY s.site_code;
