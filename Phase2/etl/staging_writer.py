from __future__ import annotations

"""Idempotent staging writer and reconciliation helpers (WP-04).

Uses psycopg v3 when available (PostgreSQL). SQLite is supported only for local
unit tests of SQL shape where compatible; production loads run through CI with a
PostgreSQL connection.

Do not pass credentials in code or chat. Connection strings come from environment
variables injected by CI or by an approved local operator.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from etl.errors import RowRejected


@dataclass
class LoadCounts:
    rows_read: int = 0
    rows_accepted: int = 0
    rows_rejected: int = 0
    rows_duplicate: int = 0
    rejects_by_reason: dict[str, int] = field(default_factory=dict)

    def reconcile_ok(self) -> bool:
        return self.rows_read == self.rows_accepted + self.rows_rejected + self.rows_duplicate

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows_read": self.rows_read,
            "rows_accepted": self.rows_accepted,
            "rows_rejected": self.rows_rejected,
            "rows_duplicate": self.rows_duplicate,
            "reconciled": self.reconcile_ok(),
            "rejects_by_reason": dict(sorted(self.rejects_by_reason.items())),
        }


def _record_reject(
    conn: Any,
    *,
    etl_run_id: Any,
    source_system: str,
    source_record_id: str | None,
    reason_code: str,
    reason_detail: str | None,
    raw_payload: Any = None,
) -> None:
    payload = None
    if raw_payload is not None:
        try:
            payload = json.dumps(raw_payload, default=str, ensure_ascii=False)
            if len(payload) > 4000:
                payload = payload[:4000] + "...(truncated)"
        except Exception:
            payload = str(raw_payload)[:4000]
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO project_staging.stg_reject
            (etl_run_id, source_system, source_record_id, reason_code, reason_detail, raw_payload)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (etl_run_id, source_system, source_record_id, reason_code, reason_detail, payload),
    )


def insert_on_conflict_do_nothing(
    conn: Any,
    *,
    table: str,
    columns: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
    conflict_target: str,
    etl_run_id: Any,
    source_system: str,
    normalizer: Any = None,
    normalizer_kwargs: Mapping[str, Any] | None = None,
) -> LoadCounts:
    """Normalize and insert rows idempotently.

    `normalizer` may raise `RowRejected`; rejected rows are recorded in `stg_reject`
    and counted. Duplicate natural keys count as `rows_duplicate` (ON CONFLICT DO
    NOTHING). Reconciliation: read = accepted + rejected + duplicate.
    """
    counts = LoadCounts()
    cur = conn.cursor()
    cols_sql = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = (
        f"INSERT INTO {table} ({cols_sql}) VALUES ({placeholders}) "
        f"ON CONFLICT {conflict_target} DO NOTHING"
    )
    kwargs = dict(normalizer_kwargs or {})
    for raw in rows:
        counts.rows_read += 1
        source_record_id = None
        try:
            record = normalizer(raw, **kwargs) if normalizer else dict(raw)
            source_record_id = str(record.get("source_record_id") or "") or None
            values = [record.get(col) for col in columns]
            cur.execute(sql, values)
            # psycopg cursor.rowcount is 1 for insert, 0 for conflict-do-nothing
            if getattr(cur, "rowcount", 1) == 0:
                counts.rows_duplicate += 1
            else:
                counts.rows_accepted += 1
        except RowRejected as exc:
            counts.rows_rejected += 1
            reason = exc.reason_code
            counts.rejects_by_reason[reason] = counts.rejects_by_reason.get(reason, 0) + 1
            _record_reject(
                conn,
                etl_run_id=etl_run_id,
                source_system=source_system,
                source_record_id=exc.source_record_id or source_record_id,
                reason_code=reason,
                reason_detail=exc.detail,
                raw_payload=raw,
            )
        except Exception as exc:  # fail-closed row, continue batch
            counts.rows_rejected += 1
            reason = "SCHEMA_DRIFT"
            counts.rejects_by_reason[reason] = counts.rejects_by_reason.get(reason, 0) + 1
            _record_reject(
                conn,
                etl_run_id=etl_run_id,
                source_system=source_system,
                source_record_id=source_record_id,
                reason_code=reason,
                reason_detail=str(exc)[:500],
                raw_payload=raw,
            )
    return counts
