from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etl.transforms import (
    derive_ceiling_ft,
    derive_flight_category,
    f_to_c,
    hpa_to_inhg,
    parse_visibility_sm,
)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text.upper() in {"M", "T", "VRB"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _optional_int(value: Any) -> int | None:
    number = _optional_float(value)
    return None if number is None else int(number)


def _awc_layers(clouds: Any) -> list[dict[str, Any]]:
    if not isinstance(clouds, list):
        return []
    return [layer for layer in clouds if isinstance(layer, dict)]


def _iem_layers(row: dict[str, Any]) -> list[dict[str, Any]]:
    layers: list[dict[str, Any]] = []
    for index in range(1, 5):
        cover = str(row.get(f"skyc{index}") or "").strip().upper()
        if cover in {"BKN", "OVC", "VV"}:
            base = _optional_int(row.get(f"skyl{index}"))
            if base is not None:
                layers.append({"cover": cover, "base": base})
    return layers


def normalize_awc_observation(
    observation: dict[str, Any],
    *,
    source_record_id: str,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    visibility = parse_visibility_sm(observation.get("visib"))
    ceiling = derive_ceiling_ft(_awc_layers(observation.get("clouds")))
    category = observation.get("fltCat") or derive_flight_category(visibility, ceiling)
    wind_direction = observation.get("wdir")
    if isinstance(wind_direction, str):
        wind_direction = None if wind_direction.strip().upper() == "VRB" else _optional_int(
            wind_direction
        )

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "AWC",
        "source_record_id": source_record_id,
        "station_icao": str(observation.get("icaoId") or "").strip().upper(),
        "observation_ts": datetime.fromtimestamp(
            int(observation["obsTime"]), tz=timezone.utc
        ),
        "report_type": observation.get("metarType"),
        "raw_text": observation.get("rawOb"),
        "temperature_c": _optional_float(observation.get("temp")),
        "dewpoint_c": _optional_float(observation.get("dewp")),
        "wind_speed_kts": _optional_float(observation.get("wspd")),
        "wind_gust_kts": _optional_float(observation.get("wgst")),
        "wind_direction_deg": _optional_int(wind_direction),
        "visibility_sm": visibility,
        "cloud_ceiling_ft": ceiling,
        "altimeter_inhg": hpa_to_inhg(_optional_float(observation.get("altim"))),
        "flight_category": category,
        "station_lat": _optional_float(observation.get("lat")),
        "station_lon": _optional_float(observation.get("lon")),
        "station_elevation_m": _optional_float(observation.get("elev")),
    }


def normalize_iem_row(
    row: dict[str, Any],
    *,
    station_icao: str,
    source_record_id: str,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    visibility = parse_visibility_sm(row.get("vsby"))
    ceiling = derive_ceiling_ft(_iem_layers(row))
    speed = _optional_float(row.get("sknt"))
    direction = _optional_float(row.get("drct"))
    if direction == 0 and speed == 0:
        direction = None

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "IEM",
        "source_record_id": source_record_id,
        "station_icao": station_icao.strip().upper(),
        "observation_ts": datetime.strptime(
            str(row["valid"]).strip(), "%Y-%m-%d %H:%M"
        ).replace(tzinfo=timezone.utc),
        "report_type": "METAR",
        "raw_text": row.get("metar"),
        "temperature_c": f_to_c(_optional_float(row.get("tmpf"))),
        "dewpoint_c": f_to_c(_optional_float(row.get("dwpf"))),
        "wind_speed_kts": speed,
        "wind_gust_kts": _optional_float(row.get("gust")),
        "wind_direction_deg": None if direction is None else int(direction),
        "visibility_sm": visibility,
        "cloud_ceiling_ft": ceiling,
        "altimeter_inhg": _optional_float(row.get("alti")),
        "flight_category": derive_flight_category(visibility, ceiling),
        "station_lat": _optional_float(row.get("lat")),
        "station_lon": _optional_float(row.get("lon")),
        "station_elevation_m": None,
    }
