"""WP-06 tracking and journey fact unit tests (Member D)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from etl.errors import RowRejected
from etl.facts import (
    ALGORITHM_VERSION,
    FACT_JOURNEY_COLUMNS,
    FACT_TRACKING_COLUMNS,
    TrackingPoint,
    build_lookups_from_rows,
    haversine_nm,
    load_tartan_flight_journeys,
    load_tartan_tracking_facts,
    map_adsb_staging_row,
    resolve_grid_key,
    resolve_vehicle_key,
    resolve_weather_key,
    segment_vehicle_journeys,
    utc_hour_bucket,
    validate_unknown_members,
)
from etl.staging_writer import insert_on_conflict_do_nothing
from etl.verify_wp06_facts import check_preflight, verify_sha256


class _InMemoryFactCursor:
    """Minimal cursor double supporting WP-06 SELECT, RETURNING, and batch savepoints."""

    def __init__(self, db: dict[str, Any]) -> None:
        self.db = db
        self.rowcount = 0
        self._last_rows: list[tuple[Any, ...]] = []

    def execute(self, sql: str, params: SequenceLike = ()) -> None:
        text = " ".join(sql.split())
        self._last_rows = []
        self.rowcount = 0

        if text.startswith("SELECT site_key, site_code FROM project_dw.dim_site"):
            self._last_rows = list(self.db["dim_site"])
            return
        if text.startswith("SELECT time_key, hour_ts FROM project_dw.dim_time"):
            self._last_rows = list(self.db["dim_time"])
            return
        if text.startswith(
            "SELECT vehicle_key, source_system, source_entity_id FROM project_dw.dim_vehicle"
        ):
            self._last_rows = list(self.db["dim_vehicle"])
            return
        if text.startswith(
            "SELECT grid_key, grid_cell_id, site_key, lat_bin, lon_bin FROM project_dw.dim_spatial_grid"
        ):
            self._last_rows = list(self.db["dim_spatial_grid"])
            return
        if text.startswith(
            "SELECT weather_key, site_key, observation_ts FROM project_dw.dim_weather"
        ):
            self._last_rows = list(self.db["dim_weather"])
            return

        if "FROM project_staging.stg_adsb_position" in text:
            rows = []
            for r in self.db["stg_adsb_position"]:
                if r[13] == "2022-REJECTED":
                    continue
                if "raw_file = %s" in text and params and r[13] != params[0]:
                    continue
                rows.append(r)
            self._last_rows = sorted(rows, key=lambda x: (x[3], x[2]))
            return

        if (
            "FROM project_dw.fact_vehicle_tracking f" in text
            and "JOIN project_staging.stg_adsb_position s" in text
        ):
            stg_by_key = {
                (r[1], r[2]): r for r in self.db["stg_adsb_position"]
            }
            out = []
            for f in self.db["fact_vehicle_tracking"]:
                key = (f["source_system"], f["source_record_id"])
                s = stg_by_key.get(key)
                if not s:
                    continue
                if "f.source_file = %s" in text and params and f["source_file"] != params[0]:
                    continue
                out.append(
                    (
                        f["vehicle_key"],
                        f["site_key"],
                        f["event_ts"],
                        f["time_key"],
                        f["grid_key"],
                        s[5],
                        s[6],
                        f["altitude_msl_ft"],
                        f["ground_speed_kts"],
                        f["source_system"],
                        f["source_record_id"],
                    )
                )
            self._last_rows = sorted(out, key=lambda r: (r[0], r[2], r[10]))
            return

        if text.startswith("INSERT INTO project_staging.stg_reject"):
            ncols = 6
            for i in range(0, len(params), ncols):
                self.db["stg_reject"].append(tuple(params[i : i + ncols]))
            self.rowcount = len(params) // ncols
            return

        if text.startswith("INSERT INTO project_dw.fact_vehicle_tracking"):
            ncols = len(FACT_TRACKING_COLUMNS)
            inserted = []
            seen = {
                (r["source_system"], r["source_record_id"])
                for r in self.db["fact_vehicle_tracking"]
            }
            for i in range(0, len(params), ncols):
                chunk = tuple(params[i : i + ncols])
                rec = dict(zip(FACT_TRACKING_COLUMNS, chunk))
                nk = (rec["source_system"], rec["source_record_id"])
                if nk not in seen:
                    seen.add(nk)
                    self.db["fact_vehicle_tracking"].append(rec)
                    inserted.append((rec["source_record_id"],))
            self._last_rows = inserted
            self.rowcount = len(inserted)
            return

        if text.startswith("INSERT INTO project_dw.fact_flight_journey"):
            ncols = len(FACT_JOURNEY_COLUMNS)
            inserted = []
            seen = {
                (r["source_system"], r["source_record_id"])
                for r in self.db["fact_flight_journey"]
            }
            for i in range(0, len(params), ncols):
                chunk = tuple(params[i : i + ncols])
                rec = dict(zip(FACT_JOURNEY_COLUMNS, chunk))
                nk = (rec["source_system"], rec["source_record_id"])
                if nk not in seen:
                    seen.add(nk)
                    self.db["fact_flight_journey"].append(rec)
                    inserted.append((rec["source_record_id"],))
            self._last_rows = inserted
            self.rowcount = len(inserted)
            return

        raise AssertionError(f"Unhandled SQL in fake: {text}")

    def fetchall(self) -> list[tuple[Any, ...]]:
        return list(self._last_rows)

    def fetchone(self) -> tuple[Any, ...]:
        if not self._last_rows:
            raise AssertionError("No row to fetchone")
        return self._last_rows.pop(0)


SequenceLike = tuple[Any, ...] | list[Any]


class _InMemoryFactConn:
    def __init__(self, db: dict[str, Any]) -> None:
        self.db = db

    def cursor(self) -> _InMemoryFactCursor:
        return _InMemoryFactCursor(self.db)


class _BatchSavepointFakeCursor:
    """Fake cursor supporting multi-row staging batch + rollback to savepoint."""

    def __init__(self, *, fail_key: str | None = None) -> None:
        self.existing: set[str] = set()
        self.fail_key = fail_key
        self.rejects: list[tuple[Any, ...]] = []
        self.rollbacks: list[str] = []
        self.failed = False
        self.rowcount = 0

    def execute(self, sql: str, params: SequenceLike = ()) -> None:
        text = " ".join(sql.split())
        if text.startswith("SAVEPOINT "):
            return
        if text.startswith("ROLLBACK TO SAVEPOINT "):
            self.rollbacks.append(text.split()[-1])
            self.failed = False
            return
        if text.startswith("RELEASE SAVEPOINT "):
            return
        if "INSERT INTO project_staging.stg_reject" in text:
            for i in range(0, len(params), 6):
                self.rejects.append(tuple(params[i : i + 6]))
            self.rowcount = len(params) // 6
            return
        if self.failed:
            raise RuntimeError("transaction aborted")
        if text.startswith("INSERT INTO project_staging.stg_adsb_position"):
            # 2 columns: (source_record_id, value)
            if self.fail_key is not None and self.fail_key in params:
                self.failed = True
                raise RuntimeError("forced DB error")
            inserted = 0
            for i in range(0, len(params), 2):
                key = str(params[i])
                if key not in self.existing:
                    self.existing.add(key)
                    inserted += 1
            self.rowcount = inserted
            return
        raise AssertionError(f"Unhandled SQL: {text}")


class _BatchSavepointFakeConn:
    def __init__(self, cursor: _BatchSavepointFakeCursor) -> None:
        self._cursor = cursor

    def cursor(self) -> _BatchSavepointFakeCursor:
        return self._cursor


def _base_lookups(
    *,
    vehicle_rows=None,
    grid_rows=None,
    weather_rows=None,
):
    return build_lookups_from_rows(
        site_rows=[(-1, "UNKNOWN"), (1, "KBTP"), (2, "KAGC")],
        time_rows=[
            (-1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc)),
            (10, datetime(2022, 1, 1, 8, 0, tzinfo=timezone.utc)),
            (11, datetime(2022, 1, 1, 9, 0, tzinfo=timezone.utc)),
        ],
        vehicle_rows=vehicle_rows
        if vehicle_rows is not None
        else [
            (-1, "UNKNOWN", "UNKNOWN"),
            (101, "tartan", "00007B"),
            (102, "TARTAN", "A037A0"),
        ],
        grid_rows=grid_rows
        if grid_rows is not None
        else [(-1, "UNKNOWN", -1, None, None)],
        weather_rows=weather_rows
        if weather_rows is not None
        else [(-1, -1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc))],
    )


def test_utc_hour_bucket_converts_timezone_and_rejects_naive():
    est = timezone(timedelta(hours=-5))
    local_ts = datetime(2022, 1, 1, 3, 45, 12, tzinfo=est)
    assert utc_hour_bucket(local_ts) == datetime(2022, 1, 1, 8, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        utc_hour_bucket(datetime(2022, 1, 1, 8, 0, 0))


def test_haversine_nm_matches_kbtp_to_kagc_and_zero_at_same_point():
    assert haversine_nm(40.777888, -79.949864, 40.777888, -79.949864) == 0.0
    dist_nm = haversine_nm(40.777888, -79.949864, 40.3544, -79.9302)
    assert 25.0 < dist_nm < 26.0


def test_vehicle_lookup_handles_source_casing_and_decimal_fallback():
    lookups = _base_lookups()
    assert resolve_vehicle_key(lookups, "TARTAN", "00007b") == 101
    assert resolve_vehicle_key(lookups, "SRC-TARTAN", "A037A0") == 102
    assert resolve_vehicle_key(lookups, "TARTAN", "FFFFFF") is None

    dec_lookups = _base_lookups(
        vehicle_rows=[
            (-1, "UNKNOWN", "UNKNOWN"),
            (201, "tartan", "123"),
            (202, "tartan", "10500000"),
        ]
    )
    assert dec_lookups.vehicle_decimal_fallback is True
    assert resolve_vehicle_key(dec_lookups, "TARTAN", "00007B") == 201
    assert resolve_vehicle_key(dec_lookups, "TARTAN", "A037A0") == 202


def test_grid_and_weather_optional_resolution_and_unknown_policy():
    lookups = _base_lookups(
        grid_rows=[
            (-1, "UNKNOWN", -1, None, None),
            (501, "KBTP_G1", 1, 40.775, -79.950),
            (502, "KBTP_G2", 1, 40.825, -79.950),
        ],
        weather_rows=[
            (-1, -1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc)),
            (601, 1, datetime(2022, 1, 1, 8, 53, tzinfo=timezone.utc)),
        ],
    )
    assert resolve_grid_key(lookups, 1, 40.777, -79.949) == 501
    assert resolve_grid_key(lookups, 1, 42.0, -79.950) == -1
    assert resolve_grid_key(lookups, 2, 40.777, -79.949) == -1

    ts_near = datetime(2022, 1, 1, 8, 30, tzinfo=timezone.utc)
    ts_far = datetime(2022, 1, 1, 10, 30, tzinfo=timezone.utc)
    assert resolve_weather_key(lookups, 1, ts_near) == 601
    assert resolve_weather_key(lookups, 1, ts_far) == -1


def test_map_adsb_staging_row_rejects_missing_required_dimension():
    lookups = _base_lookups()
    bad_vehicle_row = {
        "source_system": "TARTAN",
        "source_record_id": "tartan:missing-veh",
        "event_ts": datetime(2022, 1, 1, 8, 9, 40, tzinfo=timezone.utc),
        "icao24": "DEADBE",
        "latitude": 40.777,
        "longitude": -79.949,
        "altitude_ft": 1500.0,
        "altitude_source": "TARTAN_ALTISGNSS_FALSE",
        "ground_speed_kts": 110.0,
        "heading_deg": 180.0,
        "raw_file": "samples/kbtp/01-01-22/1.csv",
    }
    with pytest.raises(RowRejected) as excinfo:
        map_adsb_staging_row(bad_vehicle_row, lookups, etl_run_id=7)
    assert excinfo.value.reason_code == "MISSING_REQUIRED_DIMENSION"

    bad_time_row = dict(bad_vehicle_row, icao24="00007B", event_ts=datetime(2022, 1, 9, 8, 0, tzinfo=timezone.utc))
    with pytest.raises(RowRejected) as time_exc:
        map_adsb_staging_row(bad_time_row, lookups, etl_run_id=7)
    assert time_exc.value.reason_code == "MISSING_REQUIRED_DIMENSION"


def test_validate_unknown_members_fails_if_minus_one_absent():
    incomplete = build_lookups_from_rows(
        site_rows=[(1, "KBTP")],
        time_rows=[],
        vehicle_rows=[],
        grid_rows=[],
        weather_rows=[],
    )
    with pytest.raises(RuntimeError):
        validate_unknown_members(incomplete)


def test_segment_vehicle_journeys_handles_order_duplicates_gaps_and_single_points():
    t0 = datetime(2022, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    # Vehicle 101: 2 unordered points at t0+300s/t0 + exact duplicate ts, then gap >300s,
    # then a single isolated trailing point (must be skipped!).
    # Vehicle 102: single isolated point (must be skipped!).
    points = [
        TrackingPoint(101, 1, t0 + timedelta(seconds=300), 10, -1, 40.78, -79.95, 2000.0, None, "TARTAN", "r3"),
        TrackingPoint(101, 1, t0, 10, -1, 40.77, -79.95, 1500.0, 100.0, "TARTAN", "r1"),
        TrackingPoint(101, 1, t0, 10, -1, 40.77, -79.95, 1600.0, 120.0, "TARTAN", "r2"),
        TrackingPoint(101, 1, t0 + timedelta(seconds=601), 10, -1, 40.80, -79.95, 2200.0, 130.0, "TARTAN", "r4"),
        TrackingPoint(102, 1, t0 + timedelta(seconds=10), 10, -1, 40.79, -79.94, 1800.0, None, "TARTAN", "r5"),
    ]

    journeys, counts = segment_vehicle_journeys(points, etl_run_id=9, gap_split_sec=300)

    assert counts.vehicles_processed == 2
    assert counts.segments_built == 1
    assert counts.single_point_tracks_skipped == 2
    assert len(journeys) == 1

    j = journeys[0]
    assert j["vehicle_key"] == 101
    assert j["start_ts"] == t0
    assert j["end_ts"] == t0 + timedelta(seconds=300)
    assert j["flight_duration_sec"] == 300
    assert j["max_altitude_ft"] == 2000.0
    assert j["avg_speed_kts"] == 110.0  # None at r3 ignored cleanly
    assert j["total_distance_nm"] > 0.5
    assert j["journey_source"] == "ADS-B"
    assert j["segment_reason"] == "GAP_SPLIT(gap_sec=300)"
    assert j["algorithm_version"] == ALGORITHM_VERSION
    assert j["source_record_id"].startswith("journey:")


def test_fact_loaders_reconcile_and_are_idempotent_across_reruns():
    t0 = datetime(2022, 1, 1, 8, 10, 0, tzinfo=timezone.utc)
    t1 = datetime(2022, 1, 1, 8, 12, 0, tzinfo=timezone.utc)
    db: dict[str, Any] = {
        "dim_site": [(-1, "UNKNOWN"), (1, "KBTP")],
        "dim_time": [
            (-1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc)),
            (10, datetime(2022, 1, 1, 8, 0, tzinfo=timezone.utc)),
        ],
        "dim_vehicle": [(-1, "UNKNOWN", "UNKNOWN"), (101, "tartan", "00007B")],
        "dim_spatial_grid": [(-1, "UNKNOWN", -1, None, None)],
        "dim_weather": [(-1, -1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc))],
        "stg_adsb_position": [
            (1, "TARTAN", "tartan:1", t0, "00007B", 40.77, -79.95, 1500.0, "TARTAN_ALTISGNSS_FALSE", 100.0, 90.0, None, None, "samples/kbtp/01-01-22/1.csv", "ALTISGNSS_FALSE"),
            (2, "TARTAN", "tartan:2", t1, "00007B", 40.80, -79.95, 1700.0, "TARTAN_ALTISGNSS_FALSE", 110.0, 90.0, None, None, "samples/kbtp/01-01-22/1.csv", "ALTISGNSS_FALSE"),
            (3, "TARTAN", "tartan:unmapped", t1, "FFFFFF", 40.80, -79.95, 1700.0, "TARTAN_ALTISGNSS_FALSE", 110.0, 90.0, None, None, "samples/kbtp/01-01-22/1.csv", "ALTISGNSS_FALSE"),
        ],
        "stg_reject": [],
        "fact_vehicle_tracking": [],
        "fact_flight_journey": [],
    }
    conn = _InMemoryFactConn(db)

    t_pass1 = load_tartan_tracking_facts(
        conn, etl_run_id=1, source_file="samples/kbtp/01-01-22/1.csv"
    )
    assert t_pass1.rows_read == 3
    assert t_pass1.rows_inserted == 2
    assert t_pass1.rows_rejected == 1
    assert t_pass1.unknown_grid_count == 2
    assert t_pass1.unknown_weather_count == 2
    assert t_pass1.reconcile_ok()
    assert len(db["stg_reject"]) == 1
    assert db["stg_reject"][0][3] == "MISSING_REQUIRED_DIMENSION"

    j_pass1 = load_tartan_flight_journeys(
        conn, etl_run_id=1, source_file="samples/kbtp/01-01-22/1.csv"
    )
    assert j_pass1.segments_built == 1
    assert j_pass1.rows_inserted == 1
    assert j_pass1.reconcile_ok()

    # Pass 2 rerun: zero inserts, full idempotency
    t_pass2 = load_tartan_tracking_facts(
        conn, etl_run_id=2, source_file="samples/kbtp/01-01-22/1.csv"
    )
    assert t_pass2.rows_inserted == 0
    assert t_pass2.rows_duplicate == 2
    assert t_pass2.rows_rejected == 1
    assert t_pass2.reconcile_ok()

    j_pass2 = load_tartan_flight_journeys(
        conn, etl_run_id=2, source_file="samples/kbtp/01-01-22/1.csv"
    )
    assert j_pass2.rows_inserted == 0
    assert j_pass2.rows_duplicate == 1
    assert j_pass2.reconcile_ok()


def test_batched_staging_writer_handles_duplicates_and_chunk_fallback():
    cursor = _BatchSavepointFakeCursor(fail_key="bad_row")
    conn = _BatchSavepointFakeConn(cursor)

    def norm(r, **_):
        if r.get("bad_norm"):
            raise RowRejected("INVALID_NUMERIC", "bad", r["id"])
        return {"source_record_id": r["id"], "value": r["value"]}

    rows = [
        {"id": "ok1", "value": 1},
        {"id": "ok1", "value": 1},  # duplicate in batch
        {"id": "bad_norm_1", "bad_norm": True, "value": 0},
        {"id": "bad_row", "value": 2},
        {"id": "ok2", "value": 3},
    ]

    counts = insert_on_conflict_do_nothing(
        conn,
        table="project_staging.stg_adsb_position",
        columns=("source_record_id", "value"),
        rows=rows,
        conflict_target="(source_system, source_record_id)",
        etl_run_id=1,
        source_system="TARTAN",
        normalizer=norm,
        batch_size=4,
    )

    assert counts.rows_read == 5
    assert counts.rows_accepted == 2
    assert counts.rows_duplicate == 1
    assert counts.rows_rejected == 2
    assert counts.reconcile_ok()
    assert "staging_batch" in cursor.rollbacks
    assert "staging_row" in cursor.rollbacks
    assert len(cursor.rejects) == 2


def test_verifier_sha256_fails_closed_and_preflight_requires_real_vehicles(tmp_path):
    sample = tmp_path / "1.csv"
    sample.write_bytes(b"real bytes")
    with pytest.raises(ValueError):
        verify_sha256(sample, "0" * 64)

    class _PreflightCursor:
        def __init__(self) -> None:
            self._replies = [
                (True, True),
                (True, True),
                [("source_manifest",), ("etl_run_log",), ("stg_reject",), ("stg_adsb_position",)],
                [("dim_time",), ("dim_site",), ("dim_vehicle",), ("dim_spatial_grid",), ("dim_weather",), ("dim_airspace_zone",)],
                (168,),
                (1,),
                (0,),  # 0 real Tartan vehicles!
            ]

        def execute(self, sql, params=()):
            return None

        def fetchone(self):
            return self._replies.pop(0)

        def fetchall(self):
            return self._replies.pop(0)

    errs = check_preflight(_PreflightCursor())
    assert len(errs) == 1
    assert "03_seed_real.sql" in errs[0]

