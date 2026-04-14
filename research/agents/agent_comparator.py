"""
비교 에이전트 (agent_comparator.py)
역할: 수집된 게시글과 기존 DB 데이터를 비교하여 중복 제거
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']

def get_existing_posts(school_name: str = None) -> set:
    """
    기존 school_programs 테이블에서 (제목, 링크) 집합 반환
    school_name 지정 시 해당 학교만 조회
    """
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    query = sb.table('school_programs').select('title, link')
    if school_name:
        query = query.eq('school_name', school_name)
    res = query.execute()
    rows = res.data or []

    existing_titles = {r['title'].strip() for r in rows if r.get('title')}
    existing_links  = {r['link'].strip()  for r in rows if r.get('link')}
    return existing_titles, existing_links

def filter_new_posts(collected: list[dict]) -> list[dict]:
    """
    수집된 게시글에서 기존에 없는 신규 게시글만 반환
    중복 판단: 제목 일치 OR 링크 일치
    """
    if not collected:
        return []

    # 학교별로 분리하여 각각 비교
    by_school: dict[str, list] = {}
    for post in collected:
        sn = post['school_name']
        by_school.setdefault(sn, []).append(post)

    new_posts = []
    for school_name, posts in by_school.items():
        existing_titles, existing_links = get_existing_posts(school_name)
        log.info(f"{school_name}: 기존 {len(existing_titles)}개 대비 수집 {len(posts)}개 비교 중")

        for post in posts:
            title = (post.get('title') or '').strip()
            link  = (post.get('link')  or '').strip()

            if title in existing_titles:
                log.debug(f"  중복(제목): {title[:40]}")
                continue
            if link and link in existing_links:
                log.debug(f"  중복(링크): {link[:60]}")
                continue

            new_posts.append(post)
            existing_titles.add(title)  # 같은 실행 내 중복 방지
            existing_links.add(link)

        log.info(f"  → {school_name}: 신규 {sum(1 for p in new_posts if p['school_name'] == school_name)}개")

    log.info(f"중복 제거 완료: {len(collected)}개 → 신규 {len(new_posts)}개")
    return new_posts

def run(collected: list[dict]) -> list[dict]:
    """비교 실행, 신규 게시글만 반환"""
    return filter_new_posts(collected)

if __name__ == '__main__':
    # 단위 테스트용 샘플
    sample = [
        {'school_name': '테스트대학교', 'title': '2025 취업박람회 안내', 'link': 'https://example.com/1'},
        {'school_name': '테스트대학교', 'title': '중복 테스트 제목',   'link': 'https://example.com/2'},
    ]
    result = run(sample)
    print(f"신규 게시글: {len(result)}개")
    for p in result:
        print(p)
