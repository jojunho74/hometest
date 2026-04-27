# -*- coding: utf-8 -*-
"""
fvisa-fetch.py — WorldJob+ 해외취업 모집공고 API (B490007/worldjob31/openApi31)
XML 구조: <WORLDJOB><HEADER>...</HEADER><BODY><ITEM>...</ITEM><totalCount>...</totalCount></BODY></WORLDJOB>
실행: python fvisa-fetch.py
"""
import json, math, os, sys, io, urllib.request, time
import xml.etree.ElementTree as ET
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY  = 'fd0e3d05449e164a7c3f2fc5a1c1853e48fbe19516aba543055b1eb60daafac3'
API_BASE = 'https://apis.data.go.kr/B490007/worldjob31/openApi31'
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
JS_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.js')
ROWS     = 100


def make_url(page, rows=ROWS):
    return (f'{API_BASE}'
            f'?serviceKey={API_KEY}'
            f'&pageNo={page}&numOfRows={rows}')


def fetch(url, retries=3):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/xml, application/xml, */*',
    })
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
            try:
                return raw.decode('utf-8')
            except UnicodeDecodeError:
                return raw.decode('euc-kr', errors='replace')
        except Exception as e:
            if attempt < retries - 1:
                print(f'  [재시도 {attempt+1}] {e}')
                time.sleep(2)
            else:
                raise


def parse(text):
    """
    <WORLDJOB>
      <HEADER><ERR_CD>00</ERR_CD>...</HEADER>
      <BODY>
        <ITEM><rctntcSj>...</rctntcSj>...</ITEM>
        ...
        <totalCount>566</totalCount>
      </BODY>
    </WORLDJOB>
    """
    idx = text.find('<?xml')
    if idx < 0:
        idx = text.find('<WORLDJOB')
    if idx > 0:
        text = text[idx:]

    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise Exception(f'XML 파싱 실패: {e}\n원문: {text[:300]}')

    err_cd = (root.findtext('.//ERR_CD') or '').strip()
    if err_cd and err_cd != '00':
        err_nm = root.findtext('.//ERR_NM') or ''
        raise Exception(f'API 오류: {err_cd} - {err_nm}')

    total = int(root.findtext('.//totalCount') or 0)

    items = []
    for el in root.findall('.//ITEM'):
        row = {child.tag: (child.text or '').strip() for child in el}
        items.append(row)

    return items, total


def main():
    print('=' * 55)
    print(' WorldJob+ 해외취업 모집공고 API 데이터 수집 시작')
    print('=' * 55)

    # 1단계: 총 건수 파악
    print('\n[1단계] 총 건수 확인 중...')
    try:
        text = fetch(make_url(1, 1))
        sample, total = parse(text)
    except Exception as e:
        print(f'[오류] {e}')
        sys.exit(1)

    if total == 0:
        print('[오류] 수집 가능한 데이터가 없습니다.')
        sys.exit(1)

    if sample:
        print('\n[필드 목록]')
        for k, v in sample[0].items():
            print(f'  {k}: {v[:70] if v else "(없음)"}')

    pages = math.ceil(total / ROWS)
    print(f'\n  총 {total:,}건 ({pages}페이지, 페이지당 {ROWS}건)')

    # 2단계: 전체 수집
    print(f'\n[2단계] 전체 데이터 수집 중...')
    all_items = []
    for p in range(1, pages + 1):
        try:
            text = fetch(make_url(p))
            items, _ = parse(text)
            all_items.extend(items)
            print(f'  [{p:2d}/{pages}] {len(items)}건 (누계: {len(all_items):,}건)')
            time.sleep(0.3)
        except Exception as e:
            print(f'  [경고] {p}페이지 오류: {e}')

    if not all_items:
        print('[오류] 수집된 데이터가 없습니다.')
        sys.exit(1)

    # 국가별 통계
    print(f'\n[완료] 총 {len(all_items):,}건 수집')
    print('\n[국가별 현황]')
    stats = {}
    for r in all_items:
        c = r.get('rctntcNationNm', '기타')
        stats[c] = stats.get(c, 0) + 1
    for c, cnt in sorted(stats.items(), key=lambda x: -x[1])[:10]:
        print(f'  {c}: {cnt}건')

    # 저장
    output = {
        'totalCount': total,
        'fetchedAt':  datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'items':      all_items,
    }
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'\n[저장] {OUT_FILE}')

    js_str = json.dumps(output, ensure_ascii=False, separators=(',', ':'))
    with open(JS_FILE, 'w', encoding='utf-8') as f:
        f.write(f'window.FVISA_DATA={js_str};')
    print(f'[저장] {JS_FILE}')
    print('[완료] index.html을 브라우저에서 열어 확인하세요.')


if __name__ == '__main__':
    main()
