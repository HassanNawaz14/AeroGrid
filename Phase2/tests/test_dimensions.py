"""WP-05 dimension unit tests (Member C)."""

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from etl.dimensions import (
    dimension_natural_key,
    expected_hourly_spine_count,
    normalize_site_code,
)
from etl.verify_wp05_dimensions import SQL_FILES as WP05_SQL_FILES

SEED_SQL = (
    Path(__file__).resolve().parents[1]
    / "sql"
    / "02_dimensions"
    / "03_seed_real.sql"
)

DIMENSIONS = [
    "dim_time",
    "dim_site",
    "dim_vehicle",
    "dim_spatial_grid",
    "dim_weather",
    "dim_airspace_zone",
]


def test_normalize_site_code_upcases_and_trims():
    assert normalize_site_code("  kbtp ") == "KBTP"
    assert normalize_site_code("KAGC") == "KAGC"
    assert normalize_site_code("") is None
    assert normalize_site_code(None) is None


def test_dimension_natural_key_requires_all_parts():
    with pytest.raises(ValueError):
        dimension_natural_key("dim_site", {"site_code": None})
    assert dimension_natural_key("dim_site", {"site_code": "KBTP"}) == ("KBTP",)
    assert dimension_natural_key(
        "dim_vehicle",
        {"source_system": "TARTAN", "source_entity_id": "N12345"},
    ) == ("TARTAN", "N12345")


def test_all_dimensions_have_a_defined_natural_key():
    assert set(DIMENSIONS) == {
        "dim_time",
        "dim_site",
        "dim_vehicle",
        "dim_spatial_grid",
        "dim_weather",
        "dim_airspace_zone",
    }


def test_hourly_spine_matches_2022_01_01_to_2022_01_07():
    start = datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2022, 1, 8, 0, 0, 0, tzinfo=timezone.utc)
    count = expected_hourly_spine_count(start, end, timedelta(hours=1))
    # 7 days * 24 hours
    assert count == 168
    assert count >= 100  # WP-05 dimension row-count floor


def test_hourly_spine_requires_timezone_aware_inputs():
    with pytest.raises(ValueError):
        expected_hourly_spine_count(
            datetime(2022, 1, 1), datetime(2022, 1, 2), timedelta(hours=1)
        )


def test_real_dimension_seed_has_unique_real_tartan_vehicles():
    assert SEED_SQL.is_file()
    assert SEED_SQL in WP05_SQL_FILES
    text = SEED_SQL.read_text(encoding="utf-8")
    ids = re.findall(r"\('tartan', '([0-9A-F]{6})'", text)
    assert len(ids) >= 100
    assert len(ids) == len(set(ids))
    assert "0D0B8B" in ids
    assert "INSERT INTO project_dw.dim_vehicle" in text
    assert "INSERT INTO project_dw.dim_weather" not in text
    assert re.search(r"(?im)^\s*DELETE\s", text) is None
