-- WP-P3-03 / OLAP query 03 (QW-P3-03-03)
-- Business question: do the ROLLUP and CUBE grand totals equal the plain aggregation?
-- Purpose: produce the DQ3-A-004 evidence row. A FAIL here blocks the OLAP claim.
-- Grain: one row with the plain, ROLLUP grand-total, and CUBE grand-total counts.
-- Scope: the same real-site/real-vehicle base used by queries 01 and 02.
-- Sources: project_dw.fact_vehicle_tracking, dim_site, dim_vehicle.
-- Check linkage: DQ3-A-004.
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
        UPPER(TRIM(f.source_system)) AS source_system,
        f.vehicle_key
    FROM project_dw.fact_vehicle_tracking f
    JOIN project_dw.dim_site s ON s.site_key = f.site_key
    JOIN project_dw.dim_vehicle v ON v.vehicle_key = f.vehicle_key
    WHERE f.site_key > 0
      AND f.vehicle_key > 0
),
plain AS (
    SELECT
        COUNT(*)::bigint AS tracking_positions,
        COUNT(DISTINCT vehicle_key)::bigint AS distinct_vehicles
    FROM base
),
rollup_grand_total AS (
    SELECT
        COUNT(*)::bigint AS tracking_positions,
        COUNT(DISTINCT vehicle_key)::bigint AS distinct_vehicles
    FROM base
    GROUP BY ROLLUP (site_code, source_category, vehicle_type_label)
    HAVING GROUPING(site_code) = 1
),
cube_grand_total AS (
    SELECT
        COUNT(*)::bigint AS tracking_positions,
        COUNT(DISTINCT vehicle_key)::bigint AS distinct_vehicles
    FROM base
    GROUP BY CUBE (site_code, source_system)
    HAVING GROUPING(site_code) = 1 AND GROUPING(source_system) = 1
)
SELECT
    p.tracking_positions AS plain_tracking_positions,
    r.tracking_positions AS rollup_tracking_positions,
    c.tracking_positions AS cube_tracking_positions,
    p.distinct_vehicles AS plain_distinct_vehicles,
    r.distinct_vehicles AS rollup_distinct_vehicles,
    c.distinct_vehicles AS cube_distinct_vehicles,
    (p.tracking_positions = r.tracking_positions) AS rollup_positions_match,
    (p.tracking_positions = c.tracking_positions) AS cube_positions_match,
    (p.distinct_vehicles = r.distinct_vehicles) AS rollup_vehicles_match,
    (p.distinct_vehicles = c.distinct_vehicles) AS cube_vehicles_match,
    CASE
        WHEN p.tracking_positions = r.tracking_positions
         AND p.tracking_positions = c.tracking_positions
         AND p.distinct_vehicles = r.distinct_vehicles
         AND p.distinct_vehicles = c.distinct_vehicles
            THEN 'PASS'
        ELSE 'FAIL'
    END AS dq3_a_004_status
FROM plain p
CROSS JOIN rollup_grand_total r
CROSS JOIN cube_grand_total c;
