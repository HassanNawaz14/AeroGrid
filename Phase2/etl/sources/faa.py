from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Iterable

from etl.errors import RowRejected

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _attributes(feature: dict[str, Any]) -> dict[str, Any]:
    attributes = feature.get("properties")
    if attributes is None:
        attributes = feature.get("attributes")
    if not isinstance(attributes, dict):
        raise RowRejected("INVALID_FEATURE", "Missing properties/attributes")
    return attributes


def _iter_positions(value: Any) -> Iterable[tuple[float, float]]:
    if (
        isinstance(value, (list, tuple))
        and len(value) >= 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        yield float(value[0]), float(value[1])
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_positions(item)


def _ring_to_wkt(ring: Any) -> str:
    points = ", ".join(f"{lon} {lat}" for lon, lat in _iter_positions(ring))
    return f"({points})"


def geometry_to_wkt(geometry: dict[str, Any] | None) -> str | None:
    if not geometry:
        return None
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "Point":
        lon, lat = coordinates
        return f"POINT ({lon} {lat})"
    if geometry_type == "LineString":
        points = ", ".join(f"{lon} {lat}" for lon, lat in _iter_positions(coordinates))
        return f"LINESTRING ({points})"
    if geometry_type == "Polygon":
        rings = ", ".join(_ring_to_wkt(ring) for ring in coordinates)
        return f"POLYGON ({rings})"
    if geometry_type == "MultiPolygon":
        polygons = ", ".join(
            f"({', '.join(_ring_to_wkt(ring) for ring in polygon)})"
            for polygon in coordinates
        )
        return f"MULTIPOLYGON ({polygons})"
    return None


def _bbox(geometry: dict[str, Any] | None) -> tuple[float | None, ...]:
    if not geometry:
        return (None, None, None, None)
    positions = list(_iter_positions(geometry.get("coordinates")))
    if not positions:
        return (None, None, None, None)
    longitudes = [position[0] for position in positions]
    latitudes = [position[1] for position in positions]
    return (min(latitudes), min(longitudes), max(latitudes), max(longitudes))


def _parse_limit_ft(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().upper()
    if not text:
        return None
    if text in {"SFC", "SURFACE", "GND", "GROUND"}:
        return 0.0
    match = _NUMBER_RE.search(text)
    return float(match.group(0)) if match else None


def _parse_epoch_ms(value: Any) -> datetime | None:
    if value is None or str(value).strip() == "":
        return None
    return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc)


def _base_record(
    *,
    source_system: str,
    source_record_id: str,
    feature_type: str,
    service_name: str,
    attributes: dict[str, Any],
    geometry: dict[str, Any] | None,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    bbox_min_lat, bbox_min_lon, bbox_max_lat, bbox_max_lon = _bbox(geometry)
    return {
        "etl_run_id": etl_run_id,
        "source_manifest_id": source_manifest_id,
        "source_system": source_system,
        "source_record_id": source_record_id,
        "feature_type": feature_type,
        "service_name": service_name,
        "name": None,
        "ident": None,
        "icao_id": None,
        "type_code": None,
        "class_code": None,
        "local_type": None,
        "airport_icao": None,
        "lower_limit_ft": None,
        "upper_limit_ft": None,
        "lower_desc": None,
        "upper_desc": None,
        "lower_uom": None,
        "upper_uom": None,
        "active_start_ts": None,
        "active_end_ts": None,
        "alert_ts": None,
        "geometry_wkt": geometry_to_wkt(geometry),
        "bbox_min_lat": bbox_min_lat,
        "bbox_min_lon": bbox_min_lon,
        "bbox_max_lat": bbox_max_lat,
        "bbox_max_lon": bbox_max_lon,
        "raw_attributes": attributes,
    }


def normalize_airspace_feature(
    feature: dict[str, Any],
    *,
    service_name: str,
    feature_type: str,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    attributes = _attributes(feature)
    record_id = str(attributes.get("GLOBAL_ID") or "").strip()
    if not record_id:
        raise RowRejected("MISSING_NATURAL_KEY", "GLOBAL_ID")
    record = _base_record(
        source_system="FAA_AIRSPACE",
        source_record_id=record_id,
        feature_type=feature_type,
        service_name=service_name,
        attributes=attributes,
        geometry=feature.get("geometry"),
        etl_run_id=etl_run_id,
        source_manifest_id=source_manifest_id,
    )
    record.update(
        {
            "name": attributes.get("NAME"),
            "ident": attributes.get("IDENT"),
            "icao_id": attributes.get("ICAO_ID"),
            "type_code": attributes.get("TYPE_CODE"),
            "class_code": attributes.get("CLASS"),
            "local_type": attributes.get("LOCAL_TYPE"),
            "lower_limit_ft": _parse_limit_ft(attributes.get("LOWER_VAL")),
            "upper_limit_ft": _parse_limit_ft(attributes.get("UPPER_VAL")),
            "lower_desc": attributes.get("LOWER_DESC"),
            "upper_desc": attributes.get("UPPER_DESC"),
            "lower_uom": attributes.get("LOWER_UOM"),
            "upper_uom": attributes.get("UPPER_UOM"),
        }
    )
    return record


def normalize_facility_feature(
    feature: dict[str, Any],
    *,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    attributes = _attributes(feature)
    record_id = str(attributes.get("GLOBALID") or "").strip()
    if not record_id:
        raise RowRejected("MISSING_NATURAL_KEY", "GLOBALID")
    record = _base_record(
        source_system="FAA_FACILITY",
        source_record_id=record_id,
        feature_type="FACILITY_MAP",
        service_name="FAA_UAS_FacilityMap_Data_V5",
        attributes=attributes,
        geometry=feature.get("geometry"),
        etl_run_id=etl_run_id,
        source_manifest_id=source_manifest_id,
    )
    ceiling = _parse_limit_ft(attributes.get("CEILING"))
    record.update(
        {
            "name": attributes.get("APT1_NAME"),
            "airport_icao": attributes.get("APT1_ICAO"),
            "lower_limit_ft": 0.0,
            "upper_limit_ft": ceiling,
            "upper_uom": attributes.get("UNIT"),
            "grid_latitude": attributes.get("LATITUDE"),
            "grid_longitude": attributes.get("LONGITUDE"),
            "map_effective_text": attributes.get("MAP_EFF"),
            "last_edit_text": attributes.get("LAST_EDIT"),
        }
    )
    return record


def normalize_tfr_feature(
    feature: dict[str, Any],
    *,
    etl_run_id: str,
    source_manifest_id: int | None,
) -> dict[str, Any]:
    attributes = _attributes(feature)
    record_id = str(attributes.get("FAA_ID") or "").strip()
    if not record_id:
        raise RowRejected("MISSING_NATURAL_KEY", "FAA_ID")
    record = _base_record(
        source_system="FAA_TFR",
        source_record_id=record_id,
        feature_type="TFR",
        service_name="Part_Time_National_Security_UAS_Flight_Restrictions",
        attributes=attributes,
        geometry=feature.get("geometry"),
        etl_run_id=etl_run_id,
        source_manifest_id=source_manifest_id,
    )
    record.update(
        {
            "name": attributes.get("Facility"),
            "facility": attributes.get("Facility"),
            "base": attributes.get("Base"),
            "reason": attributes.get("Reason"),
            "floor_text": attributes.get("Floor"),
            "ceiling_text": attributes.get("Ceiling"),
            "lower_limit_ft": _parse_limit_ft(attributes.get("Floor")),
            "upper_limit_ft": _parse_limit_ft(attributes.get("Ceiling")),
            "alert_ts": _parse_epoch_ms(attributes.get("ALERTTIME")),
            "active_start_ts": _parse_epoch_ms(attributes.get("ACTIVETIME")),
            "active_end_ts": _parse_epoch_ms(attributes.get("ENDTIME")),
        }
    )
    return record
