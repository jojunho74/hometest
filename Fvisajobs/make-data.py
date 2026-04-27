# -*- coding: utf-8 -*-
"""
make-data.py — 브라우저에서 저장한 XML을 data.json으로 변환

사용법:
  1. 아래 URL을 Chrome 주소창에 입력
     https://apis.data.go.kr/B490007/Employment?serviceKey=fd0e3d05449e164a7c3f2fc5a1c1853e48fbe19516aba543055b1eb60daafac3&method=getApiEmployment&pageNo=1&numOfRows=1000
  2. Ctrl+S 로 저장 (파일명: page.xml 또는 아무 이름)
  3. 저장된 파일을 이 폴더(Fvisajobs)에 넣기
  4. python make-data.py 파일명.xml

"""
import sys, json, os
import xml.etree.ElementTree as ET
from datetime import datetime

def convert(xml_path):
    print(f'[변환] {xml_path}')
    with open(xml_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # XML 파싱
    root = ET.fromstring(content)
    result_code = root.findtext('.//resultCode') or ''
    if result_code != '00':
        print(f'[오류] API 오류 코드: {result_code}')
        sys.exit(1)

    items = []
    for item in root.findall('.//item'):
        obj = {}
        for child in item:
            obj[child.tag] = (child.text or '').strip()
        items.append(obj)

    total = root.findtext('.//totalCount') or str(len(items))

    output = {
        'totalCount': int(total),
        'fetchedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'items': items,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'[완료] {len(items)}건 → data.json 저장')
    print(f'       발견된 필드: {list(items[0].keys()) if items else []}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('사용법: python make-data.py 저장한파일.xml')
        print()
        print('1. 아래 URL을 Chrome에서 열고 Ctrl+S로 저장하세요:')
        print('   https://apis.data.go.kr/B490007/Employment'
              '?serviceKey=fd0e3d05449e164a7c3f2fc5a1c1853e48fbe19516aba543055b1eb60daafac3'
              '&method=getApiEmployment&pageNo=1&numOfRows=1000')
        print()
        print('2. 저장된 파일을 이 폴더에 넣고 실행:')
        print('   python make-data.py 파일명.xml')
    else:
        convert(sys.argv[1])
