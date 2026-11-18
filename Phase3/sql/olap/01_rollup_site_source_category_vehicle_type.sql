-- WP-P3-03 / OLAP query 01 (QW-P3-03-01)
-- Business question: how does observed traffic roll up from site to source category to
--   vehicle type, including every subtotal and the grand total?
-- Hierarchy: site -> source category (MANNED_ADSB / UAS / OTHER) -> vehicle type.
-- Source category is a documented mapping, not a source-provided attribute:
--   TARTAN -> MANNED_ADSB; NIGHTJAR / NOMINAL_DJI / DJI -> UAS; anything else -> OTHER.
-- vehicle_type is NULL for the real Tartan seed because the source does not define it;
--   UNSPECIFIED is an honest label, not an invented vehicle category.
-- Grain: every row is an aggregate produced by ROLLUP; aggregation_level names the level.
-- Coverage (D3-009): a zero group carries a coverage label; an absent group is missing
--   coverage, not proof of no activity.
-- Sources: project_dw.fact_vehicle_tracking, dim_site, dim_vehicle.
-- Check linkage: DQ3-A-004; reconciliation in 03_grand_total_reconciliation.sql.
-- Read-only: SELECT only.

WITH base AS (
    SELECT
        s.site_code,
        CASE
            WHEN UPPER(TRIM(COALESCE(NULLIF(v.source_system, ''), f.source_system))) = 'TARTAN'
                THEN 'MANNED_ADSB'
            WHEN UPPER(TRIM(COALESCE(NULLIF(v.source_system, ''), f.source_system)))
                IN ('NIGHTJAR', 'NOMINAL_DJI', 'DJI')
                THEN 'UAS'
            ELSE 'OTHER'
        END AS source_category,
        COALESCE(NULLIF(TRIM(v.vehicle_type), ''), 'UNSPECIFIED') AS vehicle_type_label,
        f.vehicle_key,
        f.altitude_msl_ft,
        f.ground_speed_kts
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site s ON s.site_key = f.site_key
    JOIN project_dw.dim_vehicle v ON v.vehicle_key = f.vehicle_key
    WHERE f.site_key > 0
      AND f.vehicle_key > 0
)
SELECT
    b.site_code,
    b.source_category,
    b.vehicle_type_label,
    CASE
        WHEN GROUPING(b.site_code) = 1 THEN 'GRAND_TOTAL'
        WHEN GROUPING(b.source_category) = 1 THEN 'SITE_SUBTOTAL'
        WHEN GROUPING(b.vehicle_type_label) = 1 THEN 'SITE_SOURCE_CATEGORY_SUBTOTAL'
        ELSE 'DETAIL'
    END AS aggregation_level,
    COUNT(*)::bigint AS tracking_positions,
    COUNT(DISTINCT b.vehicle_key)::bigint AS distinct_vehicles,
    ROUND(AVG(b.altitude_msl_ft), 2) AS avg_altitude_msl_ft,
    ROUND(AVG(b.ground_speed_kts), 2) AS avg_ground_speed_kts,
    CASE
        WHEN COUNT(*) = 0 THEN 'ZERO - missing coverage; not proof of no activity'
        ELSE 'OBSERVED'
    END AS coverage_status
FROM base b
GROUP BY ROLLUP (b.site_code, b.source_category, b.vehicle_type_label)
ORDER BY
    GROUPING(b.site_code), b.site_code,
    GROUPING(b.source_category), b.source_category,
    GROUPING(b.vehicle_type_label), b.vehicle_type_label;
