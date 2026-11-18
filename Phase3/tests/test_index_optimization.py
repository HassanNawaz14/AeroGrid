from __future__ import annotations

import json
from pathlib import Path

import pytest

import generate_index_report as report
import measure_indexes as measure
import run_readonly_analytics as analytics

PHASE3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PHASE3_ROOT.parent
INDEX_SQL = PHASE3_ROOT / "sql" / "indexes" / "01_indexes.sql"
QUERY_ROOT = PHASE3_ROOT / "sql" / "optimization"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "wp-p3-05-indexes.yml"

EXPECTED_IDS = ("IX-P3-05-01", "IX-P3-05-02", "IX-P3-05-03")
EXPECTED_QUERIES = ("OQ-P3-05-01", "OQ-P3-05-02", "OQ-P3-05-03")


def _definitions():
    return measure.parse_index_definitions(INDEX_SQL.read_text(encoding="utf-8"))


def test_index_ddl_has_one_idempotent_definition_per_candidate() -> None:
    definitions = _definitions()
    assert [item.index_id for item in definitions] == list(EXPECTED_IDS)
    assert [item.target_query for item in definitions] == list(EXPECTED_QUERIES)
    for item in definitions:
        assert item.statement.startswith("CREATE INDEX IF NOT EXISTS")
        assert item.table.startswith("project_dw.")
        assert item.index_name in item.statement
        assert item.rationale.endswith(".")


def test_index_rationales_keep_their_full_multi_line_text() -> None:
    definitions = {item.index_id: item for item in _definitions()}
    assert "INCLUDE columns" in definitions["IX-P3-05-02"].rationale
    assert "single-column indexes" in definitions["IX-P3-05-01"].rationale


def test_index_ddl_rejects_destructive_or_unscoped_sql() -> None:
    with pytest.raises(ValueError):
        measure.assert_index_sql("DROP INDEX project_dw.ix_any;")
    with pytest.raises(ValueError):
        measure.assert_index_sql(
            "CREATE INDEX IF NOT EXISTS ix_any ON project_staging.stg_adsb_position (event_ts);"
        )
    with pytest.raises(ValueError):
        measure.assert_index_sql("CREATE INDEX ix_any ON project_dw.dim_site (site_code);")


def test_candidate_index_names_do_not_collide_with_phase2_indexes() -> None:
    phase2_sql = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (REPO_ROOT / "Phase2" / "sql").rglob("*.sql")
    )
    for item in _definitions():
        assert item.index_name.lower() not in phase2_sql


def test_optimization_queries_are_single_read_only_statements() -> None:
    files = sorted(QUERY_ROOT.glob("*.sql"))
    assert [path.name for path in files] == [
        "01_source_monthly_volume.sql",
        "02_monthly_growth_by_site.sql",
        "03_vehicle_activity.sql",
    ]
    found_ids = []
    for path in files:
        sql = path.read_text(encoding="utf-8")
        analytics.assert_read_only_sql(sql, path)
        found_ids.append(measure.query_id(sql))
    assert found_ids == list(EXPECTED_QUERIES)


def test_summarize_explain_extracts_time_cost_and_scans() -> None:
    payload = [
        {
            "Planning Time": 1.5,
            "Execution Time": 2.5,
            "Plan": {
                "Node Type": "Seq Scan",
                "Total Cost": 10.0,
                "Plan Rows": 5,
                "Actual Rows": 5,
                "Shared Hit Blocks": 3,
                "Shared Read Blocks": 1,
                "Plans": [{"Node Type": "Aggregate", "Total Cost": 4.0}],
            },
        }
    ]
    summary = measure.summarize_explain(payload)
    assert summary["planning_time_ms"] == 1.5
    assert summary["execution_time_ms"] == 2.5
    assert summary["total_cost"] == 10.0
    assert summary["root_node"] == "Seq Scan"
    assert summary["scan_nodes"] == ["Seq Scan", "Aggregate"]
    assert summary["shared_hit_blocks"] == 3
    assert summary["shared_read_blocks"] == 1


def test_verify_rolls_back_and_apply_commits_only_on_apply() -> None:
    class FakeConnection:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def rollback(self) -> None:
            self.calls.append("rollback")

        def commit(self) -> None:
            self.calls.append("commit")

    verify_connection = FakeConnection()
    measure.finish_transaction(verify_connection, apply=False)
    assert verify_connection.calls == ["rollback"]

    apply_connection = FakeConnection()
    measure.finish_transaction(apply_connection, apply=True)
    assert apply_connection.calls == ["commit"]


def test_apply_is_blocked_outside_approved_main_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("GITHUB_ACTIONS", "WAREHOUSE_CI_APPROVED", "GITHUB_REF"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(SystemExit) as exc:
        measure.main(["--apply"])
    assert exc.value.code == 2


def test_measure_script_rolls_back_by_default() -> None:
    source = (PHASE3_ROOT / "scripts" / "measure_indexes.py").read_text(encoding="utf-8")
    assert "conn.rollback()" in source
    assert "ROLLBACK" in source
    assert "conn.read_only = True" not in source
    assert "INSERT" not in source.upper().replace("INSERT/UPDATE", "")


def _evidence() -> dict:
    baseline = {
        "planning_time_ms": 0.4,
        "execution_time_ms": 12.0,
        "total_cost": 120.0,
        "root_node": "Seq Scan",
        "scan_nodes": ["Seq Scan"],
        "shared_hit_blocks": 30,
        "shared_read_blocks": 0,
        "temp_written_blocks": 0,
        "plan_rows": 1,
        "actual_rows": 1,
    }
    improved = dict(baseline, execution_time_ms=6.5, total_cost=80.0)
    indexes = [
        {
            "index_id": index_id,
            "index_name": f"ix_test_{number}",
            "table": "project_dw.fact_vehicle_tracking",
            "target_query": query_id,
            "rationale": "unit-test fixture",
            "ddl_sha256": "0" * 64,
            "size_bytes": 65536,
            "before": baseline,
            "after": improved,
            "delta": measure.compare_summaries(baseline, improved),
        }
        for number, (index_id, query_id) in enumerate(
            zip(EXPECTED_IDS, EXPECTED_QUERIES), start=1
        )
    ]
    return {
        "schema_version": 1,
        "work_package": "WP-P3-05",
        "mode": "verify",
        "captured_at": "2026-11-19T00:00:00+00:00",
        "connected_role": "aerogrid_etl",
        "database": "neondb",
        "server": "PostgreSQL test",
        "baseline_database_size_bytes": 8388608,
        "final_database_size_bytes": 8519680,
        "storage_guard_bytes": 734003200,
        "fact_baseline": {
            "fact_vehicle_tracking": 27479,
            "fact_flight_journey": 178,
            "fact_airspace_occupancy": 1754,
        },
        "queries": [
            {"id": query_id, "file": f"Phase3/sql/optimization/{query_id}.sql", "sha256": "0" * 64}
            for query_id in EXPECTED_QUERIES
        ],
        "indexes": indexes,
    }


def test_compare_summaries_reports_honest_deltas() -> None:
    before = {"execution_time_ms": 10.0, "total_cost": 100.0}
    after = {"execution_time_ms": 5.0, "total_cost": 60.0}
    delta = measure.compare_summaries(before, after)
    assert delta["execution_time_ms"] == -5.0
    assert delta["execution_time_pct"] == -50.0
    assert delta["total_cost_pct"] == -40.0


def test_dq3_a_006_passes_only_with_complete_pairs() -> None:
    evidence = _evidence()
    assert report.dq3_a_006_status(evidence) == "PASS"
    broken = json.loads(json.dumps(evidence))
    broken["indexes"][1]["after"] = None
    assert report.dq3_a_006_status(broken) == "FAIL"


def test_report_generator_writes_pdf_and_rejects_missing_pair(tmp_path: Path) -> None:
    pytest.importorskip("reportlab")
    output = tmp_path / "Indexing_Report.pdf"
    result = report.build_report(_evidence(), output)
    assert result["dq3_a_006_status"] == "PASS"
    assert output.read_bytes().startswith(b"%PDF")

    broken = json.loads(json.dumps(_evidence()))
    broken["indexes"][0].pop("after")
    with pytest.raises(ValueError):
        report.build_report(broken, tmp_path / "broken.pdf")


def test_index_workflow_is_guarded_and_runs_phase3_tests() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "environment: warehouse" in workflow
    assert "APPROVE_WP3_INDEXES" in workflow
    assert "refs/heads/main" in workflow
    assert "Phase3/tests" in workflow
    assert "measure_indexes.py --apply" in workflow
    assert "generate_index_report.py" in workflow
