#!/usr/bin/env python3
"""Run the Phase 3 analytical and OLAP SQL files in a read-only transaction.

This runner is evidence tooling, not a data pipeline. It never writes to the
warehouse: it opens a READ ONLY transaction, executes one SELECT per file, and
records the query, SHA-256, row count, and result rows in a Markdown evidence
file. Missing coverage is never converted into a zero-activity claim.

Credentials are read from ``READONLY_DATABASE_URL`` when set, otherwise from
``DATABASE_URL`` (CI writer credentials are still used read-only). The URL is
never printed; error messages are redacted.

Usage:
    python Phase3/scripts/run_readonly_analytics.py --layer all
    python Phase3/scripts/run_readonly_analytics.py --layer olap --require-reader

The human/CI supplies the password through the environment. Do not put it in a
repository file or paste it into chat.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SQL_ROOT = REPO_ROOT / "Phase3" / "sql"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "Phase3" / "evidence"

LAYER_DIRS = {
    "analytical": SQL_ROOT / "analytical",
    "olap": SQL_ROOT / "olap",
}

WRITE_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|"
    r"VACUUM|ANALYZE|CALL|DO|COPY)\b",
    re.IGNORECASE,
)
DSN_PATTERN = re.compile(r"postgres(?:ql)?://[^\s'\"]+", re.IGNORECASE)
MAX_CELL_CHARS = 300


def executable_statements(sql: str) -> list[str]:
    """Split SQL on statement terminators outside strings and comments.

    A naive ``split(';')`` breaks on semicolons inside quoted coverage labels, so
    this scanner tracks single/double quotes, dollar quotes, line comments, and
    nested block comments.
    """
    statements: list[str] = []
    buffer: list[str] = []
    index = 0
    length = len(sql)
    quote: str | None = None
    dollar_tag: str | None = None

    while index < length:
        char = sql[index]
        following = sql[index + 1] if index + 1 < length else ""

        if dollar_tag is not None:
            if sql.startswith(dollar_tag, index):
                buffer.append(dollar_tag)
                index += len(dollar_tag)
                dollar_tag = None
            else:
                buffer.append(char)
                index += 1
            continue

        if quote is not None:
            buffer.append(char)
            if char == quote:
                if following == quote:
                    buffer.append(following)
                    index += 2
                    continue
                quote = None
            index += 1
            continue

        if char in ("'", '"'):
            quote = char
            buffer.append(char)
            index += 1
            continue

        if char == "-" and following == "-":
            index += 2
            while index < length and sql[index] != "\n":
                index += 1
            continue

        if char == "/" and following == "*":
            index += 2
            depth = 1
            while index < length and depth:
                if sql.startswith("/*", index):
                    depth += 1
                    index += 2
                elif sql.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            continue

        if char == "$":
            match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", sql[index:])
            if match:
                dollar_tag = match.group(0)
                buffer.append(dollar_tag)
                index += len(dollar_tag)
                continue

        if char == ";":
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer = []
            index += 1
            continue

        buffer.append(char)
        index += 1

    statement = "".join(buffer).strip()
    if statement:
        statements.append(statement)
    return statements


def assert_read_only_sql(sql: str, path: Path) -> None:
    """Refuse anything that is not exactly one read-only SELECT/WITH statement."""
    statements = executable_statements(sql)
    if len(statements) != 1:
        raise ValueError(
            f"{path}: expected exactly one SQL statement, found {len(statements)}"
        )
    statement = statements[0]
    if not re.match(r"^(SELECT|WITH)\b", statement, re.IGNORECASE):
        raise ValueError(f"{path}: statement must start with SELECT or WITH")
    match = WRITE_KEYWORDS.search(statement)
    if match:
        raise ValueError(f"{path}: write-capable keyword found: {match.group(1)}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sql_files(layer: str) -> list[Path]:
    if layer == "all":
        return sorted(
            path
            for directory in LAYER_DIRS.values()
            for path in directory.glob("*.sql")
        )
    directory = LAYER_DIRS[layer]
    return sorted(directory.glob("*.sql"))


def query_id(sql: str) -> str:
    match = re.search(r"\b(QW-P3-0[23]-\d{2})\b", sql)
    return match.group(1) if match else "UNSPECIFIED"


def redact(text: str, secret: str | None = None) -> str:
    cleaned = DSN_PATTERN.sub("<redacted-dsn>", text)
    if secret:
        cleaned = cleaned.replace(secret, "<redacted-dsn>")
    return cleaned


def format_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    text = str(value).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")
    if len(text) > MAX_CELL_CHARS:
        return text[:MAX_CELL_CHARS] + "..."
    return text


def markdown_table(columns: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    if not columns:
        return "_No result columns._"
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(format_value(value) for value in row) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def default_output_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_OUTPUT_DIR / f"analytics_run_{stamp}.md"


def _connect(database_url: str):
    import psycopg

    conn = psycopg.connect(database_url, connect_timeout=15)
    conn.read_only = True
    return conn


def run(
    database_url: str,
    layer: str,
    output: Path,
    max_rows: int,
    require_reader: bool,
    label: str | None,
) -> int:
    files = sql_files(layer)
    if not files:
        raise SystemExit(f"No SQL files found for layer {layer!r}")

    for path in files:
        sql = path.read_text(encoding="utf-8")
        assert_read_only_sql(sql, path)

    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = [
        "# Phase 3 read-only analytics evidence",
        "",
        f"- Captured at (UTC): {captured_at}",
        f"- Layer(s): {layer}",
        f"- SQL files: {len(files)}",
        f"- Max rows recorded per query: {max_rows}",
    ]
    if label:
        lines.append(f"- Run label: {label}")
    lines.extend(["", "## Connection", ""])

    failures: list[str] = []
    dq3_a_004_status: str | None = None
    connected_role = "UNKNOWN"
    executed = 0
    conn = None
    try:
        conn = _connect(database_url)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '300s'")
            cur.execute("SELECT current_user, current_database(), version()")
            role, database, version = cur.fetchone()
            connected_role = str(role)
            lines.extend(
                [
                    f"- Connected role: `{format_value(role)}`",
                    f"- Database: `{format_value(database)}`",
                    f"- Server: {format_value(version)}",
                    "- Transaction mode: `READ ONLY` (enforced by the connection)",
                ]
            )
        if require_reader and connected_role != "aerogrid_reader":
            raise SystemExit(
                f"--require-reader requested but connected role is {connected_role!r}"
            )

        for path in files:
            relative = path.relative_to(REPO_ROOT).as_posix()
            sql = path.read_text(encoding="utf-8")
            lines.extend(["", f"## `{relative}`", ""])
            lines.append(f"- Query ID: `{query_id(sql)}`")
            lines.append(f"- SHA-256: `{sha256_file(path)}`")
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if cur.description is None:
                        raise AssertionError("query returned no result set")
                    columns = [column.name for column in cur.description]
                    fetched = cur.fetchmany(max_rows + 1)
                    truncated = len(fetched) > max_rows
                    rows = fetched[:max_rows]
                    lines.append(f"- Rows returned: {len(fetched) if truncated else len(rows)}")
                    lines.append(f"- Columns: {len(columns)}")
                    if truncated:
                        lines.append(
                            f"- Recorded rows: first {max_rows} only (result exceeded the cap)"
                        )
                    lines.append("")
                    keys = [column.lower() for column in columns]
                    if rows:
                        lines.append(markdown_table(columns, rows))
                    else:
                        lines.append("_No rows returned._")
                        lines.append("")
                        lines.append(
                            "Missing result means missing coverage, not proof of no activity "
                            "(D3-009)."
                        )
                    if "dq3_a_004_status" in keys:
                        dq_row = rows[0]
                        dq3_a_004_status = str(
                            dq_row[keys.index("dq3_a_004_status")]
                        )
                    executed += 1
            except Exception as exc:  # noqa: BLE001 - evidence must record the failure
                conn.rollback()
                failures.append(f"{relative}: {type(exc).__name__}")
                lines.append(f"- Status: `FAIL` ({type(exc).__name__})")
                lines.append("")
                lines.append("```text")
                lines.append(redact(str(exc), database_url).splitlines()[0][:500])
                lines.append("```")
                break
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - connection failure evidence
        failures.append(f"connection: {type(exc).__name__}")
        lines.extend(
            [
                f"- Status: `FAIL` ({type(exc).__name__})",
                "",
                "```text",
                redact(str(exc), database_url).splitlines()[0][:500],
                "```",
            ]
        )
    finally:
        if conn is not None:
            try:
                conn.rollback()
            finally:
                conn.close()

    lines.extend(["", "## Summary", ""])
    lines.append(f"- Queries executed successfully: {executed} of {len(files)}")
    lines.append(f"- Failed: {len(failures)}")
    for failure in failures:
        lines.append(f"  - {failure}")
    lines.append(f"- DQ3-A-004 grand-total reconciliation: {dq3_a_004_status or 'NOT_RUN'}")
    lines.append(
        "- Zero-row results are missing coverage, never zero activity (D3-009)."
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        display_path = output.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        display_path = str(output)
    print(f"Evidence written: {display_path}")
    print(f"Connected role: {connected_role}")
    print(f"Failures: {len(failures)}")
    if dq3_a_004_status:
        print(f"DQ3-A-004: {dq3_a_004_status}")
    if failures:
        return 1
    if dq3_a_004_status is not None and dq3_a_004_status != "PASS":
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--layer",
        choices=("analytical", "olap", "all"),
        default="all",
        help="which SQL layer to execute",
    )
    parser.add_argument(
        "--database-url-env",
        default="READONLY_DATABASE_URL",
        help="environment variable holding the reader connection string",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="evidence Markdown path (default: Phase3/evidence/analytics_run_<UTC>.md)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=1000,
        help="maximum rows recorded per query",
    )
    parser.add_argument(
        "--require-reader",
        action="store_true",
        help="fail unless the connected role is exactly aerogrid_reader",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="non-secret label stored in the evidence header",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list SQL files and exit without connecting",
    )
    args = parser.parse_args(argv)

    files = sql_files(args.layer)
    if args.list:
        for path in files:
            sql = path.read_text(encoding="utf-8")
            assert_read_only_sql(sql, path)
            print(f"{query_id(sql)}  {path.relative_to(REPO_ROOT).as_posix()}")
        return 0

    database_url = os.getenv(args.database_url_env) or os.getenv("DATABASE_URL")
    if not database_url:
        parser.error(
            f"{args.database_url_env} (or DATABASE_URL) is required; "
            "the connection string is supplied by the human/CI, never committed"
        )

    output = args.output or default_output_path()
    return run(
        database_url=database_url,
        layer=args.layer,
        output=output,
        max_rows=max(1, args.max_rows),
        require_reader=args.require_reader,
        label=args.label,
    )


if __name__ == "__main__":
    raise SystemExit(main())
