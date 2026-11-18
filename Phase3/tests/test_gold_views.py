from __future__ import annotations

from pathlib import Path

import pytest

import verify_gold_views as gold

PHASE3_ROOT = Path(__file__).resolve().parents[1]
VIEWS_ROOT = PHASE3_ROOT / "sql" / "views"


def _sql() -> str:
    return (VIEWS_ROOT / "01_gold_views.sql").read_text(encoding="utf-8")


def test_expected_gold_views_exist_and_are_ordered() -> None:
    assert sorted(path.name for path in VIEWS_ROOT.glob("*.sql")) == [
        "01_gold_views.sql"
    ]
    assert gold.VIEW_NAMES == (
        "vw_monthly_traffic_growth",
        "vw_vehicle_analysis",
        "vw_source_performance",
    )


def test_gold_ddl_is_read_only_three_views_and_column_explicit() -> None:
    gold.assert_gold_view_sql(_sql(), gold.SQL_FILE)


def test_gold_views_keep_coverage_rows_and_avoid_zero_claims() -> None:
    sql = _sql()
    assert sql.count("NO_TRACKING_COVERAGE - not proof of inactivity") == 1
    assert sql.count("NO_TRACKING_COVERAGE - not proof of no activity") == 1
    assert sql.count("NO_JOURNEY_COVERAGE - not proof of no flights") == 2
    assert "COALESCE(t.tracking_positions, 0)" in sql
    assert "COALESCE(j.journeys_observed, 0)" in sql
    assert "not proof" in sql
    assert "L3-003" in sql
    assert "extrapolation" in sql
    assert "no month spine" in sql
    assert "project_staging" not in sql


def test_gold_views_document_grain_and_source_queries() -> None:
    sql = _sql()
    assert sql.count("Grain:") == 3
    assert "QW-P3-02-01" in sql
    assert "QW-P3-02-04" in sql
    assert "QW-P3-02-05" in sql
    assert "DQ3-A-001" in sql
    assert "DQ3-A-003" in sql


def test_monthly_view_is_observed_month_only_and_null_safe() -> None:
    sql = _sql()
    assert "LAG(m.month_utc)" in sql
    assert "months_since_previous <> 1" in sql
    assert "NO_ADJACENT_PRIOR_MONTH" in sql
    assert "NO_PRIOR_MONTH" in sql
    assert "PRIOR_MONTH_ZERO" in sql
    assert "generate_series" not in sql


def test_vehicle_view_exposes_time_of_day_summary_without_spine() -> None:
    sql = _sql()
    assert "EXTRACT(HOUR FROM f.event_ts AT TIME ZONE 'UTC')" in sql
    assert "peak_hour_utc" in sql
    assert "observed_hours_utc" in sql
    assert "ROW_NUMBER() OVER" in sql
    assert "generate_series" not in sql


def test_source_view_keeps_mapping_and_zero_activity_coverage() -> None:
    sql = _sql()
    assert "WHEN s.source_system = 'TARTAN' THEN 'MANNED_ADSB'" in sql
    assert "IN ('NIGHTJAR', 'NOMINAL_DJI', 'DJI') THEN 'UAS'" in sql
    assert "SELECT DISTINCT UPPER(TRIM(v.source_system)) AS source_system" in sql
    assert "observed_months" in sql
    assert "peak_month_utc" in sql


def test_static_guard_rejects_writes_and_select_star() -> None:
    sql = _sql()
    with pytest.raises(ValueError, match="expected exactly"):
        gold.assert_gold_view_sql(sql + "\nDROP VIEW project_reporting.vw_source_performance;\n", gold.SQL_FILE)
    with pytest.raises(ValueError, match="SELECT \\*"):
        gold.assert_gold_view_sql(
            sql.replace("    g.month_utc,\n", "    *\n", 1),
            gold.SQL_FILE,
        )


def test_verifier_rolls_back_by_default_and_reads_as_reader() -> None:
    source = (PHASE3_ROOT / "scripts" / "verify_gold_views.py").read_text(
        encoding="utf-8"
    )
    assert "conn.rollback()" in source
    assert "conn.read_only = True" in source
    assert "aerogrid_reader" in source
    assert "APPROVE_WP3_GOLD_VIEWS" in (
        PHASE3_ROOT.parent / ".github" / "workflows" / "wp-p3-gold-views.yml"
    ).read_text(encoding="utf-8")


def test_apply_is_blocked_outside_approved_main_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GITHUB_ACTIONS",
        "WAREHOUSE_CI_APPROVED",
        "GITHUB_REF",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(SystemExit) as exc:
        gold.main(["--apply"])
    assert exc.value.code == 2


def test_ddl_parses_with_pglast_when_available() -> None:
    pglast = pytest.importorskip("pglast")
    pglast.parse_sql(_sql())
