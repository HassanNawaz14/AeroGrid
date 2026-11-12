"""WP-07: transparent airborne eligibility and deterministic real-position grid.

These are analytical *inferences*, not changes to the raw/source on_ground flag.
Never classify an unknown input as a confirmed observation; record the method.
Only apply the Tartan KBTP fallback to the documented barometric-altitude source.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

GRID_VERSION = 'wp07-g01'
GRID_STEP_DEGREES = 0.01
KBTP_LAT = 40.7765833
KBTP_LON = -79.9510833
KBTP_FIELD_ELEVATION_FT_MSL = 1248.4
# Human/owner-reviewed analytical screening criteria (NOT FAA safety minima).
MIN_INFERRED_SPEED_KTS = 120.0
MIN_HEIGHT_OVER_KBTP_FT = 1000.0
MAX_KBTP_RADIUS_NM = 10.0


@dataclass(frozen=True)
class GridCell:
    grid_cell_id: str
    site_key: int
    lat_index: int
    lon_index: int
    lat_center: float
    lon_center: float


def grid_from_real_position(site_key: int, latitude: Any, longitude: Any) -> GridCell | None:
    """Return the cell *key* of an observed coordinate; do not create source rows."""
    try:
        lat, lon = float(latitude), float(longitude)
        if site_key <= 0 or not math.isfinite(lat) or not math.isfinite(lon):
            return None
        if not (-90.0 < lat < 90.0 and -180.0 <= lon < 180.0):
            return None
    except (ValueError, TypeError):
        return None
    i, j = math.floor(lat * 100), math.floor(lon * 100)
    return GridCell(
        grid_cell_id=f'{GRID_VERSION}:{site_key}:{i}:{j}',
        site_key=site_key, lat_index=i, lon_index=j,
        lat_center=round((i + 0.5) / 100.0, 5),
        lon_center=round((j + 0.5) / 100.0, 5),
    )


def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 3440.065 * 2 * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def airborne_assessment(p: Mapping[str, Any]) -> str:
    """Return OBSERVED_AIRBORNE, INFERRED_AIRBORNE, OBSERVED_GROUND or UNKNOWN.

    A high-confidence, scope-limited inference requires TWO independent signals:
    barometric MSL altitude >= KBTP surveyed elevation + 1000 ft, AND ground speed
    >= 120 knots, with a valid position within 10 NM of KBTP. Thresholds are
    intentionally conservative and require a recorded team/owner decision.
    KBTP field elevation is *not* local terrain elevation; therefore outside
    the 10 NM study radius (or with GNSS altitude) the status stays UNKNOWN.
    """
    observed = p.get('on_ground')
    if observed is True:
        return 'OBSERVED_GROUND'
    if observed is False:
        return 'OBSERVED_AIRBORNE'
    if str(p.get('source_system') or '').strip().upper() != 'TARTAN':
        return 'UNKNOWN'
    if str(p.get('site_code') or '').strip().upper() != 'KBTP':
        return 'UNKNOWN'
    if str(p.get('altitude_source') or '').strip().upper() != 'TARTAN_ALTISGNSS_FALSE':
        return 'UNKNOWN'
    try:
        latitude = float(p['latitude'])
        longitude = float(p['longitude'])
        speed = float(p['ground_speed_kts'])
        alt = float(p['altitude_msl_ft'])
        if not all(map(math.isfinite, (latitude, longitude, speed, alt))):
            return 'UNKNOWN'
        if not (-90 < latitude < 90 and -180 <= longitude < 180):
            return 'UNKNOWN'
    except (TypeError, ValueError, KeyError):
        return 'UNKNOWN'
    if speed < MIN_INFERRED_SPEED_KTS:
        return 'UNKNOWN'
    if alt - KBTP_FIELD_ELEVATION_FT_MSL < MIN_HEIGHT_OVER_KBTP_FT:
        return 'UNKNOWN'
    if _haversine_nm(latitude, longitude, KBTP_LAT, KBTP_LON) > MAX_KBTP_RADIUS_NM:
        return 'UNKNOWN'
    return 'INFERRED_AIRBORNE'


def eligible_airborne(p: Mapping[str, Any]) -> bool:
    return airborne_assessment(p) in ('OBSERVED_AIRBORNE', 'INFERRED_AIRBORNE')
