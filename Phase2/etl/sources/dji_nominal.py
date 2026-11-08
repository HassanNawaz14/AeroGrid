from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from etl.errors import RowRejected
from etl.sources.common import (
    optional_float,
    parse_bool,
    required_float,
    stable_record_id,
    validate_coordinates,
)
from etl.transforms import mph_to_kts

_FIELDS = (
    "timestamps",
    "timestamps_ns",
    "OSD.flyTime [s]",
    "OSD.latitude",
    "OSD.longitude",
    "OSD.height [ft]",
    "OSD.altitude [ft]",
    "OSD.hSpeed [MPH]",
    "OSD.xSpeed [MPH]",
    "OSD.ySpeed [MPH]",
    "OSD.zSpeed [MPH]",
    "OSD.flycState",
    "OSD.isGPSUsed",
    "OSD.isOnGround",
    "HOME.latitude",
    "HOME.longitude",
    "HOME.height [ft]",
    "RECOVER.aircraftSerial",
    "RECOVER.aircraftName",
)

_MPH_TO_FPS = 5280.0 / 3600.0


def nominal_record_id(source_file: str, row: dict[str, Any]) -> str:
    return stable_record_id("nominal", source_file, row, _FIELDS)


def _parse_epoch_seconds(value: Any, *, record_id: str) -> datetime:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise RowRejected("MISSING_REQUIRED_FIELD", "timestamp", record_id)
    try:
        seconds = float(text)
    except ValueError as exc:
        raise RowRejected("INVALID_TIMESTAMP", f"timestamp: {text!r}", record_id) from exc
    if seconds <= 0:
        raise RowRejected("INVALID_TIMESTAMP", f"timestamp: {text!r}", record_id)
    try:
        parsed = datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise RowRejected("INVALID_TIMESTAMP", f"timestamp: {text!r}", record_id) from exc
    if parsed.year < 2000:
        raise RowRejected("INVALID_TIMESTAMP", f"timestamp: {text!r}", record_id)
    return parsed


def normalize_nominal_row(
    row: dict[str, Any],
    *,
    source_file: str,
    row_number: int,
    etl_run_id: str,
    source_manifest_id: int | None,
    site_code: str | None,
) -> dict[str, Any]:
    record_id = nominal_record_id(source_file, row)
    timestamp_value = row.get("timestamps_ns")
    if timestamp_value is None or str(timestamp_value).strip() == "":
        timestamp_value = row.get("timestamps")
    event_ts = _parse_epoch_seconds(timestamp_value, record_id=record_id)

    latitude = required_float(row, "OSD.latitude", record_id=record_id)
    longitude = required_float(row, "OSD.longitude", record_id=record_id)
    validate_coordinates(latitude, longitude, record_id=record_id)

    altitude_agl = required_float(row, "OSD.height [ft]", record_id=record_id)
    altitude_msl = required_float(row, "OSD.altitude [ft]", record_id=record_id)
    if not -100.0 <= altitude_agl <= 10000.0:
        raise RowRejected("ALTITUDE_OUT_OF_RANGE", f"OSD.height: {altitude_agl}", record_id)

    horizontal_mph = required_float(row, "OSD.hSpeed [MPH]", record_id=record_id)
    vertical_mph = required_float(row, "OSD.zSpeed [MPH]", record_id=record_id)

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "NOMINAL_DJI",
        "source_record_id": record_id,
        "source_file": source_file,
        "source_row_number": row_number,
        "source_flight_id": source_file,
        "event_ts": event_ts,
        "flight_elapsed_sec": required_float(row, "OSD.flyTime [s]", record_id=record_id),
        "serial_number": str(row.get("RECOVER.aircraftSerial") or "").strip() or None,
        "aircraft_name": str(row.get("RECOVER.aircraftName") or "").strip() or None,
        "latitude": latitude,
        "longitude": longitude,
        "altitude_agl_ft": altitude_agl,
        "altitude_msl_ft": altitude_msl,
        "source_speed_mph": horizontal_mph,
        "ground_speed_kts": mph_to_kts(horizontal_mph),
        "source_vertical_speed_mph": vertical_mph,
        "vertical_speed_fps": vertical_mph * _MPH_TO_FPS,
        "flight_state": row.get("OSD.flycState"),
        "is_on_ground": parse_bool(row.get("OSD.isOnGround"), "OSD.isOnGround", record_id=record_id),
        "is_gps_used": parse_bool(row.get("OSD.isGPSUsed"), "OSD.isGPSUsed", record_id=record_id),
        "home_latitude": optional_float(row, "HOME.latitude", record_id=record_id),
        "home_longitude": optional_float(row, "HOME.longitude", record_id=record_id),
        "home_altitude_ft": optional_float(row, "HOME.height [ft]", record_id=record_id),
        "site_code": site_code,
    }
