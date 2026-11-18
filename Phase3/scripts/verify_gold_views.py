#!/usr/bin/env python3
"""Apply and verify the Phase 3 gold views (WP-P3-04).

Default mode is a rollback-only verification: the writer connection creates the
three views in one transaction, reconciles their rows and measures to the Phase 2
facts, checks the reader grant, then rolls back. ``--apply`` is accepted only in
the approved protected ``warehouse`` GitHub Actions job on ``main``; it commits the
views and then opens a separate ``aerogrid_reader`` connection to prove access.

The SQL file is static and lives in Git. This script never prints a connection
string; error messages are redacted. Evidence is written to
``Phase3/evidence/gold_views_<UTC>.md``.
"""
from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import run_readonly_analytics as runner

REPO_ROOT = runner.REPO_ROOT
SQL_FILE = REPO_ROOT / "Phase3" / "sql" / "views" / "01_gold_views.sql"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "Phase3" / "evidence"
VIEW_NAMES = (
    "vw_monthly_traffic_growth",
    "vw_vehicle_analysis",
    "vw_source_performance",
)
CREATE_VIEW_PATTERN = re.compile(
    r"CREATE\s+OR\s+REPLACE\s+VIEW\s+project_reporting\.(\w+)", re.IGNORECASE
)
FORBIDDEN_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|"
    r"VACUUM|ANALYZE|CALL|DO|COPY)\b",
    re.IGNORECASE,
)
SELECT_STAR_PATTERN = re.compile(r"\bSELECT\s+\*", re.IGNORECASE)


def assert_gold_view_sql(sql: str, path: Path) -> None:
    """Refuse writes, multiple view shapes, or unqualified view names."""
    statements = runner.executable_statements(sql)
    if len(statements) != len(VIEW_NAMES):
        raise ValueError(
            f"{path}: expected exactly {len(VIEW_NAMES)} view statements, "
            f"found {len(statements)}"
        )
    found: list[str] = []
    body = "\n".join(statements)
    for statement in statements:
        match = CREATE_VIEW_PATTERN.match(statement.strip())
        if not match:
            raise ValueError(
                f"{path}: every statement must start with "
                "CREATE OR REPLACE VIEW project_reporting.<name>"
            )
        found.append(match.group(1))
    if tuple(found) != VIEW_NAMES:
        raise ValueError(f"{path}: view order/names are {found}, expected {VIEW_NAMES}")
    if FORBIDDEN_PATTERN.search(body):
        raise ValueError(f"{path}: write-capable keyword outside CREATE OR REPLACE VIEW")
    if SELECT_STAR_PATTERN.search(body):
        raise ValueError(f"{path}: SELECT * is not allowed; list columns explicitly")


def _scalar(cur: Any, sql: str, params: Sequence[Any] | None = None) -> Any:
    if params is None:
        cur.execute(sql)
    else:
        cur.execute(sql, params)
    return cur.fetchone()[0]


def _safe_rollback(conn: Any) -> None:
    if conn is None:
        return
    try:
        conn.rollback()
    except Exception:  # noqa: BLE001 - preserve the original failure
        pass


def _safe_close(conn: Any) -> None:
    if conn is None:
        return
    try:
        conn.close()
    except Exception:  # noqa: BLE001 - closing is best effort
        pass


def fact_baseline(cur: Any) -> dict[str, int]:
    tracking_total = int(
        _scalar(
            cur,
            "SELECT COUNT(*)::bigint FROM project_dw.fact_vehicle_tracking "
            "WHERE site_key > 0 AND vehicle_key > 0",
        )
    )
    journey_total = int(
        _scalar(
            cur,
            "SELECT COUNT(*)::bigint FROM project_dw.fact_flight_journey "
            "WHERE site_key > 0 AND vehicle_key > 0",
        )
    )
    monthly_groups = int(
        _scalar(
            cur,
            "SELECT COUNT(*)::bigint FROM ("
            "  SELECT DISTINCT "
            "    date_trunc('month', event_ts AT TIME ZONE 'UTC')::date, site_key "
            "  FROM project_dw.fact_vehicle_tracking "
            "  WHERE site_key > 0 AND vehicle_key > 0"
            ") m",
        )
    )
    vehicle_rows = int(
        _scalar(
            cur,
            "SELECT COUNT(*)::bigint FROM project_dw.dim_vehicle "
            "WHERE vehicle_key > 0",
        )
    )
    source_rows = int(
        _scalar(
            cur,
            "SELECT COUNT(DISTINCT UPPER(TRIM(source_system)))::bigint "
            "FROM project_dw.dim_vehicle WHERE vehicle_key > 0",
        )
    )
    return {
        "tracking_positions": tracking_total,
        "journeys_observed": journey_total,
        "monthly_groups": monthly_groups,
        "vehicle_rows": vehicle_rows,
        "source_rows": source_rows,
    }


def view_stats(cur: Any, name: str) -> dict[str, int | None]:
    qualified = f"project_reporting.{name}"
    rows = int(_scalar(cur, f"SELECT COUNT(*)::bigint FROM {qualified}"))
    tracking = int(
        _scalar(cur, f"SELECT COALESCE(SUM(tracking_positions), 0)::bigint FROM {qualified}")
    )
    journeys: int | None
    if name == "vw_monthly_traffic_growth":
        journeys = None
        distinct_keys = int(
            _scalar(
                cur,
                f"SELECT COUNT(*)::bigint FROM ("
                f"  SELECT DISTINCT site_key, month_utc FROM {qualified}"
                f") k",
            )
        )
    elif name == "vw_vehicle_analysis":
        journeys = int(
            _scalar(
                cur,
                f"SELECT COALESCE(SUM(journeys_observed), 0)::bigint FROM {qualified}",
            )
        )
        distinct_keys = int(
            _scalar(cur, f"SELECT COUNT(DISTINCT vehicle_key)::bigint FROM {qualified}")
        )
    else:
        journeys = int(
            _scalar(
                cur,
                f"SELECT COALESCE(SUM(journeys_observed), 0)::bigint FROM {qualified}",
            )
        )
        distinct_keys = int(
            _scalar(cur, f"SELECT COUNT(DISTINCT source_system)::bigint FROM {qualified}")
        )
    return {
        "rows": rows,
        "tracking_positions": tracking,
        "journeys_observed": journeys,
        "distinct_keys": distinct_keys,
    }


def reconcile(cur: Any) -> tuple[dict[str, int], dict[str, dict[str, int | None]], bool]:
    baseline = fact_baseline(cur)
    expected_rows = {
        "vw_monthly_traffic_growth": baseline["monthly_groups"],
        "vw_vehicle_analysis": baseline["vehicle_rows"],
        "vw_source_performance": baseline["source_rows"],
    }
    results: dict[str, dict[str, int | None]] = {}
    passed = True
    for name in VIEW_NAMES:
        stats = view_stats(cur, name)
        stats["expected_rows"] = expected_rows[name]
        stats["rows_match"] = int(stats["rows"] == expected_rows[name])
        stats["tracking_match"] = int(
            stats["tracking_positions"] == baseline["tracking_positions"]
        )
        if stats["journeys_observed"] is None:
            stats["journeys_match"] = 1
        else:
            stats["journeys_match"] = int(
                stats["journeys_observed"] == baseline["journeys_observed"]
            )
        stats["keys_match"] = int(stats["distinct_keys"] == stats["rows"])
        stats["status"] = (
            "PASS"
            if (
                stats["rows_match"]
                and stats["tracking_match"]
                and stats["journeys_match"]
                and stats["keys_match"]
            )
            else "FAIL"
        )
        if stats["status"] != "PASS":
            passed = False
        results[name] = stats
    return baseline, results, passed


def grant_and_check_reader(cur: Any) -> None:
    for name in VIEW_NAMES:
        qualified = f"project_reporting.{name}"
        cur.execute(f"GRANT SELECT ON {qualified} TO aerogrid_reader")
        cur.execute(
            "SELECT has_table_privilege(%s, %s, %s)",
            ("aerogrid_reader", qualified, "SELECT"),
        )
        if cur.fetchone()[0] is not True:
            raise AssertionError(f"aerogrid_reader cannot SELECT {qualified}")


def reader_check(
    reader_url: str, expected_rows: dict[str, int] | None = None
) -> dict[str, Any]:
    import psycopg

    with psycopg.connect(reader_url, connect_timeout=15) as conn:
        conn.read_only = True
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '300s'")
            cur.execute("SELECT current_user, current_database(), version()")
            role, database, server = cur.fetchone()
            if str(role) != "aerogrid_reader":
                raise AssertionError(
                    f"reader connection is {role!r}, expected 'aerogrid_reader'"
                )
            view_rows: dict[str, int] = {}
            for name in VIEW_NAMES:
                qualified = f"project_reporting.{name}"
                cur.execute(
                    "SELECT has_table_privilege(current_user, %s, 'SELECT')",
                    (qualified,),
                )
                if cur.fetchone()[0] is not True:
                    raise AssertionError(f"reader cannot SELECT {qualified}")
                cur.execute(f"SELECT COUNT(*)::bigint FROM {qualified}")
                view_rows[name] = int(cur.fetchone()[0])
                if expected_rows is not None and view_rows[name] != expected_rows[name]:
                    raise AssertionError(
                        f"reader sees {view_rows[name]} rows in {qualified}, "
                        f"expected {expected_rows[name]}"
                    )
    return {
        "role": str(role),
        "database": str(database),
        "server": str(server),
        "view_rows": view_rows,
    }


def write_evidence(
    path: Path,
    captured_at: str,
    mode: str,
    label: str | None,
    writer: dict[str, Any] | None,
    baseline: dict[str, int] | None,
    results: dict[str, dict[str, int | None]] | None,
    dq3_a_001: str,
    reader: dict[str, Any] | None,
    errors: list[str],
    sql_sha: str,
) -> None:
    lines = [
        "# Phase 3 gold-view evidence",
        "",
        f"- Captured at (UTC): {captured_at}",
        f"- Mode: `{mode}`",
        f"- DDL file: `{SQL_FILE.relative_to(REPO_ROOT).as_posix()}`",
        f"- DDL SHA-256: `{sql_sha}`",
        "- Scope: `project_reporting.vw_monthly_traffic_growth`, "
        "`vw_vehicle_analysis`, `vw_source_performance`",
    ]
    if label:
        lines.append(f"- Run label: {label}")
    lines.extend(["", "## Writer connection", ""])
    if writer:
        lines.extend(
            [
                f"- Connected role: `{runner.format_value(writer.get('role'))}`",
                f"- Database: `{runner.format_value(writer.get('database'))}`",
                f"- Server: {runner.format_value(writer.get('server'))}",
                "- Transaction mode: write transaction for approved view apply"
                if mode == "apply"
                else "- Transaction mode: `ROLLBACK` (no persisted view changes)",
            ]
        )
    else:
        lines.append("_Writer connection did not complete._")

    lines.extend(["", "## Fact baseline", ""])
    if baseline:
        lines.append(
            runner.markdown_table(
                [
                    "fact_tracking_positions",
                    "fact_journeys",
                    "fact_site_months",
                    "fact_vehicle_rows",
                    "fact_source_rows",
                ],
                [
                    (
                        baseline["tracking_positions"],
                        baseline["journeys_observed"],
                        baseline["monthly_groups"],
                        baseline["vehicle_rows"],
                        baseline["source_rows"],
                    )
                ],
            )
        )
    else:
        lines.append("_Fact baseline unavailable._")

    lines.extend(["", "## DQ3-A-001 reconciliation", ""])
    if results:
        rows = []
        for name in VIEW_NAMES:
            s = results[name]
            rows.append(
                (
                    name,
                    s["rows"],
                    s["expected_rows"],
                    s["distinct_keys"],
                    s["tracking_positions"],
                    baseline["tracking_positions"] if baseline else None,
                    s["journeys_observed"],
                    baseline["journeys_observed"] if baseline else None,
                    s["status"],
                )
            )
        lines.append(
            runner.markdown_table(
                [
                    "view",
                    "rows",
                    "expected_rows",
                    "distinct_keys",
                    "sum_tracking",
                    "fact_tracking",
                    "sum_journeys",
                    "fact_journeys",
                    "status",
                ],
                rows,
            )
        )
        lines.append("")
        lines.append(f"- DQ3-A-001: `{dq3_a_001}`")
    else:
        lines.append(f"- DQ3-A-001: `{dq3_a_001}`")

    lines.extend(["", "## Reader access", ""])
    if reader:
        lines.extend(
            [
                f"- Connected role: `{runner.format_value(reader['role'])}`",
                f"- Database: `{runner.format_value(reader['database'])}`",
                f"- Server: {runner.format_value(reader['server'])}",
                "- Transaction mode: `READ ONLY`",
                "",
                runner.markdown_table(
                    ["view", "reader_select", "rows"],
                    [
                        (name, "PASS", reader["view_rows"].get(name))
                        for name in VIEW_NAMES
                    ],
                ),
            ]
        )
    else:
        lines.append("- Reader access: `NOT_RUN`")

    lines.extend(["", "## Summary", ""])
    lines.append(f"- DQ3-A-001: `{dq3_a_001}`")
    lines.append(
        f"- Reader access: `{'PASS' if reader else 'NOT_RUN'}`"
    )
    lines.append(f"- Errors: {len(errors)}")
    for error in errors:
        lines.append(f"  - {error}")
    lines.append(
        "- Coverage: absent rows are missing coverage, never zero activity (D3-009)."
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    mode: str,
    writer_url: str,
    reader_url: str | None,
    output: Path,
    label: str | None,
) -> int:
    sql = SQL_FILE.read_text(encoding="utf-8")
    assert_gold_view_sql(sql, SQL_FILE)
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sql_sha = runner.sha256_file(SQL_FILE)
    writer: dict[str, Any] | None = None
    baseline: dict[str, int] | None = None
    results: dict[str, dict[str, int | None]] | None = None
    reader: dict[str, Any] | None = None
    errors: list[str] = []
    dq3_a_001 = "NOT_RUN"
    conn = None
    try:
        import psycopg

        conn = psycopg.connect(writer_url, connect_timeout=15)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '8min'")
            cur.execute(sql)
            grant_and_check_reader(cur)
            cur.execute("SELECT current_user, current_database(), version()")
            role, database, server = cur.fetchone()
            if mode == "apply" and str(role) != "aerogrid_etl":
                raise AssertionError(
                    f"apply writer is {role!r}, expected 'aerogrid_etl'"
                )
            writer = {
                "role": str(role),
                "database": str(database),
                "server": str(server),
            }
            baseline, results, passed = reconcile(cur)
            dq3_a_001 = "PASS" if passed else "FAIL"
        if mode == "apply":
            if not reader_url:
                raise RuntimeError(
                    "READONLY_DATABASE_URL is required for the reader proof in apply mode"
                )
            conn.commit()
            expected_rows = {}
            if results is not None:
                expected_rows = {
                    name: int(results[name]["rows"]) for name in VIEW_NAMES
                }
            reader = reader_check(reader_url, expected_rows or None)
        else:
            _safe_rollback(conn)
    except Exception as exc:  # noqa: BLE001 - evidence records the failure
        message = runner.redact(str(exc), writer_url)
        if reader_url:
            message = runner.redact(message, reader_url)
        errors.append(f"{type(exc).__name__}: {message}")
        dq3_a_001 = "FAIL"
        _safe_rollback(conn)
    finally:
        _safe_close(conn)

    write_evidence(
        output,
        captured_at,
        mode,
        label,
        writer,
        baseline,
        results,
        dq3_a_001,
        reader,
        errors,
        sql_sha,
    )
    try:
        display = output.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        display = str(output)
    print(f"Evidence written: {display}")
    print(f"DQ3-A-001: {dq3_a_001}")
    print(f"Reader access: {'PASS' if reader else 'NOT_RUN'}")
    print(f"Errors: {len(errors)}")
    if errors or dq3_a_001 != "PASS":
        return 1
    if mode == "apply" and reader is None:
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="commit the views and run the reader proof (approved CI on main only)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="evidence Markdown path (default: Phase3/evidence/gold_views_<UTC>.md)",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="non-secret label stored in the evidence header",
    )
    args = parser.parse_args(argv)

    if args.apply:
        if (
            os.getenv("GITHUB_ACTIONS") != "true"
            or os.getenv("WAREHOUSE_CI_APPROVED") != "true"
            or os.getenv("GITHUB_REF", "refs/heads/main") != "refs/heads/main"
        ):
            parser.error(
                "apply requires the approved protected warehouse GitHub Actions "
                "job on main (GITHUB_ACTIONS=true, WAREHOUSE_CI_APPROVED=true)"
            )
    writer_url = os.getenv("DATABASE_URL")
    if not writer_url:
        parser.error("DATABASE_URL is required in the approved CI job")
    reader_url = os.getenv("READONLY_DATABASE_URL")
    output = args.output or (
        DEFAULT_OUTPUT_DIR
        / f"gold_views_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
    )
    return run(
        "apply" if args.apply else "verify",
        writer_url,
        reader_url,
        output,
        args.label,
    )


if __name__ == "__main__":
    raise SystemExit(main())
