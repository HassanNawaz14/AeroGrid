-- Query ID: OQ-P3-05-02
-- WP-P3-05 dashboard-critical query: observed monthly traffic and month-over-month
-- growth per site. Exercises the access path of
-- project_reporting.vw_monthly_traffic_growth so the EXPLAIN ANALYZE
-- before/after pair measures the real dashboard scan.
-- Read-only. Grain: one row per real site per observed UTC month. An absent
-- site-month is missing coverage, never zero activity (D3-009). No month spine.
SELECT
    g.month_utc,
    g.site_key,
    g.site_code,
    g.site_name,
    g.tracking_positions,
    g.distinct_vehicles,
    g.avg_altitude_msl_ft,
    g.avg_ground_speed_kts,
    g.positions_missing_a_measure,
    g.previous_month_utc,
    g.previous_tracking_positions,
    g.months_since_previous,
    CASE
        WHEN g.previous_month_utc IS NULL THEN NULL
        WHEN g.months_since_previous <> 1 THEN NULL
        WHEN g.previous_tracking_positions = 0 THEN NULL
        ELSE ROUND(
            100.0 * (g.tracking_positions - g.previous_tracking_positions)
            / g.previous_tracking_positions,
            2
        )
    END AS mom_growth_pct,
    CASE
        WHEN g.previous_month_utc IS NULL THEN 'NO_PRIOR_MONTH'
        WHEN g.months_since_previous <> 1 THEN 'NO_ADJACENT_PRIOR_MONTH'
        WHEN g.previous_tracking_positions = 0 THEN 'PRIOR_MONTH_ZERO'
        ELSE 'COMPUTED'
    END AS mom_growth_status
FROM (
    SELECT
        m.*,
        (
            (EXTRACT(YEAR FROM m.month_utc)::int * 12
             + EXTRACT(MONTH FROM m.month_utc)::int)
            - (EXTRACT(YEAR FROM m.previous_month_utc)::int * 12
               + EXTRACT(MONTH FROM m.previous_month_utc)::int)
        ) AS months_since_previous
    FROM (
        SELECT
            monthly.*,
            LAG(monthly.month_utc) OVER w AS previous_month_utc,
            LAG(monthly.tracking_positions) OVER w AS previous_tracking_positions
        FROM (
            SELECT
                date_trunc('month', f.event_ts AT TIME ZONE 'UTC')::date AS month_utc,
                f.site_key,
                s.site_code,
                s.site_name,
                COUNT(*)::bigint AS tracking_positions,
                COUNT(DISTINCT f.vehicle_key)::bigint AS distinct_vehicles,
                ROUND(AVG(f.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
                ROUND(AVG(f.ground_speed_kts), 2) AS avg_ground_speed_kts,
                COUNT(*) FILTER (
                    WHERE f.altitude_msl_ft IS NULL OR f.ground_speed_kts IS NULL
                )::bigint AS positions_missing_a_measure
            FROM project_dw.fact_vehicle_tracking f
            JOIN project_dw.dim_site s ON s.site_key = f.site_key
            WHERE f.site_key > 0
              AND f.vehicle_key > 0
            GROUP BY 1, 2, 3, 4
        ) AS monthly
        WINDOW w AS (PARTITION BY monthly.site_key ORDER BY monthly.month_utc)
    ) AS m
) AS g;
