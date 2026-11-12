"""WP-06 core movement facts: tracking and flight journey segmentation (Member D).

Transforms accepted real staging rows in ``project_staging.stg_adsb_position`` into
keyed ``project_dw.fact_vehicle_tracking`` and segmented
``project_dw.fact_flight_journey`` rows. Pure mapping and segmentation helpers are
separated from database I/O so unit tests run without PostgreSQL or Docker.
"""

from __future__ import annotations

import hashlib
import math
from bisect import bisect_left, bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from etl.errors import RowRejected
from etl.wp07_data_readiness import grid_from_real_position
from etl.staging_writer import _record_rejects_batch

ALGORITHM_VERSION = "wp06-v1"
DEFAULT_GAP_SPLIT_SEC = 300
DEFAULT_WEATHER_WINDOW_SEC = 3600
DEFAULT_BATCH_SIZE = 500
PG_MAX_BIND_PARAMS = 65535
# Mean WGS84 Earth radius (6371.0088 km) divided by international nautical mile (1.852 km).
EARTH_RADIUS_NM = 6371.0088 / 1.852
DEFAULT_GRID_HALF_STEP_DEG = 0.025
HEX_UPPER_CHARS = frozenset("0123456789ABCDEF")

TARTAN_SOURCE_ALIASES = frozenset({"TARTAN", "SRC-TARTAN"})

FACT_TRACKING_COLUMNS: tuple[str, ...] = (
    "event_ts",
    "time_key",
    "site_key",
    "vehicle_key",
    "grid_key",
    "weather_key",
    "altitude_msl_ft",
    "altitude_agl_ft",
    "altitude_source",
    "ground_speed_kts",
    "heading_deg",
    "vertical_rate_fps",
    "on_ground",
    "source_quality_flag",
    "source_system",
    "source_record_id",
    "source_file",
    "etl_run_id",
    "algorithm_version",
)

FACT_JOURNEY_COLUMNS: tuple[str, ...] = (
    "vehicle_key",
    "site_key",
    "start_ts",
    "end_ts",
    "start_time_key",
    "end_time_key",
    "origin_grid_key",
    "destination_grid_key",
    "flight_duration_sec",
    "max_altitude_ft",
    "total_distance_nm",
    "avg_speed_kts",
    "journey_source",
    "segment_reason",
    "source_system",
    "source_record_id",
    "etl_run_id",
    "algorithm_version",
)


@dataclass(frozen=True)
class GridCell:
    grid_key: int
    grid_cell_id: str
    site_key: int
    lat_bin: float
    lon_bin: float


@dataclass
class DimensionLookups:
    site_by_code: dict[str, int]
    time_by_hour: dict[datetime, int]
    vehicle_by_key: dict[tuple[str, str], int]
    vehicle_decimal_fallback: bool
    grid_cells_by_site: dict[int, list[GridCell]]
    grid_half_steps_by_site: dict[int, tuple[float, float]]
    weather_by_site: dict[int, tuple[list[datetime], list[int]]]
    has_unknown_members: dict[str, bool]
    vehicle_unpadded_hex_fallback: bool = False
    _grid_lats_by_site: dict[int, list[float]] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class TrackingPoint:
    vehicle_key: int
    site_key: int
    event_ts: datetime
    time_key: int
    grid_key: int
    latitude: float | None
    longitude: float | None
    altitude_msl_ft: float | None
    ground_speed_kts: float | None
    source_system: str
    source_record_id: str


@dataclass
class FactLoadCounts:
    rows_read: int = 0
    rows_inserted: int = 0
    rows_duplicate: int = 0
    rows_rejected: int = 0
    unknown_grid_count: int = 0
    unknown_weather_count: int = 0
    rejects_by_reason: dict[str, int] = field(default_factory=dict)

    def reconcile_ok(self) -> bool:
        return (
            self.rows_read
            == self.rows_inserted + self.rows_duplicate + self.rows_rejected
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows_read": self.rows_read,
            "rows_inserted": self.rows_inserted,
            "rows_duplicate": self.rows_duplicate,
            "rows_rejected": self.rows_rejected,
            "unknown_grid_count": self.unknown_grid_count,
            "unknown_weather_count": self.unknown_weather_count,
            "reconciled": self.reconcile_ok(),
            "rejects_by_reason": dict(sorted(self.rejects_by_reason.items())),
        }


@dataclass
class JourneyLoadCounts:
    vehicles_processed: int = 0
    segments_built: int = 0
    single_point_tracks_skipped: int = 0
    rows_inserted: int = 0
    rows_duplicate: int = 0
    rows_rejected: int = 0
    unknown_origin_grid_count: int = 0
    unknown_destination_grid_count: int = 0
    gap_split_sec: int = DEFAULT_GAP_SPLIT_SEC
    algorithm_version: str = ALGORITHM_VERSION

    def reconcile_ok(self) -> bool:
        return (
            self.segments_built
            == self.rows_inserted + self.rows_duplicate + self.rows_rejected
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "vehicles_processed": self.vehicles_processed,
            "segments_built": self.segments_built,
            "single_point_tracks_skipped": self.single_point_tracks_skipped,
            "rows_inserted": self.rows_inserted,
            "rows_duplicate": self.rows_duplicate,
            "rows_rejected": self.rows_rejected,
            "unknown_origin_grid_count": self.unknown_origin_grid_count,
            "unknown_destination_grid_count": self.unknown_destination_grid_count,
            "gap_split_sec": self.gap_split_sec,
            "algorithm_version": self.algorithm_version,
            "reconciled": self.reconcile_ok(),
        }


def ensure_utc(ts: datetime) -> datetime:
    """Convert a timezone-aware datetime to UTC; fail closed on naive inputs."""
    if not isinstance(ts, datetime) or ts.tzinfo is None or ts.utcoffset() is None:
        raise ValueError(f"Timestamp must be timezone-aware UTC datetime, got {ts!r}")
    return ts.astimezone(timezone.utc)


def utc_hour_bucket(ts: datetime) -> datetime:
    """Return the exact UTC hour boundary matching ``project_dw.dim_time.hour_ts``."""
    utc = ensure_utc(ts)
    return utc.replace(minute=0, second=0, microsecond=0)


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle geodesic distance between two WGS84 points in nautical miles."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    sin_dphi = math.sin(dphi / 2.0)
    sin_dlam = math.sin(dlam / 2.0)
    a = sin_dphi * sin_dphi + math.cos(phi1) * math.cos(phi2) * sin_dlam * sin_dlam
    # Clamp tiny IEEE-754 overshoot cleanly into [0, 1].
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_NM * c


def normalize_source_system(source_system: str | None) -> str:
    """Normalize source system identifiers cleanly across staging and dimension casing."""
    if source_system is None:
        return ""
    cleaned = source_system.strip().upper()
    if cleaned in TARTAN_SOURCE_ALIASES:
        return "TARTAN"
    return cleaned


def _infer_vehicle_decimal_fallback(tartan_entities: Sequence[str]) -> bool:
    """Detect whether dim_vehicle unambiguously seeded decimal IDs instead of 6-hex."""
    if not tartan_entities:
        return False
    if any(any(ch in "ABCDEF" for ch in ent) for ent in tartan_entities):
        return False
    return all(ent.isdigit() for ent in tartan_entities) and any(
        len(ent) != 6 for ent in tartan_entities
    )


def _infer_vehicle_unpadded_hex_fallback(
    tartan_entities: Sequence[str], *, decimal_fallback: bool
) -> bool:
    """Detect dim_vehicle rows seeded via SQL to_hex() without 6-char zero padding."""
    if decimal_fallback or not tartan_entities:
        return False
    return all(
        1 <= len(ent) <= 6 and all(ch in HEX_UPPER_CHARS for ch in ent)
        for ent in tartan_entities
    ) and any(len(ent) < 6 for ent in tartan_entities)


def _compute_grid_half_steps(cells: Sequence[GridCell]) -> tuple[float, float]:
    lats = sorted({cell.lat_bin for cell in cells})
    lons = sorted({cell.lon_bin for cell in cells})
    lat_diffs = [b - a for a, b in zip(lats, lats[1:]) if (b - a) > 1e-9]
    lon_diffs = [b - a for a, b in zip(lons, lons[1:]) if (b - a) > 1e-9]
    lat_half = (min(lat_diffs) / 2.0) if lat_diffs else DEFAULT_GRID_HALF_STEP_DEG
    lon_half = (min(lon_diffs) / 2.0) if lon_diffs else DEFAULT_GRID_HALF_STEP_DEG
    return lat_half, lon_half


def build_lookups_from_rows(
    *,
    site_rows: Iterable[tuple[int, str]],
    time_rows: Iterable[tuple[int, datetime]],
    vehicle_rows: Iterable[tuple[int, str, str]],
    grid_rows: Iterable[tuple[int, str, int, float | None, float | None]],
    weather_rows: Iterable[tuple[int, int, datetime]],
) -> DimensionLookups:
    """Build normalized in-memory lookup tables from dimension result tuples."""
    unknown_flags = {
        "dim_site": False,
        "dim_time": False,
        "dim_vehicle": False,
        "dim_spatial_grid": False,
        "dim_weather": False,
    }

    site_by_code: dict[str, int] = {}
    for site_key, site_code in site_rows:
        key = int(site_key)
        if key == -1:
            unknown_flags["dim_site"] = True
            continue
        norm_code = (site_code or "").strip().upper()
        if norm_code:
            site_by_code[norm_code] = key

    time_by_hour: dict[datetime, int] = {}
    for time_key, hour_ts in time_rows:
        key = int(time_key)
        if key == -1:
            unknown_flags["dim_time"] = True
            continue
        time_by_hour[ensure_utc(hour_ts)] = key

    vehicle_by_key: dict[tuple[str, str], int] = {}
    tartan_entities: list[str] = []
    for vehicle_key, source_system, source_entity_id in vehicle_rows:
        key = int(vehicle_key)
        if key == -1:
            unknown_flags["dim_vehicle"] = True
            continue
        norm_sys = normalize_source_system(source_system)
        norm_ent = (source_entity_id or "").strip().upper()
        if not norm_sys or not norm_ent:
            continue
        # Preserve exact 'TARTAN' row precedence if case variants coexist.
        if (norm_sys, norm_ent) not in vehicle_by_key or (source_system or "").strip() == "TARTAN":
            vehicle_by_key[(norm_sys, norm_ent)] = key
        if norm_sys == "TARTAN":
            tartan_entities.append(norm_ent)

    grid_cells_by_site: dict[int, list[GridCell]] = defaultdict(list)
    for grid_key, grid_cell_id, site_key, lat_bin, lon_bin in grid_rows:
        key = int(grid_key)
        if key == -1:
            unknown_flags["dim_spatial_grid"] = True
            continue
        if lat_bin is None or lon_bin is None:
            continue
        s_key = int(site_key)
        grid_cells_by_site[s_key].append(
            GridCell(
                grid_key=key,
                grid_cell_id=str(grid_cell_id),
                site_key=s_key,
                lat_bin=float(lat_bin),
                lon_bin=float(lon_bin),
            )
        )

    sorted_grid_cells: dict[int, list[GridCell]] = {}
    grid_lats_by_site: dict[int, list[float]] = {}
    for s_key, cells in grid_cells_by_site.items():
        ordered = sorted(cells, key=lambda c: (c.lat_bin, c.lon_bin, c.grid_key))
        sorted_grid_cells[s_key] = ordered
        grid_lats_by_site[s_key] = [c.lat_bin for c in ordered]

    grid_half_steps_by_site: dict[int, tuple[float, float]] = {
        s_key: _compute_grid_half_steps(cells)
        for s_key, cells in sorted_grid_cells.items()
    }

    weather_raw: dict[int, list[tuple[datetime, int]]] = defaultdict(list)
    for weather_key, site_key, obs_ts in weather_rows:
        key = int(weather_key)
        if key == -1:
            unknown_flags["dim_weather"] = True
            continue
        weather_raw[int(site_key)].append((ensure_utc(obs_ts), key))

    weather_by_site: dict[int, tuple[list[datetime], list[int]]] = {}
    for s_key, pairs in weather_raw.items():
        pairs.sort(key=lambda item: item[0])
        weather_by_site[s_key] = ([p[0] for p in pairs], [p[1] for p in pairs])

    decimal_fallback = _infer_vehicle_decimal_fallback(tartan_entities)
    unpadded_hex_fallback = _infer_vehicle_unpadded_hex_fallback(
        tartan_entities, decimal_fallback=decimal_fallback
    )

    return DimensionLookups(
        site_by_code=site_by_code,
        time_by_hour=time_by_hour,
        vehicle_by_key=vehicle_by_key,
        vehicle_decimal_fallback=decimal_fallback,
        grid_cells_by_site=sorted_grid_cells,
        grid_half_steps_by_site=grid_half_steps_by_site,
        weather_by_site=weather_by_site,
        has_unknown_members=unknown_flags,
        vehicle_unpadded_hex_fallback=unpadded_hex_fallback,
        _grid_lats_by_site=grid_lats_by_site,
    )


def load_dimension_lookups(conn: Any) -> DimensionLookups:
    """Query the five core dimension tables in bulk and build lookup indexes."""
    cur = conn.cursor()
    cur.execute("SELECT site_key, site_code FROM project_dw.dim_site")
    site_rows = cur.fetchall()

    cur.execute("SELECT time_key, hour_ts FROM project_dw.dim_time")
    time_rows = cur.fetchall()

    cur.execute(
        "SELECT vehicle_key, source_system, source_entity_id FROM project_dw.dim_vehicle"
    )
    vehicle_rows = cur.fetchall()

    cur.execute(
        "SELECT grid_key, grid_cell_id, site_key, lat_bin, lon_bin FROM project_dw.dim_spatial_grid"
    )
    grid_rows = cur.fetchall()

    cur.execute("SELECT weather_key, site_key, observation_ts FROM project_dw.dim_weather")
    weather_rows = cur.fetchall()

    return build_lookups_from_rows(
        site_rows=site_rows,
        time_rows=time_rows,
        vehicle_rows=vehicle_rows,
        grid_rows=grid_rows,
        weather_rows=weather_rows,
    )


def validate_unknown_members(lookups: DimensionLookups) -> None:
    """Fail closed if any required -1 unknown member is missing."""
    missing = [dim for dim, present in lookups.has_unknown_members.items() if not present]
    if missing:
        raise RuntimeError(
            "Required unknown member (-1) missing in dimension(s): "
            + ", ".join(sorted(missing))
        )


def resolve_site_key(lookups: DimensionLookups, site_code: str) -> int | None:
    norm = (site_code or "").strip().upper()
    if not norm:
        return None
    return lookups.site_by_code.get(norm)


def resolve_time_key(lookups: DimensionLookups, event_ts: datetime) -> int | None:
    return lookups.time_by_hour.get(utc_hour_bucket(event_ts))


def resolve_vehicle_key(
    lookups: DimensionLookups, source_system: str | None, entity_id: str | None
) -> int | None:
    norm_sys = normalize_source_system(source_system)
    norm_ent = (entity_id or "").strip().upper()
    if not norm_sys or not norm_ent:
        return None
    found = lookups.vehicle_by_key.get((norm_sys, norm_ent))
    if found is not None:
        return found
    if norm_sys == "TARTAN":
        if lookups.vehicle_decimal_fallback:
            try:
                decimal_id = str(int(norm_ent, 16))
            except ValueError:
                return None
            return lookups.vehicle_by_key.get((norm_sys, decimal_id))
        if lookups.vehicle_unpadded_hex_fallback:
            stripped = norm_ent.lstrip("0") or "0"
            if stripped != norm_ent:
                return lookups.vehicle_by_key.get((norm_sys, stripped))
    return None


def resolve_grid_key(
    lookups: DimensionLookups,
    site_key: int,
    latitude: float | None,
    longitude: float | None,
) -> int:
    """Resolve optional spatial cell; return -1 when outside real cells or grid empty."""
    cells = lookups.grid_cells_by_site.get(site_key)
    if not cells or latitude is None or longitude is None:
        return -1
    # WP-07 observed-grid members are deterministic 0.01-degree cells. Resolve
    # their exact ID first; the legacy nearest-center fallback remains intact.
    intended = grid_from_real_position(site_key, latitude, longitude)
    uses_observed_scheme = False
    for cell in cells:
        if cell.grid_cell_id.startswith("wp07-g01:"):
            uses_observed_scheme = True
            if intended is not None and cell.grid_cell_id == intended.grid_cell_id:
                return cell.grid_key
    if uses_observed_scheme:
        # Position is outside observed cells; never map it to the nearest
        # different grid member when the observed-grid scheme is in use.
        return -1
    lat_f = float(latitude)
    lon_f = float(longitude)
    half_lat, half_lon = lookups.grid_half_steps_by_site[site_key]
    tol_lat = half_lat * (1.0 + 1e-6)
    tol_lon = half_lon * (1.0 + 1e-6)
    lats = lookups._grid_lats_by_site.get(site_key)
    if lats is not None and len(lats) == len(cells):
        lat_window = tol_lat * (1.0 + 1e-9)
        lo = bisect_left(lats, lat_f - lat_window)
        hi = bisect_right(lats, lat_f + lat_window)
        candidates = cells[lo:hi]
    else:
        candidates = cells
    best_key = -1
    best_dist = float("inf")
    for cell in candidates:
        d_lat = abs(lat_f - cell.lat_bin)
        d_lon = abs(lon_f - cell.lon_bin)
        if d_lat <= tol_lat and d_lon <= tol_lon:
            dist = (d_lat / half_lat) + (d_lon / half_lon)
            if dist < best_dist:
                best_dist = dist
                best_key = cell.grid_key
    return best_key


def resolve_weather_key(
    lookups: DimensionLookups,
    site_key: int,
    event_ts: datetime,
    *,
    max_delta_sec: int = DEFAULT_WEATHER_WINDOW_SEC,
) -> int:
    """Resolve optional weather observation within window; return -1 if none."""
    series = lookups.weather_by_site.get(site_key)
    if not series:
        return -1
    timestamps, keys = series
    utc_ts = ensure_utc(event_ts)
    idx = bisect_left(timestamps, utc_ts)
    best_key = -1
    best_delta = float(max_delta_sec) + 1e-9
    for candidate_idx in (idx - 1, idx):
        if 0 <= candidate_idx < len(timestamps):
            delta = abs((timestamps[candidate_idx] - utc_ts).total_seconds())
            if delta <= max_delta_sec and delta < best_delta:
                best_delta = delta
                best_key = keys[candidate_idx]
    return best_key


def _round_opt(value: Any, ndigits: int) -> float | None:
    if value is None:
        return None
    return round(float(value), ndigits)


def map_adsb_staging_row(
    staging_row: Mapping[str, Any],
    lookups: DimensionLookups,
    *,
    site_code: str = "KBTP",
    etl_run_id: int,
    algorithm_version: str = ALGORITHM_VERSION,
) -> dict[str, Any]:
    """Map one accepted ``stg_adsb_position`` row to a ``fact_vehicle_tracking`` record.

    Raises ``RowRejected`` if any required dimension (``dim_site``, ``dim_time``,
    ``dim_vehicle``) or required provenance field is missing. Optional ``grid_key``
    and ``weather_key`` fall back to ``-1`` only when no real match exists.
    """
    source_record_id = str(staging_row.get("source_record_id") or "").strip() or None
    source_system = str(staging_row.get("source_system") or "TARTAN").strip()
    if not source_record_id:
        raise RowRejected("MISSING_NATURAL_KEY", "stg_adsb_position.source_record_id missing")

    raw_ts = staging_row.get("event_ts")
    if raw_ts is None:
        raise RowRejected("INVALID_TIMESTAMP", "event_ts is NULL", source_record_id)
    try:
        event_ts = ensure_utc(raw_ts)
    except ValueError as exc:
        raise RowRejected("INVALID_TIMESTAMP", str(exc), source_record_id) from exc

    site_key = resolve_site_key(lookups, site_code)
    if site_key is None:
        raise RowRejected(
            "MISSING_REQUIRED_DIMENSION",
            f"dim_site missing required site_code={site_code!r}",
            source_record_id,
        )

    time_key = resolve_time_key(lookups, event_ts)
    if time_key is None:
        raise RowRejected(
            "MISSING_REQUIRED_DIMENSION",
            f"dim_time missing UTC hour {utc_hour_bucket(event_ts).isoformat()}",
            source_record_id,
        )

    icao24 = staging_row.get("icao24")
    vehicle_key = resolve_vehicle_key(lookups, source_system, icao24)
    if vehicle_key is None:
        raise RowRejected(
            "MISSING_REQUIRED_DIMENSION",
            f"dim_vehicle missing ({normalize_source_system(source_system)!r}, {icao24!r})",
            source_record_id,
        )

    lat = staging_row.get("latitude")
    lon = staging_row.get("longitude")
    grid_key = resolve_grid_key(
        lookups,
        site_key,
        float(lat) if lat is not None else None,
        float(lon) if lon is not None else None,
    )
    weather_key = resolve_weather_key(lookups, site_key, event_ts)

    return {
        "event_ts": event_ts,
        "time_key": time_key,
        "site_key": site_key,
        "vehicle_key": vehicle_key,
        "grid_key": grid_key,
        "weather_key": weather_key,
        "altitude_msl_ft": _round_opt(staging_row.get("altitude_ft"), 2),
        "altitude_agl_ft": None,
        "altitude_source": staging_row.get("altitude_source"),
        "ground_speed_kts": _round_opt(staging_row.get("ground_speed_kts"), 2),
        "heading_deg": _round_opt(staging_row.get("heading_deg"), 2),
        "vertical_rate_fps": _round_opt(staging_row.get("vertical_rate_fps"), 2),
        "on_ground": staging_row.get("on_ground"),
        "source_quality_flag": staging_row.get("source_quality_flag"),
        "source_system": source_system,
        "source_record_id": source_record_id,
        "source_file": staging_row.get("raw_file"),
        "etl_run_id": int(etl_run_id),
        "algorithm_version": algorithm_version,
    }


def _journey_record_id(
    *,
    source_system: str,
    site_key: int,
    vehicle_key: int,
    first_source_record_id: str,
    last_source_record_id: str,
    gap_split_sec: int,
    algorithm_version: str,
) -> str:
    seed = (
        f"{source_system}|{site_key}|{vehicle_key}|"
        f"{first_source_record_id}|{last_source_record_id}|"
        f"{gap_split_sec}|{algorithm_version}"
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"journey:{digest}"


def _build_journey_row(
    segment: Sequence[TrackingPoint],
    *,
    segment_reason: str,
    etl_run_id: int,
    gap_split_sec: int,
    algorithm_version: str,
) -> dict[str, Any]:
    first = segment[0]
    last = segment[-1]
    duration_sec = int(round((last.event_ts - first.event_ts).total_seconds()))

    altitudes = [
        float(pt.altitude_msl_ft) for pt in segment if pt.altitude_msl_ft is not None
    ]
    max_altitude_ft = round(max(altitudes), 2) if altitudes else None

    speeds = [
        float(pt.ground_speed_kts) for pt in segment if pt.ground_speed_kts is not None
    ]
    avg_speed_kts = round(sum(speeds) / len(speeds), 2) if speeds else None

    distance_nm = 0.0
    for prev_pt, curr_pt in zip(segment, segment[1:]):
        if (
            prev_pt.latitude is not None
            and prev_pt.longitude is not None
            and curr_pt.latitude is not None
            and curr_pt.longitude is not None
        ):
            distance_nm += haversine_nm(
                float(prev_pt.latitude),
                float(prev_pt.longitude),
                float(curr_pt.latitude),
                float(curr_pt.longitude),
            )

    record_id = _journey_record_id(
        source_system=first.source_system,
        site_key=first.site_key,
        vehicle_key=first.vehicle_key,
        first_source_record_id=first.source_record_id,
        last_source_record_id=last.source_record_id,
        gap_split_sec=gap_split_sec,
        algorithm_version=algorithm_version,
    )

    return {
        "vehicle_key": first.vehicle_key,
        "site_key": first.site_key,
        "start_ts": first.event_ts,
        "end_ts": last.event_ts,
        "start_time_key": first.time_key,
        "end_time_key": last.time_key,
        "origin_grid_key": first.grid_key,
        "destination_grid_key": last.grid_key,
        "flight_duration_sec": max(0, duration_sec),
        "max_altitude_ft": max_altitude_ft,
        "total_distance_nm": round(distance_nm, 3),
        "avg_speed_kts": avg_speed_kts,
        "journey_source": "ADS-B",
        "segment_reason": segment_reason,
        "source_system": first.source_system,
        "source_record_id": record_id,
        "etl_run_id": int(etl_run_id),
        "algorithm_version": algorithm_version,
    }


def segment_vehicle_journeys(
    points: Iterable[TrackingPoint],
    *,
    etl_run_id: int,
    gap_split_sec: int = DEFAULT_GAP_SPLIT_SEC,
    algorithm_version: str = ALGORITHM_VERSION,
) -> tuple[list[dict[str, Any]], JourneyLoadCounts]:
    """Segment sorted real tracking points per vehicle using ``gap_split_sec``.

    Single-point segments (``len < 2``) are skipped rather than turned into artificial
    zero-length journeys. All timestamps must be timezone-aware UTC.
    """
    if gap_split_sec <= 0:
        raise ValueError(f"gap_split_sec must be positive, got {gap_split_sec}")

    counts = JourneyLoadCounts(
        gap_split_sec=gap_split_sec,
        algorithm_version=algorithm_version,
    )
    grouped: dict[tuple[str, int, int], list[TrackingPoint]] = defaultdict(list)
    for pt in points:
        utc_ts = ensure_utc(pt.event_ts)
        normalized = (
            pt
            if pt.event_ts is utc_ts
            else TrackingPoint(
                vehicle_key=pt.vehicle_key,
                site_key=pt.site_key,
                event_ts=utc_ts,
                time_key=pt.time_key,
                grid_key=pt.grid_key,
                latitude=pt.latitude,
                longitude=pt.longitude,
                altitude_msl_ft=pt.altitude_msl_ft,
                ground_speed_kts=pt.ground_speed_kts,
                source_system=pt.source_system,
                source_record_id=pt.source_record_id,
            )
        )
        grouped[(normalized.source_system, normalized.site_key, normalized.vehicle_key)].append(
            normalized
        )

    journeys: list[dict[str, Any]] = []
    gap_reason = f"GAP_SPLIT(gap_sec={gap_split_sec})"
    boundary_reason = f"FILE_BOUNDARY(gap_sec={gap_split_sec})"

    for group_key in sorted(grouped.keys()):
        counts.vehicles_processed += 1
        pts = sorted(grouped[group_key], key=lambda p: (p.event_ts, p.source_record_id))
        current: list[TrackingPoint] = [pts[0]]

        def finalize(seg: list[TrackingPoint], reason: str) -> None:
            if len(seg) < 2:
                counts.single_point_tracks_skipped += 1
                return
            row = _build_journey_row(
                seg,
                segment_reason=reason,
                etl_run_id=etl_run_id,
                gap_split_sec=gap_split_sec,
                algorithm_version=algorithm_version,
            )
            counts.segments_built += 1
            if row["origin_grid_key"] == -1:
                counts.unknown_origin_grid_count += 1
            if row["destination_grid_key"] == -1:
                counts.unknown_destination_grid_count += 1
            journeys.append(row)

        for pt in pts[1:]:
            delta = (pt.event_ts - current[-1].event_ts).total_seconds()
            if delta > gap_split_sec:
                finalize(current, gap_reason)
                current = [pt]
            else:
                current.append(pt)
        finalize(current, boundary_reason)

    return journeys, counts


def _batch_insert_facts_returning(
    conn: Any,
    *,
    table: str,
    columns: Sequence[str],
    conflict_target: str,
    rows: Sequence[Mapping[str, Any]],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> tuple[int, int]:
    """Batch insert fact rows with ON CONFLICT DO NOTHING and RETURNING source_record_id."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    if not rows:
        return 0, 0

    max_rows_per_stmt = max(1, PG_MAX_BIND_PARAMS // max(1, len(columns)))
    effective_batch = min(batch_size, max_rows_per_stmt)
    cur = conn.cursor()
    cols_sql = ", ".join(columns)
    row_placeholder = "(" + ", ".join(["%s"] * len(columns)) + ")"
    inserted = 0
    for start in range(0, len(rows), effective_batch):
        chunk = rows[start : start + effective_batch]
        placeholders = ", ".join([row_placeholder] * len(chunk))
        sql = (
            f"INSERT INTO {table} ({cols_sql}) VALUES {placeholders} "
            f"ON CONFLICT {conflict_target} DO NOTHING RETURNING source_record_id"
        )
        flat_params = [row[col] for row in chunk for col in columns]
        cur.execute(sql, flat_params)
        inserted_rows = cur.fetchall()
        inserted += len(inserted_rows)
    duplicates = len(rows) - inserted
    return inserted, duplicates


def _fetch_accepted_tartan_staging(
    conn: Any,
    *,
    source_file: str | None = None,
    start_ts: datetime | None = None,
    end_ts: datetime | None = None,
) -> list[dict[str, Any]]:
    where_clauses = [
        "UPPER(source_system) = 'TARTAN'",
        "reject_reason IS NULL",
    ]
    params: list[Any] = []
    if source_file is not None:
        where_clauses.append("raw_file = %s")
        params.append(source_file)
    if start_ts is not None:
        where_clauses.append("event_ts >= %s")
        params.append(ensure_utc(start_ts))
    if end_ts is not None:
        where_clauses.append("event_ts < %s")
        params.append(ensure_utc(end_ts))

    columns = (
        "staging_id",
        "source_system",
        "source_record_id",
        "event_ts",
        "icao24",
        "latitude",
        "longitude",
        "altitude_ft",
        "altitude_source",
        "ground_speed_kts",
        "heading_deg",
        "vertical_rate_fps",
        "on_ground",
        "raw_file",
        "source_quality_flag",
    )
    sql = (
        f"SELECT {', '.join(columns)} "
        "FROM project_staging.stg_adsb_position "
        f"WHERE {' AND '.join(where_clauses)} "
        "ORDER BY event_ts, source_record_id"
    )
    cur = conn.cursor()
    cur.execute(sql, params)
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def load_tartan_tracking_facts(
    conn: Any,
    *,
    etl_run_id: int,
    lookups: DimensionLookups | None = None,
    site_code: str = "KBTP",
    source_file: str | None = None,
    start_ts: datetime | None = None,
    end_ts: datetime | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    algorithm_version: str = ALGORITHM_VERSION,
) -> FactLoadCounts:
    """Load accepted Tartan staging rows into ``project_dw.fact_vehicle_tracking``."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    active_lookups = lookups or load_dimension_lookups(conn)
    validate_unknown_members(active_lookups)

    staging_rows = _fetch_accepted_tartan_staging(
        conn, source_file=source_file, start_ts=start_ts, end_ts=end_ts
    )
    counts = FactLoadCounts()
    valid_rows: list[dict[str, Any]] = []
    reject_rows: list[tuple[Any, str, str | None, str, str | None, Any]] = []

    for stg in staging_rows:
        counts.rows_read += 1
        try:
            mapped = map_adsb_staging_row(
                stg,
                active_lookups,
                site_code=site_code,
                etl_run_id=etl_run_id,
                algorithm_version=algorithm_version,
            )
        except RowRejected as exc:
            counts.rows_rejected += 1
            counts.rejects_by_reason[exc.reason_code] = (
                counts.rejects_by_reason.get(exc.reason_code, 0) + 1
            )
            reject_rows.append(
                (
                    etl_run_id,
                    str(stg.get("source_system") or "TARTAN"),
                    exc.source_record_id or stg.get("source_record_id"),
                    exc.reason_code,
                    exc.detail,
                    {"staging_id": stg.get("staging_id"), "icao24": stg.get("icao24")},
                )
            )
            continue

        if mapped["grid_key"] == -1:
            counts.unknown_grid_count += 1
        if mapped["weather_key"] == -1:
            counts.unknown_weather_count += 1
        valid_rows.append(mapped)

    if reject_rows:
        reject_batch = min(batch_size, max(1, PG_MAX_BIND_PARAMS // 6))
        for start in range(0, len(reject_rows), reject_batch):
            _record_rejects_batch(conn, reject_rows[start : start + reject_batch])

    inserted, duplicates = _batch_insert_facts_returning(
        conn,
        table="project_dw.fact_vehicle_tracking",
        columns=FACT_TRACKING_COLUMNS,
        conflict_target="(source_system, source_record_id)",
        rows=valid_rows,
        batch_size=batch_size,
    )
    counts.rows_inserted = inserted
    counts.rows_duplicate = duplicates
    return counts


def _fetch_tracking_points_for_journeys(
    conn: Any,
    *,
    source_file: str | None = None,
    start_ts: datetime | None = None,
    end_ts: datetime | None = None,
) -> list[TrackingPoint]:
    where_clauses = [
        "UPPER(f.source_system) = 'TARTAN'",
        "s.reject_reason IS NULL",
    ]
    params: list[Any] = []
    if source_file is not None:
        where_clauses.append("f.source_file = %s")
        params.append(source_file)
    if start_ts is not None:
        where_clauses.append("f.event_ts >= %s")
        params.append(ensure_utc(start_ts))
    if end_ts is not None:
        where_clauses.append("f.event_ts < %s")
        params.append(ensure_utc(end_ts))

    sql = (
        "SELECT "
        "    f.vehicle_key, "
        "    f.site_key, "
        "    f.event_ts, "
        "    f.time_key, "
        "    f.grid_key, "
        "    s.latitude, "
        "    s.longitude, "
        "    f.altitude_msl_ft, "
        "    f.ground_speed_kts, "
        "    f.source_system, "
        "    f.source_record_id "
        "FROM project_dw.fact_vehicle_tracking f "
        "JOIN project_staging.stg_adsb_position s "
        "  ON s.source_system = f.source_system "
        " AND s.source_record_id = f.source_record_id "
        f"WHERE {' AND '.join(where_clauses)} "
        "ORDER BY f.vehicle_key, f.event_ts, f.source_record_id"
    )
    cur = conn.cursor()
    cur.execute(sql, params)
    return [
        TrackingPoint(
            vehicle_key=int(row[0]),
            site_key=int(row[1]),
            event_ts=ensure_utc(row[2]),
            time_key=int(row[3]),
            grid_key=int(row[4]),
            latitude=float(row[5]) if row[5] is not None else None,
            longitude=float(row[6]) if row[6] is not None else None,
            altitude_msl_ft=float(row[7]) if row[7] is not None else None,
            ground_speed_kts=float(row[8]) if row[8] is not None else None,
            source_system=str(row[9]),
            source_record_id=str(row[10]),
        )
        for row in cur.fetchall()
    ]


def load_tartan_flight_journeys(
    conn: Any,
    *,
    etl_run_id: int,
    source_file: str | None = None,
    start_ts: datetime | None = None,
    end_ts: datetime | None = None,
    gap_split_sec: int = DEFAULT_GAP_SPLIT_SEC,
    batch_size: int = DEFAULT_BATCH_SIZE,
    algorithm_version: str = ALGORITHM_VERSION,
) -> JourneyLoadCounts:
    """Segment keyed tracking facts into ``project_dw.fact_flight_journey`` idempotently."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    if gap_split_sec <= 0:
        raise ValueError(f"gap_split_sec must be positive, got {gap_split_sec}")
    points = _fetch_tracking_points_for_journeys(
        conn, source_file=source_file, start_ts=start_ts, end_ts=end_ts
    )
    journeys, counts = segment_vehicle_journeys(
        points,
        etl_run_id=etl_run_id,
        gap_split_sec=gap_split_sec,
        algorithm_version=algorithm_version,
    )
    inserted, duplicates = _batch_insert_facts_returning(
        conn,
        table="project_dw.fact_flight_journey",
        columns=FACT_JOURNEY_COLUMNS,
        conflict_target="(source_system, source_record_id)",
        rows=journeys,
        batch_size=batch_size,
    )
    counts.rows_inserted = inserted
    counts.rows_duplicate = duplicates
    return counts


__all__ = [
    "ALGORITHM_VERSION",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_GAP_SPLIT_SEC",
    "DEFAULT_WEATHER_WINDOW_SEC",
    "EARTH_RADIUS_NM",
    "FACT_JOURNEY_COLUMNS",
    "FACT_TRACKING_COLUMNS",
    "DimensionLookups",
    "FactLoadCounts",
    "GridCell",
    "JourneyLoadCounts",
    "TrackingPoint",
    "build_lookups_from_rows",
    "ensure_utc",
    "haversine_nm",
    "load_dimension_lookups",
    "load_tartan_flight_journeys",
    "load_tartan_tracking_facts",
    "map_adsb_staging_row",
    "normalize_source_system",
    "resolve_grid_key",
    "resolve_site_key",
    "resolve_time_key",
    "resolve_vehicle_key",
    "resolve_weather_key",
    "segment_vehicle_journeys",
    "utc_hour_bucket",
    "validate_unknown_members",
]

