-- Query ID: OQ-P3-05-03
-- WP-P3-05 dashboard-critical query: per-vehicle observed activity, journey
-- totals, and peak UTC hour. Mirrors project_reporting.vw_vehicle_analysis so the
-- EXPLAIN ANALYZE before/after pair measures the real dashboard access path.
-- Read-only. Grain: one row per real dim_vehicle member (vehicle_key > 0).
-- Vehicles with no facts stay visible with coverage labels, never as evidence of
-- inactivity (D3-009). Identity is source-scoped only (L3-003).
SELECT
    v.vehicle_key,
    UPPER(TRIM(v.source_system)) AS source_system,
    v.source_entity_id,
    COALESCE(t.tracking_positions, 0)::bigint AS tracking_positions,
    t.first_event_ts,
    t.last_event_ts,
    COALESCE(t.active_days_utc, 0)::bigint AS active_days_utc,
    COALESCE(t.sites_observed, 0)::bigint AS sites_observed,
    t.site_codes,
    COALESCE(j.journeys_observed, 0)::bigint AS journeys_observed,
    j.observed_journey_distance_nm,
    j.avg_journey_duration_sec,
    j.avg_journey_speed_kts,
    p.peak_hour_utc,
    p.peak_hour_tracking_positions,
    CASE
        WHEN COALESCE(t.tracking_positions, 0) = 0
            THEN 'NO_TRACKING_COVERAGE - not proof of inactivity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN COALESCE(j.journeys_observed, 0) = 0
            THEN 'NO_JOURNEY_COVERAGE - not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage
FROM project_dw.dim_vehicle v
LEFT JOIN (
    SELECT
        f.vehicle_key,
        COUNT(*)::bigint AS tracking_positions,
        MIN(f.event_ts) AS first_event_ts,
        MAX(f.event_ts) AS last_event_ts,
        COUNT(DISTINCT (f.event_ts AT TIME ZONE 'UTC')::date)::bigint AS active_days_utc,
        COUNT(DISTINCT f.site_key)::bigint AS sites_observed,
        STRING_AGG(DISTINCT s.site_code, ', ' ORDER BY s.site_code) AS site_codes
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site s ON s.site_key = f.site_key
    WHERE f.vehicle_key > 0
      AND f.site_key > 0
    GROUP BY f.vehicle_key
) AS t ON t.vehicle_key = v.vehicle_key
LEFT JOIN (
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
) AS j ON j.vehicle_key = v.vehicle_key
LEFT JOIN (
    SELECT
        ranked.vehicle_key,
        ranked.hour_utc AS peak_hour_utc,
        ranked.hour_tracking_positions AS peak_hour_tracking_positions
    FROM (
        SELECT
            hourly.vehicle_key,
            hourly.hour_utc,
            hourly.hour_tracking_positions,
            ROW_NUMBER() OVER (
                PARTITION BY hourly.vehicle_key
                ORDER BY hourly.hour_tracking_positions DESC, hourly.hour_utc
            ) AS peak_rank
        FROM (
            SELECT
                f.vehicle_key,
                EXTRACT(HOUR FROM f.event_ts AT TIME ZONE 'UTC')::int AS hour_utc,
                COUNT(*)::bigint AS hour_tracking_positions
            FROM project_dw.fact_vehicle_tracking f
            WHERE f.vehicle_key > 0
              AND f.site_key > 0
            GROUP BY 1, 2
        ) AS hourly
    ) AS ranked
    WHERE ranked.peak_rank = 1
) AS p ON p.vehicle_key = v.vehicle_key
WHERE v.vehicle_key > 0
ORDER BY v.vehicle_key;
