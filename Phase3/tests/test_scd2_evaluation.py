from __future__ import annotations

import re
from pathlib import Path

import pytest

import evaluate_scd2 as scd2
from run_readonly_analytics import assert_read_only_sql, executable_statements

PHASE3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PHASE3_ROOT.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wp-p3-h3-scd2-eval.yml"
DOC = PHASE3_ROOT / "docs" / "WP-P3-H3_scd2_evaluation.md"

EXPECTED_IDS = ["QW-P3-H3-01", "QW-P3-H3-02", "QW-P3-H3-03", "QW-P3-H3-04"]


def _profile(types: int = 1, members: int = 3) -> dict:
    return {"h3_members": members, "h3_distinct_vehicle_types": types}


def _results(types: int = 1, stale: int = 0, months: int = 1, members: int = 3, multi: int = 0) -> dict:
    return {
        "QW-P3-H3-01": _profile(types, members),
        "QW-P3-H3-02": {"h3_serials_multi_source": multi},
        "QW-P3-H3-03": {"h3_stale_members": stale, "h3_max_lag_hours": 96.0 if stale else 0},
        "QW-P3-H3-04": {"h3_observed_months": months},
    }


def test_probe_files_cover_the_four_probes_in_order() -> None:
    files = scd2.probe_files()
    assert len(files) == 4
    ids = [re.search(r"QW-P3-H3-\d{2}", path.read_text(encoding="utf-8")).group(0) for path in files]
    assert ids == EXPECTED_IDS


@pytest.mark.parametrize("path", scd2.probe_files(), ids=lambda p: p.name)
def test_each_probe_is_one_read_only_statement(path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    assert_read_only_sql(sql, path)
    assert len(executable_statements(sql)) == 1


@pytest.mark.parametrize("path", scd2.probe_files(), ids=lambda p: p.name)
def test_each_probe_returns_a_query_id_and_h3_columns(path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    assert re.search(r"AS query_id\b", sql)
    assert re.search(r"AS h3_\w+", sql)


def test_probes_touch_only_modelled_tables_and_no_raw_payloads() -> None:
    allowed = {
        "project_dw.dim_vehicle", "project_dw.fact_vehicle_tracking",
        "project_staging.stg_uas_position",
    }
    for path in scd2.probe_files():
        sql = path.read_text(encoding="utf-8")
        tables = set(re.findall(r"\b(project_(?:dw|staging|reporting)\.\w+)", sql))
        assert tables <= allowed, (path.name, tables - allowed)
        assert "raw_payload" not in sql


def test_no_vehicle_means_inconclusive() -> None:
    assert scd2.decide(_results(members=0))["verdict"] == scd2.NO_DATA


def test_single_vehicle_type_defers_scd2() -> None:
    assert scd2.decide(_results(types=1))["verdict"] == scd2.DEFER


def test_varying_attribute_requires_human_review() -> None:
    decision = scd2.decide(_results(types=2))
    assert decision["verdict"] == scd2.REVIEW
    assert decision["varying_attribute"] is True


def test_stale_last_seen_is_a_type1_gap_not_a_type2_need() -> None:
    decision = scd2.decide(_results(types=1, stale=2))
    assert decision["verdict"] == scd2.DEFER
    assert decision["type1_gap"] is True
    assert decision["stale_members"] == 2


def test_single_observed_month_is_reported() -> None:
    assert scd2.decide(_results(months=1))["single_observed_month"] is True
    assert scd2.decide(_results(months=2))["single_observed_month"] is False


def test_decide_tolerates_missing_probe_rows() -> None:
    assert scd2.decide({})["verdict"] == scd2.NO_DATA


def test_report_has_findings_and_no_connection_string() -> None:
    decision = scd2.decide(_results(stale=1))
    report = scd2.render_report(
        captured_at="2026-11-21T00:00:00+00:00", role="aerogrid_reader", database="neondb",
        probe_sections=[], probes_executed=4, decision=decision, failures=[],
    )
    assert "Probes: 4 of 4 executed" in report
    assert "DEFER_SCD2" in report
    assert "Type 1 gap" in report
    assert "postgres" not in report.lower()


def test_failed_run_reports_no_verdict() -> None:
    report = scd2.render_report(
        captured_at="t", role="r", database="d", probe_sections=[], probes_executed=1, decision=None,
        failures=["connection: OperationalError"],
    )
    assert "no verdict was derived" in report


def test_list_mode_needs_no_database(capsys) -> None:
    assert scd2.main(["--list"]) == 0
    assert "01_dim_vehicle_profile.sql" in capsys.readouterr().out


def test_missing_database_variable_is_a_clean_error(monkeypatch) -> None:
    monkeypatch.delenv("READONLY_DATABASE_URL", raising=False)
    with pytest.raises(SystemExit):
        scd2.main([])


def test_workflow_is_manual_read_only_and_uses_the_warehouse_environment() -> None:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    text = "\n".join(line for line in lines if not line.lstrip().startswith("#"))
    assert "workflow_dispatch" in text
    assert "schedule:" not in text
    assert "contents: read" in text
    assert "environment: warehouse" in text
    assert "secrets.READONLY_DATABASE_URL" in text
    assert "secrets.DATABASE_URL" not in text
    assert "--require-reader" in text
    assert "timeout-minutes" in text and "concurrency:" in text
    assert "evaluate_scd2.py" in text


def test_evaluation_doc_states_the_verdict_rules() -> None:
    text = DOC.read_text(encoding="utf-8")
    for token in (scd2.DEFER, scd2.REVIEW, scd2.NO_DATA, "QW-P3-H3-01", "Type 1 gap"):
        assert token in text
