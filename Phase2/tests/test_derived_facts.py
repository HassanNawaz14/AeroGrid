"""WP-07 tests. These small test-only fixtures are never written to the warehouse."""
from datetime import datetime, timedelta, timezone

import pytest

from etl.derived_facts import (
    ALGORITHM_VERSION,
    build_encounters,
    build_occupancy,
    build_restrictions,
    encounter_class,
    haversine_nm,
    utc,
)

T = datetime(2022, 1, 1, 12, 0, tzinfo=timezone.utc)


def position(tracking_id=1, vehicle_key=10, *, ts=T, lat=40.0,
             lon=-80.0, altitude_ft=1000, grid_key=101, site_key=1,
             on_ground=False, altitude_source="baro", speed=100):
    return dict(tracking_id=tracking_id, vehicle_key=vehicle_key, event_ts=ts,
                latitude=lat, longitude=lon, altitude_msl_ft=altitude_ft,
                altitude_source=altitude_source, ground_speed_kts=speed,
                on_ground=on_ground, grid_key=grid_key, site_key=site_key,
                time_key=12, weather_key=-1)


def snapshot(staging_id=5, *, ts=T, active=True):
    return dict(staging_id=staging_id, snapshot_ts=ts, source_system="FAA",
                source_object_id="real-id", is_active=active,
                effective_start_ts=T - timedelta(hours=1),
                effective_end_ts=T + timedelta(hours=1),
                reject_reason=None, zone_key=32, time_key=12, site_key=1)


def test_thresholds_are_strict_at_boundaries():
    assert encounter_class(.499, 499) == "SEVERE"
    assert encounter_class(.5, 499) == "PROXIMITY"
    assert encounter_class(.9, 999) == "PROXIMITY"
    assert encounter_class(1.0, 100) is None
    assert encounter_class(.1, 1000) is None
    assert encounter_class(-1, 1) is None
    assert ALGORITHM_VERSION == "wp07-v1"


def test_haversine_zero_and_utc_rules():
    assert haversine_nm(40, -80, 40, -80) == 0
    with pytest.raises(ValueError):
        utc(datetime(2022, 1, 1))


def test_encounters_require_simultaneous_airborne_real_positions():
    a = position()
    b = position(2, 11, lon=-79.999, altitude_ft=1250)
    rows = build_encounters([a, b], etl_run_id=8)
    assert len(rows) == 1
    row = rows[0]
    assert row["vehicle_key_1"] == 10 and row["vehicle_key_2"] == 11
    assert row["risk_severity_class"] == "SEVERE"
    assert row["conflict_duration_sec"] == 0
    assert row["min_tracking_id_1"] == 1
    assert build_encounters([a, dict(b, on_ground=True)], etl_run_id=8) == []
    assert build_encounters([a, dict(b, site_key=2)], etl_run_id=8) == []
    assert build_encounters([a, dict(b, event_ts=T + timedelta(seconds=1))], etl_run_id=8) == []
    assert build_encounters([a, dict(b, altitude_source="geo")], etl_run_id=8) == []
    assert build_encounters([a, dict(b, altitude_msl_ft=None)], etl_run_id=8) == []


def test_encounters_discard_unknown_coordinates_vehicles_and_duplicates():
    a = position()
    b = position(2, 11, lon=-79.999)
    assert build_encounters([a, dict(b, latitude=None)], etl_run_id=8) == []
    assert build_encounters([dict(a, vehicle_key=-1), b], etl_run_id=8) == []
    rows = build_encounters([a, b, dict(b, tracking_id=300)], etl_run_id=8)
    assert len(rows) == 1
    assert rows[0]["min_tracking_id_2"] == 2


def test_occupancy_counts_distinct_vehicles_and_observed_minutes():
    pts = [position(1, 10, ts=T),
           position(2, 10, ts=T+timedelta(seconds=30)),
           position(3, 11, ts=T+timedelta(seconds=10)),
           position(4, 11, ts=T+timedelta(seconds=20))]
    rows = build_occupancy(pts, etl_run_id=8)
    assert len(rows) == 1
    row = rows[0]
    assert row["active_vehicle_count"] == 2
    assert row["supporting_tracking_count"] == 4
    assert row["total_occupancy_minutes"] == 0.67
    assert row["avg_traffic_speed_kts"] == 100
    assert row["algorithm_version"] == "wp07-v1"


def test_occupancy_does_not_extrapolate_large_gaps_or_unknown_grids():
    pts = [position(1, 10),
           position(2, 10, ts=T+timedelta(minutes=8))]
    assert build_occupancy(pts, etl_run_id=8)[0]["total_occupancy_minutes"] == 0
    assert build_occupancy([position(grid_key=-1)], etl_run_id=8) == []
    assert build_occupancy([position(on_ground=True)], etl_run_id=8) == []
    with pytest.raises(ValueError):
        build_occupancy([position(), position(2, 11, site_key=2)], etl_run_id=8)
    with pytest.raises(ValueError):
        build_occupancy(pts, etl_run_id=8, gap_cap_sec=0)


def test_restrictions_preserve_snapshot_identity_and_null_compliance():
    rows = build_restrictions([snapshot()], etl_run_id=8)
    assert len(rows) == 1
    assert rows[0]["source_record_id"] == "snapshot:5"
    assert rows[0]["is_active"] is True
    assert rows[0]["affected_traffic_count"] is None
    assert rows[0]["compliance_rate_pct"] is None
    assert build_restrictions([dict(snapshot(), zone_key=-1)], etl_run_id=8) == []
    assert build_restrictions([dict(snapshot(), reject_reason="bad")], etl_run_id=8) == []
    assert build_restrictions([dict(snapshot(), is_active=None)], etl_run_id=8) == []


def test_restrictions_respect_effective_window_and_flag_contradictions():
    expired = dict(snapshot(), effective_end_ts=T)
    rows = build_restrictions([expired], etl_run_id=8)
    assert len(rows) == 1
    assert rows[0]["is_active"] is False
    assert len(build_restrictions([snapshot(), snapshot(staging_id=7)], etl_run_id=8)) == 1
    with pytest.raises(ValueError):
        build_restrictions([expired, snapshot(staging_id=7)], etl_run_id=8)
    assert build_restrictions([], etl_run_id=8) == []


def test_derive_fails_closed_when_airborne_status_unverified():
    from unittest.mock import patch
    from etl.derived_facts import derive_and_insert
    real_shape = position(on_ground=None, grid_key=-1)
    with patch("etl.derived_facts.fetch_tracking", return_value=[real_shape]), \
         patch("etl.derived_facts.fetch_snapshots", return_value=[]):
        with pytest.raises(ValueError, match="NO_VERIFIED_AIRBORNE.*NO_REAL_GRID"):
            derive_and_insert(object(), etl_run_id=8)


def test_derive_fails_closed_when_real_grid_is_missing():
    from unittest.mock import patch
    from etl.derived_facts import derive_and_insert
    real_shape = position(on_ground=False, grid_key=-1)
    with patch("etl.derived_facts.fetch_tracking", return_value=[real_shape]), \
         patch("etl.derived_facts.fetch_snapshots", return_value=[]):
        with pytest.raises(ValueError, match="NO_REAL_GRID"):
            derive_and_insert(object(), etl_run_id=8)
