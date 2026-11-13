from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

import etl.fetch as fetch_module
from etl.config import LIMITATIONS, SOURCE_LICENSES
from etl.dimension_loaders import airspace_sql, refresh_dimensions, weather_sql
from etl.fetch import FetchedFile, arcgis_query_url, fetch_airspace_layer, iem_metar_url
from etl.run import (
    APPLY_CONFIRMATION,
    PreviewCounts,
    _persist_results,
    apply_files,
    check_apply_guard,
    check_licenses,
    check_preview_totals,
    main,
    parse_sources,
    parse_stations,
    preview_file,
    preview_sources,
    render_summary,
    resolve_window,
    run,
)
from tests.fakes import FakeConn, FakeCursor

IEM_HEADER = (
    "station,valid,tmpf,dwpf,sknt,gust,drct,vsby,alti,lat,lon,skyc1,skyl1,metar\n"
)


def write_iem_csv(path: Path, rows: list[str]) -> Path:
    path.write_text(IEM_HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def iem_row(valid: str) -> str:
    return (
        f"BTP,{valid},50.00,40.00,5,M,270,10.00,30.12,40.777,-79.949,BKN,2000,"
        "KBTP 011053Z 27005KT 10SM BKN020 10/04 A3012"
    )


def faa_feature(global_id: str) -> dict:
    return {
        "type": "Feature",
        "properties": {
            "GLOBAL_ID": global_id,
            "IDENT": "PIT",
            "NAME": "Pittsburgh Class C",
            "TYPE_CODE": "CLASS",
            "CLASS": "C",
            "LOWER_VAL": 0,
            "UPPER_VAL": 4000,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-80.2, 40.4],
                    [-80.0, 40.4],
                    [-80.0, 40.8],
                    [-80.2, 40.8],
                    [-80.2, 40.4],
                ]
            ],
        },
    }


def test_parse_sources_and_stations_normalize_and_reject_unknown():
    assert parse_sources("Weather, uas ,airspace,weather") == (
        "weather",
        "uas",
        "airspace",
    )
    with pytest.raises(ValueError, match="Unknown sources"):
        parse_sources("weather,opensky")
    with pytest.raises(ValueError, match="at least one source"):
        parse_sources(" , ")

    assert parse_stations("kbtp, kagc") == ("KBTP", "KAGC")
    with pytest.raises(ValueError, match="Invalid METAR station"):
        parse_stations("KBT")


def test_resolve_window_defaults_and_validation(monkeypatch):
    monkeypatch.setattr("etl.run.recent_window", lambda days: (100, 101))
    assert resolve_window(None, None) == (100, 101)
    assert resolve_window("2026-11-01", "2026-11-07") == (
        date(2026, 11, 1),
        date(2026, 11, 7),
    )
    with pytest.raises(ValueError, match="supplied together"):
        resolve_window("2026-11-01", None)
    with pytest.raises(ValueError, match="before --start"):
        resolve_window("2026-11-07", "2026-11-01")


def test_apply_guard_requires_ci_environment_and_confirmation():
    with pytest.raises(ValueError, match="approved warehouse"):
        check_apply_guard({}, APPLY_CONFIRMATION)
    with pytest.raises(ValueError, match="approved warehouse"):
        check_apply_guard({"GITHUB_ACTIONS": "true"}, APPLY_CONFIRMATION)
    with pytest.raises(ValueError, match="--confirm"):
        check_apply_guard(
            {"GITHUB_ACTIONS": "true", "WAREHOUSE_CI_APPROVED": "true"}, "approve"
        )
    check_apply_guard(
        {"GITHUB_ACTIONS": "true", "WAREHOUSE_CI_APPROVED": "true"},
        APPLY_CONFIRMATION,
    )


def test_iem_url_requests_utc_onlycomma_and_both_report_types():
    url = iem_metar_url("kbtp", date(2022, 1, 1), date(2022, 1, 2))
    assert "station=KBTP" in url
    assert "data=metar" in url
    assert "tz=UTC" in url
    assert "format=onlycomma" in url
    assert url.count("report_type=") == 2
    assert "day1=1" in url and "day2=2" in url


def test_arcgis_query_url_includes_bbox_offset_and_geojson():
    url = arcgis_query_url("Class_Airspace", (-80.0, 40.0, -79.5, 40.5), offset=250)
    assert "Class_Airspace/FeatureServer/0/query" in url
    assert "f=geojson" in url
    assert "resultOffset=250" in url
    assert "geometry=-80.0%2C40.0%2C-79.5%2C40.5" in url


def test_fetch_airspace_layer_stops_on_short_page(monkeypatch):
    pages = [
        {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"GLOBAL_ID": str(i)}}
            for i in range(2)
        ]},
    ]
    calls = []

    def fake_json(url):
        calls.append(url)
        return pages[len(calls) - 1]

    monkeypatch.setattr(fetch_module, "_http_json", fake_json)
    features = fetch_airspace_layer("Class_Airspace", (-80, 40, -79, 41))
    assert len(features) == 2
    assert len(calls) == 1


def test_fetch_airspace_layer_empty_followup_page_ends_pagination(monkeypatch):
    full_page = [
        {"type": "Feature", "properties": {"GLOBAL_ID": str(i)}}
        for i in range(fetch_module.PAGE_SIZE)
    ]
    pages = iter([
        {"type": "FeatureCollection", "features": full_page},
        {"type": "FeatureCollection", "features": []},
    ])
    monkeypatch.setattr(fetch_module, "_http_json", lambda url: next(pages))
    features = fetch_airspace_layer("Class_Airspace", (-80, 40, -79, 41))
    assert len(features) == fetch_module.PAGE_SIZE


def test_get_retries_transient_transport_errors(monkeypatch):
    calls = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self, size):
            return b"ok"

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) < 3:
            raise URLError("temporary")
        return Response()

    monkeypatch.setattr(fetch_module, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetch_module, "_retry_pause", lambda attempt: None)

    assert fetch_module._get("https://example.test/data?x=1", 10) == b"ok"
    assert len(calls) == 3


def test_get_does_not_retry_a_client_error(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        raise HTTPError(request.full_url, 404, "Not Found", None, None)

    monkeypatch.setattr(fetch_module, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match=r"Source unavailable \(404\)"):
        fetch_module._get("https://example.test/missing", 10)
    assert len(calls) == 1


def test_http_json_names_the_source_after_repeated_api_errors(monkeypatch):
    monkeypatch.setattr(
        fetch_module,
        "_get",
        lambda url, limit: b'{"error": {"code": 503, "message": "busy"}}',
    )
    monkeypatch.setattr(fetch_module, "_retry_pause", lambda attempt: None)

    with pytest.raises(
        ValueError, match="Source reported an API error at https://example.test/data"
    ):
        fetch_module._http_json("https://example.test/data?f=json")


def test_http_json_recovers_after_a_transient_api_error(monkeypatch):
    payloads = iter([b'{"error": "rate limited"}', b'[{"station": "KBTP"}]'])
    monkeypatch.setattr(fetch_module, "_get", lambda url, limit: next(payloads))
    monkeypatch.setattr(fetch_module, "_retry_pause", lambda attempt: None)

    assert fetch_module._http_json("https://example.test/data") == [
        {"station": "KBTP"}
    ]


def test_fetch_sources_uses_awc_for_recent_window_and_iem_for_history(monkeypatch):
    def fake_awc(stations, hours, dest):
        return [FetchedFile("weather", "AWC", dest / "a.json", "awc")]

    def fake_iem(stations, start, end, dest):
        return [FetchedFile("weather", "IEM", dest / "i.csv", "iem")]

    monkeypatch.setattr(fetch_module, "fetch_awc_metar", fake_awc)
    monkeypatch.setattr(fetch_module, "fetch_iem_metar", fake_iem)

    today = datetime.now(timezone.utc).date()
    recent = fetch_module.fetch_sources(
        ("weather",), today - timedelta(days=6), today, Path("."), stations=("KBTP",)
    )
    historical = fetch_module.fetch_sources(
        ("weather",), today - timedelta(days=30), today - timedelta(days=20),
        Path("."), stations=("KBTP",),
    )
    assert recent[0].system == "AWC"
    assert historical[0].system == "IEM"


def test_preview_file_counts_valid_and_rejected_iem_rows(tmp_path):
    path = write_iem_csv(
        tmp_path / "iem_KBTP.csv",
        [iem_row("2026-11-01 10:53"), iem_row("2026-11-01 11:53"), iem_row("bad-time")],
    )
    counts = preview_file(
        FetchedFile("weather", "IEM", path, "url", station_icao="KBTP")
    )
    assert counts.rows_read == 3
    assert counts.rows_accepted == 2
    assert counts.rows_rejected == 1
    assert counts.rejects_by_reason == {"INVALID_TIMESTAMP": 1}


def test_preview_file_rejects_airspace_feature_without_global_id(tmp_path):
    path = tmp_path / "faa.geojson"
    payload = {
        "type": "FeatureCollection",
        "features": [faa_feature("G1"), {"type": "Feature", "properties": {}}],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    counts = preview_file(
        FetchedFile(
            "airspace",
            "FAA-Airspace",
            path,
            "url",
            service_name="Class_Airspace",
            feature_type="CLASS",
        )
    )
    assert counts.rows_read == 2
    assert counts.rows_accepted == 1
    assert counts.rejects_by_reason == {"MISSING_NATURAL_KEY": 1}


def test_preview_sources_aggregates_per_source_and_fails_on_empty_source(tmp_path):
    path = write_iem_csv(
        tmp_path / "iem_KBTP.csv", [iem_row("2026-11-01 10:53")]
    )
    per_file, totals = preview_sources(
        [FetchedFile("weather", "IEM", path, "url", station_icao="KBTP")]
    )
    assert "weather:iem_KBTP.csv" in per_file
    assert totals["weather"].rows_accepted == 1
    check_preview_totals(totals)

    empty = {"weather": PreviewCounts(rows_read=2, rows_rejected=2)}
    with pytest.raises(RuntimeError, match="missing coverage"):
        check_preview_totals(empty)


def test_refresh_dimensions_runs_four_idempotent_statements():
    class Cursor:
        def __init__(self, owner):
            self.owner = owner
            self.rowcount = -1

        def execute(self, sql):
            self.owner.sql.append(" ".join(sql.split()))
            self.rowcount = self.owner.counts.pop(0)

    class Conn:
        def __init__(self, counts):
            self.counts = list(counts)
            self.sql = []

        def cursor(self):
            return Cursor(self)

    conn = Conn([3, 2, 1, -1])
    result = refresh_dimensions(conn)

    assert result == {
        "dim_time": 3,
        "dim_vehicle": 2,
        "dim_weather": 1,
        "dim_airspace_zone": 0,
    }
    assert all("ON CONFLICT" in sql for sql in conn.sql)


def test_dimension_sql_maps_documented_stations_and_anchors():
    weather = weather_sql()
    assert "WHEN 'KBTP' THEN 'KBTP'" in weather
    assert "WHEN 'KAVP' THEN 'NIGHTJAR_PA'" in weather
    # PostgreSQL has no round(double precision, integer); the metres conversion
    # must be cast to numeric before rounding or the apply transaction fails.
    assert "ROUND((w.visibility_sm * 1609.344)::numeric, 2)" in weather

    airspace = airspace_sql()
    for site in ("KBTP", "NIGHTJAR_PA", "DJI_CO"):
        assert f"THEN '{site}'" in airspace
    assert "COALESCE(ds.site_key, -1)" in airspace


def test_render_summary_validate_marks_missing_coverage_and_all_limitations():
    report = {
        "mode": "validate",
        "run_mode": "weekly",
        "status": "VALIDATED",
        "window": (date(2026, 11, 7), date(2026, 11, 13)),
        "sources": ("weather",),
        "stations": ("KBTP",),
        "code_version": "wp11-v1",
        "generated_at": "2026-11-13T12:00:00+00:00",
        "fetched": [
            {"source": "weather", "system": "IEM", "file": "iem.csv",
             "bytes": 10, "url": "https://example/iem"},
        ],
        "preview": {
            "weather:iem.csv": {
                "rows_read": 2, "rows_accepted": 0, "rows_rejected": 2,
                "rejects_by_reason": {"INVALID_TIMESTAMP": 2},
            }
        },
        "preview_totals": {},
        "run_id": None,
        "failure_run_id": None,
        "note": None,
    }
    text = render_summary(report)

    assert "**VALIDATED**" in text
    assert "missing coverage, not evidence" in text
    assert "**TOTAL**" in text
    for lim_id, _description, _check in LIMITATIONS:
        assert lim_id in text
    assert "no DQ check" in text


def test_render_summary_apply_shows_dq_and_limitation_check_status():
    report = {
        "mode": "apply",
        "run_mode": "weekly",
        "status": "SUCCESS",
        "window": (date(2026, 11, 7), date(2026, 11, 13)),
        "sources": ("weather", "uas", "airspace"),
        "stations": ("KBTP", "KAGC"),
        "code_version": "wp11-v1",
        "generated_at": "2026-11-13T12:00:00+00:00",
        "fetched": [],
        "loads": {
            "weather:awc.json": {
                "rows_read": 4, "rows_accepted": 3, "rows_rejected": 1,
                "rows_duplicate": 0, "rejects_by_reason": {"INVALID_NUMERIC": 1},
            }
        },
        "load_totals": {},
        "manifests": 1,
        "dimensions": {"dim_time": 2, "dim_weather": 3},
        "dq": [
            {"check_id": "DQ-G-002", "severity": "WARNING",
             "status": "PASS", "observed_value": 0},
        ],
        "dq_summary": {"PASS": 1, "WARN": 0, "FAIL": 0, "SKIP": 0},
        "run_id": 12,
        "failure_run_id": None,
        "note": None,
    }
    text = render_summary(report)

    assert "ETL run id: 12" in text
    assert "Source manifests recorded: 1" in text
    assert "DQ-G-002" in text
    assert "PASS=1 WARN=0 FAIL=0 SKIP=0" in text
    assert "| L-008 |" in text or "L-008" in text


def test_main_writes_a_failure_summary_when_the_run_raises(tmp_path, monkeypatch):
    def boom(args):
        raise RuntimeError("round(double precision, integer) does not exist")

    monkeypatch.setattr("etl.run.run", boom)
    summary = tmp_path / "wp11-summary.md"

    code = main(
        ["--sources", "weather", "--stations", "KBTP", "--summary-path", str(summary)]
    )

    assert code == 1
    text = summary.read_text(encoding="utf-8")
    assert "WP-11 ingestion failed" in text
    assert "Mode: validate" in text
    assert "RuntimeError" in text
    assert "round(double precision, integer) does not exist" in text


def test_apply_files_records_manifest_and_loads_iem_rows(tmp_path, monkeypatch):
    # One row per statement so the fake cursor can track natural keys.
    monkeypatch.setattr("etl.run.BATCH_SIZE", 1)
    path = write_iem_csv(
        tmp_path / "iem_KBTP.csv",
        [iem_row("2026-11-01 10:53"), iem_row("2026-11-01 11:53")],
    )
    cursor = FakeCursor(fetchone_values=[(101,)], key_index=3)
    conn = FakeConn(cursor)

    loads, totals, manifests = apply_files(
        conn,
        [FetchedFile("weather", "IEM", path, "https://example/iem",
                     station_icao="KBTP")],
        etl_run_id=1,
        fetched_at=datetime.now(timezone.utc),
    )

    assert manifests == 1
    assert totals.rows_read == 2
    assert totals.rows_accepted == 2
    assert totals.reconcile_ok()
    assert loads["weather:iem_KBTP.csv"]["rows_accepted"] == 2
    assert any(
        "INSERT INTO project_staging.source_manifest" in sql
        for sql, _ in cursor.executed
    )
    assert any(
        "INSERT INTO project_staging.stg_weather_metar" in sql
        for sql, _ in cursor.executed
    )


def test_persist_results_writes_every_captured_row():
    class Conn:
        def __init__(self):
            self.rows = []

        def execute(self, sql, params):
            self.rows.append(params)

    conn = Conn()
    _persist_results(
        conn,
        7,
        [
            {"check_id": "DQ-X", "name": "n", "severity": "CRITICAL",
             "table_name": "t", "status": "FAIL", "observed_value": 2,
             "expected_value": "0", "details": "d"},
            {"check_id": "DQ-Y", "name": "n2", "severity": "WARNING",
             "table_name": "t", "status": "WARN", "observed_value": 1,
             "expected_value": "0", "details": "d2"},
        ],
    )
    assert [row[0] for row in conn.rows] == [7, 7]
    assert [row[1] for row in conn.rows] == ["DQ-X", "DQ-Y"]


def _validate_args(tmp_path: Path, sources: str) -> argparse.Namespace:
    return argparse.Namespace(
        apply=False,
        confirm="",
        sources=sources,
        stations="KBTP",
        start="2026-11-01",
        end="2026-11-02",
        run_mode="weekly",
        work_dir=str(tmp_path / "work"),
        summary_path=str(tmp_path / "summary.md"),
    )


def test_run_validate_end_to_end_without_database(tmp_path):
    def fake_fetch(sources, start, end, dest, *, stations):
        dest.mkdir(parents=True, exist_ok=True)
        iem = write_iem_csv(
            dest / "iem_KBTP_2026-11-01_2026-11-02.csv",
            [iem_row("2026-11-01 10:53"), iem_row("2026-11-01 11:53")],
        )
        faa = dest / "faa_Class_Airspace.geojson"
        faa.write_text(
            json.dumps({"type": "FeatureCollection", "features": [faa_feature("G1")]}),
            encoding="utf-8",
        )
        return [
            FetchedFile("weather", "IEM", iem, "https://example/iem",
                        station_icao="KBTP"),
            FetchedFile("airspace", "FAA-Airspace", faa, "https://example/faa",
                        service_name="Class_Airspace", feature_type="CLASS"),
        ]

    args = _validate_args(tmp_path, "weather,airspace")
    exit_code = run(args, environ={}, fetch=fake_fetch)

    assert exit_code == 0
    text = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "**VALIDATED**" in text
    assert "weather:iem_KBTP_2026-11-01_2026-11-02.csv" in text
    assert "airspace:faa_Class_Airspace.geojson" in text


def test_every_fetched_system_has_a_recorded_license():
    systems = {"IEM", "AWC", "Nightjar", "Nominal-DJI", "FAA-Airspace"}
    assert systems <= set(SOURCE_LICENSES)


def test_check_licenses_rejects_an_unrecorded_system(tmp_path):
    f = FetchedFile("weather", "AWC", tmp_path / "a.json", "https://example/a")
    check_licenses([f])
    unknown = FetchedFile("weather", "Unknown", tmp_path / "b.json", "https://x/b")
    with pytest.raises(ValueError, match="No licence recorded"):
        check_licenses([f, unknown])


def test_run_validate_fails_when_a_source_has_no_accepted_rows(tmp_path):
    def fake_fetch(sources, start, end, dest, *, stations):
        dest.mkdir(parents=True, exist_ok=True)
        iem = write_iem_csv(dest / "iem_KBTP.csv", [iem_row("bad-time")])
        return [FetchedFile("weather", "IEM", iem, "https://example/iem",
                            station_icao="KBTP")]

    args = _validate_args(tmp_path, "weather")
    with pytest.raises(RuntimeError, match="missing coverage"):
        run(args, environ={}, fetch=fake_fetch)


def test_run_apply_refuses_an_empty_source_before_connecting(tmp_path):
    def fake_fetch(sources, start, end, dest, *, stations):
        dest.mkdir(parents=True, exist_ok=True)
        iem = write_iem_csv(dest / "iem_KBTP.csv", [iem_row("bad-time")])
        return [FetchedFile("weather", "IEM", iem, "https://example/iem",
                            station_icao="KBTP")]

    def connect(*_args, **_kwargs):
        raise AssertionError("apply must not open a connection for an empty source")

    args = _validate_args(tmp_path, "weather")
    args.apply = True
    args.confirm = APPLY_CONFIRMATION
    environ = {"GITHUB_ACTIONS": "true", "WAREHOUSE_CI_APPROVED": "true"}
    with pytest.raises(RuntimeError, match="missing coverage"):
        run(args, environ=environ, fetch=fake_fetch, connect=connect)
