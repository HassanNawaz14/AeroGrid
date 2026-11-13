-- WP-10 / AeroGrid reporting views from stored real facts only.
-- All views are idempotent (CREATE OR REPLACE), no synthetic source rows.
-- The physical grid is currently 2D. Candidate cells are NOT flight corridors.
CREATE SCHEMA IF NOT EXISTS project_reporting;

-- 01. Hour + site + cell, including unknown cells explicitly.
CREATE OR REPLACE VIEW project_reporting.vw_traffic_density_hour_grid AS
SELECT t.hour_ts, f.time_key, f.site_key, s.site_code,
       f.grid_key, g.grid_cell_id,
       COUNT(*)::bigint AS tracking_positions,
       COUNT(DISTINCT f.vehicle_key)::bigint AS distinct_vehicles,
       ROUND(AVG(f.altitude_msl_ft),2) AS avg_altitude_msl_ft,
       ROUND(AVG(f.ground_speed_kts),2) AS avg_speed_kts
FROM project_dw.fact_vehicle_tracking f
JOIN project_dw.dim_time t ON t.time_key=f.time_key
JOIN project_dw.dim_site s ON s.site_key=f.site_key
JOIN project_dw.dim_spatial_grid g ON g.grid_key=f.grid_key
GROUP BY t.hour_ts,f.time_key,f.site_key,s.site_code,f.grid_key,g.grid_cell_id;

-- 02. Hourly observed occupancy in 2D; NO altitude-band column exists physically.
CREATE OR REPLACE VIEW project_reporting.vw_occupied_grid_hours AS
SELECT o.occupancy_id,t.hour_ts,s.site_code,o.site_key,o.time_key,
       g.grid_cell_id,o.grid_key,g.lat_bin AS grid_center_lat,
       g.lon_bin AS grid_center_lon,o.algorithm_version,
       o.active_vehicle_count,o.supporting_tracking_count,
       o.total_occupancy_minutes,o.avg_traffic_speed_kts
FROM project_dw.fact_airspace_occupancy o
JOIN project_dw.dim_time t ON t.time_key=o.time_key
JOIN project_dw.dim_site s ON s.site_key=o.site_key
JOIN project_dw.dim_spatial_grid g ON g.grid_key=o.grid_key;

-- 03. Source-linked monthly traffic volume, not extrapolated operations.
CREATE OR REPLACE VIEW project_reporting.vw_monthly_traffic AS
SELECT date_trunc('month',f.event_ts AT TIME ZONE 'UTC')::date AS month_utc,
       f.site_key,s.site_code,COUNT(*)::bigint AS tracking_positions,
       COUNT(DISTINCT f.vehicle_key)::bigint AS observed_vehicles,
       ROUND(AVG(f.altitude_msl_ft),2) AS avg_altitude_msl_ft,
       ROUND(AVG(f.ground_speed_kts),2) AS avg_ground_speed_kts
FROM project_dw.fact_vehicle_tracking f
JOIN project_dw.dim_site s ON s.site_key=f.site_key
GROUP BY 1,2,3;

-- 04. Peak hourly observations by site; report sources instead of inventing operator mix.
CREATE OR REPLACE VIEW project_reporting.vw_peak_site_hours AS
SELECT f.site_key,s.site_code,t.hour_ts,COUNT(*)::bigint AS tracking_positions,
       COUNT(DISTINCT f.vehicle_key)::bigint AS observed_vehicles,
       COUNT(DISTINCT f.vehicle_key) FILTER (WHERE upper(f.source_system)='TARTAN')::bigint AS tartan_aircraft,
       COUNT(DISTINCT f.vehicle_key) FILTER (WHERE upper(f.source_system) IN ('NIGHTJAR','DJI','NOMINAL_DJI'))::bigint AS explicit_uas_sources,
       COUNT(DISTINCT f.vehicle_key) FILTER (WHERE upper(f.source_system) NOT IN ('TARTAN','NIGHTJAR','DJI','NOMINAL_DJI'))::bigint AS other_source_vehicles
FROM project_dw.fact_vehicle_tracking f
JOIN project_dw.dim_site s ON s.site_key=f.site_key
JOIN project_dw.dim_time t ON t.time_key=f.time_key
GROUP BY f.site_key,s.site_code,t.hour_ts;

-- 05. Observed close-encounter facts per day/cell (may genuinely have zero rows).
CREATE OR REPLACE VIEW project_reporting.vw_daily_encounter_hotspots AS
SELECT (e.start_ts AT TIME ZONE 'UTC')::date AS encounter_day_utc,
       e.site_key,s.site_code,e.grid_key,g.grid_cell_id,e.algorithm_version,
       count(*)::bigint AS detected_encounters,
       count(*) FILTER (WHERE e.risk_severity_class='SEVERE')::bigint AS severe_encounters,
       count(*) FILTER (WHERE e.risk_severity_class='PROXIMITY')::bigint AS proximity_encounters
FROM project_dw.fact_close_encounter e
JOIN project_dw.dim_site s ON s.site_key=e.site_key
JOIN project_dw.dim_spatial_grid g ON g.grid_key=e.grid_key
GROUP BY 1,2,3,4,5,6;

-- 06. Each encounter mapped to the two independently keyed vehicle source categories.
CREATE OR REPLACE VIEW project_reporting.vw_encounter_vehicle_types AS
SELECT e.encounter_id,e.start_ts,e.site_key,e.risk_severity_class,
       e.algorithm_version,v1.vehicle_type AS vehicle_type_1,
       v1.source_system AS source_system_1,
       v2.vehicle_type AS vehicle_type_2,
       v2.source_system AS source_system_2,
       e.min_horizontal_sep_nm,e.min_vertical_sep_ft
FROM project_dw.fact_close_encounter e
JOIN project_dw.dim_vehicle v1 ON v1.vehicle_key=e.vehicle_key_1
JOIN project_dw.dim_vehicle v2 ON v2.vehicle_key=e.vehicle_key_2;

-- 07. Each actual restriction snapshot and coarse site-hour traffic context.
-- Occupancy is site-hour aggregated before join, preventing cross-product inflation.
CREATE OR REPLACE VIEW project_reporting.vw_restriction_traffic_impact AS
WITH hourly AS (
 SELECT time_key,site_key,SUM(active_vehicle_count)::bigint AS summed_cell_vehicle_counts,
        SUM(supporting_tracking_count)::bigint AS tracking_observations
 FROM project_dw.fact_airspace_occupancy GROUP BY 1,2
)
SELECT a.activation_id,a.evaluation_ts,a.site_key,s.site_code,
       a.zone_key,z.zone_name,a.is_active,a.affected_traffic_count,
       a.compliant_count,a.compliance_rate_pct,a.algorithm_version,
       h.summed_cell_vehicle_counts,h.tracking_observations
FROM project_dw.fact_restriction_activation a
JOIN project_dw.dim_site s ON s.site_key=a.site_key
JOIN project_dw.dim_airspace_zone z ON z.zone_key=a.zone_key
LEFT JOIN hourly h ON h.time_key=a.time_key AND h.site_key=a.site_key;

-- 08. Weather-key observation and encounter aggregates, with independent CTEs.
-- Unknown weather_key=-1 is visible and is not an actual METAR observation.
CREATE OR REPLACE VIEW project_reporting.vw_weather_operations AS
WITH traffic AS (
 SELECT site_key,weather_key,count(*)::bigint AS tracking_positions,
        count(DISTINCT vehicle_key)::bigint AS observed_vehicles
 FROM project_dw.fact_vehicle_tracking GROUP BY site_key,weather_key
), encounters AS (
 SELECT site_key,weather_key,count(*)::bigint AS detected_encounters
 FROM project_dw.fact_close_encounter GROUP BY site_key,weather_key
)
SELECT t.site_key,s.site_code,t.weather_key,w.station_icao,w.observation_ts,
       w.temperature_c,w.wind_speed_kts,w.visibility_m,
       t.tracking_positions,t.observed_vehicles,
       coalesce(e.detected_encounters,0)::bigint AS detected_encounters,
       (t.weather_key=-1) AS weather_unknown
FROM traffic t
JOIN project_dw.dim_site s ON s.site_key=t.site_key
JOIN project_dw.dim_weather w ON w.weather_key=t.weather_key
LEFT JOIN encounters e ON e.site_key=t.site_key AND e.weather_key=t.weather_key;

-- 09. Evidence-based observed cell utilization, NOT certified corridor capacity.
CREATE OR REPLACE VIEW project_reporting.vw_corridor_capacity_inputs AS
WITH occupancy AS (
 SELECT site_key,grid_key,count(*)::bigint AS observed_cell_hours,
       SUM(supporting_tracking_count)::bigint AS supporting_tracking_positions,
       ROUND(AVG(active_vehicle_count),2) AS avg_hourly_active_vehicles,
       MAX(active_vehicle_count) AS peak_hourly_active_vehicles,
       SUM(total_occupancy_minutes) AS observed_occupancy_minutes
 FROM project_dw.fact_airspace_occupancy GROUP BY site_key,grid_key
), encounter AS (
 SELECT site_key,grid_key,count(*)::bigint AS detected_encounters
 FROM project_dw.fact_close_encounter GROUP BY site_key,grid_key
)
SELECT o.site_key,s.site_code,o.grid_key,g.grid_cell_id,
       g.lat_bin AS grid_center_lat,g.lon_bin AS grid_center_lon,
       o.observed_cell_hours,o.supporting_tracking_positions,
       o.avg_hourly_active_vehicles,o.peak_hourly_active_vehicles,
       o.observed_occupancy_minutes,
       coalesce(e.detected_encounters,0)::bigint AS detected_encounters
FROM occupancy o
JOIN project_dw.dim_site s ON s.site_key=o.site_key
JOIN project_dw.dim_spatial_grid g ON g.grid_key=o.grid_key
LEFT JOIN encounter e ON e.site_key=o.site_key AND e.grid_key=o.grid_key
WHERE o.grid_key > 0;

-- 10. Low-observed-traffic grid-cell screening. Not connected routes, and not safety clearance.
CREATE OR REPLACE VIEW project_reporting.vw_candidate_corridor_cells AS
SELECT row_number() OVER (
        PARTITION BY c.site_key ORDER BY c.avg_hourly_active_vehicles,
        c.detected_encounters,c.observed_cell_hours DESC,c.grid_cell_id
       )::bigint AS screening_rank_within_site,
       c.site_key,c.site_code,c.grid_key,c.grid_cell_id,
       c.grid_center_lat,c.grid_center_lon,c.observed_cell_hours,
       c.avg_hourly_active_vehicles,c.peak_hourly_active_vehicles,
       c.detected_encounters,
       'Observed 2D grid-cell screening only; not an approved flight corridor'::text AS limitation
FROM project_reporting.vw_corridor_capacity_inputs c
WHERE c.observed_cell_hours >= 1;
