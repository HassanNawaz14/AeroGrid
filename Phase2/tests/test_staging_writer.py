from etl.staging_writer import insert_on_conflict_do_nothing
from etl.errors import RowRejected


class FakeCursor:
    def __init__(self, existing_keys: set[tuple] | None = None, key_index: int = 0):
        self.existing = set(existing_keys or ())
        self.key_index = key_index
        self.rowcount = 0
        self.executed: list[tuple[str, tuple]] = []
        self.rejects: list[tuple] = []

    def execute(self, sql, params):
        self.executed.append((sql, tuple(params)))
        if "INSERT INTO project_staging.stg_reject" in sql:
            self.rejects.append(tuple(params))
            self.rowcount = 1
            return
        # For idempotent inserts, treat params[key_index] as natural key for simplicity
        key = (params[self.key_index],) if self.key_index is not None else params
        if key in self.existing:
            self.rowcount = 0
        else:
            self.existing.add(key)
            self.rowcount = 1


class FakeConn:
    def __init__(self, cursor: FakeCursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor


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
