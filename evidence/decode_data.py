import json, re

raw = r"""[
  {"Unnamed: 0": null,"기관/시험명": "5급(행시)","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "5급(과학기술)","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "7급","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "외교관 후보자","TOEIC 기준": 870,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "지역인사 7급","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "민간경력자 5급","TOEIC 기준": 870,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "민간경력자 7급","TOEIC 기준": 790,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "인사혁신청 5급 공청","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "인사혁신청 7급 공청(세무주사직 제외)","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "인사혁신청 7급 공청(세무주사직)","TOEIC 기준": 790,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "외교관후보자 신엸및화","TOEIC 기준": 870,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국회사무처 입법고시","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "대법원 법원행정고등고시","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "소방청 소방간부후보자","TOEIC 기준": 625,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "경찰간부후보자","TOEIC 기준": 625,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "대통령경호청 특정직 7급","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "놌수진흥청 연구직·지도직","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "해양경찰청 간부후보자","TOEIC 기준": 625,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "게임물관리위원회","TOEIC 기준": 900,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "경기관광공사","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "경기항만항공사","TOEIC 기준": 600,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국민건강보험공단","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국립부산과학관","TOEIC 기준": 720,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국립국어교육원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국립국어교육원 WEST 장기","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국립국어교육원 WEST 중기","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국립국어교육원 WEST 단기","TOEIC 기준": 850,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "기술보증기금","TOEIC 기준": 760,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "기초과학연구원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "대한무역투자진흥공사 (KOTRA)","TOEIC 기준": 850,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "대한체육회","TOEIC 기준": null,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "부산항만공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "부산항보안공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "서울관광재단","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "서울시립교향악단","TOEIC 기준": null,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "서울주택도시공사","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "에너지경제연구원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "여수광양항만공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "의항지흥위원회","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "우체국물류지원단","TOEIC 기준": null,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "인체항만공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "인첸국제공항공사 정규 800","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "인첸국제공항공사 인턴 700","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "중소벤첫기업진흥공단","TOEIC 기준": 850,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국가스공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국가스안전공사","TOEIC 기준": 650,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국공정거래조정원","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국공항공사 정규 750","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국공항공사 경력 700","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국과학기술평가원","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국과학기술정보연구원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국관광공사","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국국방연구원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국국제보건의료재단 인턴 830","TOEIC 기준": 830,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국국제협력단","TOEIC 기준": 730,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국기계전기연구원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국기초과학지식연구원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국남동발전","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국노인인력개발원","TOEIC 기준": 850,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국도로공사 700","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국도로공사 750","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국디자인진흥원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국도시가스공사","TOEIC 기준": 720,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국소방산업기술원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국수력원자력","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국수자원공사 600","TOEIC 기준": 600,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국수자원공사 700","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국수자원조사기술원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국통계정보원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국시스템안전통합하는켓터","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국언론진흥재단 정규 900","TOEIC 기준": 900,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국언론진흥재단 인턴 850","TOEIC 기준": 850,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국에너지공단한수혁자회","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국에너지기술연구원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국에너지통제기술원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국전기연구원","TOEIC 기준": 900,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국전력공사 정규 700","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국전력공사 보호 500","TOEIC 기준": 500,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국정보보호진흥원","TOEIC 기준": 900,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국천문연구원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국포스코공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국항공우주연구원","TOEIC 기준": 815,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국해양과학기술원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국해양진흥공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국헬스코종합연구원","TOEIC 기준": 650,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국환경공단","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국환경연구기술원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한전 KDN","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한전 KPS","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "항공안전기술원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "FITI시험연구원","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "건강보험심사평가원","TOEIC 기준": null,"Unnamed: 3": "독해점수에 200%"},
  {"Unnamed: 0": null,"기관/시험명": "한국철도공사","TOEIC 기준": 800,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "서울주택도시공사 사무직 800 기술직 700","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국남부발전","TOEIC 기준": 850,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국동부발전","TOEIC 기준": 900,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국수자원공사","TOEIC 기준": 775,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국도시쳊도항공공사","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국산업단지공단","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국산업인력공단","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국도시이연공사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국거래소","TOEIC 기준": 900,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "강원대학병원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국가철도공단","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국민연금공단","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "대한주택보증사","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국민체육진흥공단","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "신용보증기금","TOEIC 기준": 750,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국전력거래소","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "전남해양항만항공연구원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "중소기업기술정보진흥원","TOEIC 기준": 765,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "한국무역보험공사","TOEIC 기준": null,"Unnamed: 3": "공인어학성적(TOEIC, TOEFL(IBT), TEPS)으로 대체"},
  {"Unnamed: 0": null,"기관/시험명": "도로교통공단","TOEIC 기준": 445,"Unnamed: 3": "이상 한수지에 반영"},
  {"Unnamed: 0": null,"기관/시험명": "코레일관광개발","TOEIC 기준": 620,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "국방기술지흥연구원","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "산업공단인력직업진흥공단","TOEIC 기준": 700,"Unnamed: 3": "이상 개별지에 부여"},
  {"Unnamed: 0": null,"기관/시험명": "한국조평공사","TOEIC 기준": 360,"Unnamed: 3": "975점까지 한수지에 소수점 적용"},
  {"Unnamed: 0": null,"기관/시험명": "극지연구원(기술직)","TOEIC 기준": 700,"Unnamed: 3": null},
  {"Unnamed: 0": null,"기관/시험명": "근로복지공단","TOEIC 기준": 700,"Unnamed: 3": null}
]"""

data = json.loads(raw)

lines = []
for item in data:
    name = item.get("기관/시험명")
    score_raw = item.get("TOEIC 기준")
    notes_raw = item.get("Unnamed: 3")

    if not name:
        continue

    # Parse score
    if isinstance(score_raw, (int, float)) and score_raw and score_raw > 0:
        score = int(score_raw)
    else:
        score = None

    # Build notes
    notes_parts = []
    if score_raw is not None and not isinstance(score_raw, (int, float)):
        notes_parts.append(str(score_raw))
    if notes_raw:
        notes_parts.append(str(notes_raw))
    notes = ' / '.join(notes_parts) if notes_parts else None

    score_sql = str(score) if score is not None else "NULL"
    notes_sql = "'" + notes.replace("'", "''") + "'" if notes else "NULL"
    name_sql = name.replace("'", "''")

    lines.append(f"('{name_sql}', {score_sql}, false, false, {notes_sql})")

sql = "INSERT INTO pass_statistics (institution_name, toeic_score, is_deleted, gtelp_applicable, notes) VALUES\n"
sql += ",\n".join(lines) + ";"

print(sql)
print(f"\n-- 총 {len(lines)}건")
