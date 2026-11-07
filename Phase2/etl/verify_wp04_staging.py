"""WP-04 staging DDL verification (Member B / approved CI or human-coordinated run).

Reads DATABASE_URL from the environment only. Never prints or logs credentials.
Applies WP-04 SQL files in order, reruns for idempotency, and reports only
non-secret evidence (tables, row counts, idempotency status).

Usage (after setting DATABASE_URL in your shell, not in repo/chat):
  python -m etl.verify_wp04_staging          # from Phase2 with PYTHONPATH set
  python Phase2/etl/verify_wp04_staging.py   # from repo root
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running as a script from repo root.
PHASE2 = Path(__file__).resolve().parents[1]
if str(PHASE2) not in sys.path:
    sys.path.insert(0, str(PHASE2))

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


def main() -> int:
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

    # Do not echo the URL. Connect with sslmode=require honored by the URL.
    with psycopg.connect(url, connect_timeout=15) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database(), version()")
            user, db, version = cur.fetchone()
            version_short = (version or "").split(",")[0]
            print(f"connected user={user} db={db} server={version_short}")

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

    print("WP-04 DDL verification PASS (non-secret evidence only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
