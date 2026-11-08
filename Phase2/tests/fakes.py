from __future__ import annotations

from typing import Any


class FakeCursor:
    def __init__(
        self,
        existing_keys: set[tuple] | None = None,
        key_index: int = 0,
        *,
        fail_key: Any = None,
        fetchone_values: list[Any] | None = None,
    ):
        self.existing = set(existing_keys or ())
        self.key_index = key_index
        self.fail_key = fail_key
        self.fetchone_values = list(fetchone_values or [])
        self.rowcount = 0
        self.executed: list[tuple[str, tuple]] = []
        self.rejects: list[tuple] = []
        self.savepoints: list[str] = []
        self.rollbacks: list[str] = []
        self.failed = False

    def execute(self, sql, params=()):
        self.executed.append((sql, tuple(params)))
        text = " ".join(sql.split())
        if text.startswith("SAVEPOINT "):
            self.savepoints.append(text.split()[-1])
            return
        if text.startswith("ROLLBACK TO SAVEPOINT "):
            self.rollbacks.append(text.split()[-1])
            self.failed = False
            return
        if text.startswith("RELEASE SAVEPOINT "):
            return
        if "INSERT INTO project_staging.stg_reject" in text:
            self.rejects.append(tuple(params))
            self.rowcount = 1
            return
        if self.failed:
            raise RuntimeError("current transaction is aborted")

        if "INSERT INTO" in text and self.fail_key is not None and self.fail_key in params:
            self.failed = True
            raise RuntimeError("forced insert failure")

        if "RETURNING" in text:
            self.rowcount = 1
            return

        if text.startswith("UPDATE "):
            self.rowcount = 1
            return

        key = (params[self.key_index],) if self.key_index is not None else tuple(params)
        if key in self.existing:
            self.rowcount = 0
        else:
            self.existing.add(key)
            self.rowcount = 1

    def fetchone(self):
        if not self.fetchone_values:
            raise AssertionError("no fetchone value configured")
        return self.fetchone_values.pop(0)


class FakeConn:
    def __init__(self, cursor: FakeCursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor
