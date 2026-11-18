-- WP-P3-02 / analytical query 02 (QW-P3-02-02)
-- Business question: what are the headline observed-traffic KPIs and their current
--   evidence coverage?
-- Grain: one row (all-time snapshot over the loaded warehouse).
-- KPI dictionary: observed traffic positions, distinct vehicles observed, journeys
--   observed, occupied cell-hours, detected encounters, avg altitude/speed.
-- Coverage (D3-009): each zero KPI carries an explicit label. Empty means missing
--   coverage, never "no events". Detected encounters are zero for a second reason too:
--   the current predicate needs identical timestamps and only Tartan tracking is loaded
--   (L-004, L-008), so zero is not proof of no encounters.
-- Sources: project_dw.fact_vehicle_tracking, fact_flight_journey,
--   fact_airspace_occupancy, fact_close_encounter.
-- Check linkage: DQ3-A-001, DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only.

WITH tracking AS (
    SELECT
        COUNT(*)::bigint AS tracking_positions,
        COUNT(DISTINCT vehicle_key)::bigint AS distinct_vehicles,
        ROUND(AVG(altitude_msl_ft), 2) AS avg_altitude_msl_ft,
        ROUND(AVG(ground_speed_kts), 2) AS avg_ground_speed_kts,
        MIN(event_ts) AS first_event_ts,
        MAX(event_ts) AS last_event_ts,
        MAX(loaded_at) AS tracking_loaded_at,
        COUNT(*) FILTER (WHERE site_key <= 0)::bigint AS unknown_site_positions,
        COUNT(*) FILTER (WHERE vehicle_key <= 0)::bigint AS unknown_vehicle_positions,
        COUNT(*) FILTER (WHERE grid_key <= 0)::bigint AS unknown_grid_positions,
        COUNT(*) FILTER (WHERE weather_key <= 0)::bigint AS unknown_weather_positions
    FROM project_dw.fact_vehicle_tracking
),
journeys AS (
    SELECT
        COUNT(*)::bigint AS journeys_observed,
        ROUND(AVG(flight_duration_sec), 2) AS avg_journey_duration_sec,
        ROUND(SUM(total_distance_nm), 3) AS observed_journey_distance_nm,
        MAX(loaded_at) AS journeys_loaded_at
    FROM project_dw.fact_flight_journey
    WHERE site_key > 0
      AND vehicle_key > 0
),
occupancy AS (
    SELECT
        COUNT(*)::bigint AS occupied_cell_hours,
        ROUND(SUM(total_occupancy_minutes), 2) AS observed_occupancy_minutes,
        ROUND(AVG(active_vehicle_count), 2) AS avg_active_vehicles_per_cell_hour,
        MAX(active_vehicle_count) AS peak_active_vehicles_in_a_cell_hour,
        MAX(loaded_at) AS occupancy_loaded_at
    FROM project_dw.fact_airspace_occupancy
    WHERE site_key > 0
),
encounters AS (
    SELECT
        COUNT(*)::bigint AS detected_encounters,
        MAX(loaded_at) AS encounters_loaded_at
    FROM project_dw.fact_close_encounter
    WHERE site_key > 0
)
SELECT
    t.tracking_positions,
    t.distinct_vehicles,
    t.avg_altitude_msl_ft,
    t.avg_ground_speed_kts,
    j.journeys_observed,
    j.avg_journey_duration_sec,
    j.observed_journey_distance_nm,
    o.occupied_cell_hours,
    o.observed_occupancy_minutes,
    o.avg_active_vehicles_per_cell_hour,
    o.peak_active_vehicles_in_a_cell_hour,
    e.detected_encounters,
    t.first_event_ts,
    t.last_event_ts,
    GREATEST(
        t.tracking_loaded_at,
        j.journeys_loaded_at,
        o.occupancy_loaded_at,
        e.encounters_loaded_at
    ) AS data_as_of_utc,
    CASE
        WHEN t.tracking_positions = 0 THEN 'ZERO - missing tracking coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN t.distinct_vehicles = 0 THEN 'ZERO - missing vehicle coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS vehicle_coverage,
    CASE
        WHEN j.journeys_observed = 0 THEN 'ZERO - missing journey coverage; not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage,
    CASE
        WHEN o.occupied_cell_hours = 0 THEN 'ZERO - missing occupancy coverage; not proof of no activity'
        ELSE 'OBSERVED (2D grid; 60 s sample cap, L-003)'
    END AS occupancy_coverage,
    CASE
        WHEN e.detected_encounters = 0 THEN 'ZERO - no detected episodes AND insufficient overlapping evidence (exact-timestamp pairing L-004; single loaded source L-008); not proof of no encounters'
        ELSE 'DETECTED'
    END AS encounter_coverage,
    CASE
        WHEN t.avg_altitude_msl_ft IS NULL THEN 'NO_VALID_ROWS'
        ELSE 'OBSERVED'
    END AS altitude_measure_coverage,
    CASE
        WHEN t.avg_ground_speed_kts IS NULL THEN 'NO_VALID_ROWS'
        ELSE 'OBSERVED'
    END AS speed_measure_coverage,
    t.unknown_site_positions,
    t.unknown_vehicle_positions,
    t.unknown_grid_positions,
    t.unknown_weather_positions
FROM tracking t
CROSS JOIN journeys j
CROSS JOIN occupancy o
CROSS JOIN encounters e;
