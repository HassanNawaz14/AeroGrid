"""WP-05 dimension helpers (Member C).

Pure normalization helpers for dimension natural keys and seed validation.
No database access.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def normalize_site_code(site_code: str | None) -> str | None:
    """Uppercase and trim a site code; None stays None (maps to dim_site -1)."""
    if site_code is None:
        return None
    code = site_code.strip().upper()
    return code or None


def dimension_natural_key(dim: str, values: dict[str, object]) -> tuple[object, ...]:
    """Return the natural-key tuple for a dimension, raising on missing parts."""
    keys = {
        "dim_time": ("hour_ts",),
        "dim_site": ("site_code",),
        "dim_vehicle": ("source_system", "source_entity_id"),
        "dim_spatial_grid": ("grid_cell_id",),
        "dim_weather": ("station_icao", "observation_ts"),
        "dim_airspace_zone": ("source_system", "source_object_id"),
    }[dim]
    missing = [k for k in keys if k not in values or values[k] is None]
    if missing:
        raise ValueError(f"{dim} natural key missing part(s): {missing}")
    return tuple(values[k] for k in keys)


def expected_hourly_spine_count(
    start: datetime, end: datetime, interval: timedelta
) -> int:
    """Count of hourly spine rows (inclusive start, exclusive end semantics)."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start and end must be timezone-aware")
    count = 0
    cursor = start
    while cursor < end:
        count += 1
        cursor += interval
    return count


__all__ = [
    "normalize_site_code",
    "dimension_natural_key",
    "expected_hourly_spine_count",
]
