# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import urllib.request, urllib.parse, re

API_KEY = 'fd0e3d05449e164a7c3f2fc5a1c1853e48fbe19516aba543055b1eb60daafac3'
ENCODED_KEY = urllib.parse.quote(API_KEY, safe='')

urls = {
    'path+raw': f'https://apis.data.go.kr/B490007/Employment/getApiEmployment?serviceKey={API_KEY}&pageNo=1&numOfRows=3',
    'query+raw': f'https://apis.data.go.kr/B490007/Employment?serviceKey={API_KEY}&method=getApiEmployment&pageNo=1&numOfRows=3',
    'path+encoded': f'https://apis.data.go.kr/B490007/Employment/getApiEmployment?serviceKey={ENCODED_KEY}&pageNo=1&numOfRows=3',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0',
    'Accept': '*/*',
    'Referer': 'https://www.data.go.kr/',
}

for name, url in urls.items():
    print(f'\n[{name}]')
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            body = res.read().decode('utf-8', errors='replace')
            print(f'OK {res.status}')
            print(body[:400])
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'HTTP {e.code} FAIL')
        msgs = re.findall(r'<(?:title|p|h\d)[^>]*>(.*?)</(?:title|p|h\d)>', body, re.I|re.S)
        for m in msgs[:4]:
            t = m.strip()
            if t:
                print(' ', t[:120])
        if not msgs:
            print(body[:200])
    except Exception as e:
        print(f'ERR {e}')
