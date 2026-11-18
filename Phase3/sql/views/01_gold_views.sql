-- WP-P3-04 / Phase 3 gold views (P3-G3)
-- Idempotent CREATE OR REPLACE VIEW statements. Read-only with respect to base
-- tables: no INSERT/UPDATE/DELETE/DDL beyond replacing these three views.
-- Business questions and grains are documented at each view.
-- Sources: project_dw dimensions and facts only. No synthetic rows, no
-- extrapolation, no month spine; absent data means missing coverage, never zero
-- activity (D3-009).
-- Reproduce with the stored queries under Phase3/sql/analytical/ and re-run the
-- Phase 3 evidence workflow.
-- Check linkage: DQ3-A-001 (row/measure reconciliation), DQ3-A-002 (query
-- traceability), DQ3-A-003 (coverage labels).


-- 01. Observed monthly traffic and month-over-month growth.
-- Business question: how does observed traffic volume change month over month at
--   each site?
-- Grain: one row per real site per UTC calendar month that has tracking
--   observations. A site-month absent from this view is missing coverage, never
--   "zero activity".
-- Reproduce: Phase3/sql/analytical/01_monthly_traffic_growth.sql (QW-P3-02-01).
CREATE OR REPLACE VIEW project_reporting.vw_monthly_traffic_growth AS
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
                (EXTRACT(YEAR FROM p.month_utc)::int * 12
                 + EXTRACT(MONTH FROM p.month_utc)::int)
                - (EXTRACT(YEAR FROM p.previous_month_utc)::int * 12
                   + EXTRACT(MONTH FROM p.previous_month_utc)::int)
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
FROM growth g;


-- 02. Observed vehicle activity, site span, and time-of-day pattern summary.
-- Business question: how active is each observed vehicle, where was it observed,
--   and at which UTC hour is its observed activity highest?
-- Grain: one row per real dim_vehicle member (vehicle_key > 0). Vehicles with no
--   tracking or journey rows stay in the view with zero values and coverage
--   labels, never as evidence of inactivity.
-- Time-of-day pattern: peak UTC hour, positions in that hour, and count of
--   distinct UTC hours with observations. This is a summary, not a 24-hour spine.
-- Identity caveat (L3-003): a row is a source-scoped vehicle identity, not an
--   operator or owner.
-- Reproduce: Phase3/sql/analytical/04_vehicle_activity_summary.sql
--   (QW-P3-02-04) plus the hour aggregation in QW-P3-02-06.
CREATE OR REPLACE VIEW project_reporting.vw_vehicle_analysis AS
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
),
hourly AS (
    SELECT
        f.vehicle_key,
        EXTRACT(HOUR FROM f.event_ts AT TIME ZONE 'UTC')::int AS hour_utc,
        COUNT(*)::bigint AS hour_tracking_positions
    FROM project_dw.fact_vehicle_tracking f
    WHERE f.vehicle_key > 0
      AND f.site_key > 0
    GROUP BY 1, 2
),
peak AS (
    SELECT
        h.vehicle_key,
        h.hour_utc AS peak_hour_utc,
        h.hour_tracking_positions AS peak_hour_tracking_positions,
        ROW_NUMBER() OVER (
            PARTITION BY h.vehicle_key
            ORDER BY h.hour_tracking_positions DESC, h.hour_utc
        ) AS peak_rank
    FROM hourly h
),
hour_summary AS (
    SELECT
        h.vehicle_key,
        COUNT(*)::bigint AS observed_hours_utc
    FROM hourly h
    GROUP BY h.vehicle_key
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
    p.peak_hour_utc,
    p.peak_hour_tracking_positions,
    COALESCE(h.observed_hours_utc, 0)::bigint AS observed_hours_utc,
    CASE
        WHEN COALESCE(t.tracking_positions, 0) = 0
            THEN 'NO_TRACKING_COVERAGE - not proof of inactivity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN COALESCE(j.journeys_observed, 0) = 0
            THEN 'NO_JOURNEY_COVERAGE - not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage,
    'SOURCE_ENTITY_ONLY'::text AS identity_scope,
    'Observed behaviour only; not a real operator identity (L3-003)'::text AS identity_note
FROM project_dw.dim_vehicle v
LEFT JOIN tracking t ON t.vehicle_key = v.vehicle_key
LEFT JOIN journeys j ON j.vehicle_key = v.vehicle_key
LEFT JOIN peak p ON p.vehicle_key = v.vehicle_key AND p.peak_rank = 1
LEFT JOIN hour_summary h ON h.vehicle_key = v.vehicle_key
WHERE v.vehicle_key > 0;


-- 03. Observed source-system performance and coverage.
-- Business question: how much observed traffic and journey activity comes from
--   each source system, how wide is its site coverage, and what is its observed
--   monthly span?
-- Grain: one row per source system present in dim_vehicle (vehicle_key > 0).
--   UAS sources that are staged but not loaded into facts remain visible with zero
--   facts and coverage labels; their absence is not zero UAS activity (L-008).
-- Trend: observed month count, first/last observed month and their position
--   counts, and the peak observed month. No new growth KPI is invented here; the
--   month-over-month KPI lives in vw_monthly_traffic_growth.
-- Reproduce: Phase3/sql/analytical/05_source_performance.sql (QW-P3-02-05) plus
--   the monthly source aggregation in QW-P3-02-01.
CREATE OR REPLACE VIEW project_reporting.vw_source_performance AS
WITH sources AS (
    SELECT DISTINCT UPPER(TRIM(v.source_system)) AS source_system
    FROM project_dw.dim_vehicle v
    WHERE v.vehicle_key > 0
),
tracking AS (
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
),
monthly AS (
    SELECT
        UPPER(TRIM(f.source_system)) AS source_system,
        date_trunc('month', f.event_ts AT TIME ZONE 'UTC')::date AS month_utc,
        COUNT(*)::bigint AS tracking_positions
    FROM project_dw.fact_vehicle_tracking f
    WHERE f.site_key > 0
      AND f.vehicle_key > 0
    GROUP BY 1, 2
),
month_rank AS (
    SELECT
        m.*,
        ROW_NUMBER() OVER (
            PARTITION BY m.source_system ORDER BY m.month_utc
        ) AS first_rank,
        ROW_NUMBER() OVER (
            PARTITION BY m.source_system ORDER BY m.month_utc DESC
        ) AS last_rank,
        ROW_NUMBER() OVER (
            PARTITION BY m.source_system
            ORDER BY m.tracking_positions DESC, m.month_utc
        ) AS peak_rank,
        COUNT(*) OVER (PARTITION BY m.source_system)::bigint AS observed_months
    FROM monthly m
),
month_summary AS (
    SELECT
        r.source_system,
        MAX(r.observed_months)::bigint AS observed_months,
        MAX(CASE WHEN r.first_rank = 1 THEN r.month_utc END) AS first_month_utc,
        MAX(CASE WHEN r.first_rank = 1 THEN r.tracking_positions END)
            AS first_month_tracking_positions,
        MAX(CASE WHEN r.last_rank = 1 THEN r.month_utc END) AS last_month_utc,
        MAX(CASE WHEN r.last_rank = 1 THEN r.tracking_positions END)
            AS last_month_tracking_positions,
        MAX(CASE WHEN r.peak_rank = 1 THEN r.month_utc END) AS peak_month_utc,
        MAX(CASE WHEN r.peak_rank = 1 THEN r.tracking_positions END)
            AS peak_month_tracking_positions
    FROM month_rank r
    GROUP BY r.source_system
)
SELECT
    s.source_system,
    CASE
        WHEN s.source_system = 'TARTAN' THEN 'MANNED_ADSB'
        WHEN s.source_system IN ('NIGHTJAR', 'NOMINAL_DJI', 'DJI') THEN 'UAS'
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
    COALESCE(ms.observed_months, 0)::bigint AS observed_months,
    ms.first_month_utc,
    ms.first_month_tracking_positions,
    ms.last_month_utc,
    ms.last_month_tracking_positions,
    ms.peak_month_utc,
    ms.peak_month_tracking_positions,
    CASE
        WHEN COALESCE(t.tracking_positions, 0) = 0
            THEN 'NO_TRACKING_COVERAGE - not proof of no activity'
        ELSE 'OBSERVED'
    END AS tracking_coverage,
    CASE
        WHEN COALESCE(j.journeys_observed, 0) = 0
            THEN 'NO_JOURNEY_COVERAGE - not proof of no flights'
        ELSE 'OBSERVED'
    END AS journey_coverage
FROM sources s
LEFT JOIN tracking t ON t.source_system = s.source_system
LEFT JOIN journeys j ON j.source_system = s.source_system
LEFT JOIN month_summary ms ON ms.source_system = s.source_system;
