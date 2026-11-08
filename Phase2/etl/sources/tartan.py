from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from etl.errors import RowRejected

_FIELDS = (
    "ID",
    "Time",
    "Date",
    "Altitude",
    "Speed",
    "Heading",
    "Lat",
    "Lon",
    "Age",
    "Range",
    "Bearing",
    "Tail",
    "AltisGNSS",
)


def _canonical_row(row: dict[str, Any]) -> str:
    return json.dumps(
        {field: row.get(field) for field in _FIELDS},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def tartan_record_id(source_file: str, row: dict[str, Any]) -> str:
    digest = hashlib.sha256(
        f"{source_file}|{_canonical_row(row)}".encode("utf-8")
    ).hexdigest()
    return f"tartan:{digest}"


def _parse_list(value: Any, field: str, record_id: str | None = None) -> list[Any]:
    try:
        parsed = ast.literal_eval(str(value))
    except (ValueError, SyntaxError) as exc:
        raise RowRejected("INVALID_TIMESTAMP", f"{field}: {value!r}", record_id) from exc
    if not isinstance(parsed, list):
        raise RowRejected("INVALID_TIMESTAMP", f"{field}: {value!r}", record_id)
    return parsed


def parse_tartan_timestamp(
    date_value: Any, time_value: Any, record_id: str | None = None
) -> datetime:
    date_parts = _parse_list(date_value, "Date", record_id)
    time_parts = _parse_list(time_value, "Time", record_id)
    if len(date_parts) < 3 or len(time_parts) < 3:
        raise RowRejected(
            "INVALID_TIMESTAMP", "Date/Time list is too short", record_id
        )
    try:
        year, month, day = (int(part) for part in date_parts[:3])
        hour, minute = int(time_parts[0]), int(time_parts[1])
        seconds = float(time_parts[2])
    except (TypeError, ValueError) as exc:
        raise RowRejected(
            "INVALID_TIMESTAMP", "Date/Time contains non-numeric parts", record_id
        ) from exc

    whole_seconds = int(seconds)
    microseconds = int(round((seconds - whole_seconds) * 1_000_000))
    try:
        return datetime(
            year,
            month,
            day,
            hour,
            minute,
            whole_seconds,
            microseconds,
            tzinfo=timezone.utc,
        )
    except ValueError as exc:
        raise RowRejected("INVALID_TIMESTAMP", str(exc), record_id) from exc


def _required_float(
    row: dict[str, Any], field: str, record_id: str | None = None
) -> float:
    value = row.get(field)
    if value is None or str(value).strip() == "":
        raise RowRejected("MISSING_REQUIRED_FIELD", field, record_id)
    try:
        return float(str(value).strip())
    except ValueError as exc:
        raise RowRejected("INVALID_NUMERIC", f"{field}: {value!r}", record_id) from exc


def _optional_float(
    row: dict[str, Any], field: str, record_id: str | None = None
) -> float | None:
    value = row.get(field)
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).strip())
    except ValueError as exc:
        raise RowRejected("INVALID_NUMERIC", f"{field}: {value!r}", record_id) from exc


def _parse_bool(value: Any, record_id: str | None = None) -> bool:
    text = str(value).strip().lower()
    if text in {"true", "1", "t", "yes"}:
        return True
    if text in {"false", "0", "f", "no"}:
        return False
    raise RowRejected("INVALID_BOOLEAN", f"AltisGNSS: {value!r}", record_id)


def normalize_tartan_row(
    row: dict[str, Any],
    *,
    source_file: str,
    row_number: int,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    record_id = tartan_record_id(source_file, row)
    try:
        icao24 = int(str(row.get("ID", "")).strip())
    except ValueError as exc:
        raise RowRejected("INVALID_VEHICLE_ID", f"ID: {row.get('ID')!r}", record_id) from exc
    if not 0 <= icao24 <= 0xFFFFFF:
        raise RowRejected("INVALID_VEHICLE_ID", f"ID: {icao24}", record_id)

    event_ts = parse_tartan_timestamp(row.get("Date"), row.get("Time"), record_id)
    latitude = _required_float(row, "Lat", record_id)
    longitude = _required_float(row, "Lon", record_id)
    if not -90.0 <= latitude <= 90.0:
        raise RowRejected("INVALID_COORDINATE", f"Lat: {latitude}", record_id)
    if not -180.0 <= longitude <= 180.0:
        raise RowRejected("INVALID_COORDINATE", f"Lon: {longitude}", record_id)
    if latitude == 0.0 and longitude == 0.0:
        raise RowRejected("ZERO_COORDINATE", "Lat/Lon both zero", record_id)

    altitude_ft = _required_float(row, "Altitude", record_id)
    if not -1500.0 <= altitude_ft <= 60000.0:
        raise RowRejected(
            "ALTITUDE_OUT_OF_RANGE", f"Altitude: {altitude_ft}", record_id
        )

    speed = _optional_float(row, "Speed", record_id)
    if speed is not None and not 0.0 <= speed <= 1000.0:
        raise RowRejected("SPEED_OUT_OF_RANGE", f"Speed: {speed}", record_id)
    heading = _optional_float(row, "Heading", record_id)
    if heading is not None and not 0.0 <= heading < 360.0:
        raise RowRejected("HEADING_OUT_OF_RANGE", f"Heading: {heading}", record_id)

    range_km = _required_float(row, "Range", record_id)
    if range_km < 0.0:
        raise RowRejected("RANGE_OUT_OF_RANGE", f"Range: {range_km}", record_id)
    bearing = _required_float(row, "Bearing", record_id)
    if not -180.0 <= bearing <= 180.0:
        raise RowRejected("BEARING_OUT_OF_RANGE", f"Bearing: {bearing}", record_id)

    altis_gnss = _parse_bool(row.get("AltisGNSS"), record_id)
    callsign = str(row.get("Tail") or "").strip() or None

    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": "TARTAN",
        "source_record_id": record_id,
        "source_file": source_file,
        "source_row_number": row_number,
        "event_ts": event_ts,
        "raw_date_text": str(row.get("Date")),
        "raw_time_text": str(row.get("Time")),
        "icao24_int": icao24,
        "icao24_hex": f"{icao24:06X}",
        "callsign": callsign,
        "latitude": latitude,
        "longitude": longitude,
        "altitude_ft": altitude_ft,
        "altitude_source": f"TARTAN_ALTISGNSS_{str(altis_gnss).upper()}",
        "ground_speed_kts": speed,
        "heading_deg": heading,
        "age_s": _required_float(row, "Age", record_id),
        "range_km": range_km,
        "bearing_deg": bearing,
        "altis_gnss": altis_gnss,
        "site_code": "KBTP",
    }
