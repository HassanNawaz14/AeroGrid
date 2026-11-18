-- WP-P3-02 / analytical query 01 (QW-P3-02-01)
-- Business question: how does observed traffic volume change month over month at each site?
-- Grain: one row per real site per UTC calendar month that has tracking observations.
-- KPI dictionary: observed traffic positions, distinct vehicles observed, avg altitude/speed,
--   and month-over-month growth. Growth is NULL unless the prior row is the immediately
--   preceding calendar month and its volume is greater than zero.
-- Coverage (D3-009): no month spine is generated. A month absent from this result means
--   missing coverage, never "zero activity".
-- Sources: project_dw.fact_vehicle_tracking, project_dw.dim_site.
-- Check linkage: DQ3-A-001, DQ3-A-002, DQ3-A-003.
-- Read-only: SELECT only.

WITH monthly AS (
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
),
with_prior AS (
    SELECT
        m.*,
        LAG(m.month_utc) OVER w AS previous_month_utc,
        LAG(m.tracking_positions) OVER w AS previous_tracking_positions
    FROM monthly m
    WINDOW w AS (PARTITION BY m.site_key ORDER BY m.month_utc)
),
growth AS (
    SELECT
        p.*,
        CASE
            WHEN p.previous_month_utc IS NULL THEN NULL
            ELSE (
                (EXTRACT(YEAR FROM p.month_utc)::int * 12 + EXTRACT(MONTH FROM p.month_utc)::int)
                - (EXTRACT(YEAR FROM p.previous_month_utc)::int * 12 + EXTRACT(MONTH FROM p.previous_month_utc)::int)
            )
        END AS months_since_previous
    FROM with_prior p
)
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
    END AS mom_growth_status,
    CASE
        WHEN g.tracking_positions = 0 THEN 'ZERO - missing coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS coverage_status
FROM growth g
ORDER BY g.site_code, g.month_utc;
