from datetime import datetime, timezone

from etl.loaders import (
    airspace_staging_row,
    iter_tartan_csv,
    load_tartan,
    tartan_staging_row,
    uas_staging_row,
    weather_staging_row,
)
from tests.fakes import FakeConn, FakeCursor

HEADER = (
    "ID,Time,Date,Altitude,Speed,Heading,Lat,Lon,Age,Range,Bearing,Tail,AltisGNSS\n"
)


def write_tartan_csv(path):
    path.write_text(
        HEADER
        + "123,\"[8, 9, 40.645667]\",\"[2022, 1, 1]\",1200,95,270,40.777,-79.949,1.2,5.5,-45.0,N12345,False\n"
        + "not-an-int,\"[8, 10, 0]\",\"[2022, 1, 1]\",1200,95,270,40.777,-79.949,1.2,5.5,45.0,N12345,False\n",
        encoding="utf-8",
    )
    return path


def test_tartan_iterator_yields_raw_rows_with_row_numbers(tmp_path):
    path = write_tartan_csv(tmp_path / "1.csv")

    rows = list(iter_tartan_csv(path))

    assert len(rows) == 2
    assert rows[0]["ID"] == "123"
    assert rows[0]["_source_row_number"] == 2
    assert rows[1]["ID"] == "not-an-int"
    assert rows[1]["_source_row_number"] == 3


def test_load_tartan_rejects_bad_row_and_accepts_next(tmp_path):
    path = write_tartan_csv(tmp_path / "1.csv")
    cursor = FakeCursor(existing_keys=set(), key_index=3)
    conn = FakeConn(cursor)

    counts = load_tartan(
        conn,
        path,
        source_file="01-01-22/1.csv",
        etl_run_id=1,
        source_manifest_id=9,
    )

    assert counts.rows_read == 2
    assert counts.rows_accepted == 1
    assert counts.rows_rejected == 1
    assert counts.rows_duplicate == 0
    assert counts.reconcile_ok()
    assert len(cursor.rejects) == 1
    assert cursor.rejects[0][2] is not None
    assert cursor.rejects[0][3] == "INVALID_VEHICLE_ID"


def test_tartan_staging_row_maps_identity_and_file():
    record = {
        "etl_run_id": 1,
        "source_manifest_id": 9,
        "source_system": "TARTAN",
        "source_record_id": "tartan:abc",
        "source_row_number": 2,
        "source_file": "01-01-22/1.csv",
        "event_ts": datetime(2022, 1, 1, 8, 9, 40, tzinfo=timezone.utc),
        "icao24_hex": "00007B",
        "callsign": "N12345",
        "latitude": 40.777,
        "longitude": -79.949,
        "altitude_ft": 1200,
        "altitude_source": "TARTAN_ALTISGNSS_FALSE",
        "ground_speed_kts": 95,
        "heading_deg": 270,
        "altis_gnss": False,
    }

    mapped = tartan_staging_row(record)

    assert mapped["icao24"] == "00007B"
    assert mapped["raw_file"] == "01-01-22/1.csv"
    assert mapped["source_row_number"] == 2
    assert mapped["source_quality_flag"] == "ALTISGNSS_FALSE"


def test_uas_staging_row_maps_serial_and_altitudes():
    record = {
        "etl_run_id": 1,
        "source_manifest_id": 9,
        "source_system": "NIGHTJAR",
        "source_record_id": "nightjar:abc",
        "source_row_number": 4,
        "source_file": "flight.csv",
        "serial_number": "5FSCK1601121D7",
        "source_flight_id": "flight.csv",
        "event_ts": datetime(2026, 8, 4, 16, 46, 25, tzinfo=timezone.utc),
        "latitude": 41.5,
        "longitude": -75.5,
        "altitude_msl_ft": 529.43,
        "altitude_agl_ft": 100.0,
        "ground_speed_kts": 9.7,
        "source_speed_mps": 5.0,
        "vertical_speed_fps": 3.28,
        "flight_state": "GPSAtti",
        "is_on_ground": False,
        "is_motor_on": True,
        "is_gps_used": True,
        "home_latitude": 41.5,
        "home_longitude": -75.5,
        "home_altitude_ft": 429.43,
    }

    mapped = uas_staging_row(record)

    assert mapped["vehicle_serial"] == "5FSCK1601121D7"
    assert mapped["flight_id"] == "flight.csv"
    assert mapped["altitude_msl_ft"] == 529.43
    assert mapped["altitude_agl_ft"] == 100.0
    assert mapped["source_speed_value"] == 5.0
    assert mapped["source_speed_unit"] == "m/s"
    assert mapped["raw_file"] == "flight.csv"


def test_weather_staging_row_preserves_report_context():
    record = {
        "etl_run_id": 1,
        "source_manifest_id": 9,
        "source_system": "AWC",
        "source_record_id": "awc:KBTP:1730000000",
        "station_icao": "KBTP",
        "observation_ts": datetime(2024, 10, 27, tzinfo=timezone.utc),
        "report_type": "METAR",
        "raw_text": "KBTP 270000Z",
        "flight_category": "VFR",
        "temperature_c": 10.0,
        "dewpoint_c": 4.0,
        "wind_speed_kts": 8.0,
        "wind_gust_kts": None,
        "wind_direction_deg": 270,
        "visibility_sm": 10.0,
        "cloud_ceiling_ft": 2500,
        "altimeter_inhg": 29.92,
        "station_lat": 40.777,
        "station_lon": -79.949,
        "station_elevation_m": 380,
    }

    mapped = weather_staging_row(record, source_row_number=3)

    assert mapped["source_row_number"] == 3
    assert mapped["report_type"] == "METAR"
    assert mapped["station_lat"] == 40.777
    assert mapped["cloud_ceiling_ft"] == 2500


def test_airspace_staging_row_maps_feature_context():
    record = {
        "etl_run_id": 1,
        "source_manifest_id": 9,
        "source_system": "FAA_AIRSPACE",
        "source_record_id": "GLOBAL-ID",
        "feature_type": "CLASS",
        "service_name": "Class_Airspace",
        "name": "Test Class D",
        "ident": "KAGC",
        "type_code": "CLASS_D",
        "class_code": "D",
        "lower_limit_ft": 0,
        "upper_limit_ft": 3000,
        "geometry_wkt": "POLYGON ((-80 40, -79 40, -79 41, -80 40))",
        "bbox_min_lat": 40,
        "bbox_min_lon": -80,
        "bbox_max_lat": 41,
        "bbox_max_lon": -79,
        "raw_attributes": {"GLOBAL_ID": "GLOBAL-ID"},
    }

    mapped = airspace_staging_row(record)

    assert mapped["source_object_id"] == "GLOBAL-ID"
    assert mapped["restriction_id"] == "KAGC"
    assert mapped["zone_name"] == "Test Class D"
    assert mapped["restriction_type"] == "CLASS"
    assert mapped["service_name"] == "Class_Airspace"
    assert mapped["is_static"] is True
    assert mapped["bbox_max_lat"] == 41
    assert "GLOBAL-ID" in str(mapped["raw_attributes"])
