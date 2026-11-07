from datetime import datetime, timezone

import pytest

from etl.errors import RowRejected
from etl.sources.tartan import (
    normalize_tartan_row,
    parse_tartan_timestamp,
    tartan_record_id,
)


def test_parse_tartan_timestamp_from_python_lists():
    parsed = parse_tartan_timestamp("[2022, 1, 1]", "[8, 9, 40.645667]")

    assert parsed == datetime(
        2022, 1, 1, 8, 9, 40, 645667, tzinfo=timezone.utc
    )


def test_tartan_record_id_is_stable_for_the_same_row():
    row = {
        "ID": "123",
        "Time": "[8, 9, 40.645667]",
        "Date": "[2022, 1, 1]",
        "Altitude": "1200",
        "Speed": "95",
        "Heading": "270",
        "Lat": "40.777",
        "Lon": "-79.949",
        "Age": "1.2",
        "Range": "5.5",
        "Bearing": "45.0",
        "Tail": "N12345",
        "AltisGNSS": "False",
    }

    first = tartan_record_id("01-01-22/1.csv", row)
    second = tartan_record_id("01-01-22/1.csv", dict(row))
    other_file = tartan_record_id("01-02-22/1.csv", dict(row))

    assert first == second
    assert first != other_file


def test_normalize_tartan_row_converts_identity_and_altitude_source():
    row = {
        "ID": "123",
        "Time": "[8, 9, 40.645667]",
        "Date": "[2022, 1, 1]",
        "Altitude": "1200",
        "Speed": "95",
        "Heading": "270",
        "Lat": "40.777",
        "Lon": "-79.949",
        "Age": "1.2",
        "Range": "5.5",
        "Bearing": "-45.0",
        "Tail": "N12345",
        "AltisGNSS": "False",
    }

    normalized = normalize_tartan_row(
        row,
        source_file="01-01-22/1.csv",
        row_number=2,
        etl_run_id="run-1",
        source_manifest_id=9,
    )

    assert normalized["source_system"] == "TARTAN"
    assert normalized["icao24_int"] == 123
    assert normalized["icao24_hex"] == "00007B"
    assert normalized["callsign"] == "N12345"
    assert normalized["event_ts"] == datetime(
        2022, 1, 1, 8, 9, 40, 645667, tzinfo=timezone.utc
    )
    assert normalized["latitude"] == pytest.approx(40.777)
    assert normalized["longitude"] == pytest.approx(-79.949)
    assert normalized["altitude_ft"] == pytest.approx(1200)
    assert normalized["altitude_source"] == "TARTAN_ALTISGNSS_FALSE"
    assert normalized["ground_speed_kts"] == pytest.approx(95)
    assert normalized["heading_deg"] == pytest.approx(270)
    assert normalized["range_km"] == pytest.approx(5.5)
    assert normalized["bearing_deg"] == pytest.approx(-45.0)
    assert normalized["site_code"] == "KBTP"
    assert normalized["source_record_id"].startswith("tartan:")


def test_normalize_tartan_row_rejects_impossible_altitude():
    row = {
        "ID": "123",
        "Time": "[6, 0, 4.0]",
        "Date": "[2022, 7, 31]",
        "Altitude": "106600",
        "Speed": "120",
        "Heading": "90",
        "Lat": "40.777",
        "Lon": "-79.949",
        "Age": "1.2",
        "Range": "5.5",
        "Bearing": "45.0",
        "Tail": "N12345",
        "AltisGNSS": "False",
    }

    with pytest.raises(RowRejected) as excinfo:
        normalize_tartan_row(
            row,
            source_file="07-31-22/1.csv",
            row_number=3,
            etl_run_id="run-1",
            source_manifest_id=9,
        )

    assert excinfo.value.reason_code == "ALTITUDE_OUT_OF_RANGE"
