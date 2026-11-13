from etl.dq import CHECKS, assess, summary, evaluate, Check

class FakeCursor:
    def __init__(self, conn): self.conn=conn
    def execute(self, sql):
        self.conn.calls.append(sql)
        self.result=(self.conn.values.pop(0),)
    def fetchone(self):return self.result

class FakeConn:
    def __init__(self, vals): self.values=list(vals);self.calls=[];self.inserts=[]
    def cursor(self):return FakeCursor(self)
    def execute(self,sql,params):self.inserts.append((sql,params))

def test_catalog_ids_are_unique():
    assert len(CHECKS)>=20
    assert len({c.check_id for c in CHECKS})==len(CHECKS)
    assert all(c.severity in ('CRITICAL','WARNING') for c in CHECKS)

def test_coverage_guards_separate_empty_source_from_zero_events():
    by_id={c.check_id:c for c in CHECKS}
    # Only the primary source is a fatal guard; unwired sources warn.
    assert by_id['DQ-G-001'].severity=='CRITICAL'
    for check_id in ('DQ-G-002','DQ-G-003','DQ-G-004'):
        assert by_id[check_id].severity=='WARNING'
    # A zero accepted-row count must be observed as 1, not 0.
    assert 'CASE WHEN count(*) FILTER (WHERE reject_reason IS NULL) = 0 THEN 1 ELSE 0 END' in by_id['DQ-G-001'].sql

def test_only_read_only_sql():
    for c in CHECKS:
        assert c.sql.lstrip().upper().startswith('SELECT')
        assert 'INSERT ' not in c.sql.upper()

def test_count_status():
    assert assess(CHECKS[0],0)=='PASS'
    assert assess(CHECKS[0],2)=='FAIL'
    warning=next(c for c in CHECKS if c.severity=='WARNING')
    assert assess(warning,1)=='WARN'

def test_negative_count_refused():
    try: assess(CHECKS[0],-1)
    except ValueError: pass
    else: assert False

def test_all_results_persist_including_failures():
    conn=FakeConn([1]*len(CHECKS))
    rows=evaluate(conn,123,persist=True)
    assert len(rows)==len(CHECKS)==len(conn.inserts)
    assert any(r['status']=='FAIL' for r in rows)
    assert any(r['status']=='WARN' for r in rows)
    assert summary(rows)['FAIL']>0

def test_dry_run_no_writes():
    conn=FakeConn([0]*len(CHECKS))
    assert len(evaluate(conn,persist=False))==len(CHECKS)
    assert not conn.inserts

def test_requires_run_id():
    try: evaluate(FakeConn([]),persist=True)
    except ValueError: pass
    else: assert False
