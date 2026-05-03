"""
셀렉터 감지 에이전트 (agent_selector.py)
역할: 등록된 사이트에서 최적 셀렉터를 자동 감지하고 university_sites 테이블에 저장
"""

import os
import requests
import feedparser
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import load_dotenv
from urllib.parse import urljoin
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 후보 셀렉터 목록 (많이 사용되는 패턴 순서)
CANDIDATE_SELECTORS = [
    'table a[href*="mode=view"]',
    'table a[href*="seq="]',
    'table a[href*="idx="]',
    'table a[href*="no="]',
    'table a[href*="BoardView"]',
    'table a[href*="view"]',
    'a[href*="BoardView.do"]',
    'a[href*="board_view"]',
    'ul.board_list li a',
    'ul.bbs_list li a',
    '.board-list a',
    '.notice-list a',
    'tr td a',
]

def detect_rss(url: str) -> str | None:
    """페이지에서 RSS URL 감지"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=6)
        soup = BeautifulSoup(res.text, 'html.parser')
        tag = soup.find('link', type=lambda t: t and ('rss' in t.lower() or 'atom' in t.lower()))
        if tag and tag.get('href'):
            return urljoin(url, tag['href'])
    except Exception:
        pass
    # URL 자체가 RSS 패턴인지
    url_lower = url.lower().split('?')[0]
    if any(kw in url_lower for kw in ['/rss', '/feed', '.xml', '/atom', 'rss.do']):
        return url
    return None

def count_with_selector(soup: BeautifulSoup, selector: str, base_url: str) -> int:
    """셀렉터로 추출되는 유효 게시글 수 반환"""
    try:
        items = soup.select(selector)
        count = 0
        for item in items:
            if item.name == 'a':
                title = item.get_text(strip=True)
                href = item.get('href', '')
            else:
                a = item.find('a', href=True)
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a.get('href', '')
            if title and href and len(title) > 5:
                count += 1
        return count
    except Exception:
        return 0

def detect_selector_for_site(site: dict) -> dict:
    """단일 사이트 셀렉터 감지"""
    school_name = site['school_name']
    url = site['url']
    existing_selector = site.get('selector') or ''

    result = {
        'school_name': school_name,
        'url': url,
        'method': None,
        'selector': existing_selector,
        'count': 0,
        'changed': False
    }

    # 1. RSS 감지
    rss_url = detect_rss(url)
    if rss_url:
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                result['method'] = 'RSS'
                result['selector'] = ''
                result['count'] = len(feed.entries)
                result['rss_url'] = rss_url
                log.info(f"  {school_name}: RSS 감지 → {len(feed.entries)}개")
                return result
        except Exception:
            pass

    # 2. HTML 페이지 로드 (SSL 오류 자동 처리)
    try:
        from agent_collector import _requests_get_safe
        res = _requests_get_safe(url, headers=HEADERS, timeout=8)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
    except Exception as e:
        result['method'] = '실패'
        result['error'] = str(e)
        log.warning(f"  {school_name}: 페이지 로드 실패 - {e}")
        return result

    # 3. 기존 셀렉터 검증
    if existing_selector:
        count = count_with_selector(soup, existing_selector, url)
        if count > 0:
            result['method'] = '기존셀렉터'
            result['count'] = count
            log.info(f"  {school_name}: 기존 셀렉터 유효 ({count}개)")
            return result

    # 4. 후보 셀렉터 자동 탐색
    best_selector = ''
    best_count = 0
    for sel in CANDIDATE_SELECTORS:
        count = count_with_selector(soup, sel, url)
        if count > best_count:
            best_count = count
            best_selector = sel

    if best_count > 0:
        result['method'] = '자동감지'
        result['selector'] = best_selector
        result['count'] = best_count
        result['changed'] = (best_selector != existing_selector)
        log.info(f"  {school_name}: 자동감지 → {best_selector} ({best_count}개)")
    else:
        # 5. 날짜/작성자 패턴으로 자동 추출 가능한지 확인
        from agent_collector import parse_board_rows
        auto_posts = parse_board_rows(soup, url)
        if auto_posts:
            result['method'] = '자동추출'
            result['selector'] = ''
            result['count'] = len(auto_posts)
            log.info(f"  {school_name}: 자동추출 → {len(auto_posts)}개")
        else:
            result['method'] = '감지실패'
            result['count'] = 0
            log.warning(f"  {school_name}: 셀렉터 감지 실패")

    return result

def run() -> list[dict]:
    """전체 사이트 셀렉터 감지 실행"""
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = sb.table('university_sites').select('*').eq('is_active', True).execute()
    sites = res.data or []

    if not sites:
        log.warning("등록된 활성 사이트가 없습니다")
        return []

    log.info(f"총 {len(sites)}개 사이트 셀렉터 감지 시작")
    results = []

    for site in sites:
        result = detect_selector_for_site(site)
        results.append(result)

        # 자동 감지로 새 셀렉터 발견 시 DB 업데이트
        if result.get('changed') and result.get('selector'):
            try:
                sb.table('university_sites').update({
                    'selector': result['selector']
                }).eq('school_name', site['school_name']).execute()
                log.info(f"  → {site['school_name']} 셀렉터 자동 저장")
            except Exception as e:
                log.warning(f"  셀렉터 저장 실패: {e}")

    return results

if __name__ == '__main__':
    results = run()
    print(f"\n감지 결과: {len(results)}개 사이트")
    for r in results:
        print(f"  {r['school_name']}: [{r['method']}] {r.get('selector','')} ({r['count']}개)")
