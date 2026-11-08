from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etl.errors import RowRejected
from etl.transforms import (
    derive_ceiling_ft,
    derive_flight_category,
    f_to_c,
    hpa_to_inhg,
)

_MISSING = {"M", "T"}


def _optional_float(
    value: Any, *, field: str, record_id: str | None = None
) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text.upper() in _MISSING:
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise RowRejected(
            "INVALID_NUMERIC", f"{field}: {value!r}", record_id
        ) from exc


def _optional_int(
    value: Any, *, field: str, record_id: str | None = None
) -> int | None:
    number = _optional_float(value, field=field, record_id=record_id)
    return None if number is None else int(number)


def _visibility_sm(value: Any, *, record_id: str | None = None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text.upper() in _MISSING:
        return None
    if text.endswith("+"):
        text = text[:-1].strip()
    try:
        return float(text)
    except ValueError as exc:
        raise RowRejected(
            "INVALID_NUMERIC", f"visibility: {value!r}", record_id
        ) from exc


def _awc_layers(clouds: Any) -> list[dict[str, Any]]:
    if not isinstance(clouds, list):
        return []
    return [layer for layer in clouds if isinstance(layer, dict)]


def _iem_layers(row: dict[str, Any], record_id: str | None = None) -> list[dict[str, Any]]:
    layers: list[dict[str, Any]] = []
    for index in range(1, 5):
        cover = str(row.get(f"skyc{index}") or "").strip().upper()
        if cover in {"BKN", "OVC", "VV"}:
            base = _optional_int(
                row.get(f"skyl{index}"), field=f"skyl{index}", record_id=record_id
            )
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
    visibility = _visibility_sm(observation.get("visib"), record_id=source_record_id)
    ceiling = derive_ceiling_ft(_awc_layers(observation.get("clouds")))
    category = observation.get("fltCat") or derive_flight_category(visibility, ceiling)
    wind_direction = observation.get("wdir")
    if isinstance(wind_direction, str):
        wind_direction = (
            None
            if wind_direction.strip().upper() == "VRB"
            else _optional_int(
                wind_direction, field="wdir", record_id=source_record_id
            )
        )

    try:
        observation_ts = datetime.fromtimestamp(
            int(observation["obsTime"]), tz=timezone.utc
        )
    except (KeyError, TypeError, ValueError, OSError) as exc:
        raise RowRejected(
            "INVALID_TIMESTAMP", f"obsTime: {observation.get('obsTime')!r}", source_record_id
        ) from exc

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "AWC",
        "source_record_id": source_record_id,
        "station_icao": str(observation.get("icaoId") or "").strip().upper(),
        "observation_ts": observation_ts,
        "report_type": observation.get("metarType"),
        "raw_text": observation.get("rawOb"),
        "temperature_c": _optional_float(
            observation.get("temp"), field="temp", record_id=source_record_id
        ),
        "dewpoint_c": _optional_float(
            observation.get("dewp"), field="dewp", record_id=source_record_id
        ),
        "wind_speed_kts": _optional_float(
            observation.get("wspd"), field="wspd", record_id=source_record_id
        ),
        "wind_gust_kts": _optional_float(
            observation.get("wgst"), field="wgst", record_id=source_record_id
        ),
        "wind_direction_deg": wind_direction,
        "visibility_sm": visibility,
        "cloud_ceiling_ft": ceiling,
        "altimeter_inhg": hpa_to_inhg(
            _optional_float(
                observation.get("altim"), field="altim", record_id=source_record_id
            )
        ),
        "flight_category": category,
        "station_lat": _optional_float(
            observation.get("lat"), field="lat", record_id=source_record_id
        ),
        "station_lon": _optional_float(
            observation.get("lon"), field="lon", record_id=source_record_id
        ),
        "station_elevation_m": _optional_float(
            observation.get("elev"), field="elev", record_id=source_record_id
        ),
    }


def normalize_iem_row(
    row: dict[str, Any],
    *,
    station_icao: str,
    source_record_id: str,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    visibility = _visibility_sm(row.get("vsby"), record_id=source_record_id)
    ceiling = derive_ceiling_ft(_iem_layers(row, source_record_id))
    speed = _optional_float(
        row.get("sknt"), field="sknt", record_id=source_record_id
    )
    raw_direction = row.get("drct")
    if isinstance(raw_direction, str) and raw_direction.strip().upper() == "VRB":
        direction = None
    else:
        direction = _optional_float(
            raw_direction, field="drct", record_id=source_record_id
        )
    if direction == 0 and speed == 0:
        direction = None

    try:
        observation_ts = datetime.strptime(
            str(row["valid"]).strip(), "%Y-%m-%d %H:%M"
        ).replace(tzinfo=timezone.utc)
    except (KeyError, TypeError, ValueError) as exc:
        raise RowRejected(
            "INVALID_TIMESTAMP", f"valid: {row.get('valid')!r}", source_record_id
        ) from exc

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "IEM",
        "source_record_id": source_record_id,
        "station_icao": station_icao.strip().upper(),
        "observation_ts": observation_ts,
        "report_type": "METAR",
        "raw_text": row.get("metar"),
        "temperature_c": f_to_c(
            _optional_float(
                row.get("tmpf"), field="tmpf", record_id=source_record_id
            )
        ),
        "dewpoint_c": f_to_c(
            _optional_float(
                row.get("dwpf"), field="dwpf", record_id=source_record_id
            )
        ),
        "wind_speed_kts": speed,
        "wind_gust_kts": _optional_float(
            row.get("gust"), field="gust", record_id=source_record_id
        ),
        "wind_direction_deg": None if direction is None else int(direction),
        "visibility_sm": visibility,
        "cloud_ceiling_ft": ceiling,
        "altimeter_inhg": _optional_float(
            row.get("alti"), field="alti", record_id=source_record_id
        ),
        "flight_category": derive_flight_category(visibility, ceiling),
        "station_lat": _optional_float(
            row.get("lat"), field="lat", record_id=source_record_id
        ),
        "station_lon": _optional_float(
            row.get("lon"), field="lon", record_id=source_record_id
        ),
        "station_elevation_m": None,
    }
