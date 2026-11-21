"""Unit tests for WP-P3-H1 raw archive closure (L-010)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PHASE2_ROOT = Path(__file__).resolve().parents[2] / "Phase2"
if str(PHASE2_ROOT) not in sys.path:
    sys.path.insert(0, str(PHASE2_ROOT))

from etl.raw_archive import (
    ArchiveConfig,
    RawArchive,
    RawArchiveConfigError,
    content_addressed_key,
    safe_file_name,
    sha256_file,
)


class FakeNotFound(Exception):
    response = {"Error": {"Code": "404"}}


class FakeS3:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.uploads: list[tuple[str, str, dict]] = []
        self.fail_upload = False

    def head_object(self, Bucket: str, Key: str) -> dict:
        if Key not in self.objects:
            raise FakeNotFound(Key)
        return {"ContentLength": len(self.objects[Key])}

    def upload_file(self, path: str, bucket: str, key: str, ExtraArgs=None) -> None:
        if self.fail_upload:
            raise RuntimeError("storage unavailable")
        data = Path(path).read_bytes()
        self.objects[key] = data
        self.uploads.append((bucket, key, ExtraArgs or {}))

    def download_file(self, bucket: str, key: str, dest: str) -> None:
        Path(dest).write_bytes(self.objects[key])


def _archive(fake: FakeS3) -> RawArchive:
    config = ArchiveConfig(
        endpoint="https://example.invalid",
        region="us-east-1",
        bucket="aerogrid-raw",
        access_key_id="test-key",
        secret_access_key="test-secret",
    )
    return RawArchive(config, client=fake)


def test_content_addressed_key_is_stable_and_sanitises_names():
    digest = "a" * 64
    assert content_addressed_key(digest, "iem_KBTP 2026.csv") == (
        f"raw/{digest}/iem_KBTP_2026.csv"
    )
    assert content_addressed_key(digest.upper(), "a.csv") == f"raw/{digest}/a.csv"
    with pytest.raises(ValueError):
        content_addressed_key("not-a-digest", "a.csv")


def test_safe_file_name_strips_paths_and_empty_names():
    assert safe_file_name("../../etc/passwd") == "passwd"
    assert safe_file_name("") == "source.bin"
    assert safe_file_name("..") == "source.bin"


def test_archive_config_names_missing_variables_without_values():
    with pytest.raises(RawArchiveConfigError) as exc:
        ArchiveConfig.from_env({"NEON_S3_BUCKET": "aerogrid-raw"})
    message = str(exc.value)
    assert "NEON_S3_ENDPOINT" in message
    assert "NEON_S3_SECRET_ACCESS_KEY" in message
    assert "aerogrid-raw" not in message


def test_archive_config_adds_https_and_keeps_values():
    config = ArchiveConfig.from_env(
        {
            "NEON_S3_ENDPOINT": "example.invalid",
            "NEON_S3_REGION": "us-east-1",
            "NEON_S3_BUCKET": "aerogrid-raw",
            "NEON_S3_ACCESS_KEY_ID": "key",
            "NEON_S3_SECRET_ACCESS_KEY": "secret",
        }
    )
    assert config.endpoint == "https://example.invalid"
    assert config.bucket == "aerogrid-raw"


def test_put_file_uploads_once_then_skips_existing(tmp_path):
    source = tmp_path / "iem_KBTP.csv"
    source.write_text("station,valid\nKBTP,2026-11-01\n", encoding="utf-8")
    fake = FakeS3()
    archive = _archive(fake)

    first = archive.put_file(source, content_type="text/csv")
    second = archive.put_file(source, content_type="text/csv")

    digest = sha256_file(source)
    assert first.object_key == f"raw/{digest}/iem_KBTP.csv"
    assert first.uploaded is True
    assert second.uploaded is False
    assert len(fake.uploads) == 1
    assert fake.uploads[0][2]["Metadata"] == {"sha256": digest}


def test_put_file_propagates_upload_failure(tmp_path):
    source = tmp_path / "f.csv"
    source.write_text("x", encoding="utf-8")
    fake = FakeS3()
    fake.fail_upload = True
    with pytest.raises(RuntimeError, match="storage unavailable"):
        _archive(fake).put_file(source)


def test_fetch_sha256_round_trips(tmp_path):
    source = tmp_path / "f.csv"
    source.write_text("payload", encoding="utf-8")
    fake = FakeS3()
    archive = _archive(fake)
    archived = archive.put_file(source)
    assert archive.fetch_sha256(archived.object_key) == sha256_file(source)


from etl.verify_raw_archive import fetch_manifest_rows, render, verify_rows


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.description = [
            type("Column", (), {"name": name})
            for name in (
                "source_manifest_id",
                "source_name",
                "file_name",
                "byte_size",
                "sha256",
                "object_key",
            )
        ]
        self.executed = []

    def execute(self, sql, params=()):
        self.executed.append((sql, params))

    def fetchall(self):
        return self.rows

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeConn:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor


def test_fetch_manifest_rows_applies_limit():
    cursor = FakeCursor([(1, "IEM", "a.csv", 3, "a" * 64, "raw/a/a.csv")])
    rows = fetch_manifest_rows(FakeConn(cursor), limit=5)
    assert rows[0]["object_key"] == "raw/a/a.csv"
    assert cursor.executed[0][1] == (5,)


def test_verify_rows_reports_null_key_and_hash_mismatch(tmp_path):
    source = tmp_path / "a.csv"
    source.write_text("payload", encoding="utf-8")
    fake = FakeS3()
    archive = _archive(fake)
    good = archive.put_file(source)
    rows = [
        {
            "source_manifest_id": 1,
            "source_name": "IEM",
            "file_name": "a.csv",
            "byte_size": good.byte_size,
            "sha256": good.sha256,
            "object_key": good.object_key,
        },
        {
            "source_manifest_id": 2,
            "source_name": "IEM",
            "file_name": "b.csv",
            "byte_size": 1,
            "sha256": "b" * 64,
            "object_key": None,
        },
    ]
    results, failures = verify_rows(rows, archive)
    assert results[0]["status"] == "PASS"
    assert results[1]["status"] == "FAIL"
    assert any("object_key is NULL" in item for item in failures)
    text = render(results, failures, "2026-11-22T00:00:00+00:00")
    assert "Result: FAIL" in text
    assert "raw/" in text


import argparse
from datetime import datetime, timezone

from etl.fetch import FetchedFile
from etl.run import APPLY_CONFIRMATION, apply_files, run
from etl.staging_writer import LoadCounts


def _args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        apply=True,
        confirm=APPLY_CONFIRMATION,
        sources="weather",
        stations="KBTP",
        start="2026-11-01",
        end="2026-11-02",
        run_mode="weekly",
        work_dir=str(tmp_path / "work"),
        summary_path=str(tmp_path / "summary.md"),
    )


def test_apply_files_passes_archived_key_to_manifest(tmp_path, monkeypatch):
    source = tmp_path / "iem_KBTP.csv"
    source.write_text("x", encoding="utf-8")
    captured = {}

    def fake_manifest(conn, **kwargs):
        captured.update(kwargs)
        return 7

    monkeypatch.setattr("etl.run.record_source_manifest", fake_manifest)
    monkeypatch.setattr("etl.run.load_iem", lambda *a, **k: LoadCounts())
    fake = FakeS3()
    archive = _archive(fake)

    loads, totals, manifests, archived = apply_files(
        object(),
        [
            FetchedFile(
                "weather", "IEM", source, "https://example/iem", station_icao="KBTP"
            )
        ],
        etl_run_id=1,
        fetched_at=datetime.now(timezone.utc),
        archive=archive,
    )

    assert manifests == 1
    assert captured["object_key"] == archived[0]["object_key"]
    assert captured["object_key"].startswith("raw/")
    assert archived[0]["uploaded"] is True
    assert totals.rows_read == 0


def test_run_apply_fails_closed_when_archive_env_is_missing(tmp_path, monkeypatch):
    source = tmp_path / "f.csv"
    source.write_text("x", encoding="utf-8")
    monkeypatch.setattr("etl.run.preview_sources", lambda files: ({}, {}))
    monkeypatch.setattr("etl.run.check_preview_totals", lambda totals: None)

    def fake_fetch(sources, start, end, dest, *, stations):
        return [
            FetchedFile(
                "weather", "IEM", source, "https://example/iem", station_icao="KBTP"
            )
        ]

    def connect(*_args, **_kwargs):
        raise AssertionError("apply must fail before opening a connection")

    environ = {
        "GITHUB_ACTIONS": "true",
        "WAREHOUSE_CI_APPROVED": "true",
        "DATABASE_URL": "postgresql://example/db",
    }
    with pytest.raises(RawArchiveConfigError, match="NEON_S3_BUCKET"):
        run(_args(tmp_path), environ=environ, fetch=fake_fetch, connect=connect)


def test_run_validate_never_calls_the_archive(tmp_path, monkeypatch):
    source = tmp_path / "f.csv"
    source.write_text("x", encoding="utf-8")
    monkeypatch.setattr("etl.run.preview_sources", lambda files: ({}, {}))
    monkeypatch.setattr("etl.run.check_preview_totals", lambda totals: None)

    class ExplodingArchive:
        def put_file(self, *args, **kwargs):
            raise AssertionError("validate must not archive")

    def fake_fetch(sources, start, end, dest, *, stations):
        return [
            FetchedFile(
                "weather", "IEM", source, "https://example/iem", station_icao="KBTP"
            )
        ]

    args = _args(tmp_path)
    args.apply = False
    args.confirm = ""
    assert run(args, environ={}, fetch=fake_fetch, archive=ExplodingArchive()) == 0
