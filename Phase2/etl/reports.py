"""WP-09: generate both required PDFs from the *connected warehouse* only.

Requires psycopg[binary] and reportlab. Invoke from read-only GitHub Actions
warehouse job; it never inserts/updates Neon. No synthetic counts are allowed.
Reports disclose missing DQ runs, missing FAA coverage and 2D grid limits.
"""
from __future__ import annotations
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from typing import Any

TABLES = (
    'project_staging.stg_adsb_position',
    'project_staging.stg_reject',
    'project_staging.stg_airspace_zone',
    'project_staging.stg_restriction_snapshot',
    'project_dw.dim_time',
    'project_dw.dim_site',
    'project_dw.dim_vehicle',
    'project_dw.dim_spatial_grid',
    'project_dw.dim_weather',
    'project_dw.dim_airspace_zone',
    'project_dw.fact_vehicle_tracking',
    'project_dw.fact_flight_journey',
    'project_dw.fact_close_encounter',
    'project_dw.fact_airspace_occupancy',
    'project_dw.fact_restriction_activation',
)


def query(conn, sql: str, params: tuple = ()) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return list(cur.fetchall())


def snapshot(conn) -> dict[str, Any]:
    counts = {}
    for table in TABLES:  # Hard-coded identifiers only, never from external input.
        counts[table] = int(query(conn, f'SELECT COUNT(*) FROM {table}')[0][0])
    run = query(conn, '''
        SELECT etl_run_id,run_mode,started_at,status,code_version,rows_read,
               rows_accepted,rows_rejected,rows_duplicate,critical_dq_failures
        FROM project_staging.etl_run_log ORDER BY etl_run_id DESC LIMIT 1
    ''')
    latest_dq = query(conn, 'SELECT MAX(etl_run_id) FROM project_staging.dq_result')[0][0]
    dq = (query(conn, '''
        SELECT check_id,check_name,severity,status,observed_value,expected_value
        FROM project_staging.dq_result WHERE etl_run_id=%s ORDER BY check_id
    ''', (latest_dq,)) if latest_dq is not None else [])
    rejects = query(conn, '''
        SELECT source_system,reason_code,COUNT(*) AS num
        FROM project_staging.stg_reject GROUP BY 1,2 ORDER BY 3 DESC,1,2 LIMIT 30
    ''')
    manifests = query(conn, '''
        SELECT source_name,source_url,license_name,attribution,fetched_at,
               file_name,byte_size,sha256,object_key
        FROM project_staging.source_manifest ORDER BY fetched_at DESC LIMIT 25
    ''')
    storage = int(query(conn, 'SELECT pg_database_size(current_database())')[0][0])
    return {'counts':counts,'run':run[0] if run else None,'dq_run':latest_dq,
            'dq':dq,'rejects':rejects,'manifests':manifests,'database_bytes':storage,
            'generated_utc':datetime.now(timezone.utc).isoformat()}


def _styles():
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    a=getSampleStyleSheet()
    a.add(ParagraphStyle(name='AGSubtitle',parent=a['BodyText'],fontSize=9,leading=13,spaceAfter=12,textColor=colors.HexColor('#555555')))
    a.add(ParagraphStyle(name='AGFoot',parent=a['BodyText'],fontSize=8,leading=11))
    return a


def _str(v: Any) -> str:
    if v is None:return 'NULL / unavailable'
    return str(v)


def _text(v:Any):
    from reportlab.platypus import Paragraph
    return Paragraph(escape(_str(v)).replace('\n',' '),_styles()['AGFoot'])


def _tbl(rows: list[tuple|list], widths: list[int] | None = None):
    from reportlab.platypus import Table,TableStyle
    from reportlab.lib import colors
    if not rows:return []
    t=Table([[_text(c) for c in row] for row in rows],
            colWidths=widths or [519/len(rows[0])]*len(rows[0]),
            hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaeef1')),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#cccccc')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),
    ]))
    return [t]


def _report(path: Path,title: str,sections: list[tuple[str,str|list[list|tuple]]],data:dict[str,Any]) -> None:
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,KeepTogether
    from reportlab.lib.pagesizes import A4
    s=_styles()
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=42,bottomMargin=44)
    story=[Paragraph(escape(title),s['Title']),
           Paragraph('AeroGrid | Source: live Neon warehouse | UTC: '+escape(data['generated_utc']),s['AGSubtitle'])]
    for head,body in sections:
        story.append(Spacer(1,10))
        story.append(Paragraph(escape(head),s['Heading2']))
        if isinstance(body,str):story.append(Paragraph(escape(body).replace('\n','<br/>'),s['BodyText']))
        else:story.extend(_tbl(body))
    doc.build(story)


def build_reports(data: dict[str, Any], dest: Path) -> tuple[Path,Path]:
    dest.mkdir(parents=True,exist_ok=True)
    run=data['run']
    run_info=(f'Latest ETL run ID: {run[0]}, mode={run[1]}, started={run[2]}, '
              f'status={run[3]}, version={run[4]}' if run else 'NO ETL RUN FOUND')
    s=data['counts']; tracked=s['project_dw.fact_vehicle_tracking']; staged=s['project_staging.stg_adsb_position']
    accepted_rows=staged # a total (includes rejected), not accepted count
    source_rows=[('Source','License','Fetched UTC','Bytes','SHA-256')]
    for m in data['manifests']:
        source_rows.append((m[0],m[2],m[4],m[6],m[7]))
    if len(source_rows)==1:source_rows.append(('NO MANIFESTS','Unavailable','—','—','—'))
    source_details = '\n'.join(f'Source {i+1}: {m[0]} | URL: {m[1]} | Attribution: {m[3]} | Object key: {m[8]}' for i,m in enumerate(data['manifests'])) or 'No source manifest details stored.'
    rejects=[('Source','Reason','Count')]+list(data['rejects'])
    if len(rejects)==1:rejects.append(('No stored rejects','—',0))
    cleaning=[
        ('Run details',run_info),
        ('Staging and warehouse counts',[
            ('Component','Stored records'),('Staging ADS-B positions (all statuses)',staged),
            ('Warehouse tracking facts',tracked),
            ('Stored rejection records',s['project_staging.stg_reject']),
            ('Staged FAA airspace features',s['project_staging.stg_airspace_zone']),
            ('Staged FAA restriction snapshots',s['project_staging.stg_restriction_snapshot'])]),
        ('Source inventory and provenance (latest 25)',source_rows),
        ('Source URLs and attribution',source_details),
        ('Rejected records by source and rule',rejects),
        ('Cleaning methods','Source normalizers validate timestamps, position units, identifiers, and coordinates. Accepted records enter staging; rejected records retain an auditable reason. Staging rows include all statuses, so staging totals must not be called accepted totals. Source-specific duplicate handling is recorded by ETL run.'),
        ('Limitations and provenance','January 2022 KBTP Tartan positions are historical, while current FAA TFR snapshots are from 2026. Do not join present restrictions to historical flights. Unknown on_ground values remain NULL; airborne eligibility is inferred in WP07-AIR-01. The spatial grid is 2D (0.01-degree), not an altitude-band grid.'),
        ('Data authenticity','Production evidence is based on source-linked real rows, not synthetic demonstration records. Zero-source coverage is reported as zero, not imputed.'),
        ('Reproduction','Run WP-04 staging checks, WP-06 core fact reconciliation and WP-07 derived facts verifier through protected warehouse CI. Regenerate this PDF using python -m etl.reports with the read-only Neon connection in CI.')]
    p1=dest/'Data_Cleaning_Report.pdf';_report(p1,'Data Cleaning Report',cleaning,data)
    dq=data['dq']; critical=sum(row[2]=='CRITICAL' and row[3]=='FAIL' for row in dq)
    warns=sum(row[3]=='WARN' for row in dq)
    counts=[('Schema.table','Rows')]+[(k,int(v)) for k,v in s.items()]
    dq_rows=[('Check ID','Severity','Status','Observed / Expected')]+[
        (r[0],r[2],r[3],f'{r[4]} / {r[5]}') for r in dq]
    if not dq:dq_rows.append(('NO STORED DQ','—','NOT VERIFIED','—'))
    quality=[
        ('Audit summary',f'DQ run: {data["dq_run"] if data["dq_run"] is not None else "NONE"}; '
                          f'critical FAIL checks: {critical}; warning checks: {warns}. '
                          +('No stored DQ evidence is available; report is NOT an acceptance proof.' if not dq else 'Refer to each check below.')),
        ('Check catalog results',dq_rows),
        ('Real warehouse row counts',counts),
        ('Capacity',f'Actual PostgreSQL database size: {data["database_bytes"]:,} bytes. Object-storage usage is not available from the PostgreSQL connection; do not equate manifest bytes with current bucket usage.'),
        ('Encounter and restriction limitations','The WP07-v1 encounter algorithm requires identical timestamps. Near-time diagnostics were separate analytical SQL, not the production algorithm. No historical 2022 TFRs are inferred from 2026 FAA services. Zero derived rows may be legitimate source coverage, not evidence of a missing SQL table.'),
        ('Decision rule','Any stored CRITICAL FAIL blocks trusted publication even if this PDF can be generated. A green unit-test run alone does not establish data quality.'),
        ('Evidence and reproducibility',f'{run_info}. DQ check IDs map to Phase2/etl/dq.py and Phase2/docs/06_data_quality_and_reports.md. Verify the source manifests and rejected-row counts directly in Neon.')]
    p2=dest/'Data_Quality_Report.pdf';_report(p2,'Data Quality Report',quality,data)
    return p1,p2


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',default='reports')
    args=p.parse_args(argv)
    if not os.getenv('DATABASE_URL'):p.error('DATABASE_URL required (protected CI secret)')
    import psycopg
    with psycopg.connect(os.environ['DATABASE_URL'],connect_timeout=15) as conn:
        with conn.cursor() as c:c.execute('SET LOCAL statement_timeout=\'8min\'')
        data=snapshot(conn)
        conn.rollback() # Entire connection is SELECT-only.
    p1,p2=build_reports(data,Path(args.output_dir))
    print('Created',p1.name,p1.stat().st_size,'bytes')
    print('Created',p2.name,p2.stat().st_size,'bytes')
    if data['dq_run'] is None:
        print('WARNING: DQ results are not persisted; report is INCOMPLETE evidence')
    return 0

if __name__=='__main__':raise SystemExit(main())
