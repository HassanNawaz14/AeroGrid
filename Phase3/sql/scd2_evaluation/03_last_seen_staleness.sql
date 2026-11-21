-- WP-P3-H3 / SCD Type 2 evaluation probe 03 (QW-P3-H3-03)
-- Question: does the insert-only dimension refresh leave last_seen_ts behind the
-- staged data? This is the one dim_vehicle attribute that actually changes over time.
-- Grain: one summary row over dim_vehicle members that match accepted staged serials.
-- The loader uses ON CONFLICT DO NOTHING, so last_seen_ts is not advanced after the
-- first load (Phase2 docs/15). This probe measures the gap; it does not correct it.
-- Read-only: a single SELECT; run only through Phase3/scripts/evaluate_scd2.py.
-- Sources: project_dw.dim_vehicle, project_staging.stg_uas_position.
WITH staged AS (
    SELECT
        lower(source_system)  AS source_system,
        vehicle_serial,
        MAX(event_ts)         AS staged_last_ts
    FROM project_staging.stg_uas_position
    WHERE reject_reason IS NULL
      AND vehicle_serial IS NOT NULL
      AND btrim(vehicle_serial) <> ''
    GROUP BY lower(source_system), vehicle_serial
),
compared AS (
    SELECT
        d.vehicle_key,
        d.last_seen_ts,
        s.staged_last_ts
    FROM project_dw.dim_vehicle d
    JOIN staged s
      ON s.source_system = d.source_system
     AND s.vehicle_serial = d.source_entity_id
    WHERE d.vehicle_key > 0
)
SELECT
    'QW-P3-H3-03'                                                     AS query_id,
    COUNT(*)                                                          AS h3_members_compared,
    COUNT(*) FILTER (WHERE last_seen_ts IS NULL
                        OR last_seen_ts < staged_last_ts)             AS h3_stale_members,
    ROUND(COALESCE(MAX(EXTRACT(EPOCH FROM (staged_last_ts - last_seen_ts)))
                   FILTER (WHERE last_seen_ts < staged_last_ts), 0)
          / 3600.0, 2)                                                AS h3_max_lag_hours
FROM compared;
