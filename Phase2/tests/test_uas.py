from datetime import datetime, timezone

import pytest

from etl.errors import RowRejected
from etl.sources.dji_nominal import normalize_nominal_row
from etl.sources.nightjar import normalize_nightjar_row


def test_normalize_nightjar_row_converts_speed_and_altitude():
    row = {
        "CUSTOM.dateTime": "2026-08-04T16:46:25.242Z",
        "OSD.flyTime": "0.1",
        "OSD.latitude": "41.53472",
        "OSD.longitude": "-75.59528",
        "OSD.height": "100.0",
        "OSD.altitude": "529.43",
        "OSD.xSpeed": "3.0",
        "OSD.ySpeed": "4.0",
        "OSD.zSpeed": "1.0",
        "OSD.flycState": "GPSAtti",
        "OSD.isOnGround": "FALSE",
        "OSD.isMotorOn": "TRUE",
        "OSD.isGPSUsed": "TRUE",
        "HOME.latitude": "41.53472458",
        "HOME.longitude": "-75.59528016",
        "HOME.altitude": "429.42978",
        "RECOVER.aircraftSerial": "5FSCK1601121D7",
        "RECOVER.aircraftName": "Amanda",
    }

    normalized = normalize_nightjar_row(
        row,
        source_file="dji/FlightRecord_2026-08-04_[12-46-25].csv",
        row_number=2,
        etl_run_id="run-1",
        source_manifest_id=10,
    )

    assert normalized["source_system"] == "NIGHTJAR"
    assert normalized["event_ts"] == datetime(
        2026, 8, 4, 16, 46, 25, 242000, tzinfo=timezone.utc
    )
    assert normalized["serial_number"] == "5FSCK1601121D7"
    assert normalized["aircraft_name"] == "Amanda"
    assert normalized["latitude"] == pytest.approx(41.53472)
    assert normalized["longitude"] == pytest.approx(-75.59528)
    assert normalized["altitude_agl_ft"] == pytest.approx(100.0)
    assert normalized["altitude_msl_ft"] == pytest.approx(529.43)
    assert normalized["ground_speed_kts"] == pytest.approx(9.71922, rel=1e-4)
    assert normalized["vertical_speed_fps"] == pytest.approx(3.28084, rel=1e-4)
    assert normalized["site_code"] == "NIGHTJAR_PA"
    assert normalized["home_altitude_ft"] == pytest.approx(429.42978)


def test_nightjar_1970_timestamp_is_rejected():
    row = {
        "CUSTOM.dateTime": "1970-01-01T00:00:00Z",
        "OSD.flyTime": "0",
        "OSD.latitude": "41.53472",
        "OSD.longitude": "-75.59528",
        "OSD.height": "0",
        "OSD.altitude": "0",
        "OSD.xSpeed": "0",
        "OSD.ySpeed": "0",
        "OSD.zSpeed": "0",
        "OSD.flycState": "EngineStart",
        "OSD.isOnGround": "TRUE",
        "OSD.isMotorOn": "FALSE",
        "OSD.isGPSUsed": "TRUE",
        "HOME.latitude": "0",
        "HOME.longitude": "0",
        "HOME.altitude": "0",
        "RECOVER.aircraftSerial": "5FSCK1601121D7",
        "RECOVER.aircraftName": "Amanda",
    }

    with pytest.raises(RowRejected) as excinfo:
        normalize_nightjar_row(
            row,
            source_file="dji/FlightRecord_2026-08-04_[12-46-25].csv",
            row_number=3,
            etl_run_id="run-1",
            source_manifest_id=10,
        )

    assert excinfo.value.reason_code == "INVALID_TIMESTAMP"


def test_normalize_nominal_row_uses_epoch_seconds_not_nanoseconds():
    row = {
        "timestamps_ns": "1730000000",
        "OSD.flyTime [s]": "12.5",
        "OSD.latitude": "39.62655794",
        "OSD.longitude": "-105.0007319",
        "OSD.height [ft]": "100.0",
        "OSD.altitude [ft]": "5448.2",
        "OSD.hSpeed [MPH]": "10.0",
        "OSD.xSpeed [MPH]": "6.0",
        "OSD.ySpeed [MPH]": "8.0",
        "OSD.zSpeed [MPH]": "0.0",
        "OSD.flycState": "P-GPS",
        "OSD.isGPSUsed": "TRUE",
        "OSD.isOnGround": "FALSE",
        "HOME.latitude": "39.62655794",
        "HOME.longitude": "-105.0007319",
        "HOME.height [ft]": "5348.2",
        "RECOVER.aircraftSerial": "1581F6Z9C241P003",
        "RECOVER.aircraftName": "DJI Mini 4 Pro",
    }

    normalized = normalize_nominal_row(
        row,
        source_file="colorado-drone-data/FlightRecord_2024-08-02.csv",
        row_number=2,
        etl_run_id="run-1",
        source_manifest_id=11,
        site_code="DJI_CO",
    )

    assert normalized["source_system"] == "NOMINAL_DJI"
    assert normalized["event_ts"] == datetime.fromtimestamp(
        1730000000, timezone.utc
    )
    assert normalized["serial_number"] == "1581F6Z9C241P003"
    assert normalized["latitude"] == pytest.approx(39.62655794)
    assert normalized["longitude"] == pytest.approx(-105.0007319)
    assert normalized["altitude_agl_ft"] == pytest.approx(100.0)
    assert normalized["altitude_msl_ft"] == pytest.approx(5448.2)
    assert normalized["ground_speed_kts"] == pytest.approx(8.68976, rel=1e-4)
    assert normalized["site_code"] == "DJI_CO"
    assert normalized["home_altitude_ft"] == pytest.approx(5348.2)


def test_nominal_zero_coordinate_is_rejected():
    row = {
        "timestamps": "1730000000",
        "OSD.flyTime [s]": "0.0",
        "OSD.latitude": "0",
        "OSD.longitude": "0",
        "OSD.height [ft]": "0",
        "OSD.altitude [ft]": "0",
        "OSD.hSpeed [MPH]": "0",
        "OSD.xSpeed [MPH]": "0",
        "OSD.ySpeed [MPH]": "0",
        "OSD.zSpeed [MPH]": "0",
        "OSD.flycState": "Starting Motors",
        "OSD.isGPSUsed": "FALSE",
        "OSD.isOnGround": "TRUE",
        "HOME.latitude": "0",
        "HOME.longitude": "0",
        "HOME.height [ft]": "0",
        "RECOVER.aircraftSerial": "1581F6Z9C241P003",
        "RECOVER.aircraftName": "DJI Mini 4 Pro",
    }

    with pytest.raises(RowRejected) as excinfo:
        normalize_nominal_row(
            row,
            source_file="colorado-drone-data/FlightRecord_2024-08-02.csv",
            row_number=3,
            etl_run_id="run-1",
            source_manifest_id=11,
            site_code="DJI_CO",
        )

    assert excinfo.value.reason_code == "ZERO_COORDINATE"
