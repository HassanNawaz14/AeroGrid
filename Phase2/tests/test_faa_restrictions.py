"""WP07 FAA readiness tests: fake features are test-only; no production data is generated."""

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from etl.faa_restrictions import (
    classify_window,
    fetch_tfr_features,
    make_study_bbox,
    query_params,
    summarize_tfr_features,
)

NOW = datetime(2026, 11, 13, 12, tzinfo=timezone.utc)


def feature(fid="TEST-TFR-1", start=None, end=None):
    return {"type": "Feature", "properties": {
        "FAA_ID": fid,
        "ACTIVETIME": None if start is None else int(start.timestamp() * 1000),
        "ENDTIME": None if end is None else int(end.timestamp() * 1000),
        "Floor": "Surface", "Ceiling": "400' AGL",
    }, "geometry": {"type": "Polygon", "coordinates": [[
        [-79.96, 40.77], [-79.94, 40.77], [-79.94, 40.78], [-79.96, 40.77]
    ]]}}


def test_complete_window_active():
    assert classify_window(NOW - timedelta(hours=1), NOW + timedelta(hours=1), NOW) == "ACTIVE_IN_WINDOW"


def test_window_start_inclusive_end_exclusive():
    assert classify_window(NOW, NOW + timedelta(seconds=1), NOW) == "ACTIVE_IN_WINDOW"
    assert classify_window(NOW - timedelta(seconds=1), NOW, NOW) == "EXPIRED_WINDOW"


def test_missing_window_stays_unknown():
    assert classify_window(None, NOW + timedelta(hours=1), NOW) == "UNKNOWN_WINDOW"
    assert classify_window(NOW - timedelta(hours=1), None, NOW) == "UNKNOWN_WINDOW"


def test_invalid_window_stays_unknown():
    assert classify_window(NOW, NOW, NOW) == "UNKNOWN_WINDOW"
    assert classify_window(NOW + timedelta(hours=1), NOW, NOW) == "UNKNOWN_WINDOW"


def test_naive_snapshot_fails_closed():
    with pytest.raises(ValueError):
        classify_window(NOW, NOW, datetime(2026, 11, 13))


def test_future_and_expired():
    assert classify_window(NOW + timedelta(hours=1), NOW + timedelta(hours=2), NOW) == "FUTURE_WINDOW"
    assert classify_window(NOW - timedelta(hours=2), NOW - timedelta(hours=1), NOW) == "EXPIRED_WINDOW"


def test_unique_real_source_ids_and_summary():
    result = summarize_tfr_features([feature("FAA-A", NOW - timedelta(hours=1), NOW + timedelta(hours=1)),
                                     feature("FAA-B")], as_of=NOW)
    assert result.returned_features == 2
    assert result.active_in_confirmed_window == 1
    assert result.unknown_window == 1
    with pytest.raises(ValueError):
        summarize_tfr_features([feature(), feature()], as_of=NOW)


def test_bbox_and_query_are_site_scoped():
    bbox = make_study_bbox(40.7765833, -79.9510833)
    q = query_params(bbox, offset=20, page_size=10)
    assert q["f"] == "geojson"
    assert q["geometryType"] == "esriGeometryEnvelope"
    assert q["spatialRel"] == "esriSpatialRelIntersects"
    assert q["resultOffset"] == "20"
    with pytest.raises(ValueError):
        make_study_bbox(140, -79)


def test_zero_current_tfr_features_is_not_error():
    data = fetch_tfr_features(make_study_bbox(40.7765, -79.9510), fetch_json=lambda url: {"type": "FeatureCollection", "features": []})
    assert data == []
    assert summarize_tfr_features(data, as_of=NOW).active_in_confirmed_window == 0


def test_pagination():
    requested = []
    def get(url):
        offset = int(parse_qs(urlparse(url).query)["resultOffset"][0])
        requested.append(offset)
        return {"type": "FeatureCollection", "features": [feature("F" + str(offset))] if offset < 2 else []}
    assert len(fetch_tfr_features(make_study_bbox(40.77, -79.95), page_size=1, fetch_json=get)) == 2
    assert requested == [0, 1, 2]


def test_invalid_api_payload_rejected():
    with pytest.raises(ValueError):
        fetch_tfr_features(make_study_bbox(40.77, -79.95), fetch_json=lambda url: {"error": {"code": 499}})
    with pytest.raises(ValueError):
        fetch_tfr_features(make_study_bbox(40.77, -79.95), fetch_json=lambda url: {"type": "not-a-collection"})
