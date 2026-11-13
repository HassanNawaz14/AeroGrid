"""AeroGrid WP-08: read-only DQ checks and explicitly approved CI audit persistence.

Check source: Phase2/docs/06_data_quality_and_reports.md.
Checks return invalid-row counts; zero is PASS. A nonzero CRITICAL is FAIL,
nonzero WARNING is WARN. No check silently drops a database error.

Never run --apply locally: only protected GitHub Actions warehouse jobs receive
DATABASE_URL and record audit data. A failed check is *stored* as FAILED, not hidden.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any


@dataclass(frozen=True)
class Check:
    check_id: str
    name: str
    severity: str
    table: str
    sql: str
    note: str = "Expected invalid-row count: 0"


CHECKS = (
    Check("DQ-C-001", "Required tracking keys and timestamp", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking
        WHERE event_ts IS NULL OR time_key <= 0 OR site_key <= 0 OR vehicle_key <= 0
    """),
    Check("DQ-C-003", "Unknown optional weather dimension", "WARNING", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking WHERE weather_key = -1
    """, "Unknown weather is not a real METAR observation"),
    Check("DQ-C-007", "Unknown optional spatial grids", "WARNING", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking WHERE grid_key = -1
    """, "Unknown grids should be disclosed, not silently imputed"),
    Check("DQ-C-008", "Tracking rows with unknown ground state", "WARNING", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking WHERE on_ground IS NULL
    """, "Preserve NULL; WP07's eligible airborne is an inference, not observed truth"),
    Check("DQ-C-005", "Source manifest required attributes", "CRITICAL", "project_staging.source_manifest", """
        SELECT count(*) FROM project_staging.source_manifest
        WHERE NULLIF(btrim(source_url),'') IS NULL
           OR NULLIF(btrim(license_name),'') IS NULL
           OR NULLIF(btrim(sha256),'') IS NULL OR fetched_at IS NULL
    """),
    Check("DQ-C-006", "Tracking source lineage", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking
        WHERE source_system IS NULL OR NULLIF(btrim(source_record_id),'') IS NULL
           OR etl_run_id IS NULL
    """),
    Check("DQ-U-001", "Dimension vehicle natural-key duplicates", "CRITICAL", "project_dw.dim_vehicle", """
        SELECT count(*) FROM (SELECT source_system, source_entity_id FROM project_dw.dim_vehicle
        GROUP BY 1,2 HAVING count(*) > 1) q
    """),
    Check("DQ-U-002", "Tracking source natural-key duplicates", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM (SELECT source_system, source_record_id FROM project_dw.fact_vehicle_tracking
        GROUP BY 1,2 HAVING count(*) > 1) q
    """),
    Check("DQ-U-003", "Occupancy grain duplicates", "CRITICAL", "project_dw.fact_airspace_occupancy", """
        SELECT count(*) FROM (SELECT time_key, grid_key, algorithm_version
        FROM project_dw.fact_airspace_occupancy GROUP BY 1,2,3 HAVING count(*)>1) q
    """),
    Check("DQ-U-004", "Encounter grain duplicates", "CRITICAL", "project_dw.fact_close_encounter", """
        SELECT count(*) FROM (SELECT vehicle_key_1,vehicle_key_2,start_ts,algorithm_version
        FROM project_dw.fact_close_encounter GROUP BY 1,2,3,4 HAVING count(*)>1) q
    """),
    Check("DQ-A-001", "Accepted ADS-B invalid latitude", "CRITICAL", "project_staging.stg_adsb_position", """
        SELECT count(*) FROM project_staging.stg_adsb_position
        WHERE reject_reason IS NULL AND latitude IS NOT NULL AND (latitude < -90 OR latitude > 90)
    """),
    Check("DQ-A-002", "Accepted ADS-B invalid longitude", "CRITICAL", "project_staging.stg_adsb_position", """
        SELECT count(*) FROM project_staging.stg_adsb_position
        WHERE reject_reason IS NULL AND longitude IS NOT NULL AND (longitude < -180 OR longitude > 180)
    """),
    Check("DQ-A-007", "Tracking altitude missing datum", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking
        WHERE altitude_msl_ft IS NOT NULL AND NULLIF(btrim(altitude_source),'') IS NULL
    """),
    Check("DQ-A-008", "Invalid stored METAR wind direction", "WARNING", "project_staging.stg_weather_metar", """
        SELECT count(*) FROM project_staging.stg_weather_metar
        WHERE reject_reason IS NULL AND wind_direction_deg IS NOT NULL
          AND (wind_direction_deg < 0 OR wind_direction_deg >= 360)
    """),
    Check("DQ-I-001", "Tracking orphan time keys", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking f
        LEFT JOIN project_dw.dim_time d ON d.time_key=f.time_key WHERE d.time_key IS NULL
    """),
    Check("DQ-I-002", "Tracking orphan site keys", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking f
        LEFT JOIN project_dw.dim_site d ON d.site_key=f.site_key WHERE d.site_key IS NULL
    """),
    Check("DQ-I-003", "Tracking orphan vehicle keys", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking f
        LEFT JOIN project_dw.dim_vehicle d ON d.vehicle_key=f.vehicle_key WHERE d.vehicle_key IS NULL
    """),
    Check("DQ-I-004", "Tracking orphan grid keys", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking f
        LEFT JOIN project_dw.dim_spatial_grid d ON d.grid_key=f.grid_key WHERE d.grid_key IS NULL
    """),
    Check("DQ-I-005", "Tracking orphan weather keys", "CRITICAL", "project_dw.fact_vehicle_tracking", """
        SELECT count(*) FROM project_dw.fact_vehicle_tracking f
        LEFT JOIN project_dw.dim_weather d ON d.weather_key=f.weather_key WHERE d.weather_key IS NULL
    """),
    Check("DQ-I-006", "Restriction orphan zone keys", "CRITICAL", "project_dw.fact_restriction_activation", """
        SELECT count(*) FROM project_dw.fact_restriction_activation f
        LEFT JOIN project_dw.dim_airspace_zone z ON z.zone_key=f.zone_key WHERE z.zone_key IS NULL
    """),
    Check("DQ-I-009", "Derived occupancy orphan hour/grid", "CRITICAL", "project_dw.fact_airspace_occupancy", """
        SELECT count(*) FROM project_dw.fact_airspace_occupancy f
        LEFT JOIN project_dw.dim_time t ON t.time_key=f.time_key
        LEFT JOIN project_dw.dim_spatial_grid g ON g.grid_key=f.grid_key
        WHERE t.time_key IS NULL OR g.grid_key IS NULL
    """),
    Check("DQ-I-010", "Journey orphan required dimensions", "CRITICAL", "project_dw.fact_flight_journey", """
        SELECT count(*) FROM project_dw.fact_flight_journey j
        LEFT JOIN project_dw.dim_site s ON s.site_key=j.site_key
        LEFT JOIN project_dw.dim_vehicle v ON v.vehicle_key=j.vehicle_key
        LEFT JOIN project_dw.dim_time st ON st.time_key=j.start_time_key
        LEFT JOIN project_dw.dim_time et ON et.time_key=j.end_time_key
        LEFT JOIN project_dw.dim_spatial_grid og ON og.grid_key=j.origin_grid_key
        LEFT JOIN project_dw.dim_spatial_grid dg ON dg.grid_key=j.destination_grid_key
        WHERE s.site_key IS NULL OR v.vehicle_key IS NULL OR st.time_key IS NULL
          OR et.time_key IS NULL OR og.grid_key IS NULL OR dg.grid_key IS NULL
    """),
    Check("DQ-I-008", "Encounter invalid vehicle ordering", "CRITICAL", "project_dw.fact_close_encounter", """
        SELECT count(*) FROM project_dw.fact_close_encounter WHERE vehicle_key_1 >= vehicle_key_2
    """),
    Check("DQ-R-001", "ETL run-log reconciliation", "CRITICAL", "project_staging.etl_run_log", """
        SELECT count(*) FROM project_staging.etl_run_log
        WHERE rows_read <> rows_accepted + rows_rejected + rows_duplicate
    """),
    Check("DQ-R-002", "Accepted Tartan positions without tracking facts", "CRITICAL", "project_staging.stg_adsb_position", """
        SELECT count(*) FROM project_staging.stg_adsb_position s
        LEFT JOIN project_dw.fact_vehicle_tracking f
          ON f.source_system=s.source_system AND f.source_record_id=s.source_record_id
        WHERE s.reject_reason IS NULL AND upper(s.source_system)='TARTAN'
          AND f.tracking_id IS NULL
    """),
    Check("DQ-R-004", "Occupancy count integrity", "CRITICAL", "project_dw.fact_airspace_occupancy", """
        SELECT count(*) FROM project_dw.fact_airspace_occupancy
        WHERE active_vehicle_count < 0 OR active_vehicle_count > supporting_tracking_count
           OR total_occupancy_minutes < 0
    """),
    Check("DQ-R-005", "Encounter missing tracking evidence", "CRITICAL", "project_dw.fact_close_encounter", """
        SELECT count(*) FROM project_dw.fact_close_encounter e
        LEFT JOIN project_dw.fact_vehicle_tracking a ON a.tracking_id=e.min_tracking_id_1
        LEFT JOIN project_dw.fact_vehicle_tracking b ON b.tracking_id=e.min_tracking_id_2
        WHERE a.tracking_id IS NULL OR b.tracking_id IS NULL OR
              a.vehicle_key <> e.vehicle_key_1 OR b.vehicle_key <> e.vehicle_key_2
    """),
    Check("DQ-B-001", "Encounter H-013 severity thresholds", "CRITICAL", "project_dw.fact_close_encounter", """
        SELECT count(*) FROM project_dw.fact_close_encounter
        WHERE algorithm_version='wp07-v1' AND (
            (risk_severity_class='SEVERE' AND NOT (min_horizontal_sep_nm < 0.5 AND min_vertical_sep_ft < 500))
         OR (risk_severity_class='PROXIMITY' AND NOT (min_horizontal_sep_nm < 1 AND min_vertical_sep_ft < 1000
             AND NOT (min_horizontal_sep_nm < 0.5 AND min_vertical_sep_ft < 500)))
         OR risk_severity_class NOT IN ('SEVERE','PROXIMITY')
         OR min_vertical_sep_ft IS NULL)
    """),
    Check("DQ-R-006", "Restriction affected/compliant count integrity", "CRITICAL", "project_dw.fact_restriction_activation", """
        SELECT count(*) FROM project_dw.fact_restriction_activation
        WHERE affected_traffic_count < 0 OR compliant_count < 0
           OR (affected_traffic_count IS NOT NULL AND compliant_count > affected_traffic_count)
    """),
    Check("DQ-B-004", "Journey missing real source lineage", "CRITICAL", "project_dw.fact_flight_journey", """
        SELECT count(*) FROM project_dw.fact_flight_journey
        WHERE source_system IS NULL OR NULLIF(btrim(source_record_id),'') IS NULL
           OR etl_run_id IS NULL
    """),
    Check("DQ-B-003", "Restriction fact missing source snapshot", "CRITICAL", "project_dw.fact_restriction_activation", """
        SELECT count(*) FROM project_dw.fact_restriction_activation f
        LEFT JOIN project_staging.stg_restriction_snapshot s
           ON f.source_record_id = ('snapshot:' || s.staging_id::text)
          AND upper(f.source_system)=upper(s.source_system)
        WHERE s.staging_id IS NULL OR f.source_snapshot_ts IS NULL
    """),
    Check("DQ-T-003", "No real restriction snapshots available", "WARNING", "project_staging.stg_restriction_snapshot", """
        SELECT CASE WHEN count(*) FILTER (WHERE reject_reason IS NULL) = 0 THEN 1 ELSE 0 END
        FROM project_staging.stg_restriction_snapshot
    """, "Source gap for KBTP is documented; not a claim about historical 2022 TFRs"),
    Check("DQ-G-001", "Primary source produced no accepted rows", "CRITICAL", "project_staging.stg_adsb_position", """
        SELECT CASE WHEN count(*) FILTER (WHERE reject_reason IS NULL) = 0 THEN 1 ELSE 0 END
        FROM project_staging.stg_adsb_position
    """, "Coverage guard: an empty primary source must fail, not report zero events"),
    Check("DQ-G-002", "In-scope weather source not ingested", "WARNING", "project_staging.stg_weather_metar", """
        SELECT CASE WHEN count(*) FILTER (WHERE reject_reason IS NULL) = 0 THEN 1 ELSE 0 END
        FROM project_staging.stg_weather_metar
    """, "Coverage gap, not proof of clear weather: METAR/ASOS validated but never loaded"),
    Check("DQ-G-003", "In-scope UAS sources not ingested", "WARNING", "project_staging.stg_uas_position", """
        SELECT CASE WHEN count(*) FILTER (WHERE reject_reason IS NULL) = 0 THEN 1 ELSE 0 END
        FROM project_staging.stg_uas_position
    """, "Coverage gap, not proof of no UAS traffic: Nightjar/DJI validated but never loaded"),
    Check("DQ-G-004", "In-scope airspace source not ingested", "WARNING", "project_staging.stg_airspace_zone", """
        SELECT CASE WHEN count(*) FILTER (WHERE reject_reason IS NULL) = 0 THEN 1 ELSE 0 END
        FROM project_staging.stg_airspace_zone
    """, "Coverage gap, not proof of empty airspace: FAA zones validated but never staged"),
)


def assess(check: Check, value: int) -> str:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"Invalid count for {check.check_id}")
    if value == 0:
        return "PASS"
    return "FAIL" if check.severity == "CRITICAL" else "WARN"


def check_catalog() -> list[dict[str, str]]:
    return [{"id": c.check_id, "name": c.name, "severity": c.severity, "table": c.table}
            for c in CHECKS]


def evaluate(conn: Any, etl_run_id: int | None = None, *, persist: bool = False) -> list[dict[str, Any]]:
    if persist and (etl_run_id is None or etl_run_id <= 0):
        raise ValueError("An audit ETL run ID is required for persistence")
    results = []
    for check in CHECKS:
        cur = conn.cursor()
        cur.execute(check.sql)
        row = cur.fetchone()
        value = int(row[0])
        status = assess(check, value)
        result = {"check_id": check.check_id, "name": check.name, "severity": check.severity,
                  "table_name": check.table, "status": status, "observed_value": value,
                  "expected_value": "0", "details": check.note}
        results.append(result)
        if persist:
            conn.execute("""
                INSERT INTO project_staging.dq_result
                  (etl_run_id,check_id,check_name,severity,table_name,status,observed_value,expected_value,details)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (etl_run_id, check.check_id, check.name, check.severity, check.table,
                  status, str(value), "0", check.note))
    return results


def summary(results: list[dict[str, Any]]) -> dict[str, int]:
    return {s: sum(item["status"] == s for item in results) for s in ("PASS", "FAIL", "WARN", "SKIP")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Persist DQ audit from protected CI only")
    args = parser.parse_args(argv)
    if args.apply and (os.getenv("GITHUB_ACTIONS") != "true" or os.getenv("WAREHOUSE_CI_APPROVED") != "true"):
        parser.error("--apply requires the approved warehouse GitHub Actions job")
    if not os.getenv("DATABASE_URL"):
        parser.error("DATABASE_URL is required in approved CI environment")
    try:
        import psycopg
    except ImportError:
        parser.error("Install psycopg[binary] inside CI")
    from etl.staging_writer import start_etl_run, finish_etl_run
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=15) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SET LOCAL statement_timeout = '8min'")
            run_id = start_etl_run(conn, run_mode="validate", code_version="wp08-v1") if args.apply else None
            results = evaluate(conn, run_id, persist=args.apply)
            counts = summary(results)
            print(f"DQ summary={counts} total={len(results)}")
            for x in results:
                print(f"{x['check_id']} {x['status']} observed={x['observed_value']}")
            if args.apply:
                finish_etl_run(conn, etl_run_id=run_id, counts=SimpleNamespace(
                    rows_read=0,rows_accepted=0,rows_rejected=0,rows_duplicate=0),
                    status="FAILED" if counts["FAIL"] else "SUCCESS",
                    critical_dq_failures=counts["FAIL"],
                    failure_reason="Critical DQ checks failed" if counts["FAIL"] else None)
                conn.commit()  # Persist *failure evidence* as well as passes.
                print(f"DQ evidence persisted for etl_run_id={run_id}")
            else:
                conn.rollback()
                print("DQ READ-ONLY PASS; ROLLBACK")
            return 1 if counts["FAIL"] else 0
        except Exception as exc:
            conn.rollback()
            print(f"DQ FAILURE; transaction rolled back; type={type(exc).__name__}")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
