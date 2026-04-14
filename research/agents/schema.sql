-- =============================================
-- university_sites 테이블 생성
-- Supabase SQL Editor에서 실행하세요
-- =============================================

CREATE TABLE IF NOT EXISTS university_sites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  school_name TEXT NOT NULL,
  url TEXT NOT NULL,
  selector TEXT,                -- CSS 선택자 (선택사항, 없으면 자동 감지)
  is_active BOOLEAN DEFAULT true,
  last_crawled_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 설정
ALTER TABLE university_sites ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 허용 (에이전트에서 anon key로 읽기 가능)
CREATE POLICY "Public read university_sites" ON university_sites
  FOR SELECT USING (true);

-- 관리자만 쓰기 가능 (service_role key 사용)
CREATE POLICY "Service role write university_sites" ON university_sites
  FOR ALL USING (auth.role() = 'service_role');

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_university_sites_school ON university_sites(school_name);
CREATE INDEX IF NOT EXISTS idx_university_sites_active ON university_sites(is_active);
