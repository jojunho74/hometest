"""
Supabase 데이터 백업 스크립트
실행: python backup_db.py
결과: backup/ 폴더에 JSON 파일 저장
"""

import os, json
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

TABLES = [
    'school_programs',
    'university_news',
    'university_sites',
    'staff_job_postings',
    'job_postings',
    'student_applications',
    'consultations',
]

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = os.path.join(os.path.dirname(__file__), 'backup', timestamp)
os.makedirs(backup_dir, exist_ok=True)

summary = {}
for table in TABLES:
    try:
        res = sb.table(table).select('*').execute()
        data = res.data or []
        path = os.path.join(backup_dir, f'{table}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        summary[table] = len(data)
        print(f'  [OK] {table}: {len(data)}')
    except Exception as e:
        summary[table] = f'오류: {e}'
        print(f'  [ERR] {table}: {e}')

# 요약 파일
with open(os.path.join(backup_dir, '_summary.json'), 'w', encoding='utf-8') as f:
    json.dump({'timestamp': timestamp, 'tables': summary}, f, ensure_ascii=False, indent=2)

print(f'\n백업 완료: {backup_dir}')
print(f'총 {sum(v for v in summary.values() if isinstance(v, int))}개 레코드')
