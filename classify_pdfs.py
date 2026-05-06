# -*- coding: utf-8 -*-
import os, json, re, sys, anthropic, fitz

sys.stdout.reconfigure(encoding='utf-8')

key = open('c:/Users/User/Desktop/homepage/env.txt').read().strip()
client = anthropic.Anthropic(api_key=key)

resource_dir = 'c:/Users/User/Desktop/homepage/resource'
pdfs = sorted([f for f in os.listdir(resource_dir) if f.endswith('.pdf')])
print(f"총 {len(pdfs)}개 PDF 분류 시작 (30개씩 배치 처리)")

all_results = []
batch_size = 30

for batch_start in range(0, len(pdfs), batch_size):
    batch = pdfs[batch_start:batch_start+batch_size]
    filenames_text = '\n'.join([f"{i+1}. {f}" for i, f in enumerate(batch)])
    print(f"\n배치 {batch_start//batch_size+1}: {batch_start+1}~{batch_start+len(batch)}번 처리 중...")

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""채용공고 PDF 파일명을 분석해 JSON 배열로 출력하세요.

{filenames_text}

각 항목:
{{"index":<번호>,"filename":"<원본파일명>","institution":"<기관명>","title":"<공고제목(간결히)>","category":"<공공기관|공기업|대학병원|연구원|기타>","year":<연도숫자>}}

JSON 배열만 출력. 설명 없이."""
            }]
        )

        text = message.content[0].text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        batch_data = json.loads(text)
        all_results.extend(batch_data)
        print(f"  완료: {len(batch_data)}개 분류됨")

    except Exception as e:
        print(f"  오류: {e} - 파일명으로 기본 처리")
        for i, f in enumerate(batch):
            all_results.append({
                "index": batch_start + i + 1,
                "filename": f,
                "institution": f.split('_')[-1].replace('.pdf','') if '_' in f else f.replace('.pdf',''),
                "title": f.replace('.pdf',''),
                "category": "공공기관",
                "year": 2025
            })

# 파일 크기 및 페이지 수 추가
print(f"\n파일 정보 추가 중...")
for item in all_results:
    fpath = os.path.join(resource_dir, item['filename'])
    if os.path.exists(fpath):
        item['size_kb'] = round(os.path.getsize(fpath) / 1024)
        try:
            doc = fitz.open(fpath)
            item['pages'] = len(doc)
            doc.close()
        except:
            item['pages'] = 0
    else:
        item['size_kb'] = 0
        item['pages'] = 0

with open('c:/Users/User/Desktop/homepage/pdf_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n완료! pdf_catalog.json 저장 ({len(all_results)}개)")
print("\n샘플 3개:")
for item in all_results[:3]:
    print(f"  - {item['institution']} | {item['title']} | {item['category']}")
