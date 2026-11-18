-- WP-P3-02 / analytical query 05 (QW-P3-02-05)
-- Business question: how much observed traffic and journey activity comes from each
--   source system, and how wide is its site coverage?
-- Grain: one row per source system present in tracking or journey facts.
-- Source category is a documented mapping, not a source-provided attribute:
--   TARTAN -> MANNED_ADSB; NIGHTJAR / NOMINAL_DJI / DJI -> UAS; anything else -> OTHER.
-- Coverage (D3-009, L-008): UAS sources are validated but not loaded into facts. Their
--   absence from this result means missing coverage, not zero UAS activity.
-- Sources: project_dw.fact_vehicle_tracking, fact_flight_journey.
-- Check linkage: DQ3-A-001, DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only.

WITH tracking AS (
    SELECT
        UPPER(TRIM(f.source_system)) AS source_system,
        COUNT(*)::bigint AS tracking_positions,
        COUNT(DISTINCT f.vehicle_key)::bigint AS distinct_vehicles,
        COUNT(DISTINCT f.site_key)::bigint AS sites_covered,
        MIN(f.event_ts) AS first_event_ts,
        MAX(f.event_ts) AS last_event_ts,
        ROUND(AVG(f.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
        ROUND(AVG(f.ground_speed_kts), 2) AS avg_ground_speed_kts
    FROM project_dw.fact_vehicle_tracking f
    WHERE f.site_key > 0
      AND f.vehicle_key > 0
    GROUP BY 1
),
journeys AS (
    SELECT
        UPPER(TRIM(j.source_system)) AS source_system,
        COUNT(*)::bigint AS journeys_observed,
        ROUND(SUM(j.total_distance_nm), 3) AS observed_journey_distance_nm,
        ROUND(AVG(j.flight_duration_sec), 2) AS avg_journey_duration_sec
    FROM project_dw.fact_flight_journey j
    WHERE j.site_key > 0
      AND j.vehicle_key > 0
    GROUP BY 1
)
SELECT
    COALESCE(t.source_system, j.source_system) AS source_system,
    CASE
        WHEN COALESCE(t.source_system, j.source_system) = 'TARTAN' THEN 'MANNED_ADSB'
        WHEN COALESCE(t.source_system, j.source_system) IN ('NIGHTJAR', 'NOMINAL_DJI', 'DJI') THEN 'UAS'
        ELSE 'OTHER'
    END AS source_category,
    COALESCE(t.tracking_positions, 0)::bigint AS tracking_positions,
    COALESCE(t.distinct_vehicles, 0)::bigint AS distinct_vehicles,
    COALESCE(t.sites_covered, 0)::bigint AS sites_covered,
    t.first_event_ts,
    t.last_event_ts,
    t.avg_altitude_msl_ft,
    t.avg_ground_speed_kts,
    COALESCE(j.journeys_observed, 0)::bigint AS journeys_observed,
    j.observed_journey_distance_nm,
    j.avg_journey_duration_sec,
    CASE
        WHEN COALESCE(t.tracking_positions, 0) = 0 THEN 'NO_TRACKING_COVERAGE - not proof of no activity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN COALESCE(j.journeys_observed, 0) = 0 THEN 'NO_JOURNEY_COVERAGE - not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage
FROM tracking t
FULL OUTER JOIN journeys j ON j.source_system = t.source_system
ORDER BY COALESCE(t.tracking_positions, 0) DESC, 1;
