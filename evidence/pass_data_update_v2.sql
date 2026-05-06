-- ============================================================
-- pass_statistics 2차 보완 업데이트
-- 출처: 합격데이터.txt 추가 분석 (공취사 합격후기)
-- 주의: pass_score_min/avg = 합격자 실제 보유 점수 (공식 요구점수 아님)
-- ============================================================

-- ① 기존 기관 pass_score 업데이트

-- 한국동서발전 (발전전기 2025, 토익 870 보유자 확인)
UPDATE pass_statistics
SET pass_score_min=800, pass_score_avg=870, pass_year='2025'
WHERE institution_name='한국동서발전';

-- 한국수력원자력 (기계직 2024상반기, 토익 900초반 보유 / 기존 840~855 포함 재산정)
UPDATE pass_statistics
SET pass_score_min=840, pass_score_avg=875, pass_year='2024'
WHERE institution_name='한국수력원자력';

-- 한국전력기술 (사무직 2024상반기 토익 850 / 기술직 855+ 포함 재산정)
UPDATE pass_statistics
SET pass_score_min=850, pass_score_avg=880, pass_year='2025'
WHERE institution_name='한국전력기술';

-- 한국토지주택공사 (5급 행정직 2024하반기, 토익 890 보유 → 평균 상향)
UPDATE pass_statistics
SET pass_score_min=800, pass_score_avg=879, pass_year='2024'
WHERE institution_name='한국토지주택공사';

-- ② 신규 기관 추가

INSERT INTO pass_statistics (institution_name, toeic_score, is_deleted, gtelp_applicable, notes, pass_score_min, pass_score_avg, pass_year)
SELECT * FROM (VALUES
  ('서울교통공사'::text, NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 840, 840, '2024'),
  ('한전KPS'::text,      NULL::integer, false, false, '공식 기준 미확인 (합격자 보유점수 기반)', 700, 750, '2024')
) AS v(institution_name, toeic_score, is_deleted, gtelp_applicable, notes, pass_score_min, pass_score_avg, pass_year)
WHERE NOT EXISTS (
  SELECT 1 FROM pass_statistics p WHERE p.institution_name = v.institution_name
);
