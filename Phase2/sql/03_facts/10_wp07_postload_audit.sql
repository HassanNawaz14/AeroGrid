-- Read-only WP-07 post-load proof. Run AFTER approved protected persistent job.
SELECT 'tracking_rows' AS metric, COUNT(*) AS n FROM project_dw.fact_vehicle_tracking
UNION ALL SELECT 'tracking_unknown_grid',COUNT(*) FROM project_dw.fact_vehicle_tracking WHERE grid_key=-1
UNION ALL SELECT 'real_grid_cells',COUNT(*) FROM project_dw.dim_spatial_grid WHERE grid_key>0
UNION ALL SELECT 'occupancy_wp07_v1',COUNT(*) FROM project_dw.fact_airspace_occupancy WHERE algorithm_version='wp07-v1'
UNION ALL SELECT 'encounters_wp07_v1',COUNT(*) FROM project_dw.fact_close_encounter WHERE algorithm_version='wp07-v1'
UNION ALL SELECT 'restriction_activations_wp07_v1',COUNT(*) FROM project_dw.fact_restriction_activation WHERE algorithm_version='wp07-v1';

SELECT etl_run_id,run_mode,started_at,status,facts_inserted,critical_dq_failures
FROM project_staging.etl_run_log ORDER BY etl_run_id DESC LIMIT 8;

SELECT count(*) AS duplicate_cell_hour_version
FROM (SELECT time_key,grid_key,algorithm_version FROM project_dw.fact_airspace_occupancy
GROUP BY 1,2,3 HAVING count(*)>1) x;

SELECT has_table_privilege('aerogrid_reader','project_dw.fact_airspace_occupancy','SELECT')
       AS reader_has_occupancy_select;
