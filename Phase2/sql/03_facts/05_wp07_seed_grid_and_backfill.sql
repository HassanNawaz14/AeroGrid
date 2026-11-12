-- WP-07 / WP-06 remediation: grid dimension from *accepted real Tartan positions*.
-- Non-destructive, idempotent; apply ONLY in approved warehouse CI transaction.
-- In dry-run verifier, all these writes are rolled back. Real grids have no
-- synthetic telemetry: each cell exists because at least one accepted source
-- position was observed there. Grid scheme wp07-g01: 0.01-degree WGS84 bins.
-- NO DELETE, DROP, TRUNCATE. Backfill ONLY previously-unknown (-1) grid keys.

WITH real_positions AS (
    SELECT DISTINCT
        f.site_key,
        floor(s.latitude * 100)::integer AS lat_index,
        floor(s.longitude * 100)::integer AS lon_index
    FROM project_dw.fact_vehicle_tracking AS f
    JOIN project_staging.stg_adsb_position AS s
      ON s.source_system = f.source_system
     AND s.source_record_id = f.source_record_id
    WHERE upper(f.source_system) = 'TARTAN'
      AND s.reject_reason IS NULL
      AND f.site_key > 0
      AND s.latitude > -90 AND s.latitude < 90
      AND s.longitude >= -180 AND s.longitude < 180
)
INSERT INTO project_dw.dim_spatial_grid
    (grid_cell_id, site_key, lat_bin, lon_bin)
SELECT 'wp07-g01:' || site_key || ':' || lat_index || ':' || lon_index,
       site_key,
       (lat_index + 0.5)::double precision / 100.0,
       (lon_index + 0.5)::double precision / 100.0
FROM real_positions
ON CONFLICT (grid_cell_id) DO NOTHING;

WITH backfill AS (
    SELECT f.tracking_id, g.grid_key
    FROM project_dw.fact_vehicle_tracking AS f
    JOIN project_staging.stg_adsb_position AS s
      ON s.source_system = f.source_system
     AND s.source_record_id = f.source_record_id
    JOIN project_dw.dim_spatial_grid AS g
      ON g.grid_cell_id =
          'wp07-g01:' || f.site_key || ':' || floor(s.latitude * 100)::integer
          || ':' || floor(s.longitude * 100)::integer
     AND g.site_key = f.site_key
    WHERE upper(f.source_system) = 'TARTAN'
      AND f.grid_key = -1
      AND f.site_key > 0
      AND s.reject_reason IS NULL
      AND s.latitude > -90 AND s.latitude < 90
      AND s.longitude >= -180 AND s.longitude < 180
)
UPDATE project_dw.fact_vehicle_tracking f
SET grid_key = b.grid_key
FROM backfill b
WHERE f.tracking_id = b.tracking_id
  AND f.grid_key = -1;

-- Check real grid coverage, no wrong-site mappings, and any remaining UNKNOWNs.
-- Remaining UNKNOWNs must be accounted for; do not silently treat them as cells.
SELECT COUNT(*) AS all_tartan_tracking,
       COUNT(*) FILTER (WHERE grid_key > 0) AS mapped_tartan_tracking,
       COUNT(*) FILTER (WHERE grid_key = -1) AS unknown_tartan_grid
FROM project_dw.fact_vehicle_tracking
WHERE upper(source_system) = 'TARTAN';

SELECT COUNT(*) AS mismatched_site_mappings
FROM project_dw.fact_vehicle_tracking f
JOIN project_dw.dim_spatial_grid g ON g.grid_key = f.grid_key
WHERE f.grid_key > 0 AND f.site_key <> g.site_key;
