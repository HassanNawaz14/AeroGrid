-- WP-07 READ-ONLY preflight, no inserts. Run with approved reader access.
-- Counts describe actual readiness; do not fabricate missing inputs.

-- Check 1: raw on_ground field (Tartan is normally NULL).
-- The new WP07-AIR-01 *inference* is counted by the Python verifier, not this query.
SELECT COUNT(*) AS tracking_rows,
       COUNT(*) FILTER (WHERE on_ground IS FALSE) AS verified_airborne,
       COUNT(*) FILTER (WHERE on_ground IS TRUE) AS confirmed_ground,
       COUNT(*) FILTER (WHERE on_ground IS NULL) AS unknown_ground_state,
       COUNT(*) FILTER (WHERE grid_key > 0) AS rows_with_real_grid,
       COUNT(*) FILTER (WHERE grid_key = -1) AS rows_with_unknown_grid,
       COUNT(*) FILTER (WHERE altitude_source IS NULL) AS missing_altitude_datum
FROM project_dw.fact_vehicle_tracking
WHERE UPPER(source_system) = 'TARTAN';

-- Check 2: spatial dimension readiness.
SELECT COUNT(*) AS real_grid_cells
FROM project_dw.dim_spatial_grid WHERE grid_key > 0;

-- Check 3: same-site, exact-timestamp groups containing 2 or more vehicles.
-- If 0, a documented asynchronous-matching policy is needed for encounters.
SELECT COUNT(*) AS multi_vehicle_instant_groups FROM (
  SELECT site_key, event_ts
  FROM project_dw.fact_vehicle_tracking
  WHERE UPPER(source_system) = 'TARTAN' AND vehicle_key > 0
  GROUP BY site_key, event_ts
  HAVING COUNT(DISTINCT vehicle_key) >= 2
) g;

-- Check 4: real restriction source and dimension readiness.
SELECT COUNT(*) AS accepted_restriction_snapshots
FROM project_staging.stg_restriction_snapshot
WHERE reject_reason IS NULL AND is_active IS NOT NULL;

SELECT COUNT(*) AS real_zone_members
FROM project_dw.dim_airspace_zone WHERE zone_key > 0;

-- Check 5: preliminary Tartan/KBTP candidates for the *inferred* airborne rule.
-- This is a superseding indication of eligibility, not a confirmed flight count;
-- Python additionally enforces the <=10 NM geographical radius and finite inputs.
SELECT COUNT(*) AS inferred_airborne_candidates_before_radius_check
FROM project_dw.fact_vehicle_tracking f
JOIN project_dw.dim_site site ON site.site_key = f.site_key
JOIN project_staging.stg_adsb_position s
  ON s.source_system = f.source_system
 AND s.source_record_id = f.source_record_id
WHERE UPPER(f.source_system) = 'TARTAN'
  AND site.site_code = 'KBTP'
  AND s.reject_reason IS NULL
  AND f.on_ground IS NULL
  AND f.altitude_source = 'TARTAN_ALTISGNSS_FALSE'
  AND f.ground_speed_kts >= 120
  AND f.altitude_msl_ft >= 2248.4
  AND s.latitude > -90 AND s.latitude < 90
  AND s.longitude >= -180 AND s.longitude < 180;
