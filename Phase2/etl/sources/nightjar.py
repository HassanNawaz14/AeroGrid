from __future__ import annotations

from math import hypot
from typing import Any

from etl.errors import RowRejected
from etl.sources.common import (
    optional_float,
    parse_bool,
    parse_iso_utc,
    required_float,
    stable_record_id,
    validate_coordinates,
)
from etl.transforms import mps_to_kts

_FIELDS = (
    "CUSTOM.dateTime",
    "OSD.flyTime",
    "OSD.latitude",
    "OSD.longitude",
    "OSD.height",
    "OSD.altitude",
    "OSD.xSpeed",
    "OSD.ySpeed",
    "OSD.zSpeed",
    "OSD.flycState",
    "OSD.isOnGround",
    "OSD.isMotorOn",
    "OSD.isGPSUsed",
    "HOME.latitude",
    "HOME.longitude",
    "HOME.altitude",
    "RECOVER.aircraftSerial",
    "RECOVER.aircraftName",
)


def nightjar_record_id(source_file: str, row: dict[str, Any]) -> str:
    return stable_record_id("nightjar", source_file, row, _FIELDS)


def normalize_nightjar_row(
    row: dict[str, Any],
    *,
    source_file: str,
    row_number: int,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    record_id = nightjar_record_id(source_file, row)
    event_ts = parse_iso_utc(row.get("CUSTOM.dateTime"), "CUSTOM.dateTime", record_id=record_id)

    latitude = required_float(row, "OSD.latitude", record_id=record_id)
    longitude = required_float(row, "OSD.longitude", record_id=record_id)
    validate_coordinates(latitude, longitude, record_id=record_id)

    altitude_agl = required_float(row, "OSD.height", record_id=record_id)
    altitude_msl = required_float(row, "OSD.altitude", record_id=record_id)
    home_altitude = optional_float(row, "HOME.altitude", record_id=record_id)
    if home_altitude is None or home_altitude <= 0:
        altitude_msl = None
    if not -100.0 <= altitude_agl <= 10000.0:
        raise RowRejected("ALTITUDE_OUT_OF_RANGE", f"OSD.height: {altitude_agl}", record_id)

    horizontal_mps = hypot(
        required_float(row, "OSD.xSpeed", record_id=record_id),
        required_float(row, "OSD.ySpeed", record_id=record_id),
    )
    vertical_mps = required_float(row, "OSD.zSpeed", record_id=record_id)

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "NIGHTJAR",
        "source_record_id": record_id,
        "source_file": source_file,
        "source_row_number": row_number,
        "source_flight_id": source_file,
        "event_ts": event_ts,
        "flight_elapsed_sec": required_float(row, "OSD.flyTime", record_id=record_id),
        "serial_number": str(row.get("RECOVER.aircraftSerial") or "").strip() or None,
        "aircraft_name": str(row.get("RECOVER.aircraftName") or "").strip() or None,
        "latitude": latitude,
        "longitude": longitude,
        "altitude_agl_ft": altitude_agl,
        "altitude_msl_ft": altitude_msl,
        "source_speed_mps": horizontal_mps,
        "ground_speed_kts": mps_to_kts(horizontal_mps),
        "source_vertical_speed_mps": vertical_mps,
        "vertical_speed_fps": vertical_mps * 3.280839895,
        "flight_state": row.get("OSD.flycState"),
        "is_on_ground": parse_bool(row.get("OSD.isOnGround"), "OSD.isOnGround", record_id=record_id),
        "is_motor_on": parse_bool(row.get("OSD.isMotorOn"), "OSD.isMotorOn", record_id=record_id),
        "is_gps_used": parse_bool(row.get("OSD.isGPSUsed"), "OSD.isGPSUsed", record_id=record_id),
        "home_latitude": optional_float(row, "HOME.latitude", record_id=record_id),
        "home_longitude": optional_float(row, "HOME.longitude", record_id=record_id),
        "home_altitude_ft": home_altitude,
        "site_code": "NIGHTJAR_PA",
    }
