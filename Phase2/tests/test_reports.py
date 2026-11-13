from datetime import datetime,timezone
from etl.reports import build_reports, TABLES

def test_table_names_are_whitelisted():
    assert len(TABLES)>=10
    assert all(t.startswith(('project_staging.','project_dw.')) for t in TABLES)

def test_generates_both_pdfs_in_test_only_folder(tmp_path):
    fixture={'counts':{x:0 for x in TABLES},'run':None,'dq_run':None,'dq':[],
             'rejects':[],'manifests':[],'database_bytes':0,
             'generated_utc':datetime.now(timezone.utc).isoformat()}
    a,b=build_reports(fixture,tmp_path)
    assert a.name=='Data_Cleaning_Report.pdf'
    assert b.name=='Data_Quality_Report.pdf'
    assert a.read_bytes()[:4]==b'%PDF'
    assert b.read_bytes()[:4]==b'%PDF'
    assert a.stat().st_size>1000 and b.stat().st_size>1000
