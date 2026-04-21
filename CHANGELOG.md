# 작업 이력

> `competition.html`, `university-board.html` 등 주요 페이지 작업 이력

---

## 연관 파일

| 파일 | 역할 |
|------|------|
| `competition.html` | 직종별 채용 경쟁률 비교 메인 페이지 |
| `jobscript/jobscript_a.html` | 직종별 경쟁률 독립 차트 페이지 |
| `university-board.html` | 대학교 활동/소식/채용 게시판 |

---

## Supabase 보안 작업 이력

### 2026-04-21 — RLS 정책 전면 적용 (보안 강화)
- **위치**: Supabase 대시보드 → SQL Editor
- 모든 주요 테이블 RLS 활성화 및 정책 설정
- **개인정보 테이블** (`consultations`, `student_applications`): 공개 INSERT 허용 + 조회/수정/삭제는 인증된 관리자만
- **콘텐츠 테이블** (`school_programs`, `university_news`, `staff_job_postings`, `job_postings`, `company_news`, `popup_ads`): 읽기 공개 + 쓰기는 인증된 관리자만
- **추적 테이블** (`page_views`, `pdf_ratings`, `cheer_comments`): 공개 INSERT/SELECT + 삭제는 관리자만
- anon key 노출에도 개인정보 직접 조회 및 무단 데이터 조작 차단

---

## university-board.html 작업 이력

### 2026-04-21 — 사이드바 열람순위 레이블 추가
- **커밋**: `dd58c09`
- 열람 기록이 있는 학교 목록 상단에 "열람순위" 레이블 표시
- 열람된 학교가 하나도 없으면 레이블 미표시 (조건부 렌더링)

### 2026-04-20 — 사이드바 열람순 정렬 + 배지 + 구분선 추가
- **커밋**: `333f148`
- `ubSortedSchools()`: 열람 횟수 내림차순 → 가나다순 정렬
- 🥇🥈🥉 + 4위/5위 배지 (전체 순위 기준, 검색 필터 시에도 유지)
- 열람 기록 있는 학교 / 없는 학교 사이 구분선 삽입
- 학교명 옆에 열람 횟수 소형 표기

### 2026-04-20 — 기본화면(#ub-default-view) 채용공고 캐러셀 + HOT 경쟁률 추가
- **커밋**: `333f148`
- `.placeholder` 대체: 채용공고 캐러셀 + 이번주 HOT 경쟁률 그리드
- 채용공고: `job_postings` 테이블, 8개씩 슬라이드, 5초 자동전환, 도트 네비게이션
- HOT 경쟁률: `page_views?page=like.competition-click:*` 지난 7일 집계, 상위 6개 표시
- `ubRenderDots` null 가드, `setInterval` clearInterval 방어 코드 포함

---

## competition.html 작업 이력

> (구: competition.html 작업 이력 단독 섹션)

## competition.html 연관 파일

## DB 테이블

- **`alio_jobs`**: 채용 공고 원본 데이터 (직종, 기관명, 경쟁률 등)

---

## competition.html 작업 이력

### 2026-04-21 — 합격선 안내 배너 위치 수정 (차트 하단 전체 너비)
- **커밋**: `dd58c09`
- 배너가 `chart-comment-row` flex 안에 포함되어 차트 옆에 표시되던 문제 수정
- `chart-comment-row` 닫는 `</div>` 밖으로 이동 → 차트+댓글 행 아래 전체 너비 블록으로 표시

### 2026-04-20 — 공공기관 선택 시 그래프 하단 합격선 안내 배너 추가
- **커밋**: (이전 세션)
- `ratioChart` 차트 아래에 합격선 안내 배너 추가 (기관 선택 시 노출)
- 내용: 토익 750점 이상 / 지텔프 65점 이상 / 준비기간 / IBT 무료 응시 가능
- IBT 신청하기 버튼 → `student.html` 이동

### 2026-04-20 — 기본화면(#default-chart-view) 합격선 안내 배너 추가
- **커밋**: (이전 세션)
- `jv-chart-card` 아래 동일한 합격선 안내 배너 추가 (직종 검색 기본화면)

### 2026-04-20 — 직종 검색 안내 문구 shimmer 반짝이 효과 추가
- **커밋**: `db91b3c`
- 검색박스 상단 안내 문구에 shimmer 애니메이션 적용
- 파란색→흰색→노란색 그라디언트가 흐르는 텍스트 효과
- ✦ 아이콘 + `@keyframes jv-shimmer-txt` (2.8s linear infinite)

### 2026-04-20 — 직종 검색박스 상단 안내 문구 추가
- **커밋**: `87edaaf`
- `#default-chart-view` 검색박스 위에 안내 문구 추가
- 내용: "관련 직무를 입력하시면, 기관별 경쟁률을 비교할 수 있습니다."

### 2026-04-20 — 퀵네비 배너 우측 업데이트 중 표시 추가
- **커밋**: `11390c3`
- 퀵네비게이션 배너 우측에 "2026년 경쟁률 업데이트 중" 추가
- 노란색 깜빡이는 점(qnav-blink) + 텍스트
- `.qnav-banner`에 `display:flex` 추가하여 `margin-left:auto`로 우측 정렬

### 2026-04-20 — 직종별 경쟁률 기본 화면(#default-chart-view) 내장
- **커밋**: (이전 세션)
- `competition.html` 첫 화면 빈 영역에 `jobscript_a.html` 전체 UI 내장
- CSS 클래스 `jv-` 접두어, JS 함수 `jv` 접두어로 네임스페이스 충돌 방지
- 기존 `allRows` 데이터 재사용 (`_jvAllData = allRows`)
- 검색패널·활성필터·요약카드·차트·결과테이블 포함
- 공고명 선택 시 `#default-chart-view` 숨김, `#btn-back-chart` 표시

### 2026-04-20 — "← 직종별 경쟁률" 뒤로가기 버튼 추가
- **커밋**: (이전 세션)
- 공고명 선택 후 상단에 뒤로가기 버튼 표시
- 클릭 시 `location.href='competition.html'`으로 페이지 이동 (새로고침)

### 2026-04-20 — 전체선택 바 배경 가시성 개선
- **커밋**: (이전 세션)
- 전체선택 바 배경: `linear-gradient(135deg, rgba(37,99,235,.55), rgba(59,130,246,.4))`
- 테두리: `1.5px solid rgba(96,165,250,.7)`
- 박스섀도: `0 0 16px rgba(59,130,246,.35)`

---

## jobscript_a.html 작업 이력

### 2026-04-20 — 차트 툴팁에 공고명 표시
- **커밋**: (이전 세션)
- Chart.js `afterBody` 콜백으로 호버 시 공고명 리스트 표시
- `getStats()`에서 `datasets: new Set()` 수집
- 최대 5개 표시 후 "외 N개" 처리

---

## 주요 기능 정리

| 기능 | 설명 |
|------|------|
| 직종 검색 | 자동완성, 실시간 필터링 |
| 기관별 경쟁률 차트 | Chart.js 수평 바 차트, 툴팁에 공고명 표시 |
| 요약 카드 | 평균 경쟁률·최고·최저·공고 수 |
| 결과 테이블 | 기관·직종·경쟁률·채용인원·공고수 |
| 직종 태그 | 자주 검색되는 직종 태그 클릭 필터 |
| 카카오 공유 | `Kakao.Share.sendDefault()` (모바일 지원) |
