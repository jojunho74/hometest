"""
게시 에이전트 (agent_publisher.py)
역할: 신규 게시글을 Supabase school_programs 테이블에 INSERT
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']

def publish_posts(new_posts: list[dict]) -> dict:
    """
    신규 게시글을 school_programs 테이블에 INSERT
    Returns: { success: int, failed: int, errors: list }
    """
    if not new_posts:
        log.info("게시할 신규 게시글이 없습니다")
        return {'success': 0, 'failed': 0, 'errors': []}

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    success = 0
    failed = 0
    errors = []

    # 배치 INSERT (한 번에 최대 50개씩)
    batch_size = 50
    for i in range(0, len(new_posts), batch_size):
        batch = new_posts[i:i+batch_size]
        rows = [
            {
                'school_name': p['school_name'],
                'title': p['title'],
                'link': p['link'],
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            for p in batch
        ]
        try:
            res = sb.table('school_programs').insert(rows).execute()
            inserted = len(res.data or [])
            success += inserted
            log.info(f"  배치 {i//batch_size + 1}: {inserted}개 게시 완료")
        except Exception as e:
            err_msg = str(e)
            log.error(f"  ❌ 배치 INSERT 실패: {err_msg}")
            failed += len(batch)
            errors.append(err_msg)

    # 마지막 수집 시간 업데이트
    update_last_crawled(new_posts, sb)

    log.info(f"게시 완료: 성공 {success}개 / 실패 {failed}개")
    return {'success': success, 'failed': failed, 'errors': errors}

def update_last_crawled(posts: list[dict], sb):
    """university_sites 테이블의 last_crawled_at 업데이트"""
    school_names = list({p['school_name'] for p in posts})
    now = datetime.now(timezone.utc).isoformat()
    for school_name in school_names:
        try:
            sb.table('university_sites').update({'last_crawled_at': now}).eq('school_name', school_name).execute()
        except Exception as e:
            log.warning(f"last_crawled_at 업데이트 실패 ({school_name}): {e}")

def run(new_posts: list[dict]) -> dict:
    """게시 실행"""
    return publish_posts(new_posts)

if __name__ == '__main__':
    # 단위 테스트용 샘플 (실제로 INSERT되므로 주의)
    sample = [
        {'school_name': '테스트대학교', 'title': '[테스트] 자동 수집 게시글', 'link': 'https://example.com/test-auto'},
    ]
    confirm = input(f"⚠️ {len(sample)}개 게시글을 실제로 INSERT합니까? (yes/no): ")
    if confirm.lower() == 'yes':
        result = run(sample)
        print(f"결과: {result}")
    else:
        print("취소됨")
