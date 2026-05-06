-- ============================================================
-- pass_statistics 테이블 보완 업데이트
-- 출처: 합격데이터.txt (공취사 합격후기 파싱)
-- 주의: pass_score_min/avg = 합격자 실제 보유 점수 (공식 요구점수 아님)
-- ============================================================

-- ① 새 컬럼 추가 (Method C)
ALTER TABLE pass_statistics ADD COLUMN IF NOT EXISTS pass_score_min INTEGER;
ALTER TABLE pass_statistics ADD COLUMN IF NOT EXISTS pass_score_avg INTEGER;
ALTER TABLE pass_statistics ADD COLUMN IF NOT EXISTS pass_year TEXT;

-- ============================================================
-- ② 기존 기관 pass_score 보완 (Method B) — institution_name 기준 매칭
-- ============================================================

-- 건강보험심사평가원
UPDATE pass_statistics SET pass_score_min=760, pass_score_avg=760, pass_year='2025'
WHERE institution_name='건강보험심사평가원';

-- 국가철도공단
UPDATE pass_statistics SET pass_score_min=850, pass_score_avg=850, pass_year='2025'
WHERE institution_name='국가철도공단';

-- 국민건강보험공단
UPDATE pass_statistics SET pass_score_min=640, pass_score_avg=821, pass_year='2025'
WHERE institution_name='국민건강보험공단';

-- 국민연금공단
UPDATE pass_statistics SET pass_score_min=900, pass_score_avg=915, pass_year='2025'
WHERE institution_name='국민연금공단';

-- 국민체육진흥공단
UPDATE pass_statistics SET pass_score_min=735, pass_score_avg=735, pass_year='2025'
WHERE institution_name='국민체육진흥공단';

-- 근로복지공단
UPDATE pass_statistics SET pass_score_min=850, pass_score_avg=880, pass_year='2025'
WHERE institution_name='근로복지공단';

-- 대한체육회
UPDATE pass_statistics SET pass_score_min=860, pass_score_avg=860, pass_year='2025'
WHERE institution_name='대한체육회';

-- 한국가스공사
UPDATE pass_statistics SET pass_score_min=800, pass_score_avg=840, pass_year='2025'
WHERE institution_name='한국가스공사';

-- 한국공항공사 정규
UPDATE pass_statistics SET pass_score_min=800, pass_score_avg=800, pass_year='2025'
WHERE institution_name='한국공항공사 정규 750';

-- 한국관광공사
UPDATE pass_statistics SET pass_score_min=800, pass_score_avg=800, pass_year='2025'
WHERE institution_name='한국관광공사';

-- 한국도로공사 700
UPDATE pass_statistics SET pass_score_min=965, pass_score_avg=965, pass_year='2024'
WHERE institution_name='한국도로공사 700';

-- 한국도로교통공단
UPDATE pass_statistics SET pass_score_min=700, pass_score_avg=805, pass_year='2025'
WHERE institution_name='도로교통공단';

-- 한국산업단지공단
UPDATE pass_statistics SET pass_score_min=800, pass_score_avg=830, pass_year='2025'
WHERE institution_name='한국산업단지공단';

-- 한국산업인력공단
UPDATE pass_statistics SET pass_score_min=890, pass_score_avg=890, pass_year='2025'
WHERE institution_name='한국산업인력공단';

-- 한국수력원자력
UPDATE pass_statistics SET pass_score_min=840, pass_score_avg=855, pass_year='2025'
WHERE institution_name='한국수력원자력';

-- 한국수자원공사
UPDATE pass_statistics SET pass_score_min=825, pass_score_avg=850, pass_year='2025'
WHERE institution_name='한국수자원공사';

-- 한국전력공사 정규
UPDATE pass_statistics SET pass_score_min=900, pass_score_avg=900, pass_year='2025'
WHERE institution_name='한국전력공사 정규 700';

-- 한국철도공사
UPDATE pass_statistics SET pass_score_min=700, pass_score_avg=837, pass_year='2025'
WHERE institution_name='한국철도공사';

-- 한국환경공단
UPDATE pass_statistics SET pass_score_min=700, pass_score_avg=778, pass_year='2025'
WHERE institution_name='한국환경공단';

-- 중소벤처기업진흥공단
UPDATE pass_statistics SET pass_score_min=895, pass_score_avg=925, pass_year='2025'
WHERE institution_name='중소벤첫기업진흥공단';

-- ============================================================
-- ③ 신규 기관 추가 (Method A) — DB에 없는 기관
-- ============================================================

INSERT INTO pass_statistics (institution_name, toeic_score, is_deleted, gtelp_applicable, notes, pass_score_min, pass_score_avg, pass_year)
SELECT * FROM (VALUES
  ('한국토지주택공사'::text,       NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 800, 868, '2025'),
  ('한국도로공사서비스'::text,     NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 830, 843, '2025'),
  ('소상공인시장진흥공단'::text,   NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 855, 883, '2025'),
  ('한국보훈복지의료공단'::text,   NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 830, 893, '2025'),
  ('해양환경공단'::text,           NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 750, 815, '2025'),
  ('한국농수산식품유통공사'::text, NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 850, 868, '2025'),
  ('한국농어촌공사'::text,         NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 750, 845, '2024'),
  ('한국동서발전'::text,           NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 800, 800, '2025'),
  ('한국중부발전'::text,           NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 925, 925, '2025'),
  ('한국마사회'::text,             NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 980, 980, '2025'),
  ('한국전기안전공사'::text,       NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 790, 853, '2025'),
  ('한국전력기술'::text,           NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 855, 903, '2025'),
  ('한국주택금융공사'::text,       NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 700, 800, '2025'),
  ('한국지역난방공사'::text,       NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 900, 900, '2025'),
  ('한국자산관리공사'::text,       NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 800, 800, '2025'),
  ('한국양성평등교육진흥원'::text, NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 900, 900, '2025'),
  ('한전원자력연료'::text,         NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 835, 835, '2025'),
  ('대구공공시설관리공단'::text,   NULL::integer, false, false, '토익 불필요 (NCS 중심 채용)',            NULL, NULL, '2025'),
  ('한국폴리텍대학'::text,         NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 805, 805, '2025'),
  ('건강보험심사평가원'::text,     NULL::integer, false, false, '독해점수에 200% 반영',                   760,  760, '2025')
) AS v(institution_name, toeic_score, is_deleted, gtelp_applicable, notes, pass_score_min, pass_score_avg, pass_year)
WHERE NOT EXISTS (
  SELECT 1 FROM pass_statistics p WHERE p.institution_name = v.institution_name
);
