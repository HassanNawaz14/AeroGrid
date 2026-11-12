-- WP-07 read-only evidence. Run in an authorized warehouse SQL console or CI.
-- Requires derived-facts DDL. No records are inserted/updated/deleted here.
-- Each count is an observed value, not a minimum target for synthetic rows.

-- 1: Which fact tables exist and how many rows have actually been persisted?
SELECT 'fact_vehicle_tracking' AS fact, COUNT(*) AS n FROM project_dw.fact_vehicle_tracking
UNION ALL SELECT 'fact_flight_journey', COUNT(*) FROM project_dw.fact_flight_journey
UNION ALL SELECT 'fact_close_encounter', COUNT(*) FROM project_dw.fact_close_encounter
UNION ALL SELECT 'fact_airspace_occupancy', COUNT(*) FROM project_dw.fact_airspace_occupancy
UNION ALL SELECT 'fact_restriction_activation', COUNT(*) FROM project_dw.fact_restriction_activation;

-- 2: DQ-U-004: deterministic encounter pair duplicates (must be empty).
SELECT vehicle_key_1, vehicle_key_2, start_ts, algorithm_version, COUNT(*) AS duplicates
FROM project_dw.fact_close_encounter
GROUP BY vehicle_key_1, vehicle_key_2, start_ts, algorithm_version
HAVING COUNT(*) > 1;

-- 3: DQ-I-008: invalid identical/reversed vehicle pair (must be zero).
SELECT COUNT(*) AS invalid_pairs FROM project_dw.fact_close_encounter
WHERE vehicle_key_1 >= vehicle_key_2;

-- 4: DQ-B-001: incorrect stored classification by approved H-013 thresholds.
-- Use the values as stored (NUMERIC 7,3 and 8,2).
SELECT COUNT(*) AS severity_mismatches FROM project_dw.fact_close_encounter
WHERE algorithm_version = 'wp07-v1' AND (
    (risk_severity_class = 'SEVERE' AND NOT
       (min_horizontal_sep_nm < 0.5 AND min_vertical_sep_ft < 500))
 OR (risk_severity_class = 'PROXIMITY' AND NOT
       (min_horizontal_sep_nm < 1 AND min_vertical_sep_ft < 1000
        AND NOT (min_horizontal_sep_nm < 0.5 AND min_vertical_sep_ft < 500)))
 OR (risk_severity_class NOT IN ('SEVERE', 'PROXIMITY'))
);

-- 5: DQ-R-005: derived encounter evidence must resolve to real tracking rows.
SELECT COUNT(*) AS missing_tracking_evidence
FROM project_dw.fact_close_encounter e
LEFT JOIN project_dw.fact_vehicle_tracking a ON a.tracking_id = e.min_tracking_id_1
LEFT JOIN project_dw.fact_vehicle_tracking b ON b.tracking_id = e.min_tracking_id_2
WHERE a.tracking_id IS NULL OR b.tracking_id IS NULL
   OR a.vehicle_key <> e.vehicle_key_1 OR b.vehicle_key <> e.vehicle_key_2
   OR a.site_key <> e.site_key OR b.site_key <> e.site_key;

-- 6: DQ-U-003: occupancy cell/hour/version unique (must be empty).
SELECT time_key, grid_key, algorithm_version, COUNT(*) AS duplicates
FROM project_dw.fact_airspace_occupancy
GROUP BY time_key, grid_key, algorithm_version
HAVING COUNT(*) > 1;

-- 7: DQ-R-004: active vehicles <= supporting tracking records (must be zero).
SELECT COUNT(*) AS occupancy_count_errors
FROM project_dw.fact_airspace_occupancy
WHERE active_vehicle_count > supporting_tracking_count OR active_vehicle_count < 0
   OR total_occupancy_minutes < 0;

-- 8: Restriction snapshot lineage and window evidence.
SELECT a.activation_id, a.evaluation_ts, a.source_system,
       a.zone_key, a.is_active, a.source_record_id, a.source_snapshot_ts
FROM project_dw.fact_restriction_activation a
ORDER BY a.evaluation_ts DESC LIMIT 20;

-- 9: Assorted result sample; an empty result is an honest outcome.
SELECT encounter_id, start_ts, vehicle_key_1, vehicle_key_2,
       min_horizontal_sep_nm, min_vertical_sep_ft, risk_severity_class
FROM project_dw.fact_close_encounter
ORDER BY start_ts DESC LIMIT 20;
