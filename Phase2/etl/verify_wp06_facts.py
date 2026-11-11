"""WP-06 tracking and flight journey verification (Member D / CI warehouse run).

Downloads real ``samples/kbtp/01-01-22/1.csv`` from the ``aerogrid-raw`` Neon Object
Storage bucket (or uses an operator-supplied ``--tartan-sample``), verifies its exact
SHA-256 digest before touching the warehouse, applies the idempotent real dimension
seed and Phase 2 fact DDL, runs staging + tracking + journey loads twice to prove
reconciliation and idempotency, checks zero FK orphans and reader SELECT privileges,
and commits only when all checks pass (or rolls back on failure or ``--dry-run``).

Reads ``DATABASE_URL`` and ``NEON_S3_*`` strictly from environment variables. Never
prints secrets, connection strings, or raw telemetry rows.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE2 = Path(__file__).resolve().parents[1]
if str(PHASE2) not in sys.path:
    sys.path.insert(0, str(PHASE2))

from etl.facts import (
    ALGORITHM_VERSION,
    DEFAULT_BATCH_SIZE,
    DEFAULT_GAP_SPLIT_SEC,
    FactLoadCounts,
    JourneyLoadCounts,
    load_tartan_flight_journeys,
    load_tartan_tracking_facts,
)
from etl.loaders import load_tartan
from etl.staging_writer import (
    LoadCounts,
    finish_etl_run,
    record_source_manifest,
    start_etl_run,
)

EXPECTED_TARTAN_OBJECT_KEY = "samples/kbtp/01-01-22/1.csv"
EXPECTED_TARTAN_SHA256 = (
    "86342d09e5004102d765b82d04d16b43b6f15f2e7d829bfbde7909187d08a762"
)
TARTAN_SOURCE_URL = (
    "https://airlab-cloud.andrew.cmu.edu:8080/swift/v1/"
    "AUTH_ac8533a83cff4d48bc8c608ad222d330/tartanaviation-adsb/kbtp/raw/2022.zip"
)
TARTAN_LICENSE = "CC BY 4.0"
TARTAN_ATTRIBUTION = (
    "Patrikar et al., Scientific Data 12:468 (2025), DOI 10.1038/s41597-025-04775-6; "
    "TartanAviation"
)
MIN_TOTAL_FACTS = 10_000

SQL_FILES = [
    PHASE2 / "sql" / "00_schemas.sql",
    PHASE2 / "sql" / "03_facts" / "01_facts.sql",
]

DIMENSION_SEED_SQL = PHASE2 / "sql" / "02_dimensions" / "03_seed_real.sql"

DIM_TABLES = (
    "dim_time",
    "dim_site",
    "dim_vehicle",
    "dim_spatial_grid",
    "dim_weather",
    "dim_airspace_zone",
)

FACT_TABLES = (
    "fact_vehicle_tracking",
    "fact_flight_journey",
)

REQUIRED_STAGING_TABLES = (
    "source_manifest",
    "etl_run_log",
    "stg_reject",
    "stg_adsb_position",
)

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

S3_ENV_KEYS = (
    "NEON_S3_ENDPOINT",
    "NEON_S3_REGION",
    "NEON_S3_BUCKET",
    "NEON_S3_ACCESS_KEY_ID",
    "NEON_S3_SECRET_ACCESS_KEY",
)

SECRET_ENV_KEYS = (
    "DATABASE_URL",
    "READONLY_DATABASE_URL",
    "NEON_S3_ACCESS_KEY_ID",
    "NEON_S3_SECRET_ACCESS_KEY",
)

DSN_PATTERN = re.compile(r"postgres(?:ql)?://[^\s'\"]+", re.IGNORECASE)


def redact_secrets(value: object) -> str:
    """Redact PostgreSQL URIs and secret env values before printing logs/errors."""
    text = DSN_PATTERN.sub("postgresql://***", str(value))
    for name in SECRET_ENV_KEYS:
        secret = os.environ.get(name, "")
        if secret and len(secret) >= 4:
            text = text.replace(secret, "***")
    return text


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify WP-06 core tracking and flight journey facts."
    )
    parser.add_argument(
        "--tartan-sample",
        help="Optional local path to real kbtp/01-01-22/1.csv (downloads from S3 if omitted).",
    )
    parser.add_argument(
        "--object-key",
        default=EXPECTED_TARTAN_OBJECT_KEY,
        help="Object-storage key for source provenance and S3 fetch.",
    )
    parser.add_argument(
        "--expected-sha256",
        default=EXPECTED_TARTAN_SHA256,
        help="Expected SHA-256 digest; verification fails closed on mismatch.",
    )
    parser.add_argument(
        "--gap-split-sec",
        type=int,
        default=DEFAULT_GAP_SPLIT_SEC,
        help="Maximum intra-journey gap in seconds before splitting.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Batch size for multi-row inserts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run all loads and assertions inside a rolled-back transaction.",
    )
    return parser.parse_args()


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(path: Path, expected_sha256: str) -> str:
    actual = compute_sha256(path).lower()
    expected = expected_sha256.strip().lower()
    if actual != expected:
        raise ValueError(
            f"SHA-256 mismatch for {path.name}: expected {expected}, got {actual}"
        )
    return actual


def resolve_s3_config_from_env() -> dict[str, str]:
    missing = [name for name in S3_ENV_KEYS if not os.environ.get(name, "").strip()]
    if missing:
        raise RuntimeError(
            "Missing required object-storage environment variable(s): "
            + ", ".join(missing)
        )
    endpoint = os.environ["NEON_S3_ENDPOINT"].strip()
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"https://{endpoint}"
    return {
        "endpoint": endpoint,
        "region": os.environ["NEON_S3_REGION"].strip(),
        "bucket": os.environ["NEON_S3_BUCKET"].strip(),
        "access_key_id": os.environ["NEON_S3_ACCESS_KEY_ID"].strip(),
        "secret_access_key": os.environ["NEON_S3_SECRET_ACCESS_KEY"].strip(),
    }


def download_s3_object(
    *,
    bucket: str,
    endpoint: str,
    region: str,
    access_key_id: str,
    secret_access_key: str,
    object_key: str,
    dest_path: Path,
) -> Path:
    import boto3  # type: ignore
    from botocore.config import Config  # type: ignore

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region or None,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=15,
            read_timeout=60,
        ),
    )
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, object_key, str(dest_path))
    return dest_path


def check_preflight(cur: Any) -> list[str]:
    """Verify required schemas, tables, privileges, and Member C real dimension rows."""
    errors: list[str] = []

    for schema in ("project_staging", "project_dw"):
        cur.execute(
            """
            SELECT has_schema_privilege(current_user, %s, 'USAGE'),
                   has_schema_privilege(current_user, %s, 'CREATE')
            """,
            (schema, schema),
        )
        usage_ok, create_ok = cur.fetchone()
        if not (usage_ok and create_ok):
            errors.append(
                f"current_user lacks USAGE={usage_ok} CREATE={create_ok} on {schema}"
            )

    if errors:
        return errors

    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'project_staging'
        """
    )
    stg_tables = {row[0] for row in cur.fetchall()}
    missing_stg = [t for t in REQUIRED_STAGING_TABLES if t not in stg_tables]
    if missing_stg:
        errors.append(f"missing project_staging table(s): {missing_stg}")

    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'project_dw'
        """
    )
    dw_tables = {row[0] for row in cur.fetchall()}
    missing_dims = [t for t in DIM_TABLES if t not in dw_tables]
    if missing_dims:
        errors.append(f"missing project_dw dimension table(s): {missing_dims}")

    if errors:
        return errors

    cur.execute("SELECT COUNT(*) FROM project_dw.dim_time WHERE time_key <> -1")
    (real_hours,) = cur.fetchone()
    if int(real_hours) < 100:
        errors.append(
            f"dim_time has {real_hours} non-(-1) rows; expected >= 100 from WP-05 seed"
        )

    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_dw.dim_site
        WHERE site_key <> -1 AND UPPER(site_code) = 'KBTP'
        """
    )
    (kbtp_count,) = cur.fetchone()
    if int(kbtp_count) < 1:
        errors.append("dim_site is missing required site_code='KBTP'")

    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_dw.dim_vehicle
        WHERE vehicle_key <> -1
          AND UPPER(source_system) IN ('TARTAN', 'SRC-TARTAN')
        """
    )
    (tartan_vehicles,) = cur.fetchone()
    if int(tartan_vehicles) < 1:
        errors.append(
            "project_dw.dim_vehicle has 0 real Tartan rows (only -1 unknown member); "
            "apply Phase2/sql/02_dimensions/03_seed_real.sql (WP-05) before "
            "WP-06 verification"
        )

    return errors


def _assert_reconcile(label: str, counts: LoadCounts | FactLoadCounts | JourneyLoadCounts) -> None:
    if not counts.reconcile_ok():
        raise AssertionError(f"{label} counts failed reconciliation: {counts.to_dict()}")


def run_db_assertions(cur: Any, *, source_file: str) -> dict[str, Any]:
    """Execute independent warehouse checks after loads succeed."""
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'project_dw'
        ORDER BY table_name
        """
    )
    dw_tables = [row[0] for row in cur.fetchall()]
    missing_facts = [t for t in FACT_TABLES if t not in dw_tables]
    if missing_facts:
        raise AssertionError(f"missing expected fact tables: {missing_facts}")

    counts: dict[str, int] = {}
    for table in (*DIM_TABLES, *FACT_TABLES):
        cur.execute(f'SELECT COUNT(*) FROM project_dw."{table}"')
        counts[table] = int(cur.fetchone()[0])

    total_facts = counts["fact_vehicle_tracking"] + counts["fact_flight_journey"]
    if counts["fact_vehicle_tracking"] <= 0:
        raise AssertionError("fact_vehicle_tracking has 0 rows")
    if counts["fact_flight_journey"] <= 0:
        raise AssertionError("fact_flight_journey has 0 rows")
    if total_facts < MIN_TOTAL_FACTS:
        raise AssertionError(
            f"total facts={total_facts} is below required minimum {MIN_TOTAL_FACTS}"
        )

    # Natural-key uniqueness on both facts
    for fact_table in FACT_TABLES:
        cur.execute(
            f"""
            SELECT source_system, source_record_id, COUNT(*)
            FROM project_dw."{fact_table}"
            GROUP BY source_system, source_record_id
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
        dup = cur.fetchone()
        if dup:
            raise AssertionError(f"duplicate natural key in {fact_table}: {dup}")

    # FK orphan checks (every dimension + etl_run_log)
    orphan_queries = {
        "tracking_time": (
            "SELECT COUNT(*) FROM project_dw.fact_vehicle_tracking f "
            "LEFT JOIN project_dw.dim_time d ON f.time_key = d.time_key WHERE d.time_key IS NULL"
        ),
        "tracking_site": (
            "SELECT COUNT(*) FROM project_dw.fact_vehicle_tracking f "
            "LEFT JOIN project_dw.dim_site d ON f.site_key = d.site_key WHERE d.site_key IS NULL"
        ),
        "tracking_vehicle": (
            "SELECT COUNT(*) FROM project_dw.fact_vehicle_tracking f "
            "LEFT JOIN project_dw.dim_vehicle d ON f.vehicle_key = d.vehicle_key WHERE d.vehicle_key IS NULL"
        ),
        "tracking_grid": (
            "SELECT COUNT(*) FROM project_dw.fact_vehicle_tracking f "
            "LEFT JOIN project_dw.dim_spatial_grid d ON f.grid_key = d.grid_key WHERE d.grid_key IS NULL"
        ),
        "tracking_weather": (
            "SELECT COUNT(*) FROM project_dw.fact_vehicle_tracking f "
            "LEFT JOIN project_dw.dim_weather d ON f.weather_key = d.weather_key WHERE d.weather_key IS NULL"
        ),
        "tracking_etl_run": (
            "SELECT COUNT(*) FROM project_dw.fact_vehicle_tracking f "
            "LEFT JOIN project_staging.etl_run_log r ON f.etl_run_id = r.etl_run_id WHERE r.etl_run_id IS NULL"
        ),
        "journey_vehicle": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_dw.dim_vehicle d ON f.vehicle_key = d.vehicle_key WHERE d.vehicle_key IS NULL"
        ),
        "journey_site": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_dw.dim_site d ON f.site_key = d.site_key WHERE d.site_key IS NULL"
        ),
        "journey_start_time": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_dw.dim_time d ON f.start_time_key = d.time_key WHERE d.time_key IS NULL"
        ),
        "journey_end_time": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_dw.dim_time d ON f.end_time_key = d.time_key WHERE d.time_key IS NULL"
        ),
        "journey_origin_grid": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_dw.dim_spatial_grid d ON f.origin_grid_key = d.grid_key WHERE d.grid_key IS NULL"
        ),
        "journey_destination_grid": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_dw.dim_spatial_grid d ON f.destination_grid_key = d.grid_key WHERE d.grid_key IS NULL"
        ),
        "journey_etl_run": (
            "SELECT COUNT(*) FROM project_dw.fact_flight_journey f "
            "LEFT JOIN project_staging.etl_run_log r ON f.etl_run_id = r.etl_run_id WHERE r.etl_run_id IS NULL"
        ),
    }
    orphans: dict[str, int] = {}
    for label, sql in orphan_queries.items():
        cur.execute(sql)
        n = int(cur.fetchone()[0])
        orphans[label] = n
        if n != 0:
            raise AssertionError(f"FK orphan check failed for {label}: count={n}")

    # Required dimensions must never use -1
    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_dw.fact_vehicle_tracking
        WHERE time_key = -1 OR site_key = -1 OR vehicle_key = -1
        """
    )
    req_tracking_unknown = int(cur.fetchone()[0])
    if req_tracking_unknown != 0:
        raise AssertionError(
            f"fact_vehicle_tracking used -1 on required dim in {req_tracking_unknown} rows"
        )

    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_dw.fact_flight_journey
        WHERE vehicle_key = -1 OR site_key = -1 OR start_time_key = -1 OR end_time_key = -1
        """
    )
    req_journey_unknown = int(cur.fetchone()[0])
    if req_journey_unknown != 0:
        raise AssertionError(
            f"fact_flight_journey used -1 on required dim in {req_journey_unknown} rows"
        )

    # Optional -1 usage counters
    cur.execute(
        """
        SELECT
            COUNT(*) FILTER (WHERE grid_key = -1),
            COUNT(*) FILTER (WHERE weather_key = -1)
        FROM project_dw.fact_vehicle_tracking
        """
    )
    tracking_unk_grid, tracking_unk_weather = (int(v) for v in cur.fetchone())

    # Exact staging-to-tracking reconciliation for the target file
    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_staging.stg_adsb_position
        WHERE UPPER(source_system) = 'TARTAN'
          AND reject_reason IS NULL
          AND raw_file = %s
        """,
        (source_file,),
    )
    stg_accepted = int(cur.fetchone()[0])

    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_dw.fact_vehicle_tracking
        WHERE UPPER(source_system) = 'TARTAN'
          AND source_file = %s
        """,
        (source_file,),
    )
    fact_tracking_for_file = int(cur.fetchone()[0])

    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_staging.stg_adsb_position s
        LEFT JOIN project_dw.fact_vehicle_tracking f
          ON f.source_system = s.source_system
         AND f.source_record_id = s.source_record_id
        WHERE UPPER(s.source_system) = 'TARTAN'
          AND s.reject_reason IS NULL
          AND s.raw_file = %s
          AND f.tracking_id IS NULL
        """,
        (source_file,),
    )
    unmatched_staging = int(cur.fetchone()[0])

    if stg_accepted <= 0:
        raise AssertionError(f"accepted staging rows <= 0 for {source_file}: {stg_accepted}")
    if fact_tracking_for_file != stg_accepted:
        raise AssertionError(
            f"tracking count mismatch for {source_file}: fact={fact_tracking_for_file} != staging_accepted={stg_accepted}"
        )
    if unmatched_staging != 0:
        raise AssertionError(
            f"unmatched accepted staging rows for {source_file}: {unmatched_staging}"
        )

    # Reader SELECT privilege across every table in project_dw
    cur.execute(READER_ACCESS_SQL)
    (reader_ok,) = cur.fetchone()
    if not reader_ok:
        raise AssertionError("aerogrid_reader lacks SELECT on a project_dw table")

    return {
        "dw_tables": dw_tables,
        "counts": counts,
        "total_facts": total_facts,
        "orphan_total": sum(orphans.values()),
        "stg_accepted_for_file": stg_accepted,
        "fact_tracking_for_file": fact_tracking_for_file,
        "unmatched_staging_for_file": unmatched_staging,
        "tracking_unknown_grid_count": tracking_unk_grid,
        "tracking_unknown_weather_count": tracking_unk_weather,
        "reader_select_ok": bool(reader_ok),
    }


def _write_step_summary(lines: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> int:
    args = _parse_args()
    if args.batch_size < 1:
        print(f"ERROR --batch-size must be >= 1, got {args.batch_size}")
        return 2
    if args.gap_split_sec < 1:
        print(f"ERROR --gap-split-sec must be >= 1, got {args.gap_split_sec}")
        return 2
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set in this environment. Set it in your shell/CI only.")
        return 2
    try:
        import psycopg  # type: ignore
    except ImportError:
        print('psycopg is not installed. Run: python -m pip install "psycopg[binary]>=3.2,<4"')
        return 2

    for path in (*SQL_FILES, DIMENSION_SEED_SQL):
        if not path.is_file():
            print(f"Missing SQL file: {path}")
            return 2

    local_sample = Path(args.tartan_sample) if args.tartan_sample else None
    if local_sample is not None and not local_sample.is_file():
        print(f"Sample file not found: {local_sample}")
        return 2

    if local_sample is None:
        try:
            s3_cfg = resolve_s3_config_from_env()
        except RuntimeError as exc:
            print(f"preflight: FAILED; {redact_secrets(exc)}")
            return 2
    else:
        s3_cfg = None

    try:
        conn_cm = psycopg.connect(url, connect_timeout=15)
    except Exception as exc:
        print(
            f"ERROR warehouse connection failed: {exc.__class__.__name__}: "
            f"{redact_secrets(exc)}"
        )
        return 2

    with conn_cm as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database(), version()")
            user, db, version = cur.fetchone()
            version_short = (version or "").split(",")[0]
            print(f"connected user={user} db={db} server={version_short}")

            cur.execute("SELECT to_regclass('project_dw.dim_vehicle') IS NOT NULL")
            (dim_vehicle_exists,) = cur.fetchone()
            if dim_vehicle_exists:
                try:
                    cur.execute(DIMENSION_SEED_SQL.read_text(encoding="utf-8"))
                    conn.commit()
                except Exception as exc:
                    conn.rollback()
                    print(
                        f"dimension seed: FAILED on {DIMENSION_SEED_SQL.name}: "
                        f"{exc.__class__.__name__}: {redact_secrets(exc)}"
                    )
                    return 2
                print(f"dimension seed: applied {DIMENSION_SEED_SQL.name}")
            else:
                print(
                    "dimension seed: skipped; project_dw.dim_vehicle is absent "
                    "(run the WP-05 dimensions workflow first)"
                )

            preflight_errors = check_preflight(cur)
            if preflight_errors:
                for err in preflight_errors:
                    print(f"preflight: FAILED; {err}")
                return 3
            print("preflight: schema privileges, dims, and real Tartan vehicles OK")

            def apply_ddl(label: str) -> None:
                for path in SQL_FILES:
                    sql = path.read_text(encoding="utf-8")
                    try:
                        cur.execute(sql)
                    except Exception as exc:
                        conn.rollback()
                        print(
                            f"{label}: FAILED on {path.name}: {exc.__class__.__name__}: "
                            f"{redact_secrets(exc)}"
                        )
                        raise
                conn.commit()
                print(f"{label}: applied {len(SQL_FILES)} SQL files")

            apply_ddl("ddl pass1")
            apply_ddl("ddl pass2 (idempotency)")

        with tempfile.TemporaryDirectory(prefix="wp06_tartan_") as tmp_dir:
            try:
                if local_sample is not None:
                    sample_path = local_sample
                    source_key = args.object_key
                    source_url = "local-operator-verified-sample"
                else:
                    assert s3_cfg is not None
                    sample_path = Path(tmp_dir) / Path(args.object_key).name
                    source_key = args.object_key
                    source_url = TARTAN_SOURCE_URL
                    print(
                        f"fetching s3://{s3_cfg['bucket']}/{source_key} "
                        f"(temporary local path, deleted after run)"
                    )
                    download_s3_object(
                        bucket=s3_cfg["bucket"],
                        endpoint=s3_cfg["endpoint"],
                        region=s3_cfg["region"],
                        access_key_id=s3_cfg["access_key_id"],
                        secret_access_key=s3_cfg["secret_access_key"],
                        object_key=source_key,
                        dest_path=sample_path,
                    )

                verified_sha = verify_sha256(sample_path, args.expected_sha256)
            except Exception as exc:
                conn.rollback()
                print(f"ERROR sample retrieval/verification failed: {redact_secrets(exc)}")
                return 2

            print(f"sample sha256 verified={verified_sha} size_bytes={sample_path.stat().st_size}")

            code_version = os.environ.get("GITHUB_SHA", "wp06-local")[:40]
            run_mode = "validate" if args.dry_run else "initial"

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM project_staging.stg_adsb_position
                        WHERE UPPER(source_system) = 'TARTAN'
                          AND reject_reason IS NULL
                          AND raw_file = %s
                        """,
                        (source_key,),
                    )
                    preexisting_stg_accepted = int(cur.fetchone()[0])

                manifest_id = record_source_manifest(
                    conn,
                    source_name="TARTAN",
                    source_url=source_url,
                    license_name=TARTAN_LICENSE,
                    attribution=TARTAN_ATTRIBUTION,
                    fetched_at=datetime.now(timezone.utc),
                    file_path=sample_path,
                    object_key=source_key,
                    content_type="text/csv",
                    source_version="kbtp-2022-01-01",
                )

                run1 = start_etl_run(conn, run_mode=run_mode, code_version=code_version)
                stg1 = load_tartan(
                    conn,
                    sample_path,
                    source_file=source_key,
                    etl_run_id=run1,
                    source_manifest_id=manifest_id,
                    batch_size=args.batch_size,
                )
                _assert_reconcile("staging pass1", stg1)

                track1 = load_tartan_tracking_facts(
                    conn,
                    etl_run_id=run1,
                    site_code="KBTP",
                    source_file=source_key,
                    batch_size=args.batch_size,
                    algorithm_version=ALGORITHM_VERSION,
                )
                _assert_reconcile("tracking pass1", track1)
                if track1.rows_rejected != 0:
                    raise AssertionError(
                        f"tracking pass1 rejected {track1.rows_rejected} real rows: "
                        f"{track1.rejects_by_reason}"
                    )

                journey1 = load_tartan_flight_journeys(
                    conn,
                    etl_run_id=run1,
                    source_file=source_key,
                    gap_split_sec=args.gap_split_sec,
                    batch_size=args.batch_size,
                    algorithm_version=ALGORITHM_VERSION,
                )
                _assert_reconcile("journey pass1", journey1)

                finish_etl_run(
                    conn,
                    etl_run_id=run1,
                    counts=stg1,
                    status="SUCCESS" if stg1.rows_rejected == 0 else "PARTIAL",
                    facts_inserted=track1.rows_inserted + journey1.rows_inserted,
                )

                if preexisting_stg_accepted == 0:
                    if stg1.rows_accepted <= 0:
                        raise AssertionError("staging pass1 accepted 0 rows on initial load")
                    if track1.rows_inserted != stg1.rows_accepted:
                        raise AssertionError(
                            f"tracking pass1 inserted={track1.rows_inserted} != "
                            f"staging accepted={stg1.rows_accepted}"
                        )
                    if journey1.rows_inserted <= 0:
                        raise AssertionError("journey pass1 inserted 0 rows on initial load")

                print(f"pass1 staging: {stg1.to_dict()}")
                print(f"pass1 tracking: {track1.to_dict()}")
                print(f"pass1 journey: {journey1.to_dict()}")

                # Pass 2: rerun idempotency verification
                run2 = start_etl_run(conn, run_mode="validate", code_version=code_version)
                stg2 = load_tartan(
                    conn,
                    sample_path,
                    source_file=source_key,
                    etl_run_id=run2,
                    source_manifest_id=manifest_id,
                    batch_size=args.batch_size,
                )
                _assert_reconcile("staging pass2", stg2)

                track2 = load_tartan_tracking_facts(
                    conn,
                    etl_run_id=run2,
                    site_code="KBTP",
                    source_file=source_key,
                    batch_size=args.batch_size,
                    algorithm_version=ALGORITHM_VERSION,
                )
                _assert_reconcile("tracking pass2", track2)

                journey2 = load_tartan_flight_journeys(
                    conn,
                    etl_run_id=run2,
                    source_file=source_key,
                    gap_split_sec=args.gap_split_sec,
                    batch_size=args.batch_size,
                    algorithm_version=ALGORITHM_VERSION,
                )
                _assert_reconcile("journey pass2", journey2)

                finish_etl_run(
                    conn,
                    etl_run_id=run2,
                    counts=stg2,
                    status="SUCCESS" if stg2.rows_rejected == 0 else "PARTIAL",
                    facts_inserted=track2.rows_inserted + journey2.rows_inserted,
                )

                if stg2.rows_accepted != 0:
                    raise AssertionError(
                        f"staging idempotency failed: pass2 accepted={stg2.rows_accepted}"
                    )
                if track2.rows_inserted != 0:
                    raise AssertionError(
                        f"tracking idempotency failed: pass2 inserted={track2.rows_inserted}"
                    )
                if journey2.rows_inserted != 0:
                    raise AssertionError(
                        f"journey idempotency failed: pass2 inserted={journey2.rows_inserted}"
                    )

                print(f"pass2 staging: {stg2.to_dict()}")
                print(f"pass2 tracking: {track2.to_dict()}")
                print(f"pass2 journey: {journey2.to_dict()}")

                with conn.cursor() as cur:
                    report = run_db_assertions(cur, source_file=source_key)

                if args.dry_run:
                    conn.rollback()
                    mode_note = "dry-run: rolled back all staging/fact/run rows"
                else:
                    conn.commit()
                    mode_note = "persistent: committed staging, fact, manifest, and run rows"

            except Exception as exc:
                conn.rollback()
                print(
                    f"ERROR WP-06 verification failed (rolled back): {redact_secrets(exc)}"
                )
                return 1

    print(f"counts project_dw: {report['counts']}")
    print(
        f"reconciliation: staging_accepted={report['stg_accepted_for_file']} "
        f"fact_tracking={report['fact_tracking_for_file']} "
        f"unmatched={report['unmatched_staging_for_file']} "
        f"total_facts={report['total_facts']} "
        f"orphans={report['orphan_total']} "
        f"unknown_grid={report['tracking_unknown_grid_count']} "
        f"unknown_weather={report['tracking_unknown_weather_count']} "
        f"reader_select={report['reader_select_ok']}"
    )
    print(mode_note)
    print("WP-06 verification PASS (non-secret evidence only)")

    _write_step_summary(
        [
            "### WP-06 Facts Verification Summary",
            "",
            f"- Mode: `{mode_note}`",
            f"- Object key: `{args.object_key}` (`sha256` verified)",
            f"- Algorithm / gap split: `{ALGORITHM_VERSION}` / `{args.gap_split_sec}s`",
            f"- Staging pass1: `{stg1.to_dict()}`",
            f"- Staging pass2 accepted: `{stg2.rows_accepted}`",
            f"- Tracking pass1: `{track1.to_dict()}` (pass2 inserted `{track2.rows_inserted}`)",
            f"- Journey pass1: `{journey1.to_dict()}` (pass2 inserted `{journey2.rows_inserted}`)",
            f"- `fact_vehicle_tracking` count: `{report['counts']['fact_vehicle_tracking']}`",
            f"- `fact_flight_journey` count: `{report['counts']['fact_flight_journey']}`",
            f"- Total facts: `{report['total_facts']}` (`>= {MIN_TOTAL_FACTS}`)",
            f"- Unmatched staging rows: `{report['unmatched_staging_for_file']}`",
            f"- FK orphan checks failed: `{report['orphan_total']}`",
            f"- Reader SELECT on all `project_dw` tables: `{report['reader_select_ok']}`",
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
