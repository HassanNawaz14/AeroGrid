-- WP-P3-02 / analytical query 04 (QW-P3-02-04)
-- Business question: how active is each observed vehicle, and at which sites?
-- Grain: one row per real dim_vehicle member.
-- KPI dictionary: observed traffic positions, distinct vehicles observed, journeys
--   observed, avg altitude/speed.
-- Coverage (D3-009): vehicles with no tracking or journey rows keep zero values and a
--   coverage label.
-- Identity caveat (L3-003): a row is a source-scoped vehicle identity, not an
--   operator or owner. Do not present it as an operator.
-- Sources: project_dw.dim_vehicle, fact_vehicle_tracking, fact_flight_journey, dim_site.
-- Check linkage: DQ3-A-001, DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only. Independent CTEs prevent join multiplication.

WITH tracking AS (
    SELECT
        f.vehicle_key,
        COUNT(*)::bigint AS tracking_positions,
        MIN(f.event_ts) AS first_event_ts,
        MAX(f.event_ts) AS last_event_ts,
        COUNT(DISTINCT (f.event_ts AT TIME ZONE 'UTC')::date)::bigint AS active_days_utc,
        COUNT(DISTINCT f.site_key)::bigint AS sites_observed,
        STRING_AGG(DISTINCT s.site_code, ', ' ORDER BY s.site_code) AS site_codes,
        ROUND(AVG(f.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
        ROUND(AVG(f.ground_speed_kts), 2) AS avg_ground_speed_kts
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site s ON s.site_key = f.site_key
    WHERE f.vehicle_key > 0
      AND f.site_key > 0
    GROUP BY f.vehicle_key
),
journeys AS (
    SELECT
        j.vehicle_key,
        COUNT(*)::bigint AS journeys_observed,
        ROUND(SUM(j.total_distance_nm), 3) AS observed_journey_distance_nm,
        ROUND(AVG(j.flight_duration_sec), 2) AS avg_journey_duration_sec,
        ROUND(AVG(j.avg_speed_kts), 2) AS avg_journey_speed_kts
    FROM project_dw.fact_flight_journey j
    WHERE j.vehicle_key > 0
      AND j.site_key > 0
    GROUP BY j.vehicle_key
)
SELECT
    v.vehicle_key,
    UPPER(TRIM(v.source_system)) AS source_system,
    v.source_entity_id,
    COALESCE(NULLIF(TRIM(v.vehicle_type), ''), 'UNSPECIFIED') AS vehicle_type_label,
    COALESCE(t.tracking_positions, 0)::bigint AS tracking_positions,
    t.first_event_ts,
    t.last_event_ts,
    COALESCE(t.active_days_utc, 0)::bigint AS active_days_utc,
    COALESCE(t.sites_observed, 0)::bigint AS sites_observed,
    t.site_codes,
    t.avg_altitude_msl_ft,
    t.avg_ground_speed_kts,
    COALESCE(j.journeys_observed, 0)::bigint AS journeys_observed,
    j.observed_journey_distance_nm,
    j.avg_journey_duration_sec,
    j.avg_journey_speed_kts,
    CASE
        WHEN COALESCE(t.tracking_positions, 0) = 0 THEN 'NO_TRACKING_COVERAGE - not proof of inactivity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN COALESCE(j.journeys_observed, 0) = 0 THEN 'NO_JOURNEY_COVERAGE - not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage,
    'SOURCE_ENTITY_ONLY'::text AS identity_scope,
    'Observed behaviour only; not a real operator identity (L3-003)'::text AS identity_note
FROM project_dw.dim_vehicle v
LEFT JOIN tracking t ON t.vehicle_key = v.vehicle_key
LEFT JOIN journeys j ON j.vehicle_key = v.vehicle_key
WHERE v.vehicle_key > 0
ORDER BY COALESCE(t.tracking_positions, 0) DESC, v.source_entity_id;
