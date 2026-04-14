"""
수집 에이전트 (agent_collector.py)
역할: university_sites 테이블에 등록된 URL을 방문하여 게시글 목록을 수집
- 작성자 또는 날짜가 있는 행만 수집 (네비게이션 링크 제외)
- 정적 페이지: requests + BeautifulSoup
- 동적 페이지(JS 렌더링): Playwright
"""

import os
import re
import requests
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

# 날짜 패턴: 2024.01.23 / 2024-01-23 / 24.01.23 / 2024/01/23
DATE_PATTERN = re.compile(r'\d{2,4}[.\-/]\d{1,2}[.\-/]\d{1,2}')

def get_active_sites():
    """university_sites 테이블에서 활성화된 사이트 목록 조회"""
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = sb.table('university_sites').select('*').eq('is_active', True).execute()
    return res.data or []

def has_date_or_author(row_text: str) -> bool:
    """행 텍스트에 날짜 또는 작성자 패턴이 있는지 확인"""
    if DATE_PATTERN.search(row_text):
        return True
    # 작성자 관련 키워드 (관리자, 담당자, 교학처 등)
    author_keywords = ['관리자', '담당', '처', '팀', '부서', '과', '원', '실', '센터']
    for kw in author_keywords:
        if kw in row_text:
            return True
    return False

def parse_board_rows(soup, base_url: str, selector: str = None) -> list[dict]:
    """
    게시판 행(tr 또는 li) 기준으로 파싱
    - selector 지정 시: 해당 요소에서 추출
    - 미지정 시: 날짜/작성자가 있는 행만 추출
    """
    results = []

    if selector:
        items = soup.select(selector)
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
            if title and href and len(title) > 3:
                results.append({'title': title, 'link': make_absolute(href, base_url)})
        return results

    # ── 자동 감지: 테이블 행 방식 ──
    seen_links = set()
    for tr in soup.find_all('tr'):
        row_text = tr.get_text(separator=' ', strip=True)
        if not has_date_or_author(row_text):
            continue
        # 행 안의 링크 중 제목으로 보이는 것 (가장 긴 텍스트)
        links = tr.find_all('a', href=True)
        best = None
        for a in links:
            t = a.get_text(strip=True)
            if len(t) > 3 and (best is None or len(t) > len(best[0])):
                best = (t, a.get('href', ''))
        if best:
            title, href = best
            abs_link = make_absolute(href, base_url)
            if abs_link not in seen_links:
                seen_links.add(abs_link)
                results.append({'title': title, 'link': abs_link})

    if results:
        log.debug(f"  테이블 행 방식으로 {len(results)}개 추출")
        return results

    # ── 자동 감지: li 목록 방식 ──
    for li in soup.find_all('li'):
        row_text = li.get_text(separator=' ', strip=True)
        if not has_date_or_author(row_text):
            continue
        a = li.find('a', href=True)
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get('href', '')
        if title and len(title) > 3:
            results.append({'title': title, 'link': make_absolute(href, base_url)})

    return results

def collect_static(url: str, selector: str = None) -> list[dict]:
    """requests + BeautifulSoup으로 정적 페이지 수집"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    return parse_board_rows(soup, url, selector)

def collect_dynamic(url: str, selector: str = None) -> list[dict]:
    """Playwright로 JS 렌더링 페이지 수집"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, 'html.parser')
    return parse_board_rows(soup, url, selector)

def make_absolute(href: str, base_url: str) -> str:
    return urljoin(base_url, href)

def collect_from_site(site: dict) -> list[dict]:
    """단일 사이트 수집 — 정적 실패 시 동적으로 자동 전환"""
    school_name = site['school_name']
    url = site['url']
    selector = site.get('selector')

    log.info(f"수집 시작: {school_name} → {url}")

    # 1차: 정적 수집
    try:
        links = collect_static(url, selector)
        if links:
            log.info(f"  → {len(links)}개 수집 완료 (정적)")
            return [{'school_name': school_name, **l} for l in links]
        else:
            log.info(f"  정적 수집 0개 → 동적 수집 전환")
    except Exception as e:
        log.warning(f"  정적 수집 실패: {e} → 동적 수집 전환")

    # 2차: Playwright 동적 수집
    try:
        links = collect_dynamic(url, selector)
        log.info(f"  → {len(links)}개 수집 완료 (동적)")
        return [{'school_name': school_name, **l} for l in links]
    except Exception as e:
        log.error(f"  ❌ {school_name} 동적 수집도 실패: {e}")
        return []

def run() -> list[dict]:
    """전체 수집 실행"""
    sites = get_active_sites()
    if not sites:
        log.warning("등록된 활성 사이트가 없습니다")
        return []

    log.info(f"총 {len(sites)}개 사이트 수집 시작")
    all_posts = []
    for site in sites:
        posts = collect_from_site(site)
        all_posts.extend(posts)

    log.info(f"전체 수집 완료: {len(all_posts)}개")
    return all_posts

if __name__ == '__main__':
    posts = run()
    print(f"\n수집 결과: {len(posts)}개")
    for p in posts[:10]:
        print(p)
