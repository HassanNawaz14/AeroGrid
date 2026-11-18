-- WP-P3-02 / analytical query 07 (QW-P3-02-07)
-- Business question: what is the observed data coverage behind every analytical KPI?
-- Grain: one row (all-time coverage snapshot).
-- Purpose: make missing coverage and unknown-member shares visible before any KPI is
--   published (D3-009, DQ3-A-003). This query does not invent a month spine or a zero
--   activity claim.
-- Sources: project_dw tracking/journey/occupancy/encounter facts and dimensions.
-- Check linkage: DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only.

WITH tracking AS (
    SELECT
        COUNT(*)::bigint AS tracking_positions,
        COUNT(*) FILTER (WHERE site_key <= 0)::bigint AS unknown_site_positions,
        COUNT(*) FILTER (WHERE vehicle_key <= 0)::bigint AS unknown_vehicle_positions,
        COUNT(*) FILTER (WHERE grid_key <= 0)::bigint AS unknown_grid_positions,
        COUNT(*) FILTER (WHERE weather_key <= 0)::bigint AS unknown_weather_positions,
        MIN(event_ts) AS first_event_ts,
        MAX(event_ts) AS last_event_ts,
        COUNT(DISTINCT date_trunc('month', event_ts AT TIME ZONE 'UTC')::date)::bigint AS months_observed
    FROM project_dw.fact_vehicle_tracking
),
journeys AS (
    SELECT
        COUNT(*)::bigint AS journeys_observed,
        COUNT(*) FILTER (WHERE vehicle_key <= 0)::bigint AS unknown_vehicle_journeys,
        COUNT(*) FILTER (WHERE site_key <= 0)::bigint AS unknown_site_journeys
    FROM project_dw.fact_flight_journey
),
occupancy AS (
    SELECT
        COUNT(*)::bigint AS occupied_cell_hours,
        COUNT(*) FILTER (WHERE grid_key <= 0)::bigint AS unknown_grid_occupancy_rows
    FROM project_dw.fact_airspace_occupancy
),
encounters AS (
    SELECT
        COUNT(*)::bigint AS detected_encounters
    FROM project_dw.fact_close_encounter
),
dimensions AS (
    SELECT
        (SELECT COUNT(*) FROM project_dw.dim_site WHERE site_key > 0)::bigint AS real_sites,
        (SELECT COUNT(*) FROM project_dw.dim_vehicle WHERE vehicle_key > 0)::bigint AS real_vehicles,
        (SELECT COUNT(*) FROM project_dw.dim_spatial_grid WHERE grid_key > 0)::bigint AS real_grid_cells,
        (SELECT COUNT(*) FROM project_dw.dim_time WHERE time_key > 0)::bigint AS real_hour_members
)
SELECT
    t.tracking_positions,
    t.unknown_site_positions,
    t.unknown_vehicle_positions,
    t.unknown_grid_positions,
    t.unknown_weather_positions,
    j.journeys_observed,
    j.unknown_vehicle_journeys,
    j.unknown_site_journeys,
    o.occupied_cell_hours,
    o.unknown_grid_occupancy_rows,
    e.detected_encounters,
    d.real_sites,
    d.real_vehicles,
    d.real_grid_cells,
    d.real_hour_members,
    t.first_event_ts,
    t.last_event_ts,
    t.months_observed,
    CASE
        WHEN t.months_observed = 0 THEN 'NO_OBSERVED_MONTHS - missing coverage'
        WHEN t.months_observed = 1 THEN 'SINGLE_OBSERVED_MONTH - month-over-month growth cannot be computed until a second month is loaded'
        ELSE 'MULTI_MONTH_COVERAGE'
    END AS growth_coverage_note,
    CASE
        WHEN t.tracking_positions = 0 THEN 'ZERO - missing tracking coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN t.unknown_site_positions + t.unknown_vehicle_positions + o.unknown_grid_occupancy_rows = 0
            THEN 'NO_UNKNOWN_MEMBERS_IN_KEY_MEASURES'
        ELSE 'UNKNOWN_MEMBERS_PRESENT - exclude from business averages; see counts'
    END AS unknown_member_status
FROM tracking t
CROSS JOIN journeys j
CROSS JOIN occupancy o
CROSS JOIN encounters e
CROSS JOIN dimensions d;
