#!/usr/bin/env python3
"""Measure Phase 3 candidate indexes with EXPLAIN ANALYZE (WP-P3-05).

Verify mode (default) connects with the CI writer credentials, measures each
dashboard-critical query, creates one candidate index inside a transaction, runs
ANALYZE on its table, measures the same query again, records the index size, and
then ROLLBACKs. Nothing is persisted. Apply mode is allowed only on ``main`` from
the protected ``warehouse`` environment with ``WAREHOUSE_CI_APPROVED=true``, and it
commits the idempotent DDL file after a capacity guard.

The script never prints or stores the connection string. Evidence is written as
JSON plus Markdown; the PDF report is built from the JSON by
``generate_index_report.py``. Measured numbers are recorded exactly as observed:
an index that does not help is reported as neutral or worse, never as a win.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE3_ROOT = REPO_ROOT / "Phase3"
DEFAULT_INDEX_SQL = PHASE3_ROOT / "sql" / "indexes" / "01_indexes.sql"
QUERY_ROOT = PHASE3_ROOT / "sql" / "optimization"
DEFAULT_EVIDENCE_DIR = PHASE3_ROOT / "evidence"

STORAGE_GUARD_BYTES = 700 * 1024 * 1024
INDEX_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
BLOCK_SPLIT = re.compile(r"(?m)^--\s*index_id:\s*(\S+)\s*$")
FIELD_PATTERN = re.compile(
    r"(?m)^--\s*(index_name|target_query|rationale):\s*(.+?)\s*$"
)
CREATE_PATTERN = re.compile(
    r"(CREATE\s+INDEX\s+IF\s+NOT\s+EXISTS\s+([a-z_][a-z0-9_]*)\s+"
    r"ON\s+([a-z_]+\.[a-z_][a-z0-9_]*)\s*\(.*?\))\s*;?",
    re.IGNORECASE | re.DOTALL,
)
QUERY_ID = re.compile(r"\b(OQ-P3-05-\d{2})\b")
FORBIDDEN = re.compile(
    r"\b(DROP|ALTER|TRUNCATE|GRANT|REVOKE|MERGE|CALL|DO|COPY)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class IndexDefinition:
    index_id: str
    index_name: str
    table: str
    target_query: str
    rationale: str
    statement: str
    ddl_sha256: str


def executable_statements(sql: str) -> list[str]:
    from run_readonly_analytics import executable_statements as split

    return split(sql)


def assert_index_sql(statement: str) -> tuple[str, str]:
    """Return (index_name, table) or raise for anything but one safe CREATE INDEX."""
    statements = executable_statements(statement)
    if len(statements) != 1:
        raise ValueError(f"expected exactly one index statement, found {len(statements)}")
    cleaned = statements[0].strip()
    if FORBIDDEN.search(cleaned):
        raise ValueError("destructive keyword in index DDL")
    match = CREATE_PATTERN.fullmatch(cleaned)
    if not match:
        raise ValueError(
            "index DDL must be exactly CREATE INDEX IF NOT EXISTS <name> ON <table> (...)"
        )
    index_name, table = match.group(2), match.group(3)
    if not INDEX_NAME_RE.match(index_name):
        raise ValueError(f"unsafe index name: {index_name!r}")
    if not table.startswith("project_dw."):
        raise ValueError(f"indexes may only be created on project_dw, got {table!r}")
    return index_name, table


def extract_rationale(body: str) -> str:
    """Join the comment continuation lines that follow the rationale marker."""
    match = re.search(r"(?m)^--\s*rationale:\s*(.*(?:\n--.*)*)", body)
    if not match:
        return ""
    parts: list[str] = []
    for line in match.group(1).splitlines():
        text = line.strip()
        if text.startswith("--"):
            text = text[2:].strip()
        if text:
            parts.append(text)
    return " ".join(parts).strip()


def parse_index_definitions(sql: str) -> list[IndexDefinition]:
    """Parse the committed DDL into measured candidates using the comment markers."""
    parts = BLOCK_SPLIT.split(sql)
    if len(parts) < 3:
        raise ValueError("no index blocks with '-- index_id:' markers found")
    definitions: list[IndexDefinition] = []
    seen: set[str] = set()
    for offset in range(1, len(parts), 2):
        index_id = parts[offset].strip()
        body = parts[offset + 1]
        fields = {key: value for key, value in FIELD_PATTERN.findall(body)}
        rationale = extract_rationale(body)
        missing = {"index_name", "target_query"} - fields.keys()
        if missing:
            raise ValueError(f"{index_id}: missing marker(s) {sorted(missing)}")
        if not rationale:
            raise ValueError(f"{index_id}: missing rationale marker")
        match = CREATE_PATTERN.search(body)
        if not match:
            raise ValueError(f"{index_id}: no CREATE INDEX IF NOT EXISTS statement found")
        index_name, table = assert_index_sql(match.group(1) + ";")
        if index_name != fields["index_name"]:
            raise ValueError(f"{index_id}: marker name does not match DDL ({index_name})")
        if index_name in seen:
            raise ValueError(f"{index_id}: duplicate index name {index_name}")
        seen.add(index_name)
        definitions.append(
            IndexDefinition(
                index_id=index_id,
                index_name=index_name,
                table=table,
                target_query=fields["target_query"],
                rationale=rationale,
                statement=match.group(1) + ";",
                ddl_sha256=hashlib.sha256(
                    (match.group(1) + ";").encode("utf-8")
                ).hexdigest(),
            )
        )
    return definitions


def query_id(sql: str) -> str:
    match = QUERY_ID.search(sql)
    return match.group(1) if match else "UNSPECIFIED"


def load_queries(directory: Path = QUERY_ROOT) -> dict[str, dict[str, str]]:
    from run_readonly_analytics import assert_read_only_sql

    queries: dict[str, dict[str, str]] = {}
    for path in sorted(directory.glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        assert_read_only_sql(sql, path)
        identifier = query_id(sql)
        if identifier == "UNSPECIFIED":
            raise ValueError(f"{path}: missing OQ-P3-05-xx query ID")
        if identifier in queries:
            raise ValueError(f"duplicate query ID {identifier}")
        queries[identifier] = {
            "id": identifier,
            "file": path.relative_to(REPO_ROOT).as_posix(),
            "sha256": hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            "sql": sql,
        }
    if not queries:
        raise ValueError(f"no optimization queries found in {directory}")
    return queries


def _node_types(plan: dict[str, Any]) -> list[str]:
    names: list[str] = []
    node = plan.get("Node Type")
    if isinstance(node, str):
        names.append(node)
    for child in plan.get("Plans", []) or []:
        names.extend(_node_types(child))
    return names


def summarize_explain(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        payload = json.loads(payload)
    if isinstance(payload, list):
        payload = payload[0]
    if not isinstance(payload, dict):
        raise ValueError("unexpected EXPLAIN JSON shape")
    plan = payload.get("Plan") or {}
    return {
        "planning_time_ms": payload.get("Planning Time"),
        "execution_time_ms": payload.get("Execution Time"),
        "total_cost": plan.get("Total Cost"),
        "root_node": plan.get("Node Type"),
        "scan_nodes": _node_types(plan),
        "shared_hit_blocks": plan.get("Shared Hit Blocks", 0),
        "shared_read_blocks": plan.get("Shared Read Blocks", 0),
        "temp_written_blocks": plan.get("Temp Written Blocks", 0),
        "plan_rows": plan.get("Plan Rows"),
        "actual_rows": plan.get("Actual Rows"),
    }


def _pct(before: Any, after: Any) -> float | None:
    if before in (None, 0) or after is None:
        return None
    return round(100.0 * (after - before) / before, 2)


def compare_summaries(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_time = before.get("execution_time_ms")
    after_time = after.get("execution_time_ms")
    before_cost = before.get("total_cost")
    after_cost = after.get("total_cost")
    return {
        "execution_time_ms": (
            round(after_time - before_time, 3)
            if before_time is not None and after_time is not None
            else None
        ),
        "execution_time_pct": _pct(before_time, after_time),
        "total_cost": (
            round(after_cost - before_cost, 3)
            if before_cost is not None and after_cost is not None
            else None
        ),
        "total_cost_pct": _pct(before_cost, after_cost),
    }


def finish_transaction(conn: Any, apply: bool) -> None:
    if apply:
        conn.commit()
    else:
        conn.rollback()


def assert_apply_allowed() -> None:
    allowed = (
        os.getenv("GITHUB_ACTIONS") == "true"
        and os.getenv("WAREHOUSE_CI_APPROVED") == "true"
        and os.getenv("GITHUB_REF") == "refs/heads/main"
    )
    if not allowed:
        raise SystemExit(2)


def _connect(database_url: str):
    import psycopg

    conn = psycopg.connect(database_url, connect_timeout=15)
    conn.autocommit = False
    return conn


def _scalar(conn: Any, sql: str, params: Sequence[Any] | None = None) -> Any:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    return row[0] if row else None


def database_size_bytes(conn: Any) -> int:
    return int(_scalar(conn, "SELECT pg_database_size(current_database())"))


def fact_baseline(conn: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in (
        "project_dw.fact_vehicle_tracking",
        "project_dw.fact_flight_journey",
        "project_dw.fact_airspace_occupancy",
    ):
        counts[table.split(".", 1)[1]] = int(_scalar(conn, f"SELECT COUNT(*) FROM {table}"))
    return counts


def index_size_bytes(conn: Any, table: str, index_name: str) -> int:
    value = _scalar(conn, "SELECT pg_relation_size(to_regclass(%s))", (f"{table}.{index_name}",))
    return int(value or 0)


def measure_query(conn: Any, sql: str) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute("SET LOCAL statement_timeout = '300s'")
        cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql)
        payload = cur.fetchone()[0]
    return summarize_explain(payload)


def _connection_metadata(conn: Any) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("SELECT current_user, current_database(), version()")
        role, database, version = cur.fetchone()
    return {
        "connected_role": str(role),
        "database": str(database),
        "server": str(version),
    }


def _index_exists(conn: Any, table: str, index_name: str) -> bool:
    exists = _scalar(
        conn,
        "SELECT to_regclass(%s) IS NOT NULL",
        (f"{table}.{index_name}",),
    )
    return bool(exists)


def measure_indexes(database_url: str, apply: bool) -> tuple[dict[str, Any], bool]:
    definitions = parse_index_definitions(DEFAULT_INDEX_SQL.read_text(encoding="utf-8"))
    queries = load_queries()
    for definition in definitions:
        if definition.target_query not in queries:
            raise SystemExit(
                f"{definition.index_id}: target query {definition.target_query} not found"
            )

    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence: dict[str, Any] = {
        "schema_version": 1,
        "work_package": "WP-P3-05",
        "mode": "apply" if apply else "verify",
        "captured_at": captured_at,
        "storage_guard_bytes": STORAGE_GUARD_BYTES,
        "queries": [
            {"id": item["id"], "file": item["file"], "sha256": item["sha256"]}
            for item in queries.values()
        ],
        "indexes": [],
    }

    conn = _connect(database_url)
    try:
        evidence.update(_connection_metadata(conn))
        evidence["baseline_database_size_bytes"] = database_size_bytes(conn)
        evidence["fact_baseline"] = fact_baseline(conn)

        if apply:
            before_by_index = {
                definition.index_id: measure_query(
                    conn, queries[definition.target_query]["sql"]
                )
                for definition in definitions
            }
        else:
            before_by_index = {}

        for definition in definitions:
            query = queries[definition.target_query]
            if apply:
                before = before_by_index[definition.index_id]
            else:
                # Verify mode: each candidate is measured alone against the clean
                # baseline, then discarded before the next candidate.
                before = measure_query(conn, query["sql"])
            with conn.cursor() as cur:
                cur.execute(definition.statement)
                cur.execute(f"ANALYZE {definition.table}")
            after = measure_query(conn, query["sql"])
            size = index_size_bytes(conn, definition.table, definition.index_name)
            if size <= 0:
                raise RuntimeError(
                    f"{definition.index_name}: created index has no measurable size"
                )
            record = {
                "index_id": definition.index_id,
                "index_name": definition.index_name,
                "table": definition.table,
                "target_query": definition.target_query,
                "rationale": definition.rationale,
                "ddl_sha256": definition.ddl_sha256,
                "size_bytes": size,
                "before": before,
                "after": after,
                "delta": compare_summaries(before, after),
            }
            evidence["indexes"].append(record)
            if not apply:
                conn.rollback()

        evidence["final_database_size_bytes"] = database_size_bytes(conn)

        if apply:
            evidence["persisted"] = True
            evidence["indexes_present"] = [
                {
                    "index_name": record["index_name"],
                    "exists": _index_exists(conn, record["table"], record["index_name"]),
                }
                for record in evidence["indexes"]
            ]
            if any(item["exists"] is False for item in evidence["indexes_present"]):
                finish_transaction(conn, apply=False)
                raise SystemExit("apply failed: a committed index is missing")
            if evidence["final_database_size_bytes"] > STORAGE_GUARD_BYTES:
                finish_transaction(conn, apply=False)
                raise SystemExit(
                    "capacity guard: database would exceed 700 MB; rolled back"
                )
        else:
            evidence["persisted"] = False
        finish_transaction(conn, apply=apply)
        if apply:
            evidence["final_database_size_bytes"] = database_size_bytes(conn)
    except BaseException:
        try:
            conn.rollback()
        finally:
            conn.close()
        raise
    else:
        conn.close()

    evidence["dq3_a_006_status"] = (
        "PASS"
        if all(item.get("before") and item.get("after") for item in evidence["indexes"])
        else "FAIL"
    )
    return evidence, evidence["dq3_a_006_status"] == "PASS"


def _format_ms(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.3f}"


def _format_pct(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):+.2f}%"


def render_markdown(evidence: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 index optimization evidence",
        "",
        f"- Captured at (UTC): {evidence['captured_at']}",
        f"- Work package: {evidence['work_package']}",
        f"- Mode: {evidence['mode']} (persisted: {str(evidence['persisted']).lower()})",
    ]
    if evidence.get("label"):
        lines.append(f"- Run label: {evidence['label']}")
    lines.extend(
        [
            f"- Connected role: `{evidence.get('connected_role', 'UNKNOWN')}`",
            f"- Database: `{evidence.get('database', 'UNKNOWN')}`",
            f"- Server: {evidence.get('server', 'UNKNOWN')}",
            f"- Storage guard: {evidence['storage_guard_bytes'] / (1024 * 1024):.0f} MiB",
            f"- Database size before: {evidence['baseline_database_size_bytes']} bytes",
            f"- Database size at end: {evidence['final_database_size_bytes']} bytes "
            f"(persisted: {str(evidence['persisted']).lower()})",
            "",
            "## Fact baseline at capture",
            "",
            "| Fact table | Rows |",
            "| --- | --- |",
        ]
    )
    for table, count in evidence["fact_baseline"].items():
        lines.append(f"| `{table}` | {count} |")

    lines.extend(
        [
            "",
            "## EXPLAIN ANALYZE before/after (DQ3-A-006)",
            "",
            "| Index | Target query | Before ms | After ms | Delta ms | Delta % | "
            "Before cost | After cost | Size KiB |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in evidence["indexes"]:
        before = item.get("before") or {}
        after = item.get("after") or {}
        delta = item.get("delta") or {}
        lines.append(
            "| `{name}` | `{query}` | {b_ms} | {a_ms} | {d_ms} | {d_pct} | "
            "{b_cost} | {a_cost} | {size:.1f} |".format(
                name=item["index_name"],
                query=item["target_query"],
                b_ms=_format_ms(before.get("execution_time_ms")),
                a_ms=_format_ms(after.get("execution_time_ms")),
                d_ms=_format_ms(delta.get("execution_time_ms")),
                d_pct=_format_pct(delta.get("execution_time_pct")),
                b_cost=_format_ms(before.get("total_cost")),
                a_cost=_format_ms(after.get("total_cost")),
                size=item["size_bytes"] / 1024,
            )
        )

    lines.extend(["", "## Candidate detail", ""])
    for item in evidence["indexes"]:
        before = item.get("before") or {}
        after = item.get("after") or {}
        delta = item.get("delta") or {}
        verdict = "NEUTRAL"
        pct = delta.get("execution_time_pct")
        if pct is not None and pct <= -5:
            verdict = "MEASURED_FASTER"
        elif pct is not None and pct >= 5:
            verdict = "MEASURED_SLOWER"
        lines.extend(
            [
                f"### `{item['index_name']}` ({item['index_id']})",
                "",
                f"- Table: `{item['table']}`",
                f"- Target query: `{item['target_query']}`",
                f"- Rationale: {item['rationale']}",
                f"- DDL SHA-256: `{item['ddl_sha256']}`",
                f"- Plan before: `{before.get('root_node')}` / "
                f"{', '.join(before.get('scan_nodes') or [])}",
                f"- Plan after: `{after.get('root_node')}` / "
                f"{', '.join(after.get('scan_nodes') or [])}",
                f"- Measured verdict: `{verdict}` "
                f"(execution {_format_pct(pct)}; cost {_format_pct(delta.get('total_cost_pct'))})",
                "",
            ]
        )

    lines.extend(
        [
            "## Rules",
            "",
            "- Verify mode rolls back every candidate; only an apply-mode run persists DDL.",
            "- These numbers are a single EXPLAIN ANALYZE observation, not a benchmark "
            "average; the command, query SHA-256, and capture time are recorded.",
            "- A candidate that is neutral or slower is not claimed as an improvement.",
            "- Missing coverage is never reported as zero activity (D3-009).",
            "",
            f"- DQ3-A-006: {evidence['dq3_a_006_status']}",
        ]
    )
    return "\n".join(lines) + "\n"


def default_outputs(mode: str) -> tuple[Path, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = DEFAULT_EVIDENCE_DIR / f"index_optimization_{mode}_{stamp}"
    return base.with_suffix(".json"), base.with_suffix(".md")


def write_evidence(
    evidence: dict[str, Any], json_path: Path, md_path: Path
) -> tuple[Path, Path]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    md_path.write_text(render_markdown(evidence), encoding="utf-8")
    return json_path, md_path


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="persist DDL (CI only)")
    parser.add_argument(
        "--database-url-env",
        default="DATABASE_URL",
        help="environment variable holding the writer connection string",
    )
    parser.add_argument("--json-output", type=Path, default=None)
    parser.add_argument("--md-output", type=Path, default=None)
    parser.add_argument("--label", default=None, help="non-secret run label")
    args = parser.parse_args(argv)

    if args.apply:
        assert_apply_allowed()

    database_url = os.getenv(args.database_url_env)
    if not database_url:
        parser.error(
            f"{args.database_url_env} is required; the connection string is supplied "
            "by CI, never committed"
        )

    evidence, passed = measure_indexes(database_url, apply=args.apply)
    if args.label:
        evidence["label"] = args.label
    json_default, md_default = default_outputs(evidence["mode"])
    json_path = args.json_output or json_default
    md_path = args.md_output or md_default
    write_evidence(evidence, json_path, md_path)

    print(f"Evidence JSON: {_display_path(json_path)}")
    print(f"Evidence Markdown: {_display_path(md_path)}")
    print(f"Mode: {evidence['mode']} (persisted: {evidence['persisted']})")
    print(f"DQ3-A-006: {evidence['dq3_a_006_status']}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
