from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterator

from etl.sources.dji_nominal import normalize_nominal_row
from etl.sources.faa import (
    normalize_airspace_feature,
    normalize_facility_feature,
    normalize_tfr_feature,
)
from etl.sources.metar import normalize_awc_observation, normalize_iem_row
from etl.sources.nightjar import normalize_nightjar_row
from etl.sources.tartan import normalize_tartan_row


def iter_tartan_csv(path: str | Path, *, etl_run_id: str, source_manifest_id: int | None = None) -> Iterator[dict[str, Any]]:
    source_file = Path(path).as_posix()
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            yield normalize_tartan_row(
                row,
                source_file=source_file,
                row_number=row_number,
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )


def iter_nightjar_csv(path: str | Path, *, etl_run_id: str, source_manifest_id: int | None = None) -> Iterator[dict[str, Any]]:
    source_file = Path(path).as_posix()
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            yield normalize_nightjar_row(
                row,
                source_file=source_file,
                row_number=row_number,
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )


def iter_nominal_csv(
    path: str | Path,
    *,
    etl_run_id: str,
    source_manifest_id: int | None = None,
    site_code: str | None,
) -> Iterator[dict[str, Any]]:
    source_file = Path(path).as_posix()
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            yield normalize_nominal_row(
                row,
                source_file=source_file,
                row_number=row_number,
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
                site_code=site_code,
            )


def iter_awc_json(path: str | Path, *, etl_run_id: str, source_manifest_id: int | None = None) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        observations = json.load(handle)
    for obs in observations:
        station = str(obs.get("icaoId") or "").strip().upper()
        obs_time = obs.get("obsTime")
        yield normalize_awc_observation(
            obs,
            source_record_id=f"awc:{station}:{obs_time}",
            etl_run_id=etl_run_id,
            source_manifest_id=source_manifest_id,
        )


def iter_iem_csv(
    path: str | Path,
    *,
    station_icao: str,
    etl_run_id: str,
    source_manifest_id: int | None = None,
) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            valid = str(row.get("valid") or "").strip()
            yield normalize_iem_row(
                row,
                station_icao=station_icao,
                source_record_id=f"iem:{station_icao}:{valid}",
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )


def iter_faa_geojson(
    path: str | Path,
    *,
    kind: str,
    service_name: str,
    feature_type: str | None = None,
    etl_run_id: str,
    source_manifest_id: int | None = None,
) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    features = payload.get("features", []) if isinstance(payload, dict) else payload
    for feature in features:
        if kind == "airspace":
            yield normalize_airspace_feature(
                feature,
                service_name=service_name,
                feature_type=feature_type or "AIRSPACE",
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )
        elif kind == "facility":
            yield normalize_facility_feature(
                feature,
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )
        elif kind == "tfr":
            yield normalize_tfr_feature(
                feature,
                etl_run_id=etl_run_id,
                source_manifest_id=source_manifest_id,
            )
        else:
            raise ValueError(f"Unsupported FAA kind: {kind}")
