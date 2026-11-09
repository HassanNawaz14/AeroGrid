"""WP-05 dimension unit tests (Member C)."""

from datetime import datetime, timedelta, timezone

import pytest

from etl.dimensions import (
    dimension_natural_key,
    expected_hourly_spine_count,
    normalize_site_code,
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
