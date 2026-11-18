from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import run_readonly_analytics as runner

PHASE3_ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = PHASE3_ROOT / "sql"
ANALYTICAL = SQL_ROOT / "analytical"
OLAP = SQL_ROOT / "olap"


def _files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.sql"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_expected_analytical_and_olap_files_exist() -> None:
    analytical = [path.name for path in _files(ANALYTICAL)]
    olap = [path.name for path in _files(OLAP)]
    assert analytical == [
        "01_monthly_traffic_growth.sql",
        "02_kpi_snapshot.sql",
        "03_site_traffic_summary.sql",
        "04_vehicle_activity_summary.sql",
        "05_source_performance.sql",
        "06_time_of_day_pattern.sql",
        "07_coverage_diagnostics.sql",
    ]
    assert olap == [
        "01_rollup_site_source_category_vehicle_type.sql",
        "02_cube_site_source_system.sql",
        "03_grand_total_reconciliation.sql",
    ]


@pytest.mark.parametrize(
    "path",
    [*_files(ANALYTICAL), *_files(OLAP)],
    ids=lambda path: path.name,
)
def test_sql_files_are_read_only_single_statements(path: Path) -> None:
    sql = _read(path)
    assert sql.startswith("-- WP-P3-0"), f"{path.name}: missing WP header"
    runner.assert_read_only_sql(sql, path)
    assert runner.query_id(sql) != "UNSPECIFIED"


def test_monthly_growth_is_null_safe_and_uses_prior_month() -> None:
    sql = _read(ANALYTICAL / "01_monthly_traffic_growth.sql")
    assert "mom_growth_pct" in sql
    assert "LAG(" in sql
    assert "months_since_previous <> 1" in sql
    assert "NO_PRIOR_MONTH" in sql
    assert "NO_ADJACENT_PRIOR_MONTH" in sql


def test_kpi_snapshot_covers_dictionary_and_zero_labels() -> None:
    sql = _read(ANALYTICAL / "02_kpi_snapshot.sql")
    for kpi in (
        "tracking_positions",
        "distinct_vehicles",
        "journeys_observed",
        "occupied_cell_hours",
        "detected_encounters",
        "avg_altitude_msl_ft",
        "avg_ground_speed_kts",
    ):
        assert kpi in sql
    assert "ZERO -" in sql
    assert "L-004" in sql
    assert "L-008" in sql


def test_site_and_vehicle_summaries_keep_coverage_rows() -> None:
    site_sql = _read(ANALYTICAL / "03_site_traffic_summary.sql")
    vehicle_sql = _read(ANALYTICAL / "04_vehicle_activity_summary.sql")
    assert "NO_TRACKING_COVERAGE" in site_sql
    assert "NO_JOURNEY_COVERAGE" in site_sql
    assert "NO_OCCUPANCY_COVERAGE" in site_sql
    assert "NO_TRACKING_COVERAGE" in vehicle_sql
    assert "SOURCE_ENTITY_ONLY" in vehicle_sql
    assert "L3-003" in vehicle_sql


def test_source_performance_uses_documented_mapping() -> None:
    sql = _read(ANALYTICAL / "05_source_performance.sql")
    assert "MANNED_ADSB" in sql
    assert "NIGHTJAR" in sql
    assert "NOMINAL_DJI" in sql
    assert "L-008" in sql


def test_coverage_diagnostics_label_single_month_growth() -> None:
    sql = _read(ANALYTICAL / "07_coverage_diagnostics.sql")
    assert "unknown_site_positions" in sql
    assert "SINGLE_OBSERVED_MONTH" in sql
    assert "growth_coverage_note" in sql


def test_rollup_uses_documented_hierarchy_and_labels_levels() -> None:
    sql = _read(OLAP / "01_rollup_site_source_category_vehicle_type.sql")
    assert "GROUP BY ROLLUP (b.site_code, b.source_category, b.vehicle_type_label)" in sql
    assert "GRAND_TOTAL" in sql
    assert "SITE_SUBTOTAL" in sql
    assert "SITE_SOURCE_CATEGORY_SUBTOTAL" in sql
    assert "UNSPECIFIED" in sql


def test_cube_uses_site_and_source_system() -> None:
    sql = _read(OLAP / "02_cube_site_source_system.sql")
    assert "GROUP BY CUBE (b.site_code, b.source_system)" in sql
    assert "GRAND_TOTAL" in sql
    assert "SOURCE_SYSTEM_TOTAL" in sql
    assert "SITE_TOTAL" in sql


def test_reconciliation_query_emits_dq3_a_004() -> None:
    sql = _read(OLAP / "03_grand_total_reconciliation.sql")
    assert "dq3_a_004_status" in sql
    assert "GROUP BY ROLLUP" in sql
    assert "GROUP BY CUBE" in sql
    assert "THEN 'PASS'" in sql


def test_static_guard_rejects_writes_and_multiple_statements(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must start with SELECT or WITH"):
        runner.assert_read_only_sql("DELETE FROM project_dw.fact_vehicle_tracking;", tmp_path / "x.sql")
    with pytest.raises(ValueError, match="exactly one SQL statement"):
        runner.assert_read_only_sql("SELECT 1; SELECT 2;", tmp_path / "x.sql")
    with pytest.raises(ValueError, match="write-capable keyword"):
        runner.assert_read_only_sql("WITH x AS (DELETE FROM t RETURNING *) SELECT * FROM x;", tmp_path / "x.sql")


def test_value_formatting_is_evidence_safe() -> None:
    assert runner.format_value(None) == "NULL"
    assert runner.format_value(True) == "TRUE"
    assert runner.format_value(Decimal("3.50")) == "3.50"
    assert runner.format_value("a|b") == "a\\|b"
    assert runner.format_value("line\nnext") == "line<br>next"


def test_markdown_table_renders_columns_and_rows() -> None:
    table = runner.markdown_table(["a", "b"], [(1, None), (2, "x")])
    assert table.splitlines()[0] == "| a | b |"
    assert table.splitlines()[1] == "| --- | --- |"
    assert table.splitlines()[2] == "| 1 | NULL |"
