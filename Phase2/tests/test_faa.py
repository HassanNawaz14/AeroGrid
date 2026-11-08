from datetime import datetime, timezone

import pytest

from etl.sources.faa import (
    normalize_airspace_feature,
    normalize_facility_feature,
    normalize_tfr_feature,
)

POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [
            [-80.0, 40.0],
            [-79.0, 40.0],
            [-79.0, 41.0],
            [-80.0, 41.0],
            [-80.0, 40.0],
        ]
    ],
}


def test_normalize_class_airspace_feature():
    feature = {
        "type": "Feature",
        "geometry": POLYGON,
        "properties": {
            "GLOBAL_ID": "A89A815A-B9A8-496E-95F9-7B30216287A5",
            "IDENT": "ATL",
            "NAME": "HARTSFIELD-JACKSON ATLANTA INTL MODE C",
            "TYPE_CODE": "MODE-C",
            "CLASS": "Other",
            "UPPER_VAL": 10000,
            "UPPER_UOM": "FT",
            "UPPER_DESC": "MSL",
            "LOWER_VAL": 0,
            "LOWER_UOM": "FT",
            "LOWER_DESC": "SFC",
        },
    }

    normalized = normalize_airspace_feature(
        feature,
        service_name="Class_Airspace",
        feature_type="CLASS",
        etl_run_id="run-1",
        source_manifest_id=12,
    )

    assert normalized["source_system"] == "FAA_AIRSPACE"
    assert normalized["source_record_id"] == "A89A815A-B9A8-496E-95F9-7B30216287A5"
    assert normalized["feature_type"] == "CLASS"
    assert normalized["name"] == "HARTSFIELD-JACKSON ATLANTA INTL MODE C"
    assert normalized["ident"] == "ATL"
    assert normalized["type_code"] == "MODE-C"
    assert normalized["lower_limit_ft"] == pytest.approx(0)
    assert normalized["upper_limit_ft"] == pytest.approx(10000)
    assert normalized["bbox_min_lat"] == pytest.approx(40.0)
    assert normalized["bbox_max_lat"] == pytest.approx(41.0)
    assert normalized["bbox_min_lon"] == pytest.approx(-80.0)
    assert normalized["bbox_max_lon"] == pytest.approx(-79.0)
    assert normalized["geometry_wkt"].startswith("POLYGON ((")


def test_special_use_vertical_strings_parse():
    feature = {
        "type": "Feature",
        "geometry": POLYGON,
        "properties": {
            "GLOBAL_ID": "5F02297F-7DF5-478E-B876-C758B6E4B910",
            "NAME": "A-220",
            "TYPE_CODE": "A",
            "CLASS": None,
            "UPPER_VAL": "4500",
            "LOWER_VAL": "0",
            "UPPER_DESC": "MSL",
            "LOWER_DESC": "SFC",
        },
    }

    normalized = normalize_airspace_feature(
        feature,
        service_name="Special_Use_Airspace",
        feature_type="SPECIAL_USE",
        etl_run_id="run-1",
        source_manifest_id=12,
    )

    assert normalized["lower_limit_ft"] == pytest.approx(0)
    assert normalized["upper_limit_ft"] == pytest.approx(4500)
    assert normalized["type_code"] == "A"


def test_normalize_facility_feature_uses_ceiling():
    feature = {
        "type": "Feature",
        "geometry": POLYGON,
        "properties": {
            "GLOBALID": "{FACILITY-GUID}",
            "CEILING": 300,
            "UNIT": "Feet",
            "MAP_EFF": "10/6/2022",
            "LAST_EDIT": "5/27/2022",
            "APT1_ICAO": "KAGC",
            "APT1_NAME": "Allegheny County Airport",
            "LATITUDE": 40.35,
            "LONGITUDE": -79.93,
        },
    }

    normalized = normalize_facility_feature(
        feature,
        etl_run_id="run-1",
        source_manifest_id=12,
    )

    assert normalized["source_system"] == "FAA_FACILITY"
    assert normalized["source_record_id"] == "{FACILITY-GUID}"
    assert normalized["feature_type"] == "FACILITY_MAP"
    assert normalized["airport_icao"] == "KAGC"
    assert normalized["upper_limit_ft"] == pytest.approx(300)
    assert normalized["lower_limit_ft"] == pytest.approx(0)


def test_tfr_epoch_milliseconds_convert_to_utc():
    feature = {
        "type": "Feature",
        "geometry": POLYGON,
        "properties": {
            "FAA_ID": "TFR-1",
            "Facility": "Test Facility",
            "Base": "Test Base",
            "Reason": "Security",
            "Floor": "Surface",
            "Ceiling": "400' AGL",
            "ALERTTIME": 1730000000000,
            "ACTIVETIME": 1730000000000,
            "ENDTIME": 1730003600000,
        },
    }

    normalized = normalize_tfr_feature(
        feature,
        etl_run_id="run-1",
        source_manifest_id=12,
    )

    assert normalized["source_system"] == "FAA_TFR"
    assert normalized["source_record_id"] == "TFR-1"
    assert normalized["feature_type"] == "TFR"
    assert normalized["active_start_ts"] == datetime(
        2024, 10, 27, 3, 33, 20, tzinfo=timezone.utc
    )
    assert normalized["active_end_ts"] == datetime(
        2024, 10, 27, 4, 33, 20, tzinfo=timezone.utc
    )
    assert normalized["upper_limit_ft"] == pytest.approx(400)
