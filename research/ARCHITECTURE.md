# 대학활동 자동화 시스템 — 아키텍처

## 시스템 개요

대학 사이트에서 게시글을 자동 수집 → 중복 제거 → Supabase 저장 → ibtcc.kr 대학활동 페이지 자동 게시

```
[n8n 시작 버튼]
      ↓
agent_automation.py (오케스트레이터)
      ├── 1. agent_collector.py   → 등록된 대학 사이트 스크래핑
      ├── 2. agent_comparator.py  → 중복 제거 (기존 DB와 비교)
      └── 3. agent_publisher.py   → Supabase school_programs에 INSERT
                                        ↓
                              university-board.html 자동 반영
```

---

## 기술 스택

| 구분 | 도구 |
|------|------|
| OS | Windows |
| 에이전트 | Claude Code + Python |
| 자동화 트리거 | n8n (Webhook) |
| 스크래핑 | Python (requests + BeautifulSoup / Playwright) |
| AI 분석 | Claude API (claude-sonnet-4-6) |
| DB | Supabase (PostgreSQL) |
| 배포 | Vercel (정적 HTML) + GitHub |

---

## 폴더 구조

```
homepage/
├── research/
│   ├── claude.md              # 프로젝트 명세
│   ├── ARCHITECTURE.md        # 이 파일
│   └── agents/
│       ├── agent_collector.py    # 수집 에이전트
│       ├── agent_comparator.py   # 비교/중복제거 에이전트
│       ├── agent_publisher.py    # 게시 에이전트
│       ├── agent_automation.py   # 자동화 오케스트레이터
│       ├── requirements.txt      # Python 패키지 목록
│       └── .env.example          # 환경변수 예시
├── admin-k9x3.html            # 관리자 페이지 (대시보드 탭 추가)
├── university-board.html      # 대학활동 게시판 (자동 반영)
└── ...
```

---

## Supabase 테이블

### 기존 테이블 (변경 없음)
- `school_programs` — 대학 활동 게시글 (에이전트가 INSERT)

### 신규 테이블
- `university_sites` — 수집 대상 대학 사이트 목록

```sql
CREATE TABLE university_sites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  school_name TEXT NOT NULL,        -- 학교명 (school_programs.school_name과 동일하게)
  url TEXT NOT NULL,                -- 수집할 페이지 URL
  selector TEXT,                    -- CSS 선택자 (선택, 없으면 자동 감지)
  is_active BOOLEAN DEFAULT true,   -- 수집 활성화 여부
  last_crawled_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 에이전트 워크플로우

### A. 수집 에이전트 (agent_collector.py)
1. `university_sites` 테이블에서 활성화된 URL 목록 조회
2. 각 URL 접속 → 스크롤 → 게시글 목록 파싱
3. `학교명`, `제목`, `링크` 임시 수집 (메모리)
4. 수집 결과를 비교 에이전트로 전달

### B. 비교 에이전트 (agent_comparator.py)
1. 수집된 게시글 목록 수신
2. `school_programs` 테이블에서 기존 제목+링크 조회
3. 중복(제목 OR 링크 일치) 제거
4. 신규 게시글만 게시 에이전트로 전달

### C. 게시 에이전트 (agent_publisher.py)
1. 신규 게시글 목록 수신
2. Supabase `school_programs` 테이블에 INSERT
   - `school_name`: 수집 사이트의 학교명
   - `title`: 수집된 게시글 제목
   - `link`: 게시글 URL
   - `type`: '활동'
3. 게시 결과 로그 반환

### D. 자동화 에이전트 (agent_automation.py)
1. n8n Webhook 수신 → 파이프라인 시작
2. A → B → C 순서 실행
3. 결과 요약 로그 출력
4. 에러 발생 시 원인 분석 + 한국어 보고

---

## n8n 연동 방식

```
n8n Webhook 노드 (POST /webhook/university-crawler)
      ↓
Execute Command 노드
      python research/agents/agent_automation.py
      ↓
응답 반환 (성공/실패 + 신규 게시글 수)
```

### 관리자 페이지 시작 버튼
```javascript
// admin-k9x3.html 내 시작 버튼
async function startCrawler() {
  const res = await fetch('http://localhost:5678/webhook/university-crawler', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trigger: 'manual' })
  });
  const data = await res.json();
  // 결과 로그 표시
}
```

---

## 에러 처리 원칙

- 에러 발생 시 한국어로 원인 설명
- 기존 `school_programs` 데이터 절대 삭제 금지
- 각 에이전트 독립 실행 가능 (단위 테스트 지원)
- 실행 로그: `research/agents/logs/` 폴더에 저장

---

## 구현 체크리스트

### Phase 1 — 기반 세팅
- [ ] `university_sites` 테이블 Supabase에 생성
- [ ] `.env` 환경변수 설정 (SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY)
- [ ] Python 패키지 설치 (`pip install -r requirements.txt`)

### Phase 2 — 관리자 페이지 UI
- [ ] `admin-k9x3.html`에 "대학활동 대시보드" 탭 추가
- [ ] 대학 사이트 등록/수정/삭제 CRUD UI
- [ ] 에이전트 실행 버튼 + 결과 로그 표시
- [ ] 4개 섹션 패널 (기능 추후 결정)

### Phase 3 — Python 에이전트
- [ ] `agent_collector.py` 구현 및 단위 테스트
- [ ] `agent_comparator.py` 구현 및 단위 테스트
- [ ] `agent_publisher.py` 구현 및 단위 테스트
- [ ] `agent_automation.py` 파이프라인 통합 테스트

### Phase 4 — n8n 연동
- [ ] n8n Webhook 노드 생성
- [ ] Execute Command 노드 연결
- [ ] 관리자 페이지 시작 버튼 연결 테스트
