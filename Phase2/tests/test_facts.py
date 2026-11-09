"""WP-06 tracking and journey fact unit tests (Member D)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import patch

import pytest

from etl.errors import RowRejected
from etl.facts import (
    ALGORITHM_VERSION,
    FACT_JOURNEY_COLUMNS,
    FACT_TRACKING_COLUMNS,
    DimensionLookups,
    GridCell,
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
from etl.loaders import TARTAN_COLUMNS, load_tartan
from etl.staging_writer import insert_on_conflict_do_nothing
from etl.verify_wp06_facts import (
    check_preflight,
    main as verify_main,
    redact_secrets,
    run_db_assertions,
    verify_sha256,
)


class _InMemoryFactCursor:
    """Minimal cursor double supporting WP-06 SELECT, RETURNING, and batch savepoints."""

    def __init__(self, db: dict[str, Any]) -> None:
        self.db = db
        self.rowcount = 0
        self._last_rows: list[tuple[Any, ...]] = []

    def execute(self, sql: str, params: SequenceLike = ()) -> None:
        if len(params) > 65535:
            raise AssertionError(
                f"PostgreSQL 65,535 bind parameter limit exceeded: {len(params)}"
            )
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
                if len(r) > 15 and r[15] is not None:
                    continue
                if "raw_file = %s" in text and params and r[13] != params[0]:
                    continue
                rows.append(r[:15])
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

    def __init__(
        self,
        *,
        fail_key: str | None = None,
        num_cols: int = 2,
        key_col_idx: int = 0,
    ) -> None:
        self.existing: set[str] = set()
        self.fail_key = fail_key
        self.num_cols = num_cols
        self.key_col_idx = key_col_idx
        self.rejects: list[tuple[Any, ...]] = []
        self.rollbacks: list[str] = []
        self.max_params_seen = 0
        self.failed = False
        self.rowcount = 0

    def execute(self, sql: str, params: SequenceLike = ()) -> None:
        self.max_params_seen = max(self.max_params_seen, len(params))
        if len(params) > 65535:
            raise AssertionError(
                f"PostgreSQL 65,535 bind parameter limit exceeded: {len(params)}"
            )
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
            if self.fail_key is not None and self.fail_key in params:
                self.failed = True
                raise RuntimeError("forced DB error")
            inserted = 0
            for i in range(0, len(params), self.num_cols):
                key = str(params[i + self.key_col_idx])
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


def test_vehicle_lookup_handles_unpadded_sql_to_hex_ids():
    lookups = _base_lookups(
        vehicle_rows=[
            (-1, "UNKNOWN", "UNKNOWN"),
            (301, "TARTAN", "7b"),
            (302, "tartan", "a037a0"),
            (303, "TARTAN", "123"),
        ]
    )
    assert lookups.vehicle_decimal_fallback is False
    assert lookups.vehicle_unpadded_hex_fallback is True
    assert resolve_vehicle_key(lookups, "TARTAN", "00007B") == 301
    assert resolve_vehicle_key(lookups, "TARTAN", "A037A0") == 302
    assert resolve_vehicle_key(lookups, "TARTAN", "000123") == 303
    assert resolve_vehicle_key(lookups, "TARTAN", "000000") is None


def test_grid_lookup_bisect_matches_full_scan_and_manual_lookups_fallback():
    cells = []
    gid = 100
    for r in range(4):
        for c in range(4):
            gid += 1
            lat = 40.70 + r * 0.05
            lon = -80.00 + c * 0.05
            cells.append((gid, f"KBTP_{r}_{c}", 1, lat, lon))

    lookups = _base_lookups(
        grid_rows=[(-1, "UNKNOWN", -1, None, None), *reversed(cells)]
    )
    # Near exact cell center (r=2, c=1 -> lat=40.80, lon=-79.95, gid=110)
    assert resolve_grid_key(lookups, 1, 40.802, -79.948) == 110
    # Slightly off east/north inside tolerance
    assert resolve_grid_key(lookups, 1, 40.724, -79.976) == 101
    # Outside grid bounds returns -1
    assert resolve_grid_key(lookups, 1, 41.25, -79.95) == -1

    # Direct DimensionLookups construction without _grid_lats_by_site also works
    manual = DimensionLookups(
        site_by_code=lookups.site_by_code,
        time_by_hour=lookups.time_by_hour,
        vehicle_by_key=lookups.vehicle_by_key,
        vehicle_decimal_fallback=lookups.vehicle_decimal_fallback,
        grid_cells_by_site={
            1: [GridCell(c[0], c[1], c[2], c[3], c[4]) for c in cells]
        },
        grid_half_steps_by_site=lookups.grid_half_steps_by_site,
        weather_by_site=lookups.weather_by_site,
        has_unknown_members=lookups.has_unknown_members,
    )
    assert resolve_grid_key(manual, 1, 40.802, -79.948) == 110


def test_fact_loader_ignores_rejected_staging_rows_and_validates_params():
    t0 = datetime(2022, 1, 1, 8, 10, 0, tzinfo=timezone.utc)
    db: dict[str, Any] = {
        "dim_site": [(-1, "UNKNOWN"), (1, "KBTP")],
        "dim_time": [
            (-1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc)),
            (10, datetime(2022, 1, 1, 8, 0, tzinfo=timezone.utc)),
        ],
        "dim_vehicle": [(-1, "UNKNOWN", "UNKNOWN"), (101, "TARTAN", "00007B")],
        "dim_spatial_grid": [(-1, "UNKNOWN", -1, None, None)],
        "dim_weather": [(-1, -1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc))],
        "stg_adsb_position": [
            (1, "TARTAN", "tartan:ok", t0, "00007B", 40.77, -79.95, 1500.0, "TARTAN_ALTISGNSS_FALSE", 100.0, 90.0, None, None, "samples/kbtp/01-01-22/1.csv", "ALTISGNSS_FALSE", None),
            (2, "TARTAN", "tartan:stg-bad", t0, "00007B", 40.77, -79.95, 99999.0, "TARTAN_ALTISGNSS_FALSE", 100.0, 90.0, None, None, "samples/kbtp/01-01-22/1.csv", "ALTISGNSS_FALSE", "ALTITUDE_OUT_OF_RANGE"),
        ],
        "stg_reject": [],
        "fact_vehicle_tracking": [],
        "fact_flight_journey": [],
    }
    conn = _InMemoryFactConn(db)

    counts = load_tartan_tracking_facts(
        conn, etl_run_id=1, source_file="samples/kbtp/01-01-22/1.csv"
    )
    assert counts.rows_read == 1
    assert counts.rows_inserted == 1
    assert counts.rows_rejected == 0

    with pytest.raises(ValueError):
        load_tartan_tracking_facts(conn, etl_run_id=1, batch_size=0)
    with pytest.raises(ValueError):
        load_tartan_flight_journeys(conn, etl_run_id=1, batch_size=0)
    with pytest.raises(ValueError):
        load_tartan_flight_journeys(conn, etl_run_id=1, gap_split_sec=0)


def test_segment_vehicle_journeys_exact_gap_boundary_and_null_speeds():
    t0 = datetime(2022, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    points = [
        TrackingPoint(101, 1, t0, 10, 501, 40.77, -79.95, 1500.0, None, "TARTAN", "p1"),
        TrackingPoint(101, 1, t0 + timedelta(seconds=300), 10, -1, 40.78, -79.95, 1600.0, None, "TARTAN", "p2"),
        TrackingPoint(101, 1, t0 + timedelta(seconds=601), 10, 502, 40.80, -79.95, 1800.0, None, "TARTAN", "p3"),
        TrackingPoint(101, 1, t0 + timedelta(seconds=661), 10, 502, 40.81, -79.95, 1900.0, None, "TARTAN", "p4"),
    ]
    journeys, counts = segment_vehicle_journeys(points, etl_run_id=4, gap_split_sec=300)

    assert counts.segments_built == 2
    assert counts.single_point_tracks_skipped == 0
    assert counts.unknown_origin_grid_count == 0
    assert counts.unknown_destination_grid_count == 1
    assert journeys[0]["flight_duration_sec"] == 300
    assert journeys[0]["origin_grid_key"] == 501
    assert journeys[0]["destination_grid_key"] == -1
    assert journeys[0]["avg_speed_kts"] is None
    assert journeys[0]["segment_reason"] == "GAP_SPLIT(gap_sec=300)"
    assert journeys[1]["flight_duration_sec"] == 60
    assert journeys[1]["origin_grid_key"] == 502
    assert journeys[1]["destination_grid_key"] == 502
    assert journeys[1]["avg_speed_kts"] is None
    assert journeys[1]["segment_reason"] == "FILE_BOUNDARY(gap_sec=300)"

    with pytest.raises(ValueError):
        segment_vehicle_journeys(points, etl_run_id=4, gap_split_sec=0)


def test_load_tartan_malformed_csv_quirks_with_batched_savepoints(tmp_path):
    csv_path = tmp_path / "1.csv"
    csv_path.write_text(
        "ID,Time,Date,Altitude,Speed,Heading,Lat,Lon,Age,Range,Bearing,Tail,AltisGNSS\n"
        '123,"[8, 9, 40.645667]","[2022, 1, 1]",1200,95,270,40.777,-79.949,1.2,5.5,-45.0,N12345,False\n'
        '123,"[8, 9, 40.645667]","[2022, 1, 1]",1200,95,270,40.777,-79.949,1.2,5.5,-45.0,N12345,False\n'
        '10500000,"[8, 10, 5.5]","[2022, 1, 1]",1800,,,40.780,-79.945,0.5,6.0,10.0,,True\n'
        "\n"
        ",,,,,,,,,,,,\n"
        '123,"[8, 11, 0]"\n'
        'bad\x00id,"[8, 12, 0]","[2022, 1, 1]",1200,95,270,40.777,-79.949,1.2,5.5,-45.0,N999,False,EXTRA\n',
        encoding="utf-8",
    )

    cursor = _BatchSavepointFakeCursor(num_cols=len(TARTAN_COLUMNS), key_col_idx=3)
    conn = _BatchSavepointFakeConn(cursor)
    long_source_file = "samples/" + ("x/" * 95) + "1.csv"

    counts = load_tartan(
        conn,
        csv_path,
        source_file=long_source_file,
        etl_run_id=12,
        source_manifest_id=9,
        batch_size=4,
    )

    # Blank line skipped by csv.DictReader; 6 non-empty rows parsed:
    # 2 accepted (123 + 10500000 with missing Speed/Heading/Tail),
    # 1 duplicate (second 123 row), 3 rejected (comma-only, short row, bad\x00id + EXTRA col).
    assert counts.rows_read == 6
    assert counts.rows_accepted == 2
    assert counts.rows_duplicate == 1
    assert counts.rows_rejected == 3
    assert counts.reconcile_ok()
    assert len(cursor.rejects) == 3
    assert all(
        r[2] is None or (len(r[2]) <= 160 and "\x00" not in r[2])
        for r in cursor.rejects
    )
    assert all(r[5] is None or "\x00" not in r[5] for r in cursor.rejects)


def test_batch_chunking_respects_postgresql_65535_param_limit():
    # Staging writer with 17 columns + oversized batch_size=10000 -> must chunk <= 3855 rows
    stg_cursor = _BatchSavepointFakeCursor(num_cols=len(TARTAN_COLUMNS), key_col_idx=3)
    stg_conn = _BatchSavepointFakeConn(stg_cursor)
    base_ts = datetime(2022, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    stg_inputs = [
        {
            col: (f"tartan:{i}" if col == "source_record_id" else i)
            for col in TARTAN_COLUMNS
        }
        for i in range(4200)
    ]
    stg_counts = insert_on_conflict_do_nothing(
        stg_conn,
        table="project_staging.stg_adsb_position",
        columns=TARTAN_COLUMNS,
        rows=stg_inputs,
        conflict_target="(source_system, source_record_id)",
        etl_run_id=1,
        source_system="TARTAN",
        batch_size=10000,
    )
    assert stg_counts.rows_accepted == 4200
    assert stg_cursor.max_params_seen <= 65535

    # Fact tracking loader with 19 columns + batch_size=10000 -> must chunk <= 3449 rows
    db: dict[str, Any] = {
        "dim_site": [(-1, "UNKNOWN"), (1, "KBTP")],
        "dim_time": [
            (-1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc)),
            (10, datetime(2022, 1, 1, 8, 0, tzinfo=timezone.utc)),
        ],
        "dim_vehicle": [(-1, "UNKNOWN", "UNKNOWN"), (101, "TARTAN", "00007B")],
        "dim_spatial_grid": [(-1, "UNKNOWN", -1, None, None)],
        "dim_weather": [(-1, -1, datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc))],
        "stg_adsb_position": [
            (
                i + 1,
                "TARTAN",
                f"tartan:{i:05d}",
                base_ts + timedelta(seconds=(i % 3600)),
                "00007B",
                40.77,
                -79.95,
                1500.0,
                "TARTAN_ALTISGNSS_FALSE",
                100.0,
                90.0,
                None,
                None,
                "samples/kbtp/01-01-22/1.csv",
                "ALTISGNSS_FALSE",
            )
            for i in range(3600)
        ],
        "stg_reject": [],
        "fact_vehicle_tracking": [],
        "fact_flight_journey": [],
    }
    fact_conn = _InMemoryFactConn(db)
    t_counts = load_tartan_tracking_facts(
        fact_conn,
        etl_run_id=1,
        source_file="samples/kbtp/01-01-22/1.csv",
        batch_size=10000,
    )
    assert t_counts.rows_inserted == 3600
    assert t_counts.reconcile_ok()


def test_verifier_redact_secrets_db_assertions_and_cli_guards():
    dummy_dsn = "postgresql" + "://u:fake_pw_123@example.invalid/neondb?sslmode=require"
    dummy_short = "postgres" + "://u2:pw2@db/x"
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": dummy_dsn,
            "NEON_S3_SECRET_ACCESS_KEY": "s3_dummy_key_value",
        },
        clear=False,
    ):
        msg = redact_secrets(
            f"connect error on {dummy_dsn} or {dummy_short} using s3_dummy_key_value"
        )
        assert "fake_pw_123" not in msg
        assert "pw2@db" not in msg
        assert "s3_dummy_key_value" not in msg
        assert "***" in msg

        with patch("sys.argv", ["verify_wp06_facts.py", "--batch-size", "0"]):
            assert verify_main() == 2
        with patch("sys.argv", ["verify_wp06_facts.py", "--gap-split-sec", "0"]):
            assert verify_main() == 2

    class _AssertionsCursor:
        def __init__(self, *, unmatched: int = 0) -> None:
            self._replies = [
                [("dim_time",), ("fact_vehicle_tracking",), ("fact_flight_journey",)],
                (169,), (5,), (50,), (1,), (1,), (1,),  # 6 dim counts
                (20000,), (500,),  # 2 fact counts
                [],  # no dup NK tracking
                [],  # no dup NK journey
                *([(0,)] * 13),  # 13 orphan checks
                (0,),  # req tracking unknown
                (0,),  # req journey unknown
                (20000, 20000),  # optional unknown grid/weather
                (20000,),  # stg accepted
                (20000,),  # fact tracking for file
                (unmatched,),  # unmatched staging
                (True,),  # reader SELECT privilege
            ]

        def execute(self, sql, params=()):
            return None

        def fetchone(self):
            val = self._replies.pop(0)
            return val if val else None

        def fetchall(self):
            return self._replies.pop(0)

    report = run_db_assertions(_AssertionsCursor(unmatched=0), source_file="samples/kbtp/01-01-22/1.csv")
    assert report["total_facts"] == 20500
    assert report["orphan_total"] == 0
    assert report["reader_select_ok"] is True

    with pytest.raises(AssertionError):
        run_db_assertions(_AssertionsCursor(unmatched=3), source_file="samples/kbtp/01-01-22/1.csv")

