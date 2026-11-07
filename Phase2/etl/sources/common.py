from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from etl.errors import RowRejected


def canonical_row(row: dict[str, Any], fields: tuple[str, ...]) -> str:
    return json.dumps(
        {field: row.get(field) for field in fields},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def stable_record_id(
    prefix: str, source_file: str, row: dict[str, Any], fields: tuple[str, ...]
) -> str:
    digest = hashlib.sha256(
        f"{source_file}|{canonical_row(row, fields)}".encode("utf-8")
    ).hexdigest()
    return f"{prefix}:{digest}"


def required_float(
    row: dict[str, Any], field: str, *, record_id: str | None = None
) -> float:
    value = row.get(field)
    if value is None or str(value).strip() == "":
        raise RowRejected("MISSING_REQUIRED_FIELD", field, record_id)
    try:
        return float(str(value).strip())
    except ValueError as exc:
        raise RowRejected("INVALID_NUMERIC", f"{field}: {value!r}", record_id) from exc


def optional_float(
    row: dict[str, Any], field: str, *, record_id: str | None = None
) -> float | None:
    value = row.get(field)
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).strip())
    except ValueError as exc:
        raise RowRejected("INVALID_NUMERIC", f"{field}: {value!r}", record_id) from exc


def parse_bool(value: Any, field: str, *, record_id: str | None = None) -> bool:
    text = str(value).strip().lower()
    if text in {"true", "1", "t", "yes"}:
        return True
    if text in {"false", "0", "f", "no"}:
        return False
    raise RowRejected("INVALID_BOOLEAN", f"{field}: {value!r}", record_id)


def parse_iso_utc(
    value: Any, field: str, *, record_id: str | None = None
) -> datetime:
    text = str(value).strip()
    if not text:
        raise RowRejected("MISSING_REQUIRED_FIELD", field, record_id)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RowRejected("INVALID_TIMESTAMP", f"{field}: {text!r}", record_id) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed = parsed.astimezone(timezone.utc)
    if parsed.year < 2000:
        raise RowRejected("INVALID_TIMESTAMP", f"{field}: {text!r}", record_id)
    return parsed


def validate_coordinates(
    latitude: float, longitude: float, *, record_id: str | None = None
) -> None:
    if not -90.0 <= latitude <= 90.0:
        raise RowRejected("INVALID_COORDINATE", f"Lat: {latitude}", record_id)
    if not -180.0 <= longitude <= 180.0:
        raise RowRejected("INVALID_COORDINATE", f"Lon: {longitude}", record_id)
    if latitude == 0.0 and longitude == 0.0:
        raise RowRejected("ZERO_COORDINATE", "Lat/Lon both zero", record_id)
