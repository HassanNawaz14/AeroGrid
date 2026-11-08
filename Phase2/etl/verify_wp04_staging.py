"""WP-04 staging verification (Member B / approved CI or human-coordinated run).

Reads DATABASE_URL from the environment only. Never prints or logs credentials.
Applies WP-04 SQL files in order, reruns for idempotency, and reports only
non-secret evidence (tables, row counts, idempotency status).

Optional real-sample evidence:
  python -m etl.verify_wp04_staging --tartan-sample /path/to/real/1.csv
The sample is loaded twice inside a transaction that is rolled back, proving
insert/duplicate/reconciliation behavior without persisting test rows.

Usage (after setting DATABASE_URL in your shell, not in repo/chat):
  python -m etl.verify_wp04_staging          # from Phase2 with PYTHONPATH set
  python Phase2/etl/verify_wp04_staging.py   # from repo root
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running as a script from repo root.
PHASE2 = Path(__file__).resolve().parents[1]
if str(PHASE2) not in sys.path:
    sys.path.insert(0, str(PHASE2))

from etl.loaders import load_tartan
from etl.staging_writer import (
    LoadCounts,
    finish_etl_run,
    record_source_manifest,
    start_etl_run,
)

SQL_FILES = [
    PHASE2 / "sql" / "00_schemas.sql",
    PHASE2 / "sql" / "01_staging" / "01_source_manifest_run_reject_dq.sql",
    PHASE2 / "sql" / "01_staging" / "02_source_tables.sql",
]

EXPECTED_TABLES = [
    "dq_result",
    "etl_run_log",
    "source_manifest",
    "stg_adsb_position",
    "stg_airspace_zone",
    "stg_opensky_state",
    "stg_reject",
    "stg_restriction_snapshot",
    "stg_uas_position",
    "stg_weather_metar",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify WP-04 staging DDL and loaders.")
    parser.add_argument(
        "--tartan-sample",
        help="Path to a real Tartan KBTP CSV sample used for rollback-only load proof.",
    )
    parser.add_argument(
        "--source-file",
        help="Logical source object key/file name recorded in staging provenance.",
    )
    parser.add_argument("--expect-read", type=int)
    parser.add_argument("--expect-accepted", type=int)
    parser.add_argument("--expect-rejected", type=int)
    return parser.parse_args()


def _reconcile(label: str, counts: LoadCounts) -> None:
    if not counts.reconcile_ok():
        print(f"ERROR {label} counts do not reconcile: {counts.to_dict()}")
        raise SystemExit(1)
    print(f"{label} counts: {counts.to_dict()}")


def _sample_evidence(
    conn: object,
    *,
    sample_path: Path,
    source_file: str,
    expected: dict[str, int | None],
) -> None:
    manifest_id = record_source_manifest(
        conn,
        source_name="TARTAN",
        source_url="source-validation:sample",
        license_name="CC BY 4.0",
        attribution="TartanAviation",
        fetched_at=datetime.now(timezone.utc),
        file_path=sample_path,
        object_key=source_file,
        content_type="text/csv",
    )

    run1 = start_etl_run(conn, run_mode="validate", code_version="wp04-verify")
    counts1 = load_tartan(
        conn,
        sample_path,
        source_file=source_file,
        etl_run_id=run1,
        source_manifest_id=manifest_id,
    )
    finish_etl_run(
        conn,
        etl_run_id=run1,
        counts=counts1,
        status="SUCCESS" if counts1.rows_rejected == 0 else "PARTIAL",
    )
    _reconcile("sample pass1", counts1)

    run2 = start_etl_run(conn, run_mode="validate", code_version="wp04-verify")
    counts2 = load_tartan(
        conn,
        sample_path,
        source_file=source_file,
        etl_run_id=run2,
        source_manifest_id=manifest_id,
    )
    finish_etl_run(
        conn,
        etl_run_id=run2,
        counts=counts2,
        status="SUCCESS" if counts2.rows_rejected == 0 else "PARTIAL",
    )
    _reconcile("sample pass2", counts2)

    if counts2.rows_accepted != 0:
        print("ERROR idempotency failed: second load inserted rows")
        raise SystemExit(1)
    expected_duplicates = counts1.rows_accepted + counts1.rows_duplicate
    if counts2.rows_duplicate != expected_duplicates:
        print(
            "ERROR idempotency failed: expected "
            f"{expected_duplicates} duplicates, got {counts2.rows_duplicate}"
        )
        raise SystemExit(1)

    for name, value in expected.items():
        if value is not None and getattr(counts1, name) != value:
            print(
                f"ERROR sample pass1 {name}={getattr(counts1, name)} "
                f"does not match expected {value}"
            )
            raise SystemExit(1)

    print(
        "sample evidence PASS: pass2 accepted=0 "
        f"duplicates={counts2.rows_duplicate} rejected={counts2.rows_rejected} "
        f"rejects_by_reason={counts1.to_dict()['rejects_by_reason']}"
    )
    print("sample rows rolled back; no test data persisted")


def main() -> int:
    args = _parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set in this environment. Set it in your shell only.")
        return 2
    try:
        import psycopg  # type: ignore
    except ImportError:
        print('psycopg is not installed. Run: python -m pip install "psycopg[binary]>=3.2,<4"')
        return 2

    for path in SQL_FILES:
        if not path.is_file():
            print(f"Missing SQL file: {path}")
            return 2

    sample_path = Path(args.tartan_sample) if args.tartan_sample else None
    if sample_path is not None and not sample_path.is_file():
        print(f"Sample file not found: {sample_path}")
        return 2

    # Do not echo the URL. Connect with sslmode=require honored by the URL.
    with psycopg.connect(url, connect_timeout=15) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database(), version()")
            user, db, version = cur.fetchone()
            version_short = (version or "").split(",")[0]
            print(f"connected user={user} db={db} server={version_short}")

            cur.execute(
                """
                SELECT has_schema_privilege(current_user, 'project_staging', 'USAGE'),
                       has_schema_privilege(current_user, 'project_staging', 'CREATE')
                """
            )
            usage_ok, create_ok = cur.fetchone()
            if not (usage_ok and create_ok):
                print(
                    "preflight: FAILED; current_user lacks "
                    f"USAGE={usage_ok} CREATE={create_ok} on project_staging. "
                    "Run Phase2/sql/00_grants.sql as the project owner (neondb_owner) "
                    "in the Neon SQL Editor, then rerun this verifier."
                )
                return 3
            print("preflight: project_staging privileges OK")

            def apply(label: str) -> None:
                for path in SQL_FILES:
                    sql = path.read_text(encoding="utf-8")
                    try:
                        cur.execute(sql)
                    except Exception as exc:
                        conn.rollback()
                        print(f"{label}: FAILED on {path.name}: {exc.__class__.__name__}: {exc}")
                        print(
                            "Hint: DDL needs schema/database privileges. If role is aerogrid_etl, "
                            "a privileged role (Member A/human) must grant USAGE, CREATE on "
                            "project_staging or run WP-04 DDL once as owner, then rerun."
                        )
                        raise
                conn.commit()
                print(f"{label}: applied {len(SQL_FILES)} SQL files")

            apply("pass1")
            apply("pass2 (idempotency)")

            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'project_staging'
                ORDER BY table_name
                """
            )
            tables = [row[0] for row in cur.fetchall()]
            print(f"project_staging tables ({len(tables)}): {', '.join(tables)}")
            missing = [t for t in EXPECTED_TABLES if t not in tables]
            if missing:
                print(f"ERROR missing expected tables: {missing}")
                return 1
            print("all expected WP-04 staging tables present")

            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'project_staging'
                  AND table_name IN ('source_manifest','etl_run_log','stg_reject','dq_result',
                                     'stg_adsb_position','stg_uas_position','stg_weather_metar',
                                     'stg_airspace_zone','stg_restriction_snapshot','stg_opensky_state')
                ORDER BY table_name
                """
            )
            for (table,) in cur.fetchall():
                cur.execute(f'SELECT COUNT(*) FROM project_staging."{table}"')
                (count,) = cur.fetchone()
                print(f"count {table}={count}")

        if sample_path is not None:
            source_file = args.source_file or sample_path.name
            try:
                _sample_evidence(
                    conn,
                    sample_path=sample_path,
                    source_file=source_file,
                    expected={
                        "rows_read": args.expect_read,
                        "rows_accepted": args.expect_accepted,
                        "rows_rejected": args.expect_rejected,
                    },
                )
            finally:
                conn.rollback()
        else:
            print(
                "sample load skipped (no --tartan-sample). DDL evidence only; "
                "run again with a real sample for loader/idempotency evidence."
            )

    print("WP-04 verification PASS (non-secret evidence only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
