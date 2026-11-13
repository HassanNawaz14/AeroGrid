"""WP-10 reporting view verifier. Default rollback; approved CI --apply only."""
from __future__ import annotations
import argparse
import os
from pathlib import Path

VIEW_NAMES = (
    'vw_traffic_density_hour_grid', 'vw_occupied_grid_hours',
    'vw_monthly_traffic', 'vw_peak_site_hours', 'vw_daily_encounter_hotspots',
    'vw_encounter_vehicle_types', 'vw_restriction_traffic_impact',
    'vw_weather_operations', 'vw_corridor_capacity_inputs',
    'vw_candidate_corridor_cells',
)
SQL_FILE = Path(__file__).resolve().parents[1] / 'sql' / '05_reporting' / '01_reporting_views.sql'


def verify(conn, apply: bool = False) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("SET LOCAL statement_timeout = '8min'")
        cur.execute(SQL_FILE.read_text(encoding='utf-8'))
        results={}
        for name in VIEW_NAMES:
            qualified='project_reporting.'+name
            # Identifier is from hardcoded whitelist, not user input.
            cur.execute(f'GRANT SELECT ON {qualified} TO aerogrid_reader')
            cur.execute(f'SELECT count(*) FROM {qualified}')
            results[name]=int(cur.fetchone()[0])
            cur.execute('SELECT has_table_privilege(%s,%s,%s)',
                        ('aerogrid_reader',qualified,'SELECT'))
            if cur.fetchone()[0] is not True:
                raise AssertionError(f'Reader cannot SELECT {qualified}')
        return results


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply',action='store_true')
    a=p.parse_args(argv)
    if a.apply and (os.getenv('GITHUB_ACTIONS')!='true' or os.getenv('WAREHOUSE_CI_APPROVED')!='true'):
        p.error('Persistence requires approved protected warehouse GitHub Actions')
    if not os.getenv('DATABASE_URL'):p.error('DATABASE_URL required in approved CI')
    import psycopg
    with psycopg.connect(os.environ['DATABASE_URL'],connect_timeout=15) as conn:
        try:
            res=verify(conn,apply=a.apply)
            for name,n in res.items():print(f'{name}={n} rows')
            if a.apply:
                conn.commit()
                print('WP10 PASS; persisted 10 approved reporting view definitions')
            else:
                conn.rollback()
                print('WP10 PASS; ROLLBACK - no persisted view changes')
            return 0
        except Exception as exc:
            conn.rollback()
            print(f'WP10 FAIL; type={type(exc).__name__}; ROLLBACK')
            return 1

if __name__=='__main__':raise SystemExit(main())
