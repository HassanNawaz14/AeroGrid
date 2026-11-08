from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from etl.sources.dji_nominal import normalize_nominal_row
from etl.sources.faa import (
    normalize_airspace_feature,
    normalize_facility_feature,
    normalize_tfr_feature,
)
from etl.sources.metar import normalize_awc_observation, normalize_iem_row
from etl.sources.nightjar import normalize_nightjar_row
from etl.sources.tartan import normalize_tartan_row
from etl.staging_writer import insert_on_conflict_do_nothing

TARTAN_COLUMNS = (
    "etl_run_id",
    "source_manifest_id",
    "source_system",
    "source_record_id",
    "source_row_number",
    "event_ts",
    "icao24",
    "callsign",
    "latitude",
    "longitude",
    "altitude_ft",
    "altitude_source",
    "ground_speed_kts",
    "heading_deg",
    "on_ground",
    "raw_file",
    "source_quality_flag",
)

UAS_COLUMNS = (
    "etl_run_id",
    "source_manifest_id",
    "source_system",
    "source_record_id",
    "source_row_number",
    "event_ts",
    "vehicle_serial",
    "flight_id",
    "latitude",
    "longitude",
    "altitude_msl_ft",
    "altitude_agl_ft",
    "ground_speed_kts",
    "vertical_speed_fps",
    "flight_state",
    "is_on_ground",
    "is_motor_on",
    "is_gps_used",
    "home_latitude",
    "home_longitude",
    "home_altitude_ft",
    "source_speed_value",
    "source_speed_unit",
    "raw_file",
)

WEATHER_COLUMNS = (
    "etl_run_id",
    "source_manifest_id",
    "source_system",
    "source_record_id",
    "source_row_number",
    "station_icao",
    "observation_ts",
    "report_type",
    "raw_text",
    "flight_category",
    "temperature_c",
    "dewpoint_c",
    "wind_speed_kts",
    "wind_gust_kts",
    "wind_direction_deg",
    "visibility_sm",
    "cloud_ceiling_ft",
    "altimeter_inhg",
    "station_lat",
    "station_lon",
    "station_elevation_m",
)

AIRSPACE_COLUMNS = (
    "etl_run_id",
    "source_manifest_id",
    "source_system",
    "source_record_id",
    "source_object_id",
    "source_row_number",
    "service_name",
    "restriction_id",
    "zone_name",
    "airport_icao",
    "restriction_type",
    "lower_limit_ft",
    "upper_limit_ft",
    "effective_start_ts",
    "effective_end_ts",
    "is_static",
    "geometry_wkt",
    "bbox_min_lat",
    "bbox_min_lon",
    "bbox_max_lat",
    "bbox_max_lon",
    "source_url",
    "raw_attributes",
)


def _logical_source_file(path: str | Path, source_file: str | None) -> str:
    return source_file or Path(path).name


def iter_tartan_csv(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            row["_source_row_number"] = row_number
            yield row


def iter_nightjar_csv(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            row["_source_row_number"] = row_number
            yield row


def iter_nominal_csv(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            row["_source_row_number"] = row_number
            yield row


def iter_awc_json(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        observations = json.load(handle)
    for row_number, obs in enumerate(observations, start=1):
        obs["_source_row_number"] = row_number
        yield obs


def iter_iem_csv(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            row["_source_row_number"] = row_number
            yield row


def iter_faa_geojson(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    features = payload.get("features", []) if isinstance(payload, dict) else payload
    for row_number, feature in enumerate(features, start=1):
        feature["_source_row_number"] = row_number
        yield feature


def tartan_staging_row(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "etl_run_id": record.get("etl_run_id"),
        "source_manifest_id": record.get("source_manifest_id"),
        "source_system": record.get("source_system"),
        "source_record_id": record.get("source_record_id"),
        "source_row_number": record.get("source_row_number"),
        "event_ts": record.get("event_ts"),
        "icao24": record.get("icao24_hex"),
        "callsign": record.get("callsign"),
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "altitude_ft": record.get("altitude_ft"),
        "altitude_source": record.get("altitude_source"),
        "ground_speed_kts": record.get("ground_speed_kts"),
        "heading_deg": record.get("heading_deg"),
        "on_ground": None,
        "raw_file": record.get("source_file"),
        "source_quality_flag": (
            f"ALTISGNSS_{str(record.get('altis_gnss')).upper()}"
            if record.get("altis_gnss") is not None
            else None
        ),
    }


def uas_staging_row(record: Mapping[str, Any]) -> dict[str, Any]:
    speed_value = record.get("source_speed_mps")
    speed_unit = "m/s"
    if speed_value is None:
        speed_value = record.get("source_speed_mph")
        speed_unit = "mph"
    return {
        "etl_run_id": record.get("etl_run_id"),
        "source_manifest_id": record.get("source_manifest_id"),
        "source_system": record.get("source_system"),
        "source_record_id": record.get("source_record_id"),
        "source_row_number": record.get("source_row_number"),
        "event_ts": record.get("event_ts"),
        "vehicle_serial": record.get("serial_number"),
        "flight_id": record.get("source_flight_id"),
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "altitude_msl_ft": record.get("altitude_msl_ft"),
        "altitude_agl_ft": record.get("altitude_agl_ft"),
        "ground_speed_kts": record.get("ground_speed_kts"),
        "vertical_speed_fps": record.get("vertical_speed_fps"),
        "flight_state": record.get("flight_state"),
        "is_on_ground": record.get("is_on_ground"),
        "is_motor_on": record.get("is_motor_on"),
        "is_gps_used": record.get("is_gps_used"),
        "home_latitude": record.get("home_latitude"),
        "home_longitude": record.get("home_longitude"),
        "home_altitude_ft": record.get("home_altitude_ft"),
        "source_speed_value": speed_value,
        "source_speed_unit": speed_unit,
        "raw_file": record.get("source_file"),
    }


def weather_staging_row(
    record: Mapping[str, Any], *, source_row_number: int | None = None
) -> dict[str, Any]:
    return {
        "etl_run_id": record.get("etl_run_id"),
        "source_manifest_id": record.get("source_manifest_id"),
        "source_system": record.get("source_system"),
        "source_record_id": record.get("source_record_id"),
        "source_row_number": source_row_number
        if source_row_number is not None
        else record.get("source_row_number"),
        "station_icao": record.get("station_icao"),
        "observation_ts": record.get("observation_ts"),
        "report_type": record.get("report_type"),
        "raw_text": record.get("raw_text"),
        "flight_category": record.get("flight_category"),
        "temperature_c": record.get("temperature_c"),
        "dewpoint_c": record.get("dewpoint_c"),
        "wind_speed_kts": record.get("wind_speed_kts"),
        "wind_gust_kts": record.get("wind_gust_kts"),
        "wind_direction_deg": record.get("wind_direction_deg"),
        "visibility_sm": record.get("visibility_sm"),
        "cloud_ceiling_ft": record.get("cloud_ceiling_ft"),
        "altimeter_inhg": record.get("altimeter_inhg"),
        "station_lat": record.get("station_lat"),
        "station_lon": record.get("station_lon"),
        "station_elevation_m": record.get("station_elevation_m"),
    }


def _jsonb_value(value: Any) -> Any:
    if value is None or isinstance(value, str):
        return value
    try:
        from psycopg.types.json import Jsonb

        return Jsonb(value)
    except ImportError:
        return json.dumps(value, default=str, ensure_ascii=False)


def airspace_staging_row(record: Mapping[str, Any]) -> dict[str, Any]:
    feature_type = record.get("feature_type")
    raw_attributes = _jsonb_value(record.get("raw_attributes"))
    return {
        "etl_run_id": record.get("etl_run_id"),
        "source_manifest_id": record.get("source_manifest_id"),
        "source_system": record.get("source_system"),
        "source_record_id": record.get("source_record_id"),
        "source_object_id": record.get("source_record_id"),
        "source_row_number": record.get("source_row_number"),
        "service_name": record.get("service_name"),
        "restriction_id": record.get("ident") or record.get("source_record_id"),
        "zone_name": record.get("name"),
        "airport_icao": record.get("airport_icao"),
        "restriction_type": feature_type,
        "lower_limit_ft": record.get("lower_limit_ft"),
        "upper_limit_ft": record.get("upper_limit_ft"),
        "effective_start_ts": record.get("active_start_ts")
        or record.get("effective_start_ts"),
        "effective_end_ts": record.get("active_end_ts")
        or record.get("effective_end_ts"),
        "is_static": feature_type != "TFR",
        "geometry_wkt": record.get("geometry_wkt"),
        "bbox_min_lat": record.get("bbox_min_lat"),
        "bbox_min_lon": record.get("bbox_min_lon"),
        "bbox_max_lat": record.get("bbox_max_lat"),
        "bbox_max_lon": record.get("bbox_max_lon"),
        "source_url": record.get("source_url"),
        "raw_attributes": raw_attributes,
    }


def _with_source_row_number(
    record: Mapping[str, Any], raw: Mapping[str, Any]
) -> dict[str, Any]:
    mapped = dict(record)
    mapped["source_row_number"] = raw.get("_source_row_number")
    return mapped


def _load(
    conn: Any,
    *,
    table: str,
    columns: tuple[str, ...],
    rows: Iterator[Mapping[str, Any]],
    normalizer: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    row_mapper: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    conflict_target: str,
    source_system: str,
    source_file: str,
    etl_run_id: Any,
) -> Any:
    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        record = normalizer(raw)
        return _with_source_row_number(record, raw)

    return insert_on_conflict_do_nothing(
        conn,
        table=table,
        columns=columns,
        rows=rows,
        conflict_target=conflict_target,
        etl_run_id=etl_run_id,
        source_system=source_system,
        normalizer=normalize,
        row_mapper=row_mapper,
        source_file=source_file,
    )


def load_tartan(
    conn: Any,
    path: str | Path,
    *,
    etl_run_id: Any,
    source_file: str | None = None,
    source_manifest_id: int | None = None,
) -> Any:
    logical = _logical_source_file(path, source_file)

    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        return normalize_tartan_row(
            dict(raw),
            source_file=logical,
            row_number=int(raw["_source_row_number"]),
            etl_run_id=etl_run_id,
            source_manifest_id=source_manifest_id,
        )

    return _load(
        conn,
        table="project_staging.stg_adsb_position",
        columns=TARTAN_COLUMNS,
        rows=iter_tartan_csv(path),
        normalizer=normalize,
        row_mapper=tartan_staging_row,
        conflict_target="(source_system, source_record_id)",
        source_system="TARTAN",
        source_file=logical,
        etl_run_id=etl_run_id,
    )


def load_nightjar(
    conn: Any,
    path: str | Path,
    *,
    etl_run_id: Any,
    source_file: str | None = None,
    source_manifest_id: int | None = None,
) -> Any:
    logical = _logical_source_file(path, source_file)

    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        return normalize_nightjar_row(
            dict(raw),
            source_file=logical,
            row_number=int(raw["_source_row_number"]),
            etl_run_id=etl_run_id,
            source_manifest_id=source_manifest_id,
        )

    return _load(
        conn,
        table="project_staging.stg_uas_position",
        columns=UAS_COLUMNS,
        rows=iter_nightjar_csv(path),
        normalizer=normalize,
        row_mapper=uas_staging_row,
        conflict_target="(source_system, source_record_id)",
        source_system="NIGHTJAR",
        source_file=logical,
        etl_run_id=etl_run_id,
    )


def load_nominal(
    conn: Any,
    path: str | Path,
    *,
    etl_run_id: Any,
    site_code: str | None,
    source_file: str | None = None,
    source_manifest_id: int | None = None,
) -> Any:
    logical = _logical_source_file(path, source_file)

    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        return normalize_nominal_row(
            dict(raw),
            source_file=logical,
            row_number=int(raw["_source_row_number"]),
            etl_run_id=etl_run_id,
            source_manifest_id=source_manifest_id,
            site_code=site_code,
        )

    return _load(
        conn,
        table="project_staging.stg_uas_position",
        columns=UAS_COLUMNS,
        rows=iter_nominal_csv(path),
        normalizer=normalize,
        row_mapper=uas_staging_row,
        conflict_target="(source_system, source_record_id)",
        source_system="NOMINAL_DJI",
        source_file=logical,
        etl_run_id=etl_run_id,
    )


def load_awc(
    conn: Any,
    path: str | Path,
    *,
    etl_run_id: Any,
    source_file: str | None = None,
    source_manifest_id: int | None = None,
) -> Any:
    logical = _logical_source_file(path, source_file)

    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        station = str(raw.get("icaoId") or "").strip().upper()
        obs_time = raw.get("obsTime")
        return normalize_awc_observation(
            dict(raw),
            source_record_id=f"awc:{station}:{obs_time}",
            etl_run_id=etl_run_id,
            source_manifest_id=source_manifest_id,
        )

    return _load(
        conn,
        table="project_staging.stg_weather_metar",
        columns=WEATHER_COLUMNS,
        rows=iter_awc_json(path),
        normalizer=normalize,
        row_mapper=lambda record: weather_staging_row(
            record, source_row_number=record.get("source_row_number")
        ),
        conflict_target="(station_icao, observation_ts, source_system)",
        source_system="AWC",
        source_file=logical,
        etl_run_id=etl_run_id,
    )


def load_iem(
    conn: Any,
    path: str | Path,
    *,
    station_icao: str,
    etl_run_id: Any,
    source_file: str | None = None,
    source_manifest_id: int | None = None,
) -> Any:
    logical = _logical_source_file(path, source_file)

    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        valid = str(raw.get("valid") or "").strip()
        return normalize_iem_row(
            dict(raw),
            station_icao=station_icao,
            source_record_id=f"iem:{station_icao}:{valid}",
            etl_run_id=etl_run_id,
            source_manifest_id=source_manifest_id,
        )

    return _load(
        conn,
        table="project_staging.stg_weather_metar",
        columns=WEATHER_COLUMNS,
        rows=iter_iem_csv(path),
        normalizer=normalize,
        row_mapper=lambda record: weather_staging_row(
            record, source_row_number=record.get("source_row_number")
        ),
        conflict_target="(station_icao, observation_ts, source_system)",
        source_system="IEM",
        source_file=logical,
        etl_run_id=etl_run_id,
    )


def load_faa(
    conn: Any,
    path: str | Path,
    *,
    kind: str,
    service_name: str,
    etl_run_id: Any,
    feature_type: str | None = None,
    source_file: str | None = None,
    source_manifest_id: int | None = None,
) -> Any:
    logical = _logical_source_file(path, source_file)

    def normalize(raw: Mapping[str, Any]) -> Mapping[str, Any]:
        if kind == "airspace":
            return normalize_airspace_feature(
                dict(raw),
                service_name=service_name,
                feature_type=feature_type or "AIRSPACE",
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )
        if kind == "facility":
            return normalize_facility_feature(
                dict(raw),
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )
        if kind == "tfr":
            return normalize_tfr_feature(
                dict(raw),
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )
        raise ValueError(f"Unsupported FAA kind: {kind}")

    source_system = {
        "airspace": "FAA_AIRSPACE",
        "facility": "FAA_FACILITY",
        "tfr": "FAA_TFR",
    }[kind]
    return _load(
        conn,
        table="project_staging.stg_airspace_zone",
        columns=AIRSPACE_COLUMNS,
        rows=iter_faa_geojson(path),
        normalizer=normalize,
        row_mapper=airspace_staging_row,
        conflict_target="(source_system, source_record_id)",
        source_system=source_system,
        source_file=logical,
        etl_run_id=etl_run_id,
    )
