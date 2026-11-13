"""WP-11: fetch approved raw sources into a temporary directory.

Every request is read-only, unauthenticated, size-capped, and fails closed.
No credentials are read here; GitHub provides DATABASE_URL only to the apply job.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from etl.config import (
    AIRSPACE_SERVICES,
    AWC_URL,
    ARC_GIS_ROOT,
    DJI_FILES,
    DJI_ROOT,
    IEM_URL,
    NIGHTJAR_URL,
    study_boxes,
)

USER_AGENT = "AeroGrid-WP11-ingest/1.0"
PAGE_BYTES = 8 * 1024 * 1024
FILE_BYTES = 96 * 1024 * 1024
MAX_PAGES = 20
PAGE_SIZE = 250


@dataclass(frozen=True)
class FetchedFile:
    source: str
    system: str
    path: Path
    url: str
    station_icao: str | None = None
    site_code: str | None = None
    service_name: str | None = None
    feature_type: str | None = None


def _get(url: str, limit: int) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            blob = response.read(limit + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Source unavailable: {url.split('?')[0]}") from exc
    if len(blob) > limit:
        raise ValueError(f"Response exceeded {limit} bytes: {url.split('?')[0]}")
    if not blob:
        raise ValueError(f"Empty response: {url.split('?')[0]}")
    return blob


def _write(dest: Path, name: str, blob: bytes) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / name
    path.write_bytes(blob)
    return path


def _http_json(url: str):
    blob = _get(url, PAGE_BYTES)
    try:
        payload = json.loads(blob)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Source returned non-JSON content") from exc
    if isinstance(payload, dict) and "error" in payload:
        raise ValueError("Source reported an API error")
    return payload


def iem_metar_url(station: str, start: date, end: date) -> str:
    params = [
        ("station", station.upper()),
        ("data", "metar"),
        ("year1", start.year),
        ("month1", start.month),
        ("day1", start.day),
        ("year2", end.year),
        ("month2", end.month),
        ("day2", end.day),
        ("tz", "UTC"),
        ("format", "onlycomma"),
        ("latlon", "no"),
        ("missing", "M"),
        ("trace", "T"),
        ("direct", "no"),
        ("report_type", "3"),
        ("report_type", "4"),
    ]
    return f"{IEM_URL}?{urlencode(params)}"


def fetch_iem_metar(
    stations: tuple[str, ...], start: date, end: date, dest: Path
) -> list[FetchedFile]:
    files = []
    for station in stations:
        url = iem_metar_url(station, start, end)
        blob = _get(url, FILE_BYTES)
        if blob.lstrip().startswith(b"<"):
            raise ValueError("IEM returned HTML instead of CSV")
        path = _write(
            dest, f"iem_{station.upper()}_{start.isoformat()}_{end.isoformat()}.csv", blob
        )
        files.append(
            FetchedFile(
                "weather",
                "IEM",
                path,
                url,
                station_icao=station.upper(),
            )
        )
    return files


def fetch_awc_metar(
    stations: tuple[str, ...], hours: int, dest: Path
) -> list[FetchedFile]:
    if not 1 <= hours <= 168:
        raise ValueError("AWC hours must be between 1 and 168")
    params = {
        "ids": ",".join(station.upper() for station in stations),
        "format": "json",
        "hours": str(hours),
    }
    url = f"{AWC_URL}?{urlencode(params)}"
    payload = _http_json(url)
    if not isinstance(payload, list):
        raise ValueError("AWC response is not a JSON array")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")
    path = _write(
        dest,
        f"awc_{'_'.join(station.upper() for station in stations)}_{stamp}.json",
        json.dumps(payload).encode("utf-8"),
    )
    return [FetchedFile("weather", "AWC", path, url)]


def fetch_nightjar(dest: Path) -> list[FetchedFile]:
    blob = _get(NIGHTJAR_URL, FILE_BYTES)
    path = _write(dest, "nightjar_20260804.csv", blob)
    return [FetchedFile("uas", "Nightjar", path, NIGHTJAR_URL)]


def fetch_dji(dest: Path) -> list[FetchedFile]:
    files = []
    for relative, label, site_code in DJI_FILES:
        url = f"{DJI_ROOT}/{quote(relative, safe='/')}"
        blob = _get(url, FILE_BYTES)
        path = _write(dest, f"nominal_{label}.csv", blob)
        files.append(
            FetchedFile("uas", "Nominal-DJI", path, url, site_code=site_code)
        )
    return files


def arcgis_query_url(layer: str, bbox, *, offset: int) -> str:
    params = {
        "where": "1=1",
        "geometry": ",".join(str(float(value)) for value in bbox),
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outSR": "4326",
        "outFields": "*",
        "returnGeometry": "true",
        "resultOffset": str(offset),
        "resultRecordCount": str(PAGE_SIZE),
        "f": "geojson",
    }
    return f"{ARC_GIS_ROOT}/{layer}/FeatureServer/0/query?{urlencode(params)}"


def fetch_airspace_layer(layer: str, bbox) -> list[dict]:
    features: list[dict] = []
    for page in range(MAX_PAGES):
        payload = _http_json(arcgis_query_url(layer, bbox, offset=page * PAGE_SIZE))
        if (
            not isinstance(payload, dict)
            or payload.get("type") != "FeatureCollection"
            or not isinstance(payload.get("features"), list)
        ):
            raise ValueError("ArcGIS response is not a GeoJSON FeatureCollection")
        batch = payload["features"]
        if not batch:
            # ArcGIS GeoJSON does not report exceededTransferLimit; an empty page is
            # the only reliable end-of-results signal, so a full last page costs one
            # extra request rather than silently truncating data.
            return features
        for feature in batch:
            if not isinstance(feature, dict) or feature.get("type") != "Feature":
                raise ValueError("ArcGIS returned an invalid feature")
        features.extend(batch)
        if len(batch) < PAGE_SIZE:
            return features
    raise ValueError("ArcGIS pagination limit reached; no partial data accepted")


def fetch_faa_airspace(dest: Path) -> list[FetchedFile]:
    """One merged file per approved granular service, deduplicated by GLOBAL_ID."""
    files = []
    for layer, service_name, feature_type in AIRSPACE_SERVICES:
        merged: dict[str, dict] = {}
        for _site, bbox in study_boxes():
            for feature in fetch_airspace_layer(layer, bbox):
                key = str(
                    (feature.get("properties") or {}).get("GLOBAL_ID") or ""
                ).strip()
                if not key:
                    raise ValueError("Airspace feature is missing GLOBAL_ID")
                merged[key] = feature
        # An empty result is real evidence (the service answered, nothing intersects
        # the documented study boxes), so keep an empty collection instead of
        # failing. If every airspace service is empty the validate summary still
        # rejects the run as missing coverage.
        path = _write(
            dest,
            f"faa_{layer}.geojson",
            json.dumps(
                {"type": "FeatureCollection", "features": list(merged.values())}
            ).encode("utf-8"),
        )
        files.append(
            FetchedFile(
                "airspace",
                "FAA-Airspace",
                path,
                f"{ARC_GIS_ROOT}/{layer}/FeatureServer",
                service_name=service_name,
                feature_type=feature_type,
            )
        )
    return files


def fetch_sources(
    sources: tuple[str, ...],
    start: date,
    end: date,
    dest: Path,
    *,
    stations: tuple[str, ...],
) -> list[FetchedFile]:
    if end < start:
        raise ValueError("end date must not be before start date")
    files: list[FetchedFile] = []
    if "weather" in sources:
        today = datetime.now(timezone.utc).date()
        # AWC retains 7 days at 168 hours; a longer window must use IEM, otherwise
        # the run would silently load only the most recent week.
        if start <= today <= end and (today - start).days <= 6:
            hours = min(168, max(1, (today - start).days * 24 + 24))
            files.extend(fetch_awc_metar(stations, hours, dest))
        else:
            files.extend(fetch_iem_metar(stations, start, end, dest))
    if "uas" in sources:
        files.extend(fetch_nightjar(dest))
        files.extend(fetch_dji(dest))
    if "airspace" in sources:
        files.extend(fetch_faa_airspace(dest))
    return files


def recent_window(days: int = 7) -> tuple[date, date]:
    today = datetime.now(timezone.utc).date()
    return today - timedelta(days=days - 1), today


__all__ = [
    "FetchedFile",
    "arcgis_query_url",
    "fetch_airspace_layer",
    "fetch_awc_metar",
    "fetch_dji",
    "fetch_faa_airspace",
    "fetch_iem_metar",
    "fetch_nightjar",
    "fetch_sources",
    "iem_metar_url",
    "recent_window",
]
