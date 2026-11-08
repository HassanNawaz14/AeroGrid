import hashlib
from datetime import datetime, timezone

from etl.errors import RowRejected
from etl.staging_writer import (
    finish_etl_run,
    insert_on_conflict_do_nothing,
    record_source_manifest,
    start_etl_run,
)
from tests.fakes import FakeConn, FakeCursor


def good(row, **_):
    return {
        "source_record_id": row["id"],
        "value": row.get("value"),
        "etl_run_id": row.get("etl_run_id"),
    }


def test_load_counts_reconcile_and_idempotent_duplicate():
    cursor = FakeCursor(existing_keys=set(), key_index=0)
    conn = FakeConn(cursor)
    rows = [{"id": "a", "value": 1}, {"id": "a", "value": 1}, {"id": "b", "value": 2}]
    counts = insert_on_conflict_do_nothing(
        conn,
        table="project_staging.stg_adsb_position",
        columns=["source_record_id", "value", "etl_run_id"],
        rows=rows,
        conflict_target="(source_record_id)",
        etl_run_id="run-1",
        source_system="TARTAN",
        normalizer=good,
        normalizer_kwargs={"etl_run_id": "run-1"},
    )
    assert counts.rows_read == 3
    assert counts.rows_accepted == 2
    assert counts.rows_duplicate == 1
    assert counts.rows_rejected == 0
    assert counts.reconcile_ok()


def bad(row, **_):
    if row.get("id") == "bad":
        raise RowRejected("INVALID_TIMESTAMP", "bad time", row.get("id"))
    return {"source_record_id": row["id"], "value": 1, "etl_run_id": "run-1"}


def test_rejected_rows_are_counted_and_recorded():
    cursor = FakeCursor(existing_keys=set(), key_index=0)
    conn = FakeConn(cursor)
    rows = [{"id": "ok"}, {"id": "bad"}, {"id": "ok2"}]
    counts = insert_on_conflict_do_nothing(
        conn,
        table="project_staging.stg_adsb_position",
        columns=["source_record_id", "value", "etl_run_id"],
        rows=rows,
        conflict_target="(source_record_id)",
        etl_run_id="run-1",
        source_system="TARTAN",
        normalizer=bad,
    )
    assert counts.rows_read == 3
    assert counts.rows_accepted == 2
    assert counts.rows_rejected == 1
    assert counts.rows_duplicate == 0
    assert counts.rejects_by_reason["INVALID_TIMESTAMP"] == 1
    assert counts.reconcile_ok()
    assert len(cursor.rejects) == 1
    assert cursor.rejects[0][2] == "bad"  # source_record_id
    assert cursor.rejects[0][3] == "INVALID_TIMESTAMP"


def test_db_error_rolls_back_savepoint_and_continues_batch():
    cursor = FakeCursor(existing_keys=set(), key_index=0, fail_key="bad")
    conn = FakeConn(cursor)
    rows = [{"id": "ok"}, {"id": "bad"}, {"id": "ok2"}]
    counts = insert_on_conflict_do_nothing(
        conn,
        table="project_staging.stg_adsb_position",
        columns=["source_record_id", "value", "etl_run_id"],
        rows=rows,
        conflict_target="(source_record_id)",
        etl_run_id="run-1",
        source_system="TARTAN",
        normalizer=good,
    )

    assert counts.rows_read == 3
    assert counts.rows_accepted == 2
    assert counts.rows_rejected == 1
    assert counts.rows_duplicate == 0
    assert counts.rejects_by_reason["SCHEMA_DRIFT"] == 1
    assert counts.reconcile_ok()
    assert cursor.rollbacks == ["staging_row"]
    assert len(cursor.rejects) == 1
    assert cursor.rejects[0][2] == "bad"


def test_reject_without_source_id_uses_file_and_row_fallback():
    cursor = FakeCursor(existing_keys=set(), key_index=0)
    conn = FakeConn(cursor)

    def reject_without_id(row, **_):
        raise RowRejected("INVALID_NUMERIC", "bad number")

    counts = insert_on_conflict_do_nothing(
        conn,
        table="project_staging.stg_adsb_position",
        columns=["source_record_id"],
        rows=[{"_source_row_number": 5}],
        conflict_target="(source_record_id)",
        etl_run_id=1,
        source_system="TARTAN",
        normalizer=reject_without_id,
        source_file="01-01-22/1.csv",
    )

    assert counts.rows_rejected == 1
    assert cursor.rejects[0][2] == "01-01-22/1.csv#5"


def test_row_mapper_maps_normalized_record_to_staging_columns():
    cursor = FakeCursor(existing_keys=set(), key_index=0)
    conn = FakeConn(cursor)

    def normalize(row, **_):
        return {"source_record_id": row["id"], "icao24_hex": "00007B"}

    def mapper(record):
        return {"source_record_id": record["source_record_id"], "icao24": record["icao24_hex"]}

    counts = insert_on_conflict_do_nothing(
        conn,
        table="project_staging.stg_adsb_position",
        columns=["source_record_id", "icao24"],
        rows=[{"id": "a"}],
        conflict_target="(source_record_id)",
        etl_run_id=1,
        source_system="TARTAN",
        normalizer=normalize,
        row_mapper=mapper,
    )

    assert counts.rows_accepted == 1
    insert_sql, params = next(
        (sql, params)
        for sql, params in cursor.executed
        if "INSERT INTO project_staging.stg_adsb_position" in sql
    )
    assert params == ("a", "00007B")


def test_start_and_finish_run_log():
    cursor = FakeCursor(fetchone_values=[(42,)])
    conn = FakeConn(cursor)

    run_id = start_etl_run(conn, run_mode="validate", code_version="abc123")
    assert run_id == 42

    counts = type(
        "Counts",
        (),
        {
            "rows_read": 3,
            "rows_accepted": 2,
            "rows_rejected": 1,
            "rows_duplicate": 0,
        },
    )()
    finish_etl_run(conn, etl_run_id=42, counts=counts, status="PARTIAL")
    update_sql, params = cursor.executed[-1]
    assert "UPDATE project_staging.etl_run_log" in update_sql
    assert params[0] == "PARTIAL"
    assert params[1] == 3
    assert params[2] == 2
    assert params[3] == 1
    assert params[4] == 0
    assert params[8] == 42


def test_record_source_manifest_hashes_file(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_bytes(b"real-sample-bytes")
    cursor = FakeCursor(fetchone_values=[(7,)])
    conn = FakeConn(cursor)

    manifest_id = record_source_manifest(
        conn,
        source_name="TARTAN",
        source_url="https://example.invalid/kbtp/raw/2022.zip",
        license_name="CC BY 4.0",
        attribution="TartanAviation",
        fetched_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        file_path=path,
        object_key="raw/tartan/kbtp/2022.zip",
    )

    assert manifest_id == 7
    insert_sql, params = cursor.executed[-1]
    assert "INSERT INTO project_staging.source_manifest" in insert_sql
    assert params[0] == "TARTAN"
    assert params[5] == "sample.csv"
    assert params[6] == len(b"real-sample-bytes")
    assert params[7] == hashlib.sha256(b"real-sample-bytes").hexdigest()
    assert params[8] == "raw/tartan/kbtp/2022.zip"
