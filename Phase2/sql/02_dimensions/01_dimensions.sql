-- WP-05: dimensions, surrogate keys, unknown members (Member C)
-- Idempotent: safe to rerun. Objects created by aerogrid_etl; 00_schemas.sql grants
-- reader SELECT on existing ETL-owned tables and sets defaults for later ones.

CREATE SCHEMA IF NOT EXISTS project_dw;

CREATE TABLE IF NOT EXISTS project_dw.dim_time (
    time_key  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hour_ts   timestamptz NOT NULL,
    date_utc  date NOT NULL,
    hour_utc  smallint NOT NULL,
    CONSTRAINT uq_dim_time_hour_ts UNIQUE (hour_ts)
);

CREATE TABLE IF NOT EXISTS project_dw.dim_site (
    site_key   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_code  text NOT NULL,
    site_name  text,
    CONSTRAINT uq_dim_site_code UNIQUE (site_code)
);

CREATE TABLE IF NOT EXISTS project_dw.dim_vehicle (
    vehicle_key       bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_system     text NOT NULL,
    source_entity_id  text NOT NULL,
    vehicle_type      text,
    first_seen_ts     timestamptz,
    last_seen_ts      timestamptz,
    CONSTRAINT uq_dim_vehicle_natural UNIQUE (source_system, source_entity_id)
);

CREATE TABLE IF NOT EXISTS project_dw.dim_spatial_grid (
    grid_key     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    grid_cell_id text NOT NULL,
    site_key     bigint NOT NULL REFERENCES project_dw.dim_site(site_key),
    lat_bin      double precision,
    lon_bin      double precision,
    CONSTRAINT uq_dim_spatial_grid_cell UNIQUE (grid_cell_id)
);

CREATE TABLE IF NOT EXISTS project_dw.dim_weather (
    weather_key        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    station_icao       text NOT NULL,
    observation_ts     timestamptz NOT NULL,
    site_key           bigint NOT NULL REFERENCES project_dw.dim_site(site_key),
    temperature_c      numeric(5,2),
    wind_speed_kts     numeric(6,2),
    visibility_m       numeric(9,2),
    CONSTRAINT uq_dim_weather_station_ts UNIQUE (station_icao, observation_ts)
);

CREATE TABLE IF NOT EXISTS project_dw.dim_airspace_zone (
    zone_key         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_system    text NOT NULL,
    source_object_id text NOT NULL,
    zone_name        text,
    site_key         bigint NOT NULL REFERENCES project_dw.dim_site(site_key),
    CONSTRAINT uq_dim_airspace_zone_natural UNIQUE (source_system, source_object_id)
);

-- Unknown members (-1). Insert site unknown first so other -1 rows can reference it.
INSERT INTO project_dw.dim_site (site_key, site_code, site_name)
OVERRIDING SYSTEM VALUE
VALUES (-1, 'UNKNOWN', 'Unknown site')
ON CONFLICT (site_key) DO NOTHING;

INSERT INTO project_dw.dim_time (time_key, hour_ts, date_utc, hour_utc)
OVERRIDING SYSTEM VALUE
VALUES (-1, '1900-01-01T00:00:00Z', DATE '1900-01-01', 0)
ON CONFLICT (time_key) DO NOTHING;

INSERT INTO project_dw.dim_vehicle (vehicle_key, source_system, source_entity_id, vehicle_type)
OVERRIDING SYSTEM VALUE
VALUES (-1, 'UNKNOWN', 'UNKNOWN', 'Unknown vehicle')
ON CONFLICT (vehicle_key) DO NOTHING;

INSERT INTO project_dw.dim_spatial_grid (grid_key, grid_cell_id, site_key, lat_bin, lon_bin)
OVERRIDING SYSTEM VALUE
VALUES (-1, 'UNKNOWN', -1, NULL, NULL)
ON CONFLICT (grid_key) DO NOTHING;

INSERT INTO project_dw.dim_weather (weather_key, station_icao, observation_ts, site_key)
OVERRIDING SYSTEM VALUE
VALUES (-1, 'UNKNOWN', '1900-01-01T00:00:00Z', -1)
ON CONFLICT (weather_key) DO NOTHING;

INSERT INTO project_dw.dim_airspace_zone (zone_key, source_system, source_object_id, zone_name, site_key)
OVERRIDING SYSTEM VALUE
VALUES (-1, 'UNKNOWN', 'UNKNOWN', 'Unknown zone', -1)
ON CONFLICT (zone_key) DO NOTHING;

-- Repoint identity sequences past the seeded -1 rows so future keys start at 1.
SELECT setval(pg_get_serial_sequence('project_dw.dim_site','site_key'),
              GREATEST(1, (SELECT COALESCE(MAX(site_key),0) FROM project_dw.dim_site)), true);
SELECT setval(pg_get_serial_sequence('project_dw.dim_time','time_key'),
              GREATEST(1, (SELECT COALESCE(MAX(time_key),0) FROM project_dw.dim_time)), true);
SELECT setval(pg_get_serial_sequence('project_dw.dim_vehicle','vehicle_key'),
              GREATEST(1, (SELECT COALESCE(MAX(vehicle_key),0) FROM project_dw.dim_vehicle)), true);
SELECT setval(pg_get_serial_sequence('project_dw.dim_spatial_grid','grid_key'),
              GREATEST(1, (SELECT COALESCE(MAX(grid_key),0) FROM project_dw.dim_spatial_grid)), true);
SELECT setval(pg_get_serial_sequence('project_dw.dim_weather','weather_key'),
              GREATEST(1, (SELECT COALESCE(MAX(weather_key),0) FROM project_dw.dim_weather)), true);
SELECT setval(pg_get_serial_sequence('project_dw.dim_airspace_zone','zone_key'),
              GREATEST(1, (SELECT COALESCE(MAX(zone_key),0) FROM project_dw.dim_airspace_zone)), true);
