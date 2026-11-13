"""WP-09: source-scoped reconciliation and real DQ warning interpretation."""
from datetime import datetime, timezone

from etl.reports import (
    TABLES, build_reports, coverage_rows, reconciliation_rows, warning_rows, snapshot,
)


def test_coverage_rows_mark_unloaded_sources_instead_of_zero():
    rows = coverage_rows([
        ('Tartan ADS-B (KBTP)', 'stg_adsb_position', 27479),
        ('AWC/IEM METAR', 'stg_weather_metar', 0),
    ])
    assert rows[1][3] == 'LOADED'
    assert rows[2][3] == 'NO DATA LOADED'
    assert rows[2][2] == 0
    assert coverage_rows([])[1][0] == 'UNAVAILABLE'


def test_run_reconciliation_is_not_aggregate_staging_plus_rejects():
    result = reconciliation_rows([
        (11, "initial", "wp06-v1", 27897, 27479, 418, 0),
        (12, "validate", "wp07-v1", 100, 95, 0, 5),
    ])
    assert result[1][-1] == "YES"
    assert result[2][-1] == "YES"
    assert len(result) == 3  # independently scoped ETL runs
    assert reconciliation_rows([])[1][0] == "NO ROW-COUNT RUN"
    assert reconciliation_rows([(1, 'initial', 'x', 3, 1, 1, 0)])[1][-1] == 'NO'


def test_warning_explanations_use_stored_values_and_correct_interpretations():
    data = [
        ('DQ-C-003', 'Unknown weather', 'WARNING', 'WARN', '27479', '0', ''),
        ('DQ-C-008', 'Unknown ground state', 'WARNING', 'WARN', '27479', '0', ''),
        ('DQ-T-003', 'Missing snapshots', 'WARNING', 'WARN', '1', '0', ''),
        ('DQ-U-001', 'Uniqueness', 'CRITICAL', 'PASS', '0', '0', ''),
    ]
    rows = warning_rows(data)
    assert len(rows) == 4
    assert 'METAR' in rows[1][2]
    assert 'inferred' in rows[2][2]
    assert 'NOT one missing flight' in rows[3][2]
    assert rows[3][1] == '1'
    assert warning_rows([])[1][0] == 'NONE'


def test_warning_fallback_uses_persisted_detail():
    rows = warning_rows([('DQ-OTHER','a check','WARNING','WARN','12','0','Stored meaningful detail')])
    assert rows[1][2] == 'Stored meaningful detail'


def test_snapshot_uses_real_run_and_staging_evidence(monkeypatch):
    class Cursor:
        def __init__(self): self.sql = ''
        def __enter__(self): return self
        def __exit__(self, *_): return False
        def execute(self, sql, params=()): self.sql = sql
        def fetchall(self):
            s = self.sql
            if 'MAX(etl_run_id)' in s: return [(7,)]
            if 'FROM project_staging.dq_result WHERE' in s:
                return [('DQ-T-003','Snapshots','WARNING','WARN','1','0','Missing source')]
            if 'WHERE rows_read > 0' in s:
                return [(3,'initial','wp06-v1',100,95,5,0)]
            if 'COUNT(*) FILTER (WHERE reject_reason IS NULL)' in s: return [(95,0)]
            if 'FROM project_staging.stg_reject GROUP BY' in s: return [('TARTAN','INVALID_ID',5)]
            if 'FROM project_staging.source_manifest' in s: return []
            if 'FROM project_staging.etl_run_log ORDER' in s:
                return [(7, 'validate', datetime.now(timezone.utc),'SUCCESS','wp08-v1',0,0,0,0,0)]
            if 'pg_database_size' in s: return [(6400,)]
            return [(95,)]
    class Conn:
        def cursor(self): return Cursor()
    result = snapshot(Conn())
    assert result['source_runs'][0][0] == 3
    assert result['staging_status'] == (95,0)
    assert result['dq'][0][-1] == 'Missing source'
    assert len(result['counts']) == len(TABLES)


def test_reports_generate_with_additional_source_run_and_warning_evidence(tmp_path):
    data = {
        'counts': {name: 0 for name in TABLES},
        'run': (7, 'validate', datetime.now(timezone.utc),'SUCCESS','wp08-v1',0,0,0,0,0),
        'source_runs': [(3,'initial','wp06-v1',100,95,5,0)],
        'staging_status': (95,0),
        'coverage': [('Tartan ADS-B (KBTP)','stg_adsb_position',95),
                     ('AWC/IEM METAR','stg_weather_metar',0)],
        'dq_run': 7,
        'dq': [('DQ-T-003','Snapshots','WARNING','WARN','1','0','Missing source')],
        'rejects': [('TARTAN','INVALID_ID',5)],
        'manifests': [],
        'database_bytes': 6400,
        'generated_utc':datetime.now(timezone.utc).isoformat(),
    }
    a,b=build_reports(data,tmp_path)
    assert a.read_bytes()[:4] == b.read_bytes()[:4] == b'%PDF'
    assert a.stat().st_size > 1500 and b.stat().st_size > 1500
