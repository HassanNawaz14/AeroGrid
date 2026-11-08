-- WP-05 dimension seeds (Member C). Idempotent: safe to rerun.
-- Seeds are derived from approved real sources only (WP-03 findings):
--   - dim_time: deterministic hourly spine over 2022-01-01..2022-01-07 (derived,
--     not synthetic source records) -- satisfies the >=100 row floor.
--   - dim_site: site codes KBTP, KAGC, NIGHTJAR_PA, DJI_CO (WP-03 source findings).
--   - Unresolved DJI site mapping stays null and maps to dim_site(-1).
--   - dim_vehicle / dim_spatial_grid / dim_weather / dim_airspace_zone: seeded only
--     with their -1 unknown member; real rows come from approved source loads in later
--     work packages (no invented sites, vehicles, zones, or weather rows).

INSERT INTO project_dw.dim_site (site_key, site_code, site_name)
OVERRIDING SYSTEM VALUE
VALUES
  (1, 'KBTP', 'Kyle City Airport / Pittsburgh Butler'),
  (2, 'KAGC', 'Allegheny County Airport'),
  (3, 'NIGHTJAR_PA', 'Nightjar study site, Pennsylvania'),
  (4, 'DJI_CO', 'DJI site, Colorado (mapping unresolved; optional keys map to -1)')
ON CONFLICT (site_code) DO UPDATE
SET site_name = EXCLUDED.site_name;

INSERT INTO project_dw.dim_time (hour_ts, date_utc, hour_utc)
SELECT
  gs,
  gs::date,
  EXTRACT(hour FROM gs)::smallint
FROM generate_series(
  TIMESTAMPTZ '2022-01-01 00:00:00+00',
  TIMESTAMPTZ '2022-01-07 23:00:00+00',
  INTERVAL '1 hour'
) AS gs
ON CONFLICT (hour_ts) DO NOTHING;

-- Advance identity sequences past explicitly seeded keys so future DEFAULT inserts
-- never collide with seeded rows. Idempotent: safe to rerun.
SELECT setval(pg_get_serial_sequence('project_dw.dim_site','site_key'),
              GREATEST(1, (SELECT COALESCE(MAX(site_key),0) FROM project_dw.dim_site)), true);
