"""WP-07 protected-warehouse verifier. Default is full transaction rollback.

Do NOT run this against Neon from a laptop. Run under the repository's approved
GitHub Actions ``warehouse`` environment, using its DATABASE_URL secret.
--apply is allowed only inside CI and only after explicit project-owner approval.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from types import SimpleNamespace

from etl.derived_facts import ALGORITHM_VERSION, derive_and_insert
from etl.staging_writer import finish_etl_run, start_etl_run

SQL_DIR = Path(__file__).resolve().parents[1] / "sql" / "03_facts"
GRID_SQL_FILE = SQL_DIR / "05_wp07_seed_grid_and_backfill.sql"
DERIVED_SQL_FILE = SQL_DIR / "02_derived_facts.sql"


def _scalar(conn, sql: str) -> int:
    cur = conn.cursor()
    cur.execute(sql)
    return int(cur.fetchone()[0])


def validate(conn) -> dict[str, int]:
    """Fatal only on integrity failures. No minimum derived row count is invented."""
    checks = {
        "invalid_encounter_pairs": """
            SELECT COUNT(*) FROM project_dw.fact_close_encounter
            WHERE vehicle_key_1 >= vehicle_key_2
        """,
        "encounter_missing_evidence": """
            SELECT COUNT(*) FROM project_dw.fact_close_encounter e
            LEFT JOIN project_dw.fact_vehicle_tracking a ON a.tracking_id = e.min_tracking_id_1
            LEFT JOIN project_dw.fact_vehicle_tracking b ON b.tracking_id = e.min_tracking_id_2
            WHERE a.tracking_id IS NULL OR b.tracking_id IS NULL
               OR a.vehicle_key <> e.vehicle_key_1 OR b.vehicle_key <> e.vehicle_key_2
               OR a.site_key <> e.site_key OR b.site_key <> e.site_key
        """,
        "incorrect_severity": """
            SELECT COUNT(*) FROM project_dw.fact_close_encounter
            WHERE algorithm_version = 'wp07-v1' AND (
                (risk_severity_class = 'SEVERE' AND NOT
                    (min_horizontal_sep_nm < 0.5 AND min_vertical_sep_ft < 500))
             OR (risk_severity_class = 'PROXIMITY' AND NOT
                    (min_horizontal_sep_nm < 1 AND min_vertical_sep_ft < 1000
                     AND NOT (min_horizontal_sep_nm < 0.5 AND min_vertical_sep_ft < 500)))
             OR risk_severity_class NOT IN ('SEVERE','PROXIMITY')
            )
        """,
        "occupancy_invalid_counts": """
            SELECT COUNT(*) FROM project_dw.fact_airspace_occupancy
            WHERE active_vehicle_count < 0
               OR active_vehicle_count > supporting_tracking_count
               OR total_occupancy_minutes < 0
        """,
        "occupancy_duplicate_keys": """
            SELECT COUNT(*) FROM (
                SELECT 1 FROM project_dw.fact_airspace_occupancy
                GROUP BY time_key, grid_key, algorithm_version HAVING COUNT(*) > 1
            ) t
        """,
        "encounter_duplicate_keys": """
            SELECT COUNT(*) FROM (
                SELECT 1 FROM project_dw.fact_close_encounter
                GROUP BY vehicle_key_1, vehicle_key_2, start_ts, algorithm_version
                HAVING COUNT(*) > 1
            ) t
        """,
        "restriction_missing_source": """
            SELECT COUNT(*) FROM project_dw.fact_restriction_activation
            WHERE source_record_id IS NULL OR source_snapshot_ts IS NULL
        """,
    }
    results = {key: _scalar(conn, sql) for key, sql in checks.items()}
    failing = {k: v for k, v in results.items() if v != 0}
    if failing:
        raise AssertionError(f"WP-07 integrity failures: {failing}")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Persist only from explicitly approved protected GitHub Actions")
    args = parser.parse_args(argv)
    if args.apply and os.getenv("GITHUB_ACTIONS") != "true":
        parser.error("--apply requires approved GitHub Actions warehouse environment")
    url = os.getenv("DATABASE_URL")
    if not url:
        parser.error("DATABASE_URL must be a GitHub Actions environment secret")
    try:
        import psycopg
    except ImportError:
        parser.error("Install psycopg[binary] in the approved CI job")

    with psycopg.connect(url, connect_timeout=15) as conn:
        try:
            # DDL and all verifications share one transaction; rollback on failures.
            with conn.cursor() as cur:
                cur.execute("SET LOCAL statement_timeout = '10min'")
                cur.execute(GRID_SQL_FILE.read_text(encoding="utf-8"))
                cur.execute(DERIVED_SQL_FILE.read_text(encoding="utf-8"))
            run_id = start_etl_run(
                conn, run_mode="initial" if args.apply else "validate",
                code_version=os.getenv("GITHUB_SHA", "wp07-verification")[:40]
            )
            pass1 = derive_and_insert(conn, etl_run_id=run_id)
            pass2 = derive_and_insert(conn, etl_run_id=run_id)
            if any(pass2[name]["inserted_rows"] for name in ("encounters", "occupancy", "restrictions")):
                raise AssertionError("idempotency failure: second pass inserted duplicates")
            quality = validate(conn)
            fact_count = sum(pass1[name]["inserted_rows"]
                             for name in ("encounters", "occupancy", "restrictions"))
            total_source = (pass1["inputs"]["accepted_tracking_rows"]
                            + pass1["inputs"]["accepted_snapshot_rows"])
            counts = SimpleNamespace(rows_read=total_source, rows_accepted=total_source,
                                     rows_rejected=0, rows_duplicate=0)
            finish_etl_run(conn, etl_run_id=run_id, counts=counts,
                           status="SUCCESS", facts_inserted=fact_count)
            # These summaries contain no raw telemetry, secrets, or identifying data.
            print(f"algorithm_version={ALGORITHM_VERSION}")
            print(f"pass1={pass1}")
            print(f"pass2={pass2}")
            print(f"checks={quality}")
            if args.apply:
                conn.commit()
                print("WP07 PASS; committed approved derived facts")
            else:
                conn.rollback()
                print("WP07 PASS; ROLLBACK (no persistent DDL or fact writes)")
            return 0
        except Exception as exc:
            conn.rollback()
            # Avoid printing DB exceptions because server diagnostics may contain
            # connection parameters or raw payloads. The known policy blocker is safe.
            reason = (
                "NO_VERIFIED_AIRBORNE/NO_REAL_GRID" if "NO_VERIFIED_AIRBORNE" in str(exc)
                and "NO_REAL_GRID" in str(exc)
                else "NO_VERIFIED_AIRBORNE" if "NO_VERIFIED_AIRBORNE" in str(exc)
                else "NO_REAL_GRID" if "NO_REAL_GRID" in str(exc)
                else type(exc).__name__
            )
            print(f"WP07 FAIL; transaction rolled back; reason={reason}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
