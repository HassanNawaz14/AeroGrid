"""WP-07: inspect *current* approved FAA TFR coverage, without DB writes.

Run: cd Phase2 && python -m etl.faa_restrictions --site KBTP

This is a source-readiness probe, NOT a historical TFR backfill and NOT a
production restriction fact loader. Output contains counts, never raw data.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from etl.sources.faa import normalize_tfr_feature

TFR_LAYER = (
    "https://services6.arcgis.com/ssFJjBXIUyZDrSYZ/ArcGIS/rest/services/"
    "Part_Time_National_Security_UAS_Flight_Restrictions/FeatureServer/0/query"
)
# KBTP reference point from documented source-validation work. The box is a
# study-area search window, NOT the airport property boundary.
KBTP_LAT = 40.7765833
KBTP_LON = -79.9510833
DEFAULT_HALF_WIDTH_DEG = 0.25
DEFAULT_PAGE_SIZE = 250
MAX_PAGES = 20
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


@dataclass(frozen=True)
class CoverageSummary:
    site_code: str
    as_of_utc: datetime
    returned_features: int
    distinct_tfr_ids: int
    active_in_confirmed_window: int
    future_window: int
    expired_window: int
    unknown_window: int


def utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Snapshot time must be timezone-aware")
    return value.astimezone(timezone.utc)


def make_study_bbox(lat: float, lon: float, half_width: float = DEFAULT_HALF_WIDTH_DEG) -> tuple[float, float, float, float]:
    """Bounding-box order: min longitude, min latitude, max longitude, max latitude."""
    import math

    if not all(map(math.isfinite, (lat, lon, half_width))):
        raise ValueError("Non-finite bbox input")
    if not (-90 < lat < 90 and -180 < lon < 180 and 0 < half_width <= 1):
        raise ValueError("Invalid study center or box width")
    if abs(lat) + half_width > 90 or abs(lon) + half_width > 180:
        raise ValueError("Study box crosses an unsupported world boundary")
    return (lon - half_width, lat - half_width, lon + half_width, lat + half_width)


def query_params(bbox: tuple[float, float, float, float], *, offset: int = 0, page_size: int = DEFAULT_PAGE_SIZE) -> dict[str, str]:
    if len(bbox) != 4 or not (bbox[0] < bbox[2] and bbox[1] < bbox[3]):
        raise ValueError("Invalid bbox")
    if offset < 0 or not (1 <= page_size <= 1000):
        raise ValueError("Invalid page parameters")
    return {
        "where": "1=1",
        "geometry": ",".join(str(float(p)) for p in bbox),
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outSR": "4326",
        "outFields": "*",
        "returnGeometry": "true",
        "resultOffset": str(offset),
        "resultRecordCount": str(page_size),
        "f": "geojson",
    }


def _http_json(url: str) -> Mapping[str, Any]:
    req = Request(url, headers={"User-Agent": "AeroGrid-WP07-readonly/1.0", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=25) as response:
            blob = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError("FAA source unavailable (network/status error)") from exc
    if len(blob) > MAX_RESPONSE_BYTES:
        raise ValueError("FAA page exceeded read limit")
    try:
        return json.loads(blob)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("FAA returned non-JSON response") from exc


def fetch_tfr_features(
    bbox: tuple[float, float, float, float],
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    fetch_json: Callable[[str], Mapping[str, Any]] = _http_json,
) -> list[Mapping[str, Any]]:
    """Read only approved FAA layer; no local archive or database writes.

    Fail closed if pagination is ambiguous or an ArcGIS error is returned.
    """
    features: list[Mapping[str, Any]] = []
    for page in range(MAX_PAGES):
        params = query_params(bbox, offset=page * page_size, page_size=page_size)
        payload = fetch_json(f"{TFR_LAYER}?{urlencode(params)}")
        if not isinstance(payload, Mapping) or "error" in payload:
            raise ValueError("FAA ArcGIS query reported an error")
        if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
            raise ValueError("FAA response is not a GeoJSON FeatureCollection")
        batch = payload["features"]
        for feature in batch:
            if not isinstance(feature, Mapping) or feature.get("type") != "Feature":
                raise ValueError("FAA returned an invalid feature")
        features.extend(batch)
        # ArcGIS GeoJSON supports limit/offset; a full page could mean there is more.
        if len(batch) < page_size and not payload.get("exceededTransferLimit", False):
            return features
        if len(batch) == 0:
            if payload.get("exceededTransferLimit", False):
                raise ValueError("FAA pagination made no progress")
            return features
    raise ValueError("FAA pagination limit reached; no partial data accepted")


def classify_window(start: datetime | None, end: datetime | None, as_of: datetime) -> str:
    """Only a *complete* timestamp window can verify activation.

    Null time fields mean UNKNOWN, not active. We do not infer standing TFR
    activity from a layer label or from the fact a feature was returned.
    """
    now = utc(as_of)
    if start is None or end is None:
        return "UNKNOWN_WINDOW"
    start, end = utc(start), utc(end)
    if end <= start:
        return "UNKNOWN_WINDOW"
    if now < start:
        return "FUTURE_WINDOW"
    if now >= end:
        return "EXPIRED_WINDOW"
    return "ACTIVE_IN_WINDOW"


def summarize_tfr_features(
    features: list[Mapping[str, Any]],
    *, site_code: str = "KBTP",
    as_of: datetime,
) -> CoverageSummary:
    now = utc(as_of)
    seen: dict[str, str] = {}
    for raw in features:
        record = normalize_tfr_feature(dict(raw), etl_run_id="readonly-preview", source_manifest_id=None)
        key = str(record["source_record_id"]).strip()
        if key in seen:
            raise ValueError("FAA returned a repeated FAA_ID; snapshot is ambiguous")
        seen[key] = classify_window(record["active_start_ts"], record["active_end_ts"], now)
    statuses = list(seen.values())
    return CoverageSummary(
        site_code=site_code,
        as_of_utc=now,
        returned_features=len(features),
        distinct_tfr_ids=len(seen),
        active_in_confirmed_window=statuses.count("ACTIVE_IN_WINDOW"),
        future_window=statuses.count("FUTURE_WINDOW"),
        expired_window=statuses.count("EXPIRED_WINDOW"),
        unknown_window=statuses.count("UNKNOWN_WINDOW"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only FAA TFR study-box coverage probe")
    parser.add_argument("--site", default="KBTP", choices=["KBTP"])
    args = parser.parse_args(argv)
    bbox = make_study_bbox(KBTP_LAT, KBTP_LON)
    try:
        features = fetch_tfr_features(bbox)
        summary = summarize_tfr_features(features, site_code=args.site, as_of=datetime.now(timezone.utc))
    except Exception as exc:
        print(f"FAA PREVIEW FAILED: {type(exc).__name__}: {exc}")
        return 1
    print(f"site={summary.site_code}; as_of_utc={summary.as_of_utc.isoformat()}")
    print(f"real_tfr_features_in_study_box={summary.returned_features}")
    print(f"distinct_faa_ids={summary.distinct_tfr_ids}")
    print(f"active_by_complete_window={summary.active_in_confirmed_window}")
    print(f"future={summary.future_window}; expired={summary.expired_window}; unknown_window={summary.unknown_window}")
    print("READ-ONLY: no warehouse writes; not a historical TFR audit; not airport boundary coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
