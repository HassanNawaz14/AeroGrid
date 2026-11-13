"""WP-11: idempotent dimension refresh from accepted staging rows.

Real members only. Rows that cannot be mapped fall back to the documented -1
unknown member; nothing is invented. Re-running is safe (ON CONFLICT DO NOTHING).
"""
from __future__ import annotations

from typing import Any

from etl.config import SITE_ANCHORS, STATION_SITE_CODES


def _weather_site_case() -> str:
    pairs = sorted(STATION_SITE_CODES.items())
    whens = " ".join(
        f"WHEN '{station}' THEN '{site}'" for station, site in pairs
    )
    return f"CASE w.station_icao {whens} ELSE NULL END"


def _airspace_site_case() -> str:
    """First documented anchor inside the zone bbox, else NULL (-> site -1)."""
    clauses = []
    for site_code, (lat, lon) in SITE_ANCHORS.items():
        clauses.append(
            "WHEN s.bbox_min_lat <= {lat} AND s.bbox_max_lat >= {lat} "
            "AND s.bbox_min_lon <= {lon} AND s.bbox_max_lon >= {lon} "
            "THEN '{site}'".format(lat=lat, lon=lon, site=site_code)
        )
    return "CASE " + " ".join(clauses) + " ELSE NULL END"


TIME_SQL = """
    INSERT INTO project_dw.dim_time (hour_ts, date_utc, hour_utc)
    SELECT hour_ts,
           (hour_ts AT TIME ZONE 'UTC')::date,
           EXTRACT(hour FROM (hour_ts AT TIME ZONE 'UTC'))::smallint
    FROM (
        SELECT DISTINCT
               date_trunc('hour', observation_ts AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'
                   AS hour_ts
        FROM project_staging.stg_weather_metar
        WHERE reject_reason IS NULL AND observation_ts IS NOT NULL
        UNION
        SELECT DISTINCT
               date_trunc('hour', event_ts AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'
        FROM project_staging.stg_uas_position
        WHERE reject_reason IS NULL AND event_ts IS NOT NULL
    ) hours
    WHERE hour_ts IS NOT NULL
    ON CONFLICT (hour_ts) DO NOTHING
"""

VEHICLE_SQL = """
    INSERT INTO project_dw.dim_vehicle
        (source_system, source_entity_id, vehicle_type, first_seen_ts, last_seen_ts)
    SELECT lower(source_system), vehicle_serial, 'UAS',
           min(event_ts), max(event_ts)
    FROM project_staging.stg_uas_position
    WHERE reject_reason IS NULL
      AND vehicle_serial IS NOT NULL
      AND btrim(vehicle_serial) <> ''
    GROUP BY lower(source_system), vehicle_serial
    ON CONFLICT (source_system, source_entity_id) DO NOTHING
"""


def weather_sql() -> str:
    return f"""
    INSERT INTO project_dw.dim_weather
        (station_icao, observation_ts, site_key, temperature_c, wind_speed_kts,
         visibility_m)
    SELECT DISTINCT ON (w.station_icao, w.observation_ts)
           w.station_icao, w.observation_ts, COALESCE(ds.site_key, -1),
           w.temperature_c, w.wind_speed_kts,
           ROUND(w.visibility_sm * 1609.344, 2)
    FROM project_staging.stg_weather_metar w
    LEFT JOIN project_dw.dim_site ds
        ON ds.site_code = {_weather_site_case()}
    WHERE w.reject_reason IS NULL
      AND w.observation_ts IS NOT NULL
    ORDER BY w.station_icao, w.observation_ts, w.etl_run_id DESC
    ON CONFLICT (station_icao, observation_ts) DO NOTHING
    """


def airspace_sql() -> str:
    return f"""
    INSERT INTO project_dw.dim_airspace_zone
        (source_system, source_object_id, zone_name, site_key)
    SELECT DISTINCT ON (s.source_system, s.source_record_id)
           s.source_system, s.source_record_id, s.zone_name,
           COALESCE(ds.site_key, -1)
    FROM project_staging.stg_airspace_zone s
    LEFT JOIN project_dw.dim_site ds
        ON ds.site_code = {_airspace_site_case()}
    WHERE s.reject_reason IS NULL
      AND s.source_record_id IS NOT NULL
    ORDER BY s.source_system, s.source_record_id, s.etl_run_id DESC
    ON CONFLICT (source_system, source_object_id) DO NOTHING
    """


def _execute(conn: Any, sql: str) -> int:
    cur = conn.cursor()
    cur.execute(sql)
    return max(0, int(getattr(cur, "rowcount", 0)))


def refresh_dimensions(conn: Any) -> dict[str, int]:
    return {
        "dim_time": _execute(conn, TIME_SQL),
        "dim_vehicle": _execute(conn, VEHICLE_SQL),
        "dim_weather": _execute(conn, weather_sql()),
        "dim_airspace_zone": _execute(conn, airspace_sql()),
    }


__all__ = [
    "airspace_sql",
    "refresh_dimensions",
    "weather_sql",
]
