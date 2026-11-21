"""Read-only verifier for WP-P3-H1: manifest rows must resolve to archived bytes.

For every ``project_staging.source_manifest`` row, confirm the linked
``object_key`` exists in the private ``aerogrid-raw`` bucket and that the
downloaded bytes still hash to the recorded ``sha256``. No writes.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from etl.raw_archive import ArchiveConfig, RawArchive


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Only verify the first N manifests")
    parser.add_argument("--evidence", help="Write a markdown evidence file here")
    return parser.parse_args(argv)


def fetch_manifest_rows(conn: Any, limit: int | None = None) -> list[dict[str, Any]]:
    sql = (
        "SELECT source_manifest_id, source_name, file_name, byte_size, sha256,"
        " object_key FROM project_staging.source_manifest"
        " ORDER BY source_manifest_id"
    )
    params: tuple[Any, ...] = ()
    if limit is not None:
        sql += " LIMIT %s"
        params = (limit,)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        names = [column.name for column in cur.description]
        return [dict(zip(names, row)) for row in cur.fetchall()]


def verify_rows(rows, archive) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    for row in rows:
        key = row.get("object_key")
        if not key:
            failures.append(f"manifest {row['source_manifest_id']}: object_key is NULL")
            results.append({**row, "actual_sha256": None, "status": "FAIL"})
            continue
        try:
            actual = archive.fetch_sha256(key)
        except Exception as exc:  # noqa: BLE001 - any storage error is a failure
            failures.append(f"manifest {row['source_manifest_id']} {key}: {exc}")
            results.append({**row, "actual_sha256": None, "status": "FAIL"})
            continue
        expected = str(row["sha256"]).strip().lower()
        status = "PASS" if actual == expected else "FAIL"
        if status == "FAIL":
            failures.append(
                f"manifest {row['source_manifest_id']} {key}: sha256 mismatch"
            )
        results.append({**row, "actual_sha256": actual, "status": status})
    return results, failures


def render(results, failures, captured_at: str) -> str:
    lines = [
        "# WP-P3-H1 raw archive verification",
        "",
        f"- Captured (UTC): {captured_at}",
        f"- Manifests checked: {len(results)}",
        f"- Result: {'PASS' if not failures else 'FAIL'}",
        "",
        "| Manifest | Source | File | Bytes | SHA-256 (recorded) | Object key | Status |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for row in results:
        lines.append(
            f"| {row['source_manifest_id']} | {row['source_name']} | {row['file_name']}"
            f" | {row['byte_size']} | `{row['sha256']}`"
            f" | `{row.get('object_key') or ''}` | {row['status']} |"
        )
    if failures:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {item}" for item in failures)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("Install psycopg[binary]") from exc
    archive = RawArchive(ArchiveConfig.from_env())
    with psycopg.connect(database_url, connect_timeout=15) as conn:
        rows = fetch_manifest_rows(conn, args.limit)
    results, failures = verify_rows(rows, archive)
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    text = render(results, failures, captured_at)
    sys.stdout.write(text)
    if args.evidence:
        path = Path(args.evidence)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
