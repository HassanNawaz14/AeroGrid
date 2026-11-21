-- WP-P3-H3 / SCD Type 2 evaluation probe 01 (QW-P3-H3-01)
-- Question: how many descriptive attributes does dim_vehicle carry, and do they vary?
-- Grain: one summary row over real dim_vehicle members (vehicle_key > 0; the -1
-- unknown member is excluded).
-- Read-only: a single SELECT; run only through Phase3/scripts/evaluate_scd2.py.
-- Sources: project_dw.dim_vehicle.
SELECT
    'QW-P3-H3-01'                                         AS query_id,
    COUNT(*)                                              AS h3_members,
    COUNT(DISTINCT source_system)                         AS h3_distinct_source_systems,
    COUNT(DISTINCT vehicle_type)                          AS h3_distinct_vehicle_types,
    COUNT(*) FILTER (WHERE first_seen_ts IS NULL
                        OR last_seen_ts IS NULL)          AS h3_null_seen_members,
    COUNT(*) FILTER (WHERE first_seen_ts = last_seen_ts)  AS h3_zero_span_members,
    MIN(first_seen_ts)                                    AS h3_first_seen_min_ts,
    MAX(last_seen_ts)                                     AS h3_last_seen_max_ts
FROM project_dw.dim_vehicle
WHERE vehicle_key > 0;
