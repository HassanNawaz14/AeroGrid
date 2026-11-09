from __future__ import annotations

"""Idempotent staging writer and reconciliation helpers (WP-04).

Connection strings come from environment variables injected by CI or by an
approved local operator. Never put credentials in code, logs, or chat.
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

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


def _serialize_reject_payload(raw_payload: Any) -> str | None:
    if raw_payload is None:
        return None
    try:
        payload = json.dumps(raw_payload, default=str, ensure_ascii=False)
    except Exception:
        payload = str(raw_payload)
    # PostgreSQL TEXT columns reject literal NUL bytes.
    payload = payload.replace("\x00", "")
    if len(payload) > 4000:
        payload = payload[:4000] + "...(truncated)"
    return payload


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
    payload = _serialize_reject_payload(raw_payload)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO project_staging.stg_reject
            (etl_run_id, source_system, source_record_id, reason_code, reason_detail, raw_payload)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (etl_run_id, source_system, source_record_id, reason_code, reason_detail, payload),
    )


def _record_rejects_batch(
    conn: Any,
    rejects: Sequence[tuple[Any, str, str | None, str, str | None, Any]],
) -> None:
    if not rejects:
        return
    if len(rejects) == 1:
        etl_run_id, source_system, sid, code, detail, raw_payload = rejects[0]
        _record_reject(
            conn,
            etl_run_id=etl_run_id,
            source_system=source_system,
            source_record_id=sid,
            reason_code=code,
            reason_detail=detail,
            raw_payload=raw_payload,
        )
        return
    cur = conn.cursor()
    placeholders = ", ".join(["(%s, %s, %s, %s, %s, %s)"] * len(rejects))
    flat_params: list[Any] = []
    for etl_run_id, source_system, sid, code, detail, raw_payload in rejects:
        flat_params.extend(
            (
                etl_run_id,
                source_system,
                sid,
                code,
                detail,
                _serialize_reject_payload(raw_payload),
            )
        )
    cur.execute(
        f"""
        INSERT INTO project_staging.stg_reject
            (etl_run_id, source_system, source_record_id, reason_code, reason_detail, raw_payload)
        VALUES {placeholders}
        """,
        flat_params,
    )


def _fallback_source_id(
    raw: Any, source_file: str | None
) -> str | None:
    if not source_file or not isinstance(raw, Mapping):
        return None
    row_number = raw.get("_source_row_number")
    if row_number is None:
        return None
    return f"{source_file}#{row_number}"


def insert_on_conflict_do_nothing(
    conn: Any,
    *,
    table: str,
    columns: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
    conflict_target: str,
    etl_run_id: Any,
    source_system: str,
    normalizer: Callable[..., Mapping[str, Any]] | None = None,
    normalizer_kwargs: Mapping[str, Any] | None = None,
    row_mapper: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    source_file: str | None = None,
    batch_size: int = 1,
) -> LoadCounts:
    """Normalize, map, and insert rows idempotently.

    Rejected rows are written to ``stg_reject``. Database errors are rolled back
    to a per-row savepoint so one bad row cannot abort the rest of the batch.
    When ``batch_size > 1``, valid rows are sent in chunked multi-row inserts
    with automatic fallback to per-row savepoints on a batch database error.
    Reconciliation: read = accepted + rejected + duplicate.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    counts = LoadCounts()
    cur = conn.cursor()
    cols_sql = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = (
        f"INSERT INTO {table} ({cols_sql}) VALUES ({placeholders}) "
        f"ON CONFLICT {conflict_target} DO NOTHING"
    )
    kwargs = dict(normalizer_kwargs or {})

    def record_reject_count(
        *,
        raw: Mapping[str, Any],
        reason_code: str,
        detail: str,
        source_record_id: str | None,
        pending_rejects: list[tuple[Any, str, str | None, str, str | None, Any]] | None = None,
    ) -> None:
        counts.rows_rejected += 1
        counts.rejects_by_reason[reason_code] = (
            counts.rejects_by_reason.get(reason_code, 0) + 1
        )
        sid = source_record_id or _fallback_source_id(raw, source_file)
        if pending_rejects is not None:
            pending_rejects.append(
                (etl_run_id, source_system, sid, reason_code, detail, raw)
            )
            return
        _record_reject(
            conn,
            etl_run_id=etl_run_id,
            source_system=source_system,
            source_record_id=sid,
            reason_code=reason_code,
            reason_detail=detail,
            raw_payload=raw,
        )

    def insert_single(
        *,
        source_record_id: str | None,
        raw: Mapping[str, Any],
        values: list[Any],
    ) -> None:
        cur.execute("SAVEPOINT staging_row")
        try:
            cur.execute(sql, values)
            if getattr(cur, "rowcount", 1) == 0:
                counts.rows_duplicate += 1
            else:
                counts.rows_accepted += 1
        except Exception as exc:
            cur.execute("ROLLBACK TO SAVEPOINT staging_row")
            record_reject_count(
                raw=raw,
                reason_code="SCHEMA_DRIFT",
                detail=str(exc)[:500],
                source_record_id=source_record_id,
            )
        finally:
            cur.execute("RELEASE SAVEPOINT staging_row")

    if batch_size == 1:
        for raw in rows:
            counts.rows_read += 1
            source_record_id = None
            try:
                record = normalizer(raw, **kwargs) if normalizer else dict(raw)
                source_record_id = str(record.get("source_record_id") or "") or None
                if row_mapper is not None:
                    record = row_mapper(record)
            except RowRejected as exc:
                record_reject_count(
                    raw=raw,
                    reason_code=exc.reason_code,
                    detail=exc.detail,
                    source_record_id=exc.source_record_id or source_record_id,
                )
                continue
            except Exception as exc:
                record_reject_count(
                    raw=raw,
                    reason_code="SCHEMA_DRIFT",
                    detail=str(exc)[:500],
                    source_record_id=source_record_id,
                )
                continue

            values = [record.get(col) for col in columns]
            insert_single(source_record_id=source_record_id, raw=raw, values=values)

        return counts

    row_placeholder = f"({placeholders})"
    pending: list[tuple[str | None, Mapping[str, Any], list[Any]]] = []
    pending_rejects: list[tuple[Any, str, str | None, str, str | None, Any]] = []

    def flush_pending() -> None:
        if not pending:
            return
        batch_sql = (
            f"INSERT INTO {table} ({cols_sql}) VALUES "
            f"{', '.join([row_placeholder] * len(pending))} "
            f"ON CONFLICT {conflict_target} DO NOTHING"
        )
        flat_values = [val for _, _, vals in pending for val in vals]
        cur.execute("SAVEPOINT staging_batch")
        try:
            cur.execute(batch_sql, flat_values)
            inserted = int(getattr(cur, "rowcount", len(pending)))
            if inserted < 0:
                raise RuntimeError(f"Unexpected cursor rowcount={inserted} for batch insert")
            cur.execute("RELEASE SAVEPOINT staging_batch")
        except Exception:
            cur.execute("ROLLBACK TO SAVEPOINT staging_batch")
            cur.execute("RELEASE SAVEPOINT staging_batch")
            for sid, item_raw, vals in pending:
                insert_single(source_record_id=sid, raw=item_raw, values=vals)
        else:
            counts.rows_accepted += inserted
            counts.rows_duplicate += len(pending) - inserted
        finally:
            pending.clear()

    def flush_rejects() -> None:
        if not pending_rejects:
            return
        _record_rejects_batch(conn, pending_rejects)
        pending_rejects.clear()

    for raw in rows:
        counts.rows_read += 1
        source_record_id = None
        try:
            record = normalizer(raw, **kwargs) if normalizer else dict(raw)
            source_record_id = str(record.get("source_record_id") or "") or None
            if row_mapper is not None:
                record = row_mapper(record)
        except RowRejected as exc:
            record_reject_count(
                raw=raw,
                reason_code=exc.reason_code,
                detail=exc.detail,
                source_record_id=exc.source_record_id or source_record_id,
                pending_rejects=pending_rejects,
            )
            if len(pending_rejects) >= batch_size:
                flush_rejects()
            continue
        except Exception as exc:
            record_reject_count(
                raw=raw,
                reason_code="SCHEMA_DRIFT",
                detail=str(exc)[:500],
                source_record_id=source_record_id,
                pending_rejects=pending_rejects,
            )
            if len(pending_rejects) >= batch_size:
                flush_rejects()
            continue

        values = [record.get(col) for col in columns]
        pending.append((source_record_id, raw, values))
        if len(pending) >= batch_size:
            flush_pending()

    flush_pending()
    flush_rejects()
    return counts


def start_etl_run(
    conn: Any, *, run_mode: str, code_version: str | None = None
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO project_staging.etl_run_log (run_mode, code_version)
        VALUES (%s, %s)
        RETURNING etl_run_id
        """,
        (run_mode, code_version),
    )
    return int(cur.fetchone()[0])


def finish_etl_run(
    conn: Any,
    *,
    etl_run_id: int,
    counts: Any,
    status: str,
    facts_inserted: int = 0,
    critical_dq_failures: int = 0,
    failure_reason: str | None = None,
) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE project_staging.etl_run_log
        SET finished_at = NOW(),
            status = %s,
            rows_read = %s,
            rows_accepted = %s,
            rows_rejected = %s,
            rows_duplicate = %s,
            facts_inserted = %s,
            critical_dq_failures = %s,
            failure_reason = %s
        WHERE etl_run_id = %s
        """,
        (
            status,
            counts.rows_read,
            counts.rows_accepted,
            counts.rows_rejected,
            counts.rows_duplicate,
            facts_inserted,
            critical_dq_failures,
            failure_reason,
            etl_run_id,
        ),
    )


def record_source_manifest(
    conn: Any,
    *,
    source_name: str,
    source_url: str,
    license_name: str,
    attribution: str,
    fetched_at: Any,
    file_path: str | Path,
    object_key: str | None = None,
    content_type: str | None = None,
    source_version: str | None = None,
) -> int:
    path = Path(file_path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO project_staging.source_manifest
            (source_name, source_url, license_name, attribution, fetched_at,
             file_name, byte_size, sha256, object_key, content_type, source_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_name, sha256) DO UPDATE
        SET source_url = EXCLUDED.source_url,
            license_name = EXCLUDED.license_name,
            attribution = EXCLUDED.attribution,
            fetched_at = EXCLUDED.fetched_at,
            object_key = EXCLUDED.object_key,
            content_type = EXCLUDED.content_type,
            source_version = EXCLUDED.source_version
        RETURNING source_manifest_id
        """,
        (
            source_name,
            source_url,
            license_name,
            attribution,
            fetched_at,
            path.name,
            path.stat().st_size,
            digest.hexdigest(),
            object_key,
            content_type,
            source_version,
        ),
    )
    return int(cur.fetchone()[0])
