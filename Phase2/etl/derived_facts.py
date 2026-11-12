"""WP-07 Member E: evidence-backed derived facts.

Pure algorithms are deliberately separate from database I/O. No synthetic business
records, generated encounters, or predicted restrictions enter production facts.
The database caller owns transaction commit/rollback and run-log lifecycle.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Mapping, Sequence

from etl.wp07_data_readiness import airborne_assessment, eligible_airborne

ALGORITHM_VERSION = "wp07-v1"
SEVERE_HORIZONTAL_NM = 0.5
SEVERE_VERTICAL_FT = 500.0
PROXIMITY_HORIZONTAL_NM = 1.0
PROXIMITY_VERTICAL_FT = 1000.0
OBSERVATION_GAP_CAP_SEC = 60  # Conservative occupancy estimate; seek review.

ENCOUNTER_COLUMNS = (
    "start_ts", "end_ts", "start_time_key", "site_key", "grid_key",
    "weather_key", "vehicle_key_1", "vehicle_key_2", "min_tracking_id_1",
    "min_tracking_id_2", "min_horizontal_sep_nm", "min_vertical_sep_ft",
    "conflict_duration_sec", "closing_speed_kts", "risk_severity_class",
    "risk_severity_score", "algorithm_version", "etl_run_id",
)
OCCUPANCY_COLUMNS = (
    "time_key", "site_key", "grid_key", "active_vehicle_count",
    "total_occupancy_minutes", "avg_traffic_speed_kts",
    "supporting_tracking_count", "algorithm_version", "etl_run_id",
)
RESTRICTION_COLUMNS = (
    "time_key", "evaluation_ts", "site_key", "zone_key", "is_active",
    "affected_traffic_count", "compliant_count", "compliance_rate_pct",
    "source_system", "source_record_id", "source_snapshot_ts", "etl_run_id",
    "algorithm_version",
)


def utc(ts: datetime) -> datetime:
    if not isinstance(ts, datetime) or ts.tzinfo is None or ts.utcoffset() is None:
        raise ValueError("event time must be timezone-aware")
    return ts.astimezone(timezone.utc)


def _finite_coordinate(lat: Any, lon: Any) -> bool:
    if lat is None or lon is None:
        return False
    try:
        la, lo = float(lat), float(lon)
    except (TypeError, ValueError):
        return False
    return math.isfinite(la) and math.isfinite(lo) and -90 <= la <= 90 and -180 <= lo <= 180


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Real WGS84 positions -> great-circle nautical miles."""
    r_nm = 3440.065
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl / 2)**2
    return 2 * r_nm * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def encounter_class(horizontal_nm: float, vertical_ft: float) -> str | None:
    """Strict (<) H-013 thresholds. None means not a qualifying encounter."""
    if not (math.isfinite(horizontal_nm) and math.isfinite(vertical_ft)):
        return None
    if horizontal_nm < 0 or vertical_ft < 0:
        return None
    if horizontal_nm < SEVERE_HORIZONTAL_NM and vertical_ft < SEVERE_VERTICAL_FT:
        return "SEVERE"
    if horizontal_nm < PROXIMITY_HORIZONTAL_NM and vertical_ft < PROXIMITY_VERTICAL_FT:
        return "PROXIMITY"
    return None


def build_encounters(points: Sequence[Mapping[str, Any]], *, etl_run_id: int) -> list[dict]:
    """One *observed* conflict per site/instant/vehicle pair (zero inferred duration).

    Uses identical event timestamps only: it does not interpolate asynchronous
    telemetry or invent episode duration. If continuous episodes are required,
    review/approve temporal matching and segmentation separately before G5.
    Requires compatible, nonblank altitude datum for both vehicles.
    """
    groups: dict[tuple, dict[int, Mapping[str, Any]]] = defaultdict(dict)
    for p in points:
        if not eligible_airborne(p) or not _finite_coordinate(p.get("latitude"), p.get("longitude")):
            continue
        if p.get("altitude_msl_ft") is None or not p.get("altitude_source"):
            continue
        try:
            alt = float(p["altitude_msl_ft"])
            if not math.isfinite(alt):
                continue
            veh, site, tkey = int(p["vehicle_key"]), int(p["site_key"]), int(p["time_key"])
            if veh <= 0 or site <= 0 or tkey <= 0:
                continue
            ts = utc(p["event_ts"])
        except (TypeError, ValueError, KeyError):
            continue
        key = (site, ts)
        # Stable choice if multiple records exist for the same vehicle and instant.
        if veh not in groups[key] or int(p["tracking_id"]) < int(groups[key][veh]["tracking_id"]):
            groups[key][veh] = p

    records = []
    for (site, ts), vehicles in sorted(groups.items()):
        for a, b in combinations((vehicles[k] for k in sorted(vehicles)), 2):
            if int(a["time_key"]) != int(b["time_key"]):
                continue
            if str(a["altitude_source"]).strip().upper() != str(b["altitude_source"]).strip().upper():
                continue
            horizontal = haversine_nm(float(a["latitude"]), float(a["longitude"]),
                                    float(b["latitude"]), float(b["longitude"]))
            vertical = abs(float(a["altitude_msl_ft"]) - float(b["altitude_msl_ft"]))
            severity = encounter_class(round(horizontal, 3), round(vertical, 2))
            if severity is None:
                continue
            # Vehicle ordering is inherited from sorted(vehicle_key).
            records.append({
                "start_ts": ts, "end_ts": ts, "start_time_key": int(a["time_key"]),
                "site_key": site, "grid_key": int(a.get("grid_key") or -1),
                "weather_key": int(a.get("weather_key") or -1),
                "vehicle_key_1": int(a["vehicle_key"]), "vehicle_key_2": int(b["vehicle_key"]),
                "min_tracking_id_1": int(a["tracking_id"]), "min_tracking_id_2": int(b["tracking_id"]),
                "min_horizontal_sep_nm": round(horizontal, 3),
                "min_vertical_sep_ft": round(vertical, 2),
                "conflict_duration_sec": 0, "closing_speed_kts": None,
                "risk_severity_class": severity, "risk_severity_score": None,
                "algorithm_version": ALGORITHM_VERSION, "etl_run_id": etl_run_id,
            })
    return records


def build_occupancy(points: Sequence[Mapping[str, Any]], *, etl_run_id: int,
                    gap_cap_sec: int = OBSERVATION_GAP_CAP_SEC) -> list[dict]:
    """Hourly grid occupancy from real airborne tracking rows.

    For each vehicle, observed adjacent samples contribute at most gap_cap_sec each.
    No duration is extrapolated after a last isolated sample; values are lower-bound
    observation-based estimates, not total exposure inferred from a single ping.
    """
    if gap_cap_sec <= 0:
        raise ValueError("gap_cap_sec must be positive")
    groups: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for p in points:
        if not eligible_airborne(p):
            continue
        try:
            time_key, grid_key = int(p["time_key"]), int(p["grid_key"])
            site, vehicle = int(p["site_key"]), int(p["vehicle_key"])
            if min(time_key, grid_key, site, vehicle) <= 0:
                continue  # do not turn unknown grid (-1) into fabricated occupancy
            utc(p["event_ts"])
        except (KeyError, TypeError, ValueError):
            continue
        groups[(time_key, grid_key)].append(p)

    out = []
    for (time_key, grid_key), rows in sorted(groups.items()):
        sites = {int(p["site_key"]) for p in rows}
        if len(sites) != 1:
            raise ValueError("one spatial grid cell mapped to multiple sites")
        by_vehicle: dict[int, list[datetime]] = defaultdict(list)
        speeds = []
        for p in rows:
            by_vehicle[int(p["vehicle_key"])].append(utc(p["event_ts"]))
            speed = p.get("ground_speed_kts")
            if speed is not None:
                try:
                    speed = float(speed)
                    if math.isfinite(speed) and speed >= 0:
                        speeds.append(speed)
                except (TypeError, ValueError):
                    pass
        observed_seconds = 0.0
        for times in by_vehicle.values():
            ordered = sorted(set(times))
            for a, b in zip(ordered, ordered[1:]):
                # Positions share the same time_key; a gap can still cross an
                # hour boundary only if upstream time keys are invalid (DQ checks).
                delta = (b-a).total_seconds()
                if (0 < delta <= gap_cap_sec
                    and a.replace(minute=0, second=0, microsecond=0)
                    == b.replace(minute=0, second=0, microsecond=0)):
                    observed_seconds += delta
        out.append({
            "time_key": time_key, "site_key": next(iter(sites)), "grid_key": grid_key,
            "active_vehicle_count": len(by_vehicle),
            "total_occupancy_minutes": round(observed_seconds/60, 2),
            "avg_traffic_speed_kts": round(sum(speeds)/len(speeds), 2) if speeds else None,
            "supporting_tracking_count": len(rows),
            "algorithm_version": ALGORITHM_VERSION, "etl_run_id": etl_run_id,
        })
    return out


def build_restrictions(snapshots: Sequence[Mapping[str, Any]], *, etl_run_id: int) -> list[dict]:
    """Only map real, accepted snapshot rows with known site/zone/hour keys.

    Compliance is NULL until geometry + zone limits are validated; never invent
    an affected count or assume unknown traffic is compliant.
    """
    out = []
    seen: dict[tuple, bool] = {}
    for s in snapshots:
        if s.get("is_active") is None or s.get("reject_reason") is not None:
            continue
        try:
            zone, tkey, site = int(s["zone_key"]), int(s["time_key"]), int(s["site_key"])
            if min(zone, tkey, site) <= 0:
                continue
            at = utc(s["snapshot_ts"])
            start = utc(s["effective_start_ts"]) if s.get("effective_start_ts") else None
            end = utc(s["effective_end_ts"]) if s.get("effective_end_ts") else None
            source = str(s["source_system"]).strip()
            sid = int(s["staging_id"])
            if not source:
                continue
        except (TypeError, ValueError, KeyError):
            continue
        # No fabricated activation outside the published effective window.
        active = bool(s["is_active"]) and (start is None or at >= start) and (end is None or at < end)
        key = (zone, at, source.upper())
        if key in seen:
            if seen[key] != active:
                raise ValueError("conflicting real restriction snapshots for one zone/time/source")
            continue
        seen[key] = active
        out.append({
            "time_key": tkey, "evaluation_ts": at, "site_key": site,
            "zone_key": zone, "is_active": active,
            "affected_traffic_count": None, "compliant_count": None,
            "compliance_rate_pct": None, "source_system": source,
            "source_record_id": f"snapshot:{sid}", "source_snapshot_ts": at,
            "etl_run_id": etl_run_id, "algorithm_version": ALGORITHM_VERSION,
        })
    return out


def _rows(cur: Any, sql: str) -> list[dict]:
    """Map cursor rows to dicts without a psycopg-specific row_factory."""
    cur.execute(sql)
    names = [c.name if hasattr(c, "name") else c[0] for c in cur.description]
    return [dict(zip(names, record)) for record in cur.fetchall()]


def fetch_tracking(conn: Any) -> list[dict]:
    """Use accepted real ADS-B staging geometry for encounter evidence.

    Scope initially Tartan ADS-B, the real sample accepted by WP-06. Extension to
    UAS needs a separately verified source join, datum, and site/time policy.
    """
    return _rows(conn.cursor(), """
        SELECT f.tracking_id, f.event_ts, f.time_key, f.site_key, f.grid_key,
               f.weather_key, f.vehicle_key, f.altitude_msl_ft, f.altitude_source,
               f.ground_speed_kts, f.on_ground, s.latitude, s.longitude,
               f.source_system, ds.site_code
        FROM project_dw.fact_vehicle_tracking f
        JOIN project_dw.dim_site ds ON ds.site_key = f.site_key
        JOIN project_staging.stg_adsb_position s
          ON s.source_system = f.source_system
         AND s.source_record_id = f.source_record_id
        WHERE s.reject_reason IS NULL AND UPPER(f.source_system) = 'TARTAN'
        ORDER BY f.site_key, f.event_ts, f.vehicle_key, f.tracking_id
    """)


def fetch_snapshots(conn: Any) -> list[dict]:
    """Inner joins intentionally exclude unresolved natural keys and absent hours."""
    return _rows(conn.cursor(), """
        SELECT s.staging_id, s.snapshot_ts, s.source_system, s.source_object_id,
               s.is_active, s.effective_start_ts, s.effective_end_ts,
               s.reject_reason, d.zone_key, d.site_key, t.time_key
        FROM project_staging.stg_restriction_snapshot s
        JOIN project_dw.dim_airspace_zone d
          ON UPPER(d.source_system) = UPPER(s.source_system)
         AND d.source_object_id = s.source_object_id
        JOIN project_dw.dim_time t
          ON t.hour_ts = date_trunc('hour', s.snapshot_ts, 'UTC')
        WHERE s.reject_reason IS NULL AND s.is_active IS NOT NULL
        ORDER BY s.snapshot_ts, s.staging_id
    """)


def insert_rows(conn: Any, *, table: str, columns: tuple[str, ...],
                conflict_columns: tuple[str, ...], primary_key: str,
                records: Sequence[Mapping[str, Any]], chunk_size: int = 200) -> int:
    """Parameterized idempotent inserts, no commit, controlled known table names."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if not records:
        return 0
    whitelisted = {
        "project_dw.fact_close_encounter", "project_dw.fact_airspace_occupancy",
        "project_dw.fact_restriction_activation"
    }
    if table not in whitelisted:
        raise ValueError("unapproved table")
    cols = ", ".join(columns)
    conflict = ", ".join(conflict_columns)
    per_chunk = min(chunk_size, max(1, 65535 // len(columns)))
    cur = conn.cursor()
    inserted = 0
    for idx in range(0, len(records), per_chunk):
        batch = records[idx:idx + per_chunk]
        template = "(" + ", ".join(["%s"] * len(columns)) + ")"
        placeholders = ", ".join([template] * len(batch))
        params = [row[col] for row in batch for col in columns]
        cur.execute(f"INSERT INTO {table} ({cols}) VALUES {placeholders} "
                    f"ON CONFLICT ({conflict}) DO NOTHING RETURNING {primary_key}", params)
        inserted += len(cur.fetchall())
    return inserted


def derive_and_insert(conn: Any, *, etl_run_id: int) -> dict[str, dict[str, int]]:
    """Compute from warehouse source rows and insert within caller's transaction."""
    if etl_run_id <= 0:
        raise ValueError("etl_run_id must reference a real run-log row")
    pts, snapshots = fetch_tracking(conn), fetch_snapshots(conn)
    verified_airborne = sum(eligible_airborne(p) for p in pts)
    real_grid_count = sum(int(p.get("grid_key") or -1) > 0 for p in pts)
    blockers = []
    if pts and verified_airborne == 0:
        blockers.append("NO_VERIFIED_AIRBORNE")
    if pts and real_grid_count == 0:
        blockers.append("NO_REAL_GRID")
    if blockers:
        raise ValueError("; ".join(blockers) +
                         ": ask Members C/D to approve real airborne and spatial-grid evidence")
    batches = (
        ("encounters", "project_dw.fact_close_encounter", ENCOUNTER_COLUMNS,
         ("vehicle_key_1", "vehicle_key_2", "start_ts", "algorithm_version"),
         "encounter_id", build_encounters(pts, etl_run_id=etl_run_id)),
        ("occupancy", "project_dw.fact_airspace_occupancy", OCCUPANCY_COLUMNS,
         ("time_key", "grid_key", "algorithm_version"),
         "occupancy_id", build_occupancy(pts, etl_run_id=etl_run_id)),
        ("restrictions", "project_dw.fact_restriction_activation", RESTRICTION_COLUMNS,
         ("zone_key", "evaluation_ts", "source_system"),
         "activation_id", build_restrictions(snapshots, etl_run_id=etl_run_id)),
    )
    result = {}
    for label, table, cols, conflict, pk, rows in batches:
        inserted = insert_rows(conn, table=table, columns=cols,
                               conflict_columns=conflict, primary_key=pk, records=rows)
        result[label] = {"candidate_rows": len(rows), "inserted_rows": inserted,
                         "already_present": len(rows) - inserted}
    result["inputs"] = {"accepted_tracking_rows": len(pts),
                         "eligible_airborne_rows": verified_airborne,
                         "observed_airborne_rows": sum(airborne_assessment(p) == "OBSERVED_AIRBORNE" for p in pts),
                         "inferred_airborne_rows": sum(airborne_assessment(p) == "INFERRED_AIRBORNE" for p in pts),
                         "real_grid_tracking_rows": real_grid_count,
                         "unknown_airborne_state_rows": sum(airborne_assessment(p) == "UNKNOWN" for p in pts),
                         "accepted_snapshot_rows": len(snapshots)}
    return result
