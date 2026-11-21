-- WP-P3-H3 / SCD Type 2 evaluation probe 02 (QW-P3-H3-02)
-- Question: does the staged UAS data show any per-vehicle attribute that changes
-- between observations, or an identity conflict a Type 2 design would have to handle?
-- Grain: one summary row over accepted staged UAS positions (reject_reason IS NULL).
-- stg_uas_position carries no descriptive vehicle attribute (no model, operator or
-- registration); the only per-vehicle columns are the serial and the source system.
-- home_* is a per-flight launch point, so it is reported as flight-level behaviour,
-- not as a dimension attribute.
-- Read-only: a single SELECT; run only through Phase3/scripts/evaluate_scd2.py.
-- Sources: project_staging.stg_uas_position.
WITH accepted AS (
    SELECT
        lower(source_system)                               AS source_system,
        vehicle_serial,
        (event_ts AT TIME ZONE 'UTC')::date                AS observed_day,
        round(home_latitude::numeric, 3)                   AS home_lat,
        round(home_longitude::numeric, 3)                  AS home_lon
    FROM project_staging.stg_uas_position
    WHERE reject_reason IS NULL
      AND vehicle_serial IS NOT NULL
      AND btrim(vehicle_serial) <> ''
),
per_serial AS (
    SELECT
        vehicle_serial,
        COUNT(DISTINCT source_system)                      AS source_systems,
        COUNT(DISTINCT observed_day)                       AS observed_days,
        COUNT(DISTINCT (home_lat, home_lon))
            FILTER (WHERE home_lat IS NOT NULL
                      AND home_lon IS NOT NULL)            AS home_points
    FROM accepted
    GROUP BY vehicle_serial
)
SELECT
    'QW-P3-H3-02'                                          AS query_id,
    COUNT(*)                                               AS h3_serials,
    COUNT(*) FILTER (WHERE source_systems > 1)             AS h3_serials_multi_source,
    COUNT(*) FILTER (WHERE observed_days > 1)              AS h3_serials_multi_day,
    COUNT(*) FILTER (WHERE home_points > 1)                AS h3_serials_multi_home_point
FROM per_serial;
