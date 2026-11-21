#!/usr/bin/env python3
"""Evidence harness for WP-P3-H3: should dim_vehicle become SCD Type 2?

Runs the four read-only probes in ``Phase3/sql/scd2_evaluation/`` and records the
results, then derives a verdict from the numbers using the rules in
``Phase3/docs/WP-P3-H3_scd2_evaluation.md``. It never writes to the warehouse: each probe is a
single SELECT, checked by the same guard as the analytics runner, executed in a READ
ONLY connection. It creates no Type 2 table and changes no dimension.

Credentials come from ``READONLY_DATABASE_URL`` (or the variable named by
``--database-url-env``). The URL is never printed; errors are redacted.

Usage:
    python Phase3/scripts/evaluate_scd2.py --require-reader
    python Phase3/scripts/evaluate_scd2.py --list
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from run_readonly_analytics import (
    DEFAULT_OUTPUT_DIR,
    REPO_ROOT,
    _connect,
    assert_read_only_sql,
    format_value,
    markdown_table,
    redact,
    sha256_file,
)

PROBE_DIR = REPO_ROOT / "Phase3" / "sql" / "scd2_evaluation"

DEFER = "DEFER_SCD2"
REVIEW = "REVIEW_SCD2"
NO_DATA = "INCONCLUSIVE_NO_DATA"


def probe_files() -> list[Path]:
    return sorted(PROBE_DIR.glob("*.sql"))


def _number(row: Mapping[str, Any], key: str) -> float:
    value = row.get(key)
    return float(value) if value is not None else 0.0


def decide(results: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Pure decision rules; ``results`` maps query ID to its single summary row.

    * No real vehicles -> ``INCONCLUSIVE_NO_DATA`` (the evidence cannot support a decision).
    * One or fewer distinct ``vehicle_type`` values -> no descriptive attribute varies,
      so Type 2 would version nothing -> ``DEFER_SCD2``.
    * More than one value -> a varying attribute exists -> ``REVIEW_SCD2`` (human decides).
    * Stale ``last_seen_ts`` members are reported separately as a Type 1 gap; they never
      justify Type 2 on their own.
    """
    profile = results.get("QW-P3-H3-01", {})
    identity = results.get("QW-P3-H3-02", {})
    staleness = results.get("QW-P3-H3-03", {})
    span = results.get("QW-P3-H3-04", {})

    members = _number(profile, "h3_members")
    varying = _number(profile, "h3_distinct_vehicle_types") > 1
    if members == 0:
        verdict = NO_DATA
    elif varying:
        verdict = REVIEW
    else:
        verdict = DEFER

    return {
        "verdict": verdict,
        "members": int(members),
        "varying_attribute": varying,
        "single_observed_month": _number(span, "h3_observed_months") <= 1,
        "type1_gap": _number(staleness, "h3_stale_members") > 0,
        "stale_members": int(_number(staleness, "h3_stale_members")),
        "max_lag_hours": _number(staleness, "h3_max_lag_hours"),
        "multi_source_serials": int(_number(identity, "h3_serials_multi_source")),
    }


def findings_lines(decision: Mapping[str, Any]) -> list[str]:
    lines = [f"- Verdict: **{decision['verdict']}**"]
    if decision["verdict"] == NO_DATA:
        lines.append("- No real `dim_vehicle` members were found; this run cannot support a decision.")
        return lines
    if decision["varying_attribute"]:
        lines.append("- A descriptive attribute varies across members; a human must decide whether history is needed.")
    else:
        lines.append("- No descriptive attribute varies across members, so Type 2 would version nothing.")
    if decision["single_observed_month"]:
        lines.append("- Tracking data spans one observed month or less, so a version change could not be shown.")
    if decision["type1_gap"]:
        lines.append(
            f"- Type 1 gap: {decision['stale_members']} member(s) have `last_seen_ts` behind staged "
            f"data (max lag {decision['max_lag_hours']} h). This is a refresh defect, not a Type 2 need."
        )
    else:
        lines.append("- No stale `last_seen_ts` members were found.")
    if decision["multi_source_serials"]:
        lines.append(
            f"- {decision['multi_source_serials']} serial(s) appear under more than one source system; "
            "identity stays source-scoped (L3-003)."
        )
    return lines


def render_report(
    *,
    captured_at: str,
    role: str,
    database: str,
    probe_sections: Sequence[str],
    probes_executed: int,
    decision: Mapping[str, Any] | None,
    failures: Sequence[str],
) -> str:
    lines = [
        "# WP-P3-H3 SCD Type 2 evaluation evidence",
        "",
        f"- Captured at (UTC): {captured_at}",
        f"- Connected role: `{role}`",
        f"- Database: `{database}`",
        "- Transaction mode: `READ ONLY`; no Type 2 object was created",
        f"- Probes: {probes_executed} of {len(probe_files())} executed",
        "",
    ]
    lines.extend(probe_sections)
    lines.extend(["", "## Findings", ""])
    if failures:
        lines.append("- Evaluation incomplete; no verdict was derived.")
        lines.extend(f"- FAIL: {item}" for item in failures)
    elif decision is not None:
        lines.extend(findings_lines(decision))
    lines.extend(
        [
            "",
            "Decision rules: `Phase3/docs/WP-P3-H3_scd2_evaluation.md`. Zero rows mean missing "
            "coverage, never proof of no activity (D3-009).",
            "",
        ]
    )
    return "\n".join(lines)


def run(database_url: str, output: Path, require_reader: bool) -> int:
    files = probe_files()
    if not files:
        raise SystemExit(f"No probe files found in {PROBE_DIR}")
    for path in files:
        assert_read_only_sql(path.read_text(encoding="utf-8"), path)

    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sections: list[str] = []
    results: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    role = database = "UNKNOWN"
    conn = None
    try:
        conn = _connect(database_url)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '120s'")
            cur.execute("SELECT current_user, current_database()")
            role, database = (str(v) for v in cur.fetchone())
        if require_reader and role != "aerogrid_reader":
            raise SystemExit(f"--require-reader requested but connected role is {role!r}")
        for path in files:
            relative = path.relative_to(REPO_ROOT).as_posix()
            try:
                with conn.cursor() as cur:
                    cur.execute(path.read_text(encoding="utf-8"))
                    columns = [column.name for column in cur.description]
                    row = cur.fetchone()
                results[str(row[0])] = dict(zip(columns, row))
                sections.extend(
                    ["", f"## `{relative}`", "", f"- Query ID: `{row[0]}`",
                     f"- SHA-256: `{sha256_file(path)}`", "", markdown_table(columns, [row])]
                )
            except Exception as exc:  # noqa: BLE001 - evidence must record the failure
                conn.rollback()
                failures.append(f"{relative}: {type(exc).__name__}")
                sections.extend(["", f"## `{relative}`", "", "- Status: `FAIL`", "", "```text",
                                 redact(str(exc), database_url).splitlines()[0][:300], "```"])
                break
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - connection failure evidence
        failures.append(f"connection: {type(exc).__name__}")
        sections.extend(["", "- Status: `FAIL` (connection)", "", "```text",
                         redact(str(exc), database_url).splitlines()[0][:300], "```"])
    finally:
        if conn is not None:
            try:
                conn.rollback()
            finally:
                conn.close()

    decision = None if failures else decide(results)
    report = render_report(captured_at=captured_at, role=role, database=database,
                           probe_sections=sections, probes_executed=len(results),
                           decision=decision, failures=failures)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    shown = output.relative_to(REPO_ROOT).as_posix() if output.is_relative_to(REPO_ROOT) else str(output)
    print(f"Evidence written: {shown}")
    print(f"Connected role: {role}")
    print(f"Verdict: {decision['verdict'] if decision else 'NONE'}")
    if failures or decision is None or decision["verdict"] == NO_DATA:
        return 1
    return 0


def default_output_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_OUTPUT_DIR / f"scd2_evaluation_{stamp}.md"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url-env", default="READONLY_DATABASE_URL")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--require-reader", action="store_true")
    parser.add_argument("--list", action="store_true", help="list probes and exit without connecting")
    args = parser.parse_args(argv)

    files = probe_files()
    for path in files:
        assert_read_only_sql(path.read_text(encoding="utf-8"), path)
    if args.list:
        for path in files:
            print(path.relative_to(REPO_ROOT).as_posix())
        return 0
    database_url = os.environ.get(args.database_url_env)
    if not database_url:
        raise SystemExit(f"Environment variable {args.database_url_env} is not set")
    return run(database_url, args.output or default_output_path(), args.require_reader)


if __name__ == "__main__":
    raise SystemExit(main())
