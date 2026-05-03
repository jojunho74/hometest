"""
수집 에이전트 (agent_collector.py)
역할: university_sites 테이블에 등록된 URL을 방문하여 게시글 목록을 수집
- 수집 우선순위: RSS → 정적(HTML) → 동적(Playwright)
- RSS: feedparser로 파싱 (가장 정확하고 안정적)
- 정적 페이지: requests + BeautifulSoup
- 동적 페이지(JS 렌더링): Playwright
"""

import os
import re
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
        seen_links = set()
        for item in items:
            if item.name == 'a':
                href = item.get('href', '')
                # <a> 안에 <h3>, <h2>, <h4>, <p>, <span> 순서로 제목 추출 시도
                title_tag = item.find(['h3', 'h2', 'h4', 'p', 'span'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                else:
                    # img 태그 제거 후 텍스트 추출
                    for img in item.find_all('img'):
                        img.decompose()
                    title = item.get_text(strip=True)
            else:
                a = item.find('a', href=True)
                if not a:
                    continue
                href = a.get('href', '')
                title_tag = item.find(['h3', 'h2', 'h4', 'p', 'span'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                else:
                    title = a.get_text(strip=True)
            abs_link = make_absolute(href, base_url)
            if title and href and len(title) > 3 and abs_link not in seen_links:
                seen_links.add(abs_link)
                results.append({'title': title, 'link': abs_link})
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

def _requests_get_safe(url: str, **kwargs):
    """SSL 오류에 강한 requests.get: 인증서 오류 → verify=False, 핸드셰이크 실패 → 레거시 TLS 어댑터"""
    import ssl, urllib3
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context

    try:
        return requests.get(url, verify=True, **kwargs)
    except requests.exceptions.SSLError as e:
        err = str(e)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 핸드셰이크 실패 → 레거시 TLS 컨텍스트 (TLS 1.0~1.2 허용, 오래된 서버 호환)
        ctx = create_urllib3_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if 'HANDSHAKE_FAILURE' in err or 'handshake' in err.lower():
            try:
                ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
                ctx.minimum_version = ssl.TLSVersion.TLSv1
            except Exception:
                pass

        class _LegacyTLSAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kw):
                kw['ssl_context'] = ctx
                super().init_poolmanager(*args, **kw)

        s = requests.Session()
        s.mount('https://', _LegacyTLSAdapter())
        kw = {k: v for k, v in kwargs.items() if k != 'verify'}
        return s.get(url, verify=False, **kw)

def collect_static(url: str, selector: str = None) -> list[dict]:
    """requests + BeautifulSoup으로 정적 페이지 수집 (SSL 오류 자동 처리)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    res = _requests_get_safe(url, headers=headers, timeout=15)
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

def is_rss_url(url: str) -> bool:
    """URL이 RSS/Atom 피드인지 판단"""
    url_lower = url.lower().split('?')[0]
    return any(kw in url_lower for kw in ['/rss', '/feed', '.xml', '/atom', 'rss.do', 'feed.do'])

def collect_rss(url: str) -> list[dict]:
    """RSS/Atom 피드 파싱으로 게시글 수집"""
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        raise ValueError(f"RSS 파싱 실패: {feed.bozo_exception}")
    results = []
    seen_links = set()
    for entry in feed.entries:
        title = (entry.get('title') or '').strip()
        link  = (entry.get('link')  or '').strip()
        if title and link and len(title) > 3 and link not in seen_links:
            seen_links.add(link)
            results.append({'title': title, 'link': link})
    return results

def detect_rss_from_page(url: str) -> str | None:
    """HTML 페이지에서 RSS 링크 자동 감지 (SSL 오류 자동 처리)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = _requests_get_safe(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        tag = soup.find('link', type=lambda t: t and 'rss' in t.lower())
        if tag and tag.get('href'):
            return make_absolute(tag['href'], url)
        tag = soup.find('link', type=lambda t: t and 'atom' in t.lower())
        if tag and tag.get('href'):
            return make_absolute(tag['href'], url)
    except Exception:
        pass
    return None

def collect_from_site(site: dict) -> list[dict]:
    """단일 사이트 수집 — RSS → 정적 → 동적 순서로 시도"""
    school_name = site['school_name']
    url = site['url']
    selector = site.get('selector')

    log.info(f"수집 시작: {school_name} → {url}")

    # 0차: RSS 수집 (URL이 RSS이거나 페이지에서 RSS 감지)
    rss_url = url if is_rss_url(url) else detect_rss_from_page(url)
    if rss_url:
        try:
            links = collect_rss(rss_url)
            if links:
                log.info(f"  → {len(links)}개 수집 완료 (RSS)")
                return [{'school_name': school_name, **l} for l in links]
            log.info(f"  RSS 수집 0개 → HTML 수집 전환")
        except Exception as e:
            log.warning(f"  RSS 수집 실패: {e} → HTML 수집 전환")

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
