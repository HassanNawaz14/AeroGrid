import pytest

from etl.transforms import (
    c_to_f,
    derive_ceiling_ft,
    derive_flight_category,
    f_to_c,
    hpa_to_inhg,
    mph_to_kts,
    mps_to_kts,
    parse_visibility_sm,
)


def test_celsius_fahrenheit_round_trip():
    assert c_to_f(0) == pytest.approx(32.0)
    assert c_to_f(15) == pytest.approx(59.0)
    assert f_to_c(32) == pytest.approx(0.0)
    assert f_to_c(59) == pytest.approx(15.0)


def test_hpa_to_inhg():
    assert hpa_to_inhg(1013.2) == pytest.approx(29.92, abs=0.01)
    assert hpa_to_inhg(None) is None


def test_speed_conversions_to_knots():
    assert mps_to_kts(10.0) == pytest.approx(19.4384, rel=1e-4)
    assert mph_to_kts(10.0) == pytest.approx(8.68976, rel=1e-4)
    assert mps_to_kts(None) is None
    assert mph_to_kts(None) is None


def test_visibility_parsing():
    assert parse_visibility_sm("10+") == pytest.approx(10.0)
    assert parse_visibility_sm("3") == pytest.approx(3.0)
    assert parse_visibility_sm("M") is None
    assert parse_visibility_sm("") is None
    assert parse_visibility_sm(None) is None


def test_ceiling_uses_lowest_broken_overcast_or_vertical_visibility():
    layers = [
        {"cover": "FEW", "base": 1000},
        {"cover": "SCT", "base": 2000},
        {"cover": "BKN", "base": 3500},
        {"cover": "OVC", "base": 5000},
    ]
    assert derive_ceiling_ft(layers) == 3500


def test_ceiling_is_none_for_clear_or_only_few_sct():
    assert derive_ceiling_ft([]) is None
    assert derive_ceiling_ft([{"cover": "FEW", "base": 1000}]) is None
    assert derive_ceiling_ft([{"cover": "SCT", "base": 1000}]) is None


def test_flight_category_thresholds():
    assert derive_flight_category(10.0, 5000) == "VFR"
    assert derive_flight_category(5.0, 5000) == "MVFR"
    assert derive_flight_category(2.0, 5000) == "IFR"
    assert derive_flight_category(10.0, 800) == "IFR"
    assert derive_flight_category(0.5, 5000) == "LIFR"
    assert derive_flight_category(None, 5000) is None
