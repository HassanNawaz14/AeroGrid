from pathlib import Path
from etl.verify_wp10_views import VIEW_NAMES, SQL_FILE

def test_exactly_ten_distinct_view_names():
    assert len(VIEW_NAMES)==len(set(VIEW_NAMES))==10

def test_sql_creates_all_views():
    sql=SQL_FILE.read_text(encoding='utf-8').upper()
    for name in VIEW_NAMES:
        assert f'CREATE OR REPLACE VIEW PROJECT_REPORTING.{name.upper()}' in sql

def test_no_destructive_sql():
    sql=SQL_FILE.read_text(encoding='utf-8').upper()
    for s in ('DROP TABLE', 'TRUNCATE', 'DELETE FROM','INSERT INTO','UPDATE PROJECT_DW'):
        assert s not in sql

def test_screening_disclaimer():
    sql=SQL_FILE.read_text(encoding='utf-8')
    assert 'not an approved flight corridor' in sql
    assert 'No synthetic source rows'.lower() in sql.lower()
