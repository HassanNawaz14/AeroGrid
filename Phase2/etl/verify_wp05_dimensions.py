"""WP-05 dimension verification (Member C / approved CI or human-coordinated run).

Reads DATABASE_URL from the environment only. Never prints or logs credentials.
Applies the dimension DDL + seed SQL in order, reruns for idempotency, and reports
only non-secret evidence (tables, row counts, unknown members, duplicate-natural-key
checks, FK-target checks, reader access).

Usage (after setting DATABASE_URL in your shell, not in repo/chat):
  python -m etl.verify_wp05_dimensions          # from Phase2 with PYTHONPATH set
  python Phase2/etl/verify_wp05_dimensions.py   # from repo root
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PHASE2 = Path(__file__).resolve().parents[1]
if str(PHASE2) not in sys.path:
    sys.path.insert(0, str(PHASE2))

SQL_FILES = [
    PHASE2 / "sql" / "00_schemas.sql",
    PHASE2 / "sql" / "02_dimensions" / "01_dimensions.sql",
    PHASE2 / "sql" / "02_dimensions" / "02_seed.sql",
]

DIMENSIONS = [
    "dim_time",
    "dim_site",
    "dim_vehicle",
    "dim_spatial_grid",
    "dim_weather",
    "dim_airspace_zone",
]

NATURAL_KEYS = {
    "dim_time": ["hour_ts"],
    "dim_site": ["site_code"],
    "dim_vehicle": ["source_system", "source_entity_id"],
    "dim_spatial_grid": ["grid_cell_id"],
    "dim_weather": ["station_icao", "observation_ts"],
    "dim_airspace_zone": ["source_system", "source_object_id"],
}

READER_ACCESS_SQL = """
SELECT NOT EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'project_dw'
      AND c.relkind IN ('r','p')
      AND NOT has_table_privilege('aerogrid_reader', c.oid, 'SELECT')
)
"""


def _parse_args() -> object:
    import argparse
    parser = argparse.ArgumentParser(description="Verify WP-05 dimensions DDL and seeds.")
    return parser.parse_args()


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
                        raise
                conn.commit()
                print(f"{label}: applied {len(SQL_FILES)} SQL files")

            apply("pass1")
            apply("pass2 (idempotency)")

            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'project_dw'
                ORDER BY table_name
                """
            )
            tables = [row[0] for row in cur.fetchall()]
            missing = [t for t in DIMENSIONS if t not in tables]
            if missing:
                print(f"ERROR missing expected dimensions: {missing}")
                return 1
            print(f"project_dw tables ({len(tables)}): {', '.join(tables)}")
            print("all expected WP-05 dimension tables present")

            # Unknown member (-1) present in every dimension.
            for dim in DIMENSIONS:
                cur.execute(
                    f'SELECT COUNT(*) FROM project_dw."{dim}" '
                    f"WHERE {_pk_col(dim)} = -1"
                )
                (count,) = cur.fetchone()
                if count != 1:
                    print(f"ERROR {dim} unknown-member count={count} (expected 1)")
                    return 1
                cur.execute(f'SELECT COUNT(*) FROM project_dw."{dim}"')
                (total,) = cur.fetchone()
                print(f"count {dim}={total} unknown_member(-1)=1")

            # No duplicate natural keys.
            for dim, keys in NATURAL_KEYS.items():
                cols = ", ".join(keys)
                cur.execute(
                    f"SELECT {cols}, COUNT(*) FROM project_dw.\"{dim}\" "
                    f"GROUP BY {cols} HAVING COUNT(*) > 1 LIMIT 1"
                )
                dup = cur.fetchone()
                if dup:
                    print(f"ERROR duplicate natural key in {dim}: {dup}")
                    return 1
            print("no duplicate natural keys in any dimension")

            # FK targets exist: every dimension FK to dim_site resolves.
            for dim in ("dim_spatial_grid", "dim_weather", "dim_airspace_zone"):
                cur.execute(
                    f"SELECT COUNT(*) FROM project_dw.\"{dim}\" d "
                    f"LEFT JOIN project_dw.dim_site s ON d.site_key = s.site_key "
                    f"WHERE s.site_key IS NULL"
                )
                (orphan,) = cur.fetchone()
                if orphan:
                    print(f"ERROR {dim} has {orphan} rows with unresolved site_key")
                    return 1
            print("all dim_site FK targets exist")

            # Reader access check (the WP-05 acceptance query).
            cur.execute(READER_ACCESS_SQL)
            (reader_ok,) = cur.fetchone()
            if not reader_ok:
                print("ERROR aerogrid_reader lacks SELECT on a project_dw table")
                return 1
            print("reader SELECT access: true on all project_dw tables")

    print("WP-05 verification PASS (non-secret evidence only)")
    return 0


def _pk_col(dim: str) -> str:
    return {
        "dim_time": "time_key",
        "dim_site": "site_key",
        "dim_vehicle": "vehicle_key",
        "dim_spatial_grid": "grid_key",
        "dim_weather": "weather_key",
        "dim_airspace_zone": "zone_key",
    }[dim]


if __name__ == "__main__":
    raise SystemExit(main())
