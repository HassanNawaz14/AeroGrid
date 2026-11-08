from datetime import datetime, timezone

import pytest

from etl.errors import RowRejected
from etl.sources.metar import normalize_awc_observation, normalize_iem_row


def test_normalize_awc_observation_units_and_time():
    obs = {
        "icaoId": "KBTP",
        "obsTime": 1730000000,
        "reportTime": "2026-11-07T09:00:00Z",
        "metarType": "METAR",
        "temp": 10.0,
        "dewp": 4.0,
        "wdir": 270,
        "wspd": 8,
        "wgst": None,
        "visib": "10+",
        "altim": 1013.2,
        "slp": None,
        "clouds": [
            {"cover": "FEW", "base": 1000},
            {"cover": "BKN", "base": 2500},
        ],
        "fltCat": "MVFR",
        "rawOb": "KBTP 070900Z 27008KT 10SM FEW010 BKN025 10/04 A2992",
        "lat": 40.777,
        "lon": -79.949,
        "elev": 380,
    }

    row = normalize_awc_observation(
        obs,
        source_record_id="awc:KBTP:1730000000",
        etl_run_id="run-1",
        source_manifest_id=7,
    )

    assert row["source_system"] == "AWC"
    assert row["station_icao"] == "KBTP"
    assert row["observation_ts"] == datetime.fromtimestamp(1730000000, timezone.utc)
    assert row["temperature_c"] == pytest.approx(10.0)
    assert row["dewpoint_c"] == pytest.approx(4.0)
    assert row["wind_speed_kts"] == pytest.approx(8.0)
    assert row["wind_gust_kts"] is None
    assert row["wind_direction_deg"] == 270
    assert row["visibility_sm"] == pytest.approx(10.0)
    assert row["cloud_ceiling_ft"] == 2500
    assert row["altimeter_inhg"] == pytest.approx(29.92, abs=0.01)
    assert row["flight_category"] == "MVFR"
    assert row["source_record_id"] == "awc:KBTP:1730000000"
    assert row["etl_run_id"] == "run-1"


def test_normalize_awc_variable_wind_is_null():
    obs = {
        "icaoId": "KAGC",
        "obsTime": 1730000000,
        "metarType": "SPECI",
        "temp": 4,
        "dewp": 2,
        "wdir": "VRB",
        "wspd": 3,
        "visib": "3",
        "altim": 1000.0,
        "clouds": [{"cover": "OVC", "base": 600}],
        "fltCat": "IFR",
        "rawOb": "KAGC 070900Z VRB03KT 3SM OVC006 04/02 A2953",
        "lat": 40.35,
        "lon": -79.93,
        "elev": 380,
    }

    row = normalize_awc_observation(
        obs,
        source_record_id="awc:KAGC:1730000000",
        etl_run_id="run-1",
        source_manifest_id=7,
    )

    assert row["wind_direction_deg"] is None
    assert row["report_type"] == "SPECI"
    assert row["cloud_ceiling_ft"] == 600
    assert row["flight_category"] == "IFR"


def test_normalize_iem_row_converts_units_and_calm_wind():
    row = {
        "station": "BTP",
        "valid": "2022-01-01 00:53",
        "lon": "-79.949",
        "lat": "40.777",
        "tmpf": "32.00",
        "dwpf": "30.00",
        "relh": "88",
        "drct": "0",
        "sknt": "0",
        "gust": "M",
        "p01i": "M",
        "alti": "30.12",
        "mslp": "M",
        "vsby": "10.00",
        "skyc1": "BKN",
        "skyl1": "2000",
        "skyc2": "CLR",
        "skyl2": "M",
        "skyc3": "",
        "skyl3": "M",
        "skyc4": "",
        "skyl4": "M",
        "wxcodes": "",
        "metar": "KBTP 010053Z AUTO 00000KT 10SM BKN020 00/M01 A3012",
    }

    normalized = normalize_iem_row(
        row,
        station_icao="KBTP",
        source_record_id="iem:KBTP:2022-01-01 00:53",
        etl_run_id="run-1",
        source_manifest_id=8,
    )

    assert normalized["source_system"] == "IEM"
    assert normalized["station_icao"] == "KBTP"
    assert normalized["observation_ts"] == datetime(
        2022, 1, 1, 0, 53, tzinfo=timezone.utc
    )
    assert normalized["temperature_c"] == pytest.approx(0.0)
    assert normalized["dewpoint_c"] == pytest.approx(-1.1111, abs=0.001)
    assert normalized["wind_speed_kts"] == pytest.approx(0.0)
    assert normalized["wind_direction_deg"] is None
    assert normalized["wind_gust_kts"] is None
    assert normalized["visibility_sm"] == pytest.approx(10.0)
    assert normalized["cloud_ceiling_ft"] == 2000
    assert normalized["altimeter_inhg"] == pytest.approx(30.12)
    assert normalized["flight_category"] == "MVFR"


def test_awc_invalid_numeric_is_rejected_not_silently_nulled():
    obs = {
        "icaoId": "KBTP",
        "obsTime": 1730000000,
        "metarType": "METAR",
        "temp": "not-a-number",
        "dewp": 4,
        "wspd": 8,
        "visib": "10",
        "altim": 1013.2,
        "clouds": [],
        "rawOb": "KBTP 270000Z",
    }

    with pytest.raises(RowRejected) as excinfo:
        normalize_awc_observation(
            obs,
            source_record_id="awc:KBTP:1730000000",
            etl_run_id="run-1",
            source_manifest_id=7,
        )

    assert excinfo.value.reason_code == "INVALID_NUMERIC"


def test_iem_invalid_timestamp_is_rejected_with_source_id():
    row = {
        "valid": "not-a-time",
        "tmpf": "32",
        "dwpf": "30",
        "sknt": "0",
        "drct": "0",
        "vsby": "10",
        "alti": "30.12",
    }

    with pytest.raises(RowRejected) as excinfo:
        normalize_iem_row(
            row,
            station_icao="KBTP",
            source_record_id="iem:KBTP:not-a-time",
            etl_run_id="run-1",
            source_manifest_id=8,
        )

    assert excinfo.value.reason_code == "INVALID_TIMESTAMP"
    assert excinfo.value.source_record_id == "iem:KBTP:not-a-time"
