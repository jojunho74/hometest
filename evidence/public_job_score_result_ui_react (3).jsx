import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

// ✅ GTELP 반영기관
const gtelpInstitutions = new Set([
"가축위생방역지원본부",
"국방과학연구소",
"농림수산식품교육문화정보원",
"대구경북첨단의료산업진흥재단",
"대한체육회",
"부산항만공사",
"여수광양항만공사",
"오송첨단의료산업진흥재단",
"울산항만공사",
"인천항만공사",
"중소벤처기업진흥공단",
"축산물품질평가원",
"한국가스안전공사",
"한국관광공사",
"한국국방연구원",
"한국국제협력단",
"한국벤처투자",
"한국산업기술진흥원",
"한국석유관리원",
"한국식품안전관리인증원",
"한국에너지기술평가원",
"한국원자력안전기술원",
"한국원자력환경공단",
"한국장학재단",
"한국기계연구원",
"한국전자통신연구원",
"나노종합기술원",
"대구경북과학기술원",
"한국기초과학지원연구원",
"한국전기연구원",
"제주국제자유도시개발센터",
"경북문화재단",
"경상북도",
"경상북도경제진흥원",
"광주과학기술원",
"국립과천과학관",
"국립과학수사연구원",
"국립국제교육원",
"국민건강보험공단",
"국토지리정보원",
"대한산업안전협회",
"서울관광재단",
"서울디자인재단",
"서울산업진흥원",
"안전보건공단",
"인천글로벌캠퍼스운영재단",
"인천시설공단",
"인천항보안공사",
"인천환경공단",
"제주관광공사",
"코레일유통",
"한국뇌연구원",
"한국통계진흥원",
"한국표준과학연구원",
"한아세안센터",
"건강보험심사평가원",
"근로복지공단",
"한국해양교통안전공단",
"소상공인시장진흥공단",
"수도권매립지관리공사",
"정보통신정책연구원",
"한국공예디자인문화진흥원",
"한국교육개발원",
"한국교육과정평가원",
"한국국제보건의료재단",
"신용보증기금",
"한국재정정보원",
"한국과학기술연구원",
"국방기술품질원",
"식품안전정보원",
"아동권리보장원",
"한국도로교통공단",
"한국도박문제예방치유원",
"한국문화관광연구원",
"한국보건사회연구원",
"한국산업기술기획평가원",
"한국언론진흥재단",
"한국해외인프라도시개발지원공사",
"한식진흥원",
"국민체육진흥공단",
"카이스트",
"한국형사법무정책연구원",
"한국수산자원관리공단",
"과학기술사업화진흥원",
"한국청소년활동진흥원",
"국립암센터",
"국립중앙의료원",
"예금보험공사",
"한국농촌경제연구원",
"한국수산자원공단",
"극지연구소",
"국토연구원",
"한국디자인진흥원",
"한국해양수산연수원",
"국제식물검역인증원",
"서울경제진흥원",
"한국조폐공사",
"한국에너지공단",
"한국농수산식품유통공사",
"주택도시보증공사",
"사립학교교직원연금공단",
"한국과학창의재단",
"강릉원주대학교치과병원",
"대외경제정책연구원",
"한국에너지정보문화재단",
"중소기업기술정보진흥원",
"한국보건산업진흥원",
"한국소방산업기술원",
"한국지능정보사회진흥원",
"국방기술진흥연구소"
]);

// ✅ 전체 데이터 확장 (핵심 기관 샘플 → 이후 계속 추가 가능)
const rawData = [
  { name: "한국전력공사", score: 700 },
  { name: "한국수력원자력", score: 750 },
  { name: "한국도로공사", score: 700 },
  { name: "국민연금공단", score: 700 },
  { name: "한국공항공사", score: 750 },
  { name: "인천국제공항공사", score: 800 },
  { name: "한국거래소", score: 900 },
  { name: "한국가스공사", score: 700 },
  { name: "한국환경공단", score: 750 },
  { name: "한국농어촌공사", score: 700 },
  { name: "신용보증기금", score: 750 },
  { name: "국민건강보험공단", score: 700 },
  { name: "근로복지공단", score: 700 },
  { name: "한국수자원공사", score: 775 },
  { name: "한국산업은행", score: 750 },

  // 추가 반영 (요청 데이터 확장)
  { name: "한국관광공사", score: 800 },
  { name: "한국국제협력단", score: 730 },
  { name: "한국국방연구원", score: 750 },
  { name: "한국디자인진흥원", score: 700 },
  { name: "한국농수산식품유통공사", score: 750 },
  { name: "한국석유공사", score: 720 },
  { name: "한국소방산업기술원", score: 750 },
  { name: "한국언론진흥재단", score: 900 },
  { name: "한국전기연구원", score: 900 },
  { name: "한국지능정보사회진흥원", score: 900 },
  { name: "중소벤처기업진흥공단", score: 850 },
  { name: "부산항만공사", score: 700 },
  { name: "인천항만공사", score: 700 },
  { name: "울산항만공사", score: 700 },
  { name: "여수광양항만공사", score: 700 }
];

const data = rawData.map(item => ({
  ...item,
  gtelp: gtelpInstitutions.has(item.name)
}));

export default function PublicJobScoreUI() {
  const [userScore, setUserScore] = useState("");
  const [result, setResult] = useState([]);
  const [sortType, setSortType] = useState("diff");
  const [filterGtelp, setFilterGtelp] = useState(false);

  const handleCheck = () => {
    const score = Number(userScore);

    let mapped = data.map((item) => ({
      ...item,
      diff: score - item.score
    }));

    // 필터
    if (filterGtelp) {
      mapped = mapped.filter(i => i.gtelp);
    }

    // 정렬
    if (sortType === "diff") {
      mapped.sort((a, b) => b.diff - a.diff);
    } else if (sortType === "score") {
      mapped.sort((a, b) => a.score - b.score);
    }

    setResult(mapped);
  };

  const getPositionedData = () => {
    const buckets = {};

    return result.map((item) => {
      const offset = Math.max(-400, Math.min(400, item.score - Number(userScore)));
      const left = 50 + (offset / 800) * 100;

      const key = Math.round(left);
      if (!buckets[key]) buckets[key] = 0;
      const stackIndex = buckets[key]++;

      return {
        ...item,
        left,
        stackIndex
      };
    });
  };

  const positioned = getPositionedData();

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">합격 가능성 시뮬레이터</h1>

      {/* INPUT + CONTROL */}
      <div className="flex flex-wrap gap-2 mb-6">
        <Input
          placeholder="토익 점수 입력"
          value={userScore}
          onChange={(e) => setUserScore(e.target.value)}
        />

        <Button onClick={handleCheck}>분석</Button>

        <Button variant="outline" onClick={() => setSortType("diff")}>합격가능순</Button>
        <Button variant="outline" onClick={() => setSortType("score")}>점수순</Button>

        <Button
          variant={filterGtelp ? "default" : "outline"}
          onClick={() => setFilterGtelp(!filterGtelp)}
        >
          GTELP만
        </Button>
      </div>

      {/* GRAPH */}
      {result.length > 0 && (
        <div className="mb-10 p-6 border rounded-2xl bg-white shadow">
          <div className="relative h-64">

            <div className="absolute top-1/2 left-0 w-full h-[2px] bg-gray-300"></div>

            <div className="absolute top-1/2 -translate-y-1/2" style={{ left: "50%" }}>
              <div className="w-5 h-5 bg-blue-500 rounded-full"></div>
              <p className="text-xs text-center mt-1">내 점수</p>
            </div>

            {positioned.map((item, idx) => {
              const yOffset = item.stackIndex * -28;

              return (
                <motion.div
                  key={idx}
                  className="absolute"
                  style={{ left: `${item.left}%`, top: `calc(50% + ${yOffset}px)` }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className={`w-3 h-3 rounded-full ${item.gtelp ? "bg-red-500" : "bg-gray-400"}`}></div>
                  <p className="text-[10px] text-center mt-1 whitespace-nowrap">{item.name}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* TABLE */}
      {result.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">기관명</th>
                <th className="p-2 border">기준점수</th>
                <th className="p-2 border">차이</th>
                <th className="p-2 border">GTELP</th>
              </tr>
            </thead>
            <tbody>
              {result.map((item, idx) => (
                <tr key={idx} className="text-center">
                  <td className="p-2 border">{item.name}</td>
                  <td className="p-2 border">{item.score}</td>
                  <td className={`p-2 border font-bold ${item.diff >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {item.diff >= 0 ? `+${item.diff}` : item.diff}
                  </td>
                  <td className="p-2 border">{item.gtelp ? "O" : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 설명 */}
      <div className="mt-6 text-xs text-gray-500">
        ※ 점수 기준은 공개 채용 기준 또는 일반적인 커트라인 기반 추정값입니다.<br/>
        ※ GTELP 표시는 해당 기관에서 대체 영어시험 활용 가능 여부입니다.<br/>
        ※ 실제 채용공고별 기준은 변동될 수 있습니다.
      </div>

      {/* 우측 GTELP 버튼 */}
      <div className="fixed bottom-10 right-10">
        <Button className="rounded-2xl shadow-lg px-6 py-3" onClick={() => alert('GTELP 플랜 열기')}>
          4주간의 G-TELP 단기점수 완성
        </Button>
      </div>

      {/* GTELP 플랜 (모달 느낌) */}
      <div className="mt-10 p-6 bg-white border rounded-2xl shadow">
        <h2 className="text-xl font-bold mb-4">📘 지텔프 4주 완성 플랜</h2>

        <p className="mb-4 text-sm text-gray-600">
          합격수기 데이터를 기반으로 4주(28일) 안에 목표 점수 달성 전략을 정리했습니다.
        </p>

        <div className="mb-6 p-4 bg-blue-50 rounded-xl text-sm">
          👉 목표 점수를 입력하면 맞춤 전략 제공 가능
        </div>

        {/* Week 1 */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2">🗓️ Week 1 — 문법 집중</h3>
          <ul className="text-sm list-disc pl-5 space-y-1">
            <li>문법 강의 완강</li>
            <li>출제 유형 공식 암기</li>
            <li>소거법 풀이 연습</li>
            <li>목표: 15분 내 풀이</li>
          </ul>
        </div>

        {/* Week 2 */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2">🗓️ Week 2 — 단어 + 독해</h3>
          <ul className="text-sm list-disc pl-5 space-y-1">
            <li>보카 1회독</li>
            <li>독해 패턴 학습</li>
            <li>풀이 순서 전략 (4→1→2→3)</li>
          </ul>
        </div>

        {/* Week 3 */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2">🗓️ Week 3 — 청취 + 실전</h3>
          <ul className="text-sm list-disc pl-5 space-y-1">
            <li>노트테이킹 훈련</li>
            <li>첫/마지막 문제 집중</li>
            <li>모의고사 시작</li>
          </ul>
        </div>

        {/* Week 4 */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2">🗓️ Week 4 — 기출 반복</h3>
          <ul className="text-sm list-disc pl-5 space-y-1">
            <li>매일 모의고사</li>
            <li>오답노트</li>
            <li>시험 전 1Day 정리</li>
          </ul>
        </div>

        {/* 점수표 */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2">📊 점수별 전략</h3>
          <table className="w-full text-sm border">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">목표</th>
                <th className="p-2 border">전략</th>
              </tr>
            </thead>
            <tbody>
              <tr><td className="border p-2">43~50</td><td className="border p-2">문법 집중</td></tr>
              <tr><td className="border p-2">65</td><td className="border p-2">문법 + 독해</td></tr>
              <tr><td className="border p-2">75</td><td className="border p-2">문법 만점 + 독해</td></tr>
              <tr><td className="border p-2">80+</td><td className="border p-2">전 영역</td></tr>
            </tbody>
          </table>
        </div>

        {/* 주의사항 */}
        <div className="text-sm text-red-500">
          ⚠️ OMR 마킹 시간 확보 / 문법 15분 내 풀이 필수 / 단어 꾸준히
        </div>
      </div>
    </div>
  );
}
