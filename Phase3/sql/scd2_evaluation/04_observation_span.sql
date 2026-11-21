-- WP-P3-H3 / SCD Type 2 evaluation probe 04 (QW-P3-H3-04)
-- Question: is the observed history long enough for a Type 2 dimension to show any
-- change between versions?
-- Grain: one summary row over fact_vehicle_tracking for real vehicles
-- (vehicle_key > 0).
-- Read-only: a single SELECT; run only through Phase3/scripts/evaluate_scd2.py.
-- Sources: project_dw.fact_vehicle_tracking.
SELECT
    'QW-P3-H3-04'                                                        AS query_id,
    COUNT(*)                                                             AS h3_tracking_rows,
    COUNT(DISTINCT vehicle_key)                                          AS h3_tracked_vehicles,
    COUNT(DISTINCT date_trunc('month', event_ts AT TIME ZONE 'UTC'))     AS h3_observed_months,
    MIN(event_ts)                                                        AS h3_first_event_ts,
    MAX(event_ts)                                                        AS h3_last_event_ts
FROM project_dw.fact_vehicle_tracking
WHERE vehicle_key > 0;
