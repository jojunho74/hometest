"""
웹서버 (server.py)
n8n HTTP Request 노드에서 호출받아 파이프라인 실행
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import sys
import os
import re
from urllib.parse import urljoin

# 같은 폴더에서 실행
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import agent_automation
import agent_selector
import agent_collector

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/run':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # 백그라운드에서 파이프라인 실행
            def run():
                os.makedirs('logs', exist_ok=True)
                result = agent_automation.run_pipeline()
                print(f"[완료] {result}")

            t = threading.Thread(target=run)
            t.start()

            self.wfile.write(json.dumps({
                'status': 'started',
                'message': '수집 파이프라인이 시작되었습니다'
            }, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/preview':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            sites = agent_collector.get_active_sites()
            preview = []
            for site in sites:
                posts = agent_collector.collect_from_site(site)
                preview.append({
                    'school_name': site['school_name'],
                    'posts': posts[:5]  # 최대 5개만 미리보기
                })
            self.wfile.write(json.dumps({
                'status': 'ok',
                'preview': preview
            }, ensure_ascii=False).encode('utf-8'))

        elif self.path == '/detect':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            detect_results = {'status': 'running', 'results': []}

            def do_detect():
                detect_results['results'] = agent_selector.run()
                detect_results['status'] = 'done'
                print(f"[감지완료] {len(detect_results['results'])}개")

            t = threading.Thread(target=do_detect)
            t.start()
            t.join(timeout=120)  # 최대 2분 대기

            self.wfile.write(json.dumps({
                'status': 'ok',
                'results': detect_results['results']
            }, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/crawl':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                payload = json.loads(body)
                url = payload.get('url', '').strip()
            except Exception:
                url = ''
            if not url:
                self.wfile.write(json.dumps({'status': 'error', 'message': 'URL 없음'}, ensure_ascii=False).encode('utf-8'))
                return
            try:
                result = crawl_article(url)
                self.wfile.write(json.dumps({'status': 'ok', **result}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        elif self.path.startswith('/proxy?url='):
            import urllib.parse, urllib.request
            try:
                target_url = urllib.parse.unquote(self.path[len('/proxy?url='):])
                req = urllib.request.Request(target_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'ko-KR,ko;q=0.9',
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    html = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(html)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")


def _mirror_image(img_url, page_url):
    """외부 이미지를 Supabase Storage에 업로드하고 공개 URL 반환. 실패 시 원본 URL 반환."""
    import requests, hashlib, mimetypes
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    sb_key = os.environ.get('SUPABASE_KEY', '')
    if not sb_url or not sb_key:
        return img_url
    try:
        r = requests.get(img_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': page_url,
            'Accept': 'image/*,*/*',
        }, timeout=10)
        if r.status_code != 200 or len(r.content) < 1000:
            return img_url
        ct = r.headers.get('Content-Type', 'image/jpeg').split(';')[0].strip()
        ext = mimetypes.guess_extension(ct) or '.jpg'
        if ext in ('.jpe', '.jpeg'):
            ext = '.jpg'
        path = f"cardnews/{hashlib.md5(img_url.encode()).hexdigest()}{ext}"
        up = requests.post(
            f"{sb_url}/storage/v1/object/logo/{path}",
            headers={'Authorization': f'Bearer {sb_key}', 'Content-Type': ct, 'x-upsert': 'true'},
            data=r.content, timeout=15
        )
        if up.status_code in (200, 201):
            return f"{sb_url}/storage/v1/object/public/logo/{path}"
    except Exception as e:
        print(f"[이미지 미러 실패] {img_url}: {e}")
    return img_url


def crawl_article(url):
    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'ko-KR,ko;q=0.9',
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, 'html.parser')

    # 제목
    title = ''
    for sel in ['h1', '.title', '.subject', '#subject', '.view-title', 'h2']:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 4:
            title = el.get_text(strip=True)
            break
    if not title:
        og = soup.find('meta', {'property': 'og:title'})
        if og:
            title = og.get('content', '').strip()
    if not title:
        t = soup.find('title')
        if t:
            title = t.text.strip()

    # 본문 텍스트
    content_text = ''
    for sel in ['.view-content', '.board-content', '.bbs-view', '#content', 'article', '.post-body', '.view_content', '.td_content']:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 30:
            content_text = el.get_text(separator=' ', strip=True)
            break
    if not content_text:
        paras = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 20]
        content_text = ' '.join(paras)

    content_100 = content_text[:100] if len(content_text) > 100 else content_text

    # 부제목 (첫 의미있는 문장)
    subtitle = ''
    if content_text:
        for s in re.split(r'[.。\n]', content_text):
            s = s.strip()
            if 10 < len(s) < 80 and s != title:
                subtitle = s
                break

    # 이미지 (최대 3개)
    images = []
    # 명백한 UI 요소만 제외 (logo는 포함 허용)
    skip_kw = ['icon', 'btn', 'button', 'arrow', 'bullet', 'banner_top', '/common/', 'spinner', 'loading']
    # 명백한 비이미지 확장자 제외 목록
    skip_ext = ['.js', '.css', '.pdf', '.hwp', '.doc', '.xls', '.zip', '.svg']
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-original') or ''
        if not src or src.startswith('data:'):
            continue
        abs_src = urljoin(url, src)
        if not abs_src.startswith('http'):
            continue
        lower = abs_src.lower()
        if any(kw in lower for kw in skip_kw):
            continue
        if any(lower.endswith(ext) for ext in skip_ext):
            continue
        # 크기 필터: 명시된 경우만 적용
        try:
            w = int(img.get('width', 0))
            h = int(img.get('height', 0))
            if w and h and (w < 60 or h < 60):
                continue
            # alt가 공백이고 크기가 아주 작으면 장식 이미지로 간주
            if (w and w < 30) or (h and h < 30):
                continue
        except Exception:
            pass
        if abs_src not in images:
            images.append(abs_src)
        if len(images) >= 3:
            break

    # 날짜
    date_str = ''
    for prop in ['article:published_time', 'og:updated_time']:
        m = soup.find('meta', {'property': prop})
        if m and m.get('content'):
            date_str = m['content'][:10]
            break
    if not date_str:
        t = soup.find('time')
        if t:
            date_str = (t.get('datetime') or t.text.strip())[:10]
    if not date_str:
        m = re.search(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', soup.get_text())
        if m:
            date_str = f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"

    # 조회수
    view_count = None
    page_text = soup.get_text()
    for pat in [r'조회\s*[수]?\s*[:：]?\s*([0-9,]+)', r'[Hh]it\s*[:：]?\s*([0-9,]+)', r'[Rr]ead\s*[:：]?\s*([0-9,]+)', r'조회수\D{0,5}([0-9,]+)']:
        m = re.search(pat, page_text)
        if m:
            try:
                view_count = int(m.group(1).replace(',', ''))
                break
            except Exception:
                pass

    return {
        'title': title,
        'subtitle': subtitle,
        'content': content_100,
        'date': date_str,
        'images': images,
        'view_count': view_count,
        'url': url,
    }


if __name__ == '__main__':
    port = 8765
    print(f"서버 시작: http://localhost:{port}")
    print(f"수집 실행: POST http://localhost:{port}/run")
    print(f"상태 확인: GET  http://localhost:{port}/health")
    HTTPServer(('', port), Handler).serve_forever()
