"""Only invented TEST FIXTURES; never loaded to Neon or treated as real evidence."""
import pytest

from etl.wp07_data_readiness import (
    grid_from_real_position, airborne_assessment, eligible_airborne,
    KBTP_LAT, KBTP_LON, KBTP_FIELD_ELEVATION_FT_MSL,
)


def candidate(**override):
    row = dict(source_system='TARTAN', site_code='KBTP',
               altitude_source='TARTAN_ALTISGNSS_FALSE', on_ground=None,
               latitude=KBTP_LAT, longitude=KBTP_LON,
               ground_speed_kts=160, altitude_msl_ft=2600)
    row.update(override)
    return row


def test_grid_determinism_same_cell_negative_longitude():
    a = grid_from_real_position(5, 40.776, -79.951)
    b = grid_from_real_position(5, 40.779, -79.959)
    assert a.grid_cell_id == b.grid_cell_id == 'wp07-g01:5:4077:-7996'
    assert a.lat_center == 40.775 and a.lon_center == -79.955


def test_grid_changes_at_boundary_and_site():
    a = grid_from_real_position(5, 40.779, -79.959)
    assert grid_from_real_position(5, 40.7801, -79.959).grid_cell_id != a.grid_cell_id
    assert grid_from_real_position(6, 40.779, -79.959).grid_cell_id != a.grid_cell_id
    assert grid_from_real_position(0, 40.779, -79.959) is None
    assert grid_from_real_position(5, None, -79.959) is None
    assert grid_from_real_position(5, 95, -79.959) is None
    assert grid_from_real_position(5, float('nan'), -79.959) is None


def test_inference_scoped_to_realistic_barometric_kbtp_telemetry():
    assert airborne_assessment(candidate()) == 'INFERRED_AIRBORNE'
    assert eligible_airborne(candidate()) is True
    assert airborne_assessment(candidate(on_ground=False)) == 'OBSERVED_AIRBORNE'
    assert airborne_assessment(candidate(on_ground=True)) == 'OBSERVED_GROUND'
    assert airborne_assessment(candidate(source_system='DJI')) == 'UNKNOWN'
    assert airborne_assessment(candidate(site_code='KAGC')) == 'UNKNOWN'
    assert airborne_assessment(candidate(altitude_source='TARTAN_ALTISGNSS_TRUE')) == 'UNKNOWN'


def test_both_signals_are_required():
    assert airborne_assessment(candidate(ground_speed_kts=110)) == 'UNKNOWN'
    assert airborne_assessment(candidate(altitude_msl_ft=KBTP_FIELD_ELEVATION_FT_MSL+999)) == 'UNKNOWN'
    assert airborne_assessment(candidate(latitude=41.1)) == 'UNKNOWN'
    assert airborne_assessment(candidate(ground_speed_kts=None)) == 'UNKNOWN'
    assert airborne_assessment(candidate(altitude_msl_ft=None)) == 'UNKNOWN'
    assert airborne_assessment(candidate(latitude=float('nan'))) == 'UNKNOWN'


def test_source_explicit_ground_wins_over_high_speed_and_altitude():
    assert airborne_assessment(candidate(on_ground=True, ground_speed_kts=400, altitude_msl_ft=10000)) == 'OBSERVED_GROUND'


def test_original_derived_fact_builder_can_use_inferred_rows_without_mutating_source():
    from etl.derived_facts import build_occupancy
    from datetime import datetime, timezone, timedelta
    t = datetime(2022, 1, 1, 12, tzinfo=timezone.utc)
    p1 = dict(candidate(), tracking_id=11, vehicle_key=21, event_ts=t,
              time_key=44, grid_key=5, site_key=5, weather_key=-1)
    p2 = dict(p1, tracking_id=12, event_ts=t+timedelta(seconds=30))
    rows = build_occupancy([p1, p2], etl_run_id=9)
    assert len(rows) == 1
    assert rows[0]['active_vehicle_count'] == 1
    assert rows[0]['supporting_tracking_count'] == 2
    assert rows[0]['total_occupancy_minutes'] == 0.5
    assert p1['on_ground'] is None
