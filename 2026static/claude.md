file:///C:/Users/User/Desktop/homepage/static/alio-admin.html 운영중이야. 현재 데이터추가버튼이 있고 신규로  옆에 데이터자동 버튼을 만들고 버튼을 누르면 새로운 페이지를 만들어
새로운 페이지의 기능을 설명할게. 
file:///C:/Users/User/Desktop/homepage/static/alio-admin.html의 데이터 파싱기능을 활용해
먼저 자동화데이터 등록버튼을 만들고
자동화데이터 버튼을 누르면  "ALIO URL 자동 파싱"의 기존메뉴를 참고해서
url을 입력하면, 파싱하기를 시작해
파싱된 데이터는 해당사이트의 컨트롤+u 버튼으로 html을 가져와서 supabase 신규로 생성된 테이블에 저장하고,저장된 데이터를 html소스란에 자동으로 가져와
그리고 아래에 소스로 파싱하기를 만들고
완성된 파싱테이터는 업로드데이터로 수정하여 저장해
완성된 데이터는 https://ibtcc.kr/competition.html에 같이 보여지게 할거야. 게시는 재확인후 연결예정

---

## ✅ 진행 완료 내역 (2026-04-18)

### 1. static/alio-admin.html 수정
- 사이드바 "데이터 추가" 아래에 **⚡ 데이터 자동** 버튼 추가
- 클릭 시 `alio-auto.html`로 이동

### 2. static/alio-auto.html 신규 생성
3단계 파이프라인 구현:

**Step 1 — URL 입력 → HTML 소스 자동 수집**
- ALIO URL 입력 후 "파싱하기" 클릭
- 프록시 순서대로 HTML 자동 수집 (ibtcc.kr서버 → server.py → allorigins → corsproxy.io → codetabs)
- 수집된 HTML을 Supabase `alio_source_cache` 테이블에 저장

**Step 2 — HTML 소스란**
- 수집된 HTML 소스 textarea에 자동 표시
- "소스로 파싱하기" 버튼으로 alio-admin.html과 동일한 파싱 로직 실행

**Step 3 — 파싱 결과 → 업로드데이터 저장**
- 파싱 결과를 JSON으로 편집 가능
- 기업명 입력 후 "업로드데이터 저장" → `alio_jobs` 테이블에 INSERT
- 저장 후 `alio_source_cache.status = 'published'`로 업데이트

**추가 기능**
- 🗂️ 저장된 소스 목록: 과거 수집 목록 조회/불러오기/삭제
- 🔄 업데이트 버튼: URL 재수집 → `alio_source_cache` + `alio_jobs` 동시 갱신 (기존 삭제 후 재삽입)
- 🗄️ 테이블 SQL 가이드 제공

### 3. Supabase 신규 테이블: alio_source_cache
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID | 기본키 |
| url | TEXT | 수집한 원본 ALIO URL |
| html_source | TEXT | 수집된 HTML 전문 |
| dataset_name | TEXT | 기업명 |
| upload_data | JSONB | 최종 업로드 데이터 JSON 배열 |
| status | TEXT | draft / published |
| created_at | TIMESTAMPTZ | 저장 시각 |

### 4. competition.html 수정
- 기존: `alio_jobs` 단독 조회
- 변경: `alio_jobs` + `alio_source_cache` 병합 조회
- 동일 기관명은 `alio_jobs` 우선, 없으면 `alio_source_cache.upload_data`로 보완
- 기관명 검색 시 자동 수집 데이터도 함께 출력됨

### 5. 배포
- GitHub 푸시 완료 (commit: fdc8f39)
- Vercel 자동 배포 완료
- 배포 URL: https://ibtcc.kr/competition.html

### 남은 작업
- competition.html 게시 최종 확인 후 추가 연동 예정

### 추가사항
- 배포하기 전에 먼저 file:///C:/Users/User/Desktop/homepage/index.html 페이지로 먼저 반영
- 이상이 없는 경우 배포를 항상 물어보고 진행할 것