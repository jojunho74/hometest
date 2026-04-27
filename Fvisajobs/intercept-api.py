# -*- coding: utf-8 -*-
"""
intercept-api.py v2 — 미리보기 클릭 시 발생하는 모든 XHR/fetch 요청 캡처
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright

xhr_requests = []

def on_response(res):
    req = res.request
    rtype = req.resource_type
    # XHR, fetch, document 요청만 캡처 (이미지/CSS/폰트 제외)
    if rtype in ('xhr', 'fetch', 'document', 'other'):
        url = res.url
        # data.go.kr 내부 API나 외부 API 도메인 요청만 출력
        if 'data.go.kr' in url or 'apis.' in url or 'go.kr' in url:
            try:
                body = res.body().decode('utf-8', errors='replace')
            except Exception:
                body = ''
            item = {
                'type': rtype,
                'method': req.method,
                'status': res.status,
                'url': url,
                'body_head': body[:300]
            }
            xhr_requests.append(item)
            print(f'[{rtype.upper()}] {req.method} {res.status} {url}')
            if body and len(body) > 0 and '<' not in body[:5]:
                print(f'  body: {body[:150]}')

with sync_playwright() as pw:
    print('[시작] Chrome 실행...')
    try:
        browser = pw.chromium.launch(channel='chrome', headless=False)
    except Exception:
        browser = pw.chromium.launch(headless=False)

    context = browser.new_context(locale='ko-KR')
    page = context.new_page()
    page.on('response', on_response)

    page.goto('https://www.data.go.kr', timeout=20000, wait_until='domcontentloaded')

    print()
    print('='*55)
    print(' Chrome에서:')
    print(' 1. 로그인')
    print(' 2. "외국인력 채용정보" 검색 → API 클릭')
    print(' 3. 미리보기 버튼 클릭')
    print(' 4. 데이터 확인 후 여기서 Enter')
    print('='*55)

    input('>>> Enter: ')

    print()
    print(f'=== 캡처된 요청: {len(xhr_requests)}건 ===')
    for item in xhr_requests:
        print(json.dumps(item, ensure_ascii=False))

    with open('captured.json', 'w', encoding='utf-8') as f:
        json.dump(xhr_requests, f, ensure_ascii=False, indent=2)

    print('[저장] captured.json')
    browser.close()
