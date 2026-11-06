#!/usr/bin/env python3
"""WP-02 platform validation probe.

Proves that CI can write to the shared Neon warehouse, that the raw bucket is
readable and writable, and that the read-only role can read but cannot write.
Only non-secret evidence is printed; connection strings and credentials are
always redacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import boto3
import psycopg
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from psycopg.conninfo import conninfo_to_dict, make_conninfo

SCHEMAS = ("project_staging", "project_dw", "project_reporting")
PROBE_TABLE = "project_staging.wp02_read_probe"
READER_ROLE = "aerogrid_reader"
WRITER_ROLE = "aerogrid_etl"
MARKER_KEY = "validation/wp-02/marker.json"

GIB = 1024**3
MIB = 1024**2
DB_FREE_LIMIT = 1 * GIB
DB_TARGET = 500 * MIB
BUCKET_FREE_LIMIT = 5 * GIB
BUCKET_TARGET = 2 * GIB

SECRET_VARS = (
    "DATABASE_URL",
    "READONLY_DATABASE_URL",
    "NEON_S3_ACCESS_KEY_ID",
    "NEON_S3_SECRET_ACCESS_KEY",
)

DSN_PATTERN = re.compile(r"postgres(?:ql)?://[^\s'\"]+")

READER_DENIED_CASES = (
    (
        "reader insert",
        f"INSERT INTO {PROBE_TABLE} (probe_id, note) VALUES (999, 'should fail')",
        None,
    ),
    (
        "reader update",
        f"UPDATE {PROBE_TABLE} SET note = note",
        None,
    ),
    (
        "reader delete",
        f"DELETE FROM {PROBE_TABLE}",
        None,
    ),
    (
        "reader create table",
        "CREATE TABLE project_staging.wp02_reader_should_fail (probe_id integer)",
        "DROP TABLE IF EXISTS project_staging.wp02_reader_should_fail",
    ),
    (
        "reader create schema",
        "CREATE SCHEMA wp02_reader_should_fail",
        "DROP SCHEMA IF EXISTS wp02_reader_should_fail",
    ),
)

PROBE_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS project_staging.wp02_read_probe (
    probe_id integer PRIMARY KEY,
    note text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
)
""".strip()


def redact(value: object) -> str:
    text = DSN_PATTERN.sub("postgresql://***", str(value))
    for name in SECRET_VARS:
        secret = os.environ.get(name)
        if secret and len(secret) >= 4:
            text = text.replace(secret, "***")
    return text


def human_bytes(size: int) -> str:
    if size >= GIB:
        return f"{size / GIB:.2f} GiB"
    return f"{size / MIB:.1f} MiB"


@dataclass
class Report:
    rows: list[tuple[str, str, str]] = field(default_factory=list)

    def add(self, check: str, status: str, evidence: str = "") -> None:
        self.rows.append((check, status, evidence))
        print(f"[{status}] {check}: {evidence}")

    def failures(self) -> list[tuple[str, str, str]]:
        return [row for row in self.rows if row[1] == "FAIL"]

    def skipped(self) -> list[tuple[str, str, str]]:
        return [row for row in self.rows if row[1] == "SKIP"]

    def render(self) -> str:
        counts = {status: 0 for status in ("PASS", "WARN", "SKIP", "FAIL", "INFO")}
        for _, status, _ in self.rows:
            counts[status] = counts.get(status, 0) + 1
        if counts["FAIL"]:
            overall = "FAIL"
        elif counts["SKIP"]:
            overall = "PARTIAL"
        else:
            overall = "PASS"
        lines = [
            "## WP-02 platform validation",
            "",
            f"- Overall: **{overall}**",
            f"- Pass: {counts['PASS']} | Warnings: {counts['WARN']} | "
            f"Skipped: {counts['SKIP']} | Failures: {counts['FAIL']}",
            "",
            "| Check | Result | Evidence |",
            "|---|---|---|",
        ]
        for check, status, evidence in self.rows:
            safe = evidence.replace("|", "\\|")
            lines.append(f"| {check} | {status} | {safe} |")
        lines.append("")
        return "\n".join(lines)


def parse_dsn(dsn: str) -> dict[str, str]:
    try:
        return conninfo_to_dict(dsn)
    except Exception:
        return {}


def connect(dsn: str) -> tuple[psycopg.Connection, float, float]:
    started = time.perf_counter()
    conn = psycopg.connect(
        dsn,
        connect_timeout=10,
        prepare_threshold=None,
        autocommit=True,
        application_name="aerogrid-wp02-probe",
    )
    connected = time.perf_counter() - started
    conn.execute("SELECT 1").fetchone()
    first_query = time.perf_counter() - started
    return conn, connected, first_query


def run_writer(report: Report) -> dict[str, object]:
    state: dict[str, object] = {"probe_table": False}
    dsn = os.environ.get("DATABASE_URL", "").strip()
    if not dsn:
        report.add("writer connection", "FAIL", "DATABASE_URL is not set")
        return state

    info = parse_dsn(dsn)
    host = info.get("host", "unknown")
    sslmode = info.get("sslmode", "default")
    endpoint_kind = "pooled" if "-pooler" in host else "direct"

    try:
        conn, connect_ms, first_ms = connect(dsn)
    except Exception as exc:  # noqa: BLE001 - probe must report any failure
        report.add("writer connection", "FAIL", redact(exc))
        return state

    report.add(
        "writer connection",
        "PASS",
        f"{connect_ms * 1000:.0f} ms to connect, {first_ms * 1000:.0f} ms to first "
        f"query; host={host}; endpoint={endpoint_kind}; sslmode={sslmode}",
    )

    try:
        row = conn.execute(
            "SELECT ssl, version, cipher, bits FROM pg_stat_ssl "
            "WHERE pid = pg_backend_pid()"
        ).fetchone()
        if row and row[0]:
            report.add(
                "TLS",
                "PASS",
                f"{row[1]}, {row[2]}, {row[3]} bits",
            )
        elif "-pooler" in host:
            # The pooler terminates client TLS and connects to the compute over
            # loopback, so pg_stat_ssl on the pooled backend reports no TLS.
            direct_info = dict(info)
            direct_info["host"] = host.replace("-pooler", "")
            try:
                with psycopg.connect(
                    make_conninfo(**direct_info),
                    connect_timeout=10,
                    prepare_threshold=None,
                    autocommit=True,
                    application_name="aerogrid-wp02-tls-probe",
                ) as direct:
                    direct_row = direct.execute(
                        "SELECT ssl, version, cipher, bits FROM pg_stat_ssl "
                        "WHERE pid = pg_backend_pid()"
                    ).fetchone()
                if direct_row and direct_row[0]:
                    report.add(
                        "TLS",
                        "PASS",
                        f"pooled client connection requires sslmode={sslmode}; "
                        f"direct endpoint reports {direct_row[1]}, "
                        f"{direct_row[2]}, {direct_row[3]} bits",
                    )
                else:
                    report.add(
                        "TLS",
                        "WARN",
                        f"pooled client connection requires sslmode={sslmode}, "
                        "but the direct endpoint does not report TLS",
                    )
            except Exception as exc:  # noqa: BLE001
                report.add(
                    "TLS",
                    "WARN",
                    f"pooled connection enforces sslmode={sslmode}, but the direct "
                    f"endpoint check failed: {redact(exc)}",
                )
        else:
            report.add("TLS", "FAIL", "pg_stat_ssl reports no TLS on this connection")

        ident = conn.execute(
            "SELECT current_user, current_database(), current_setting('server_version'), "
            "current_setting('search_path'), coalesce(inet_server_addr()::text, 'local')"
        ).fetchone()
        report.add(
            "identity",
            "PASS",
            f"user={ident[0]}, database={ident[1]}, server={ident[2]}, "
            f"search_path={ident[3]}, server_addr={ident[4]}",
        )
        if ident[0] != WRITER_ROLE:
            report.add(
                "writer role",
                "WARN",
                f"expected {WRITER_ROLE}, connected as {ident[0]}",
            )

        schema_rows = conn.execute(
            "SELECT nspname, "
            "has_schema_privilege(current_user, nspname, 'USAGE'), "
            "has_schema_privilege(current_user, nspname, 'CREATE') "
            "FROM pg_namespace WHERE nspname = ANY(%s) ORDER BY nspname",
            (list(SCHEMAS),),
        ).fetchall()
        present = {row[0]: (row[1], row[2]) for row in schema_rows}
        missing = [name for name in SCHEMAS if name not in present]
        if missing:
            report.add(
                "schemas",
                "WARN",
                f"missing: {', '.join(missing)}; WP-04/WP-05 create them",
            )
        else:
            grants = ", ".join(
                f"{name}(usage={present[name][0]}, create={present[name][1]})"
                for name in SCHEMAS
            )
            report.add("schemas", "PASS", grants)

        try:
            conn.execute(
                "CREATE TEMP TABLE wp02_writer_probe ("
                "probe_id integer PRIMARY KEY, note text)"
            )
            conn.execute(
                "INSERT INTO wp02_writer_probe VALUES (1, 'wp-02 write proof')"
            )
            count = conn.execute("SELECT count(*) FROM wp02_writer_probe").fetchone()[0]
            conn.execute("DROP TABLE wp02_writer_probe")
            if count == 1:
                report.add("database write", "PASS", "temp table create/insert/select/drop")
            else:
                report.add("database write", "FAIL", f"unexpected row count {count}")
        except Exception as exc:  # noqa: BLE001
            report.add("database write", "FAIL", redact(exc))

        try:
            conn.execute("SET statement_timeout = '1000ms'")
            started = time.perf_counter()
            timed_out = False
            try:
                conn.execute("SELECT pg_sleep(3)")
            except psycopg.errors.QueryCanceled:
                timed_out = True
            elapsed_ms = (time.perf_counter() - started) * 1000
            if timed_out:
                report.add(
                    "statement timeout",
                    "PASS",
                    f"pg_sleep(3) cancelled after {elapsed_ms:.0f} ms with a 1 s timeout",
                )
            else:
                report.add("statement timeout", "FAIL", "slow query was not cancelled")
        except Exception as exc:  # noqa: BLE001
            report.add("statement timeout", "FAIL", redact(exc))
        finally:
            try:
                conn.execute("SET statement_timeout = '30s'")
            except Exception:  # noqa: BLE001
                pass

        size = conn.execute("SELECT pg_database_size(current_database())").fetchone()[0]
        if size > DB_FREE_LIMIT:
            report.add("database size", "FAIL", f"{human_bytes(size)} exceeds 1 GiB")
        elif size > DB_TARGET:
            report.add(
                "database size",
                "WARN",
                f"{human_bytes(size)} above the 500 MiB Phase 2 target",
            )
        else:
            report.add("database size", "PASS", f"{human_bytes(size)} of 1 GiB free tier")

        table_count = conn.execute(
            "SELECT count(*) FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = ANY(%s) "
            "AND c.relkind IN ('r', 'p', 'v', 'm', 'f')",
            (list(SCHEMAS),),
        ).fetchone()[0]
        report.add(
            "warehouse objects",
            "INFO",
            f"{table_count} tables/views in the three schemas; no production data expected",
        )

        staging = present.get("project_staging")
        can_create_staging = bool(staging and staging[1])
        table_exists = conn.execute(
            "SELECT to_regclass(%s) IS NOT NULL", (PROBE_TABLE,)
        ).fetchone()[0]
        if table_exists:
            state["probe_table"] = True
            report.add("read-only probe table", "PASS", f"{PROBE_TABLE} exists")
        elif can_create_staging:
            try:
                conn.execute(PROBE_TABLE_DDL)
                conn.execute(
                    f"INSERT INTO {PROBE_TABLE} (probe_id, note) "
                    "VALUES (1, 'WP-02 read-only access proof') "
                    "ON CONFLICT (probe_id) DO NOTHING"
                )
                conn.execute(f"GRANT USAGE ON SCHEMA project_staging TO {READER_ROLE}")
                conn.execute(f"GRANT SELECT ON {PROBE_TABLE} TO {READER_ROLE}")
                state["probe_table"] = True
                report.add(
                    "read-only probe table",
                    "PASS",
                    f"created {PROBE_TABLE} and granted SELECT to {READER_ROLE}",
                )
            except Exception as exc:  # noqa: BLE001
                report.add(
                    "read-only probe table",
                    "WARN",
                    "could not create/grant; run the owner snippet in docs/07 "
                    f"({redact(exc).splitlines()[0]})",
                )
        else:
            report.add(
                "read-only probe table",
                "WARN",
                f"{PROBE_TABLE} absent and the writer lacks CREATE on project_staging; "
                "run the owner snippet in docs/07",
            )

        started = time.perf_counter()
        try:
            warm, _, _ = connect(dsn)
            warm.close()
            report.add(
                "warm connection",
                "PASS",
                f"{(time.perf_counter() - started) * 1000:.0f} ms",
            )
        except Exception as exc:  # noqa: BLE001
            report.add("warm connection", "WARN", redact(exc))
    finally:
        conn.close()

    return state


def run_storage(report: Report) -> None:
    required = (
        "NEON_S3_ENDPOINT",
        "NEON_S3_REGION",
        "NEON_S3_BUCKET",
        "NEON_S3_ACCESS_KEY_ID",
        "NEON_S3_SECRET_ACCESS_KEY",
    )
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        report.add("storage credentials", "FAIL", f"missing: {', '.join(missing)}")
        return

    endpoint = os.environ["NEON_S3_ENDPOINT"].strip()
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"https://{endpoint}"
    bucket = os.environ["NEON_S3_BUCKET"].strip()

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=os.environ["NEON_S3_REGION"].strip() or None,
        aws_access_key_id=os.environ["NEON_S3_ACCESS_KEY_ID"].strip(),
        aws_secret_access_key=os.environ["NEON_S3_SECRET_ACCESS_KEY"].strip(),
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=30,
        ),
    )

    body = json.dumps(
        {
            "package": "WP-02",
            "purpose": "platform validation marker",
            "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
            "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "note": "non-sensitive scratch object; deleted after verification",
        },
        sort_keys=True,
    ).encode("utf-8")

    try:
        started = time.perf_counter()
        client.put_object(
            Bucket=bucket,
            Key=MARKER_KEY,
            Body=body,
            ContentType="application/json",
        )
        report.add(
            "storage write",
            "PASS",
            f"put {MARKER_KEY} ({len(body)} bytes) in {bucket} "
            f"in {(time.perf_counter() - started) * 1000:.0f} ms",
        )
    except (BotoCoreError, ClientError) as exc:
        report.add("storage write", "FAIL", redact(exc))
        return

    try:
        head = client.head_object(Bucket=bucket, Key=MARKER_KEY)
        report.add("storage head", "PASS", f"{head['ContentLength']} bytes")
    except (BotoCoreError, ClientError) as exc:
        report.add("storage head", "FAIL", redact(exc))

    try:
        obj = client.get_object(Bucket=bucket, Key=MARKER_KEY)
        stored = obj["Body"].read()
        if hashlib.sha256(stored).hexdigest() == hashlib.sha256(body).hexdigest():
            report.add("storage read-back", "PASS", "sha256 matches the written marker")
        else:
            report.add("storage read-back", "FAIL", "sha256 mismatch")
    except (BotoCoreError, ClientError) as exc:
        report.add("storage read-back", "FAIL", redact(exc))

    try:
        client.delete_object(Bucket=bucket, Key=MARKER_KEY)
        report.add("storage delete", "PASS", f"removed {MARKER_KEY}")
    except (BotoCoreError, ClientError) as exc:
        report.add("storage delete", "FAIL", redact(exc))
        return

    try:
        client.head_object(Bucket=bucket, Key=MARKER_KEY)
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code in ("404", "NoSuchKey", "NotFound"):
            report.add("storage cleanup", "PASS", "marker no longer exists")
        else:
            report.add("storage cleanup", "WARN", f"unexpected error code {code}")
    except BotoCoreError as exc:
        report.add("storage cleanup", "WARN", redact(exc))
    else:
        report.add("storage cleanup", "FAIL", "marker still exists after delete")

    try:
        total_bytes = 0
        object_count = 0
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=bucket,
            PaginationConfig={"PageSize": 1000, "MaxItems": 100000},
        ):
            for obj in page.get("Contents", []):
                object_count += 1
                total_bytes += int(obj.get("Size", 0))
        if total_bytes > BUCKET_FREE_LIMIT:
            report.add(
                "bucket size",
                "FAIL",
                f"{human_bytes(total_bytes)} exceeds the 5 GiB free tier",
            )
        elif total_bytes > BUCKET_TARGET:
            report.add(
                "bucket size",
                "WARN",
                f"{object_count} objects, {human_bytes(total_bytes)} above the "
                "2 GiB Phase 2 target",
            )
        else:
            report.add(
                "bucket size",
                "PASS",
                f"{object_count} objects, {human_bytes(total_bytes)} of 5 GiB free tier",
            )
    except (BotoCoreError, ClientError) as exc:
        report.add("bucket size", "WARN", redact(exc))

    report.add(
        "compute and egress quota",
        "INFO",
        "100 CU-hours and 5 GiB egress are console metrics; confirm in Neon after the "
        "first real run",
    )


def expect_denied(conn: psycopg.Connection, sql: str, cleanup: str | None) -> tuple[str, str]:
    try:
        conn.execute(sql)
    except psycopg.Error as exc:
        if exc.sqlstate == "42501":
            return "PASS", "rejected with SQLSTATE 42501"
        return (
            "FAIL",
            f"unexpected {exc.sqlstate}: {redact(exc).splitlines()[0]}",
        )
    else:
        if cleanup:
            try:
                conn.execute(cleanup)
            except psycopg.Error:
                pass
        return "FAIL", "statement succeeded; write privilege is present"


def run_reader(report: Report, state: dict[str, object]) -> None:
    dsn = os.environ.get("READONLY_DATABASE_URL", "").strip()
    if not dsn:
        report.add(
            "reader connection",
            "SKIP",
            "READONLY_DATABASE_URL is not set; run the manual reader check in docs/07",
        )
        return

    try:
        conn, connect_ms, _ = connect(dsn)
    except Exception as exc:  # noqa: BLE001
        report.add("reader connection", "FAIL", redact(exc))
        return

    try:
        user = conn.execute("SELECT current_user").fetchone()[0]
        if user != READER_ROLE:
            report.add(
                "reader connection",
                "FAIL",
                f"expected {READER_ROLE}, connected as {user}; negative checks skipped",
            )
            return
        report.add(
            "reader connection",
            "PASS",
            f"connected as {user} in {connect_ms * 1000:.0f} ms",
        )

        try:
            conn.execute("SELECT 1").fetchone()
            report.add("reader select", "PASS", "SELECT 1 succeeded")
        except Exception as exc:  # noqa: BLE001
            report.add("reader select", "FAIL", redact(exc))

        table_ready = bool(state.get("probe_table"))
        if not table_ready:
            exists = conn.execute(
                "SELECT to_regclass(%s) IS NOT NULL", (PROBE_TABLE,)
            ).fetchone()[0]
            table_ready = bool(exists)

        if table_ready:
            try:
                count = conn.execute(
                    f"SELECT count(*) FROM {PROBE_TABLE}"
                ).fetchone()[0]
                report.add(
                    "reader select probe table",
                    "PASS",
                    f"{count} row(s) visible in {PROBE_TABLE}",
                )
            except Exception as exc:  # noqa: BLE001
                report.add(
                    "reader select probe table",
                    "FAIL",
                    redact(exc),
                )
        else:
            report.add(
                "reader select probe table",
                "SKIP",
                f"{PROBE_TABLE} is absent; run the owner snippet in docs/07",
            )

        table_cases = ("reader insert", "reader update", "reader delete")
        for label, sql, cleanup in READER_DENIED_CASES:
            if not table_ready and label in table_cases:
                report.add(label, "SKIP", f"{PROBE_TABLE} is absent")
                continue
            status, evidence = expect_denied(conn, sql, cleanup)
            report.add(label, status, evidence)
            if status == "FAIL":
                break
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="WP-02 platform validation probe")
    parser.add_argument(
        "--mode",
        choices=("all", "writer", "reader"),
        default="all",
        help="writer covers database and storage; reader needs READONLY_DATABASE_URL",
    )
    args = parser.parse_args()

    report = Report()
    state: dict[str, object] = {}
    if args.mode in ("all", "writer"):
        state = run_writer(report)
        run_storage(report)
    if args.mode in ("all", "reader"):
        run_reader(report, state)

    summary = report.render()
    print()
    print(summary)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(summary + "\n")

    if report.failures():
        print("::error title=WP-02 platform validation::One or more checks failed")
        return 1
    if report.skipped():
        print(
            "::warning title=WP-02 platform validation::Proof is partial; "
            "see skipped checks"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
