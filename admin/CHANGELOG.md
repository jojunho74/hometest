# admin 작업 이력

> 관리자 페이지 (`admin-k9x3.html`) 및 분석 대시보드 (`admin/analy.html`) 작업 이력

---

## 연관 파일

| 파일 | 역할 |
|------|------|
| `admin-k9x3.html` | 관리자 메인 페이지 (비공개 경로) |
| `admin/analy.html` | 방문 흐름 분석 대시보드 (로컬 개발용 독립 파일) |
| `api/ai-insights.js` | Claude API 연동 서버리스 함수 |

## DB 테이블

- **`page_views`**: 페이지별 방문 로그 (`page`, `visited_at`, `referrer`)

---

## 작업 이력

### 2026-04-20 — 통계·추적 탭 방문수 기준 통일
- **커밋**: `d59a7d4`
- 통계 탭(원래 기준)이 정확한 수치임을 확인
- 추적 탭에서 `competition-click:` 필터 제거 → 두 탭 동일 기준으로 집계
- 통계 탭은 원래 쿼리로 복원 (앞선 수정 롤백)

### 2026-04-20 — 추적 탭 iframe → 직접 내장으로 전환
- **커밋**: `417882f`
- iframe 방식 완전 제거 → `section-tracking` 안에 HTML/CSS/JS 직접 삽입
- 모든 CSS 클래스 `trk-` 접두어 스코프, JS 함수 `trk` 접두어로 충돌 방지
- `trkLoaded` 플래그: 탭 첫 진입 시 1회만 Supabase 로드
- **개발 방식 확정**: `admin/analy.html`에서 로컬 개발 → 완료 후 "analy.html 내용을 관리자 페이지 추적 탭에 반영해줘"로 병합

### 2026-04-20 — vercel.json 헤더 순서 수정 (iframe 차단 해제 시도)
- **커밋**: `f9ac413`
- Vercel 헤더는 배열 마지막 규칙이 우선 적용
- `/admin/analy.html` 예외 규칙을 배열 맨 끝으로 이동
- 결론: iframe 방식 자체를 포기하고 직접 내장으로 전환

### 2026-04-20 — 추적 탭 추가 (iframe 방식, 1차 시도)
- **커밋**: `7d5324e`
- 사이드바 통계 아래 📡 추적 버튼 추가
- `section-tracking`: `admin/analy.html`을 iframe으로 임베드
- `vercel.json` X-Frame-Options `DENY`로 인해 차단 → iframe 방식 실패

### 2026-04-20 — admin/analy.html 초기 버전 복원
- **커밋**: `2e835c8`
- KPI 스파크라인·주간 트렌드·AI 전문가 분석 추가 버전 → 초기 버전으로 롤백
- 사유: 사용자가 단순한 초기 버전 선호

### 2026-04-20 — analy.html 페이지별 방문수 TOP 10 바 레이아웃 수정
- **커밋**: `4244980`
- `#page-bars` 자체에 `class="loading"`(`display:flex`) 잔류 → 자식 div로 이동
- `.card`에 `min-width:0; overflow:hidden` 추가 (grid 오버플로우 방지)
- `.bar-row`, `.bar-label`, `.bar-track`에 `min-width:0` 추가

### 2026-04-20 — admin/analy.html 최초 생성
- **커밋**: `ad3d788`
- `page_views` 테이블 기반 방문 흐름 분석 로컬 테스트 페이지
- 조회: `select('page, visited_at, referrer').order('visited_at', desc).limit(10000)`
- KPI 5개: 총 방문수·페이지 수·직접접속%·외부유입%·내부이동%
- ① 유입채널 도넛 차트 + 페이지별 방문 TOP 10 바
- ② 내부이동흐름 TOP 15 + 페이지 진입 직전 페이지
- ③ 시간대별(0~23시) 막대 + 요일별 막대 (주말 빨강)
- ④ 페이지×시간대 히트맵
- ⑤ 외부 referrer URL TOP 20 + 외부 유입 착지 페이지
- 기간 버튼: 오늘 / 어제 / 7일 / 30일(기본) / 전체

---

## 주요 기능 정리

| 기능 | 설명 |
|------|------|
| KPI 카드 | 총 방문수·페이지 수·직접접속%·외부유입%·내부이동% |
| 유입채널 도넛 | 직접접속·내부링크·Google·Naver·네이버블로그·카카오 등 분류 |
| 페이지별 TOP 10 | 수평 바 차트, 방문 많은 순 |
| 이동 경로 TOP 15 | 페이지 → 페이지 내부 이동 흐름 |
| 시간대·요일 패턴 | 피크 시간대 강조, 주말 빨강 표시 |
| 히트맵 | 페이지 × 2시간 슬롯, 6단계 색상 농도 |
| 외부유입 상세 | referrer URL TOP 20 + 착지 페이지 |
| 기간 필터 | 오늘·어제·7일·30일·전체 (KST 기준) |

## 개발 워크플로우

```
1. admin/analy.html 에서 로컬 수정·테스트
2. 완료 후 명령: "analy.html 내용을 관리자 페이지 추적 탭에 반영해줘"
3. Claude가 section-tracking HTML/CSS/JS 교체 + 커밋 + 배포
```

## referrer 분류 규칙 (trkClassifyRef)

| 조건 | 분류 |
|------|------|
| referrer 없음 | 직접접속 |
| `ibtcc.kr` 또는 `vercel.app` | 내부링크 |
| `blog.naver` | 네이버블로그 |
| `google` | Google |
| `naver` | Naver검색 |
| `kakao` / `kakaotalk` | 카카오 |
| `instagram` | 인스타그램 |
| `facebook` | 페이스북 |
| `youtube` | 유튜브 |
| 그 외 | 기타외부 |
