# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('c:/Users/User/Desktop/homepage/pdf_catalog.json', encoding='utf-8'))
categories = ['전체', '공공기관', '공기업', '연구원', '대학병원', '기타']

badge_colors = {
    '공공기관': '#1E4D8C',
    '공기업':   '#166534',
    '연구원':   '#6D28D9',
    '대학병원': '#DC2626',
    '기타':     '#92400E'
}

# 카드 HTML
cards_html = ''
for item in data:
    fn = item['filename'].replace('"', '&quot;')
    color = badge_colors.get(item['category'], '#4B5563')
    cards_html += (
        f'<div class="card" data-category="{item["category"]}" '
        f'data-institution="{item["institution"]}" data-title="{item["title"]}">'
        f'<div class="card-header">'
        f'<span class="badge" style="background:{color};">{item["category"]}</span>'
        f'<span class="pages">{item.get("pages",0)}p · {item.get("size_kb",0)}KB</span>'
        f'</div>'
        f'<p class="institution">{item["institution"]}</p>'
        f'<p class="title">{item["title"]}</p>'
        f'<a href="./resource/{fn}" download class="dl-btn">↓ 다운로드</a>'
        f'</div>'
    )

# 필터 버튼
filter_btns = ''
for c in categories:
    active = ' active' if c == '전체' else ''
    filter_btns += f'<button class="filter-btn{active}" onclick="setCategory(this,\'{c}\')">{c}</button>'

html = '''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>채용공고 자료실</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;}
    body{font-family:"Apple SD Gothic Neo","Noto Sans KR",sans-serif;background:#F8FAFF;color:#1E293B;}
    .wrap{max-width:1100px;margin:0 auto;padding:40px 16px;}
    h1{font-size:1.75rem;font-weight:800;color:#0B1D3A;margin:16px 0 4px;}
    .subtitle{color:#64748B;font-size:14px;margin-bottom:24px;}
    #search{width:100%;padding:10px 16px;border:1.5px solid #CBD5E1;border-radius:10px;font-size:14px;outline:none;}
    #search:focus{border-color:#1E4D8C;}
    .filters{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0;}
    .filter-btn{padding:6px 16px;border-radius:999px;font-size:13px;font-weight:600;cursor:pointer;border:1.5px solid #CBD5E1;background:#fff;color:#475569;transition:background .3s,color .3s,border-color .3s,box-shadow .3s,transform .2s;}
    .filter-btn.active{background:#1E4D8C;color:#fff;border-color:#1E4D8C;}
    .filter-btn.pulse{background:#D4A017;color:#fff;border-color:#D4A017;transform:scale(1.08);box-shadow:0 4px 14px rgba(212,160,23,0.45);}
    #count{font-size:13px;color:#64748B;margin-bottom:16px;}
    #grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;}
    .card{background:#fff;border-radius:12px;padding:18px;border:1px solid #E2E8F0;display:flex;flex-direction:column;gap:8px;box-shadow:0 1px 4px rgba(0,0,0,.06);transition:box-shadow .2s,transform .2s;}
    .card:hover{box-shadow:0 4px 16px rgba(0,0,0,.1);transform:translateY(-2px);}
    .card.hidden{display:none;}
    .card-header{display:flex;justify-content:space-between;align-items:center;}
    .badge{color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;}
    .pages{font-size:11px;color:#94A3B8;}
    .institution{font-size:11px;font-weight:700;color:#1E4D8C;}
    .title{font-size:13px;font-weight:600;color:#1E293B;line-height:1.4;flex:1;}
    .dl-btn{display:block;text-align:center;padding:7px 0;background:#1E4D8C;color:#fff;border-radius:8px;font-size:12px;font-weight:600;text-decoration:none;transition:background .15s;}
    .dl-btn:hover{background:#163870;}
    #empty{display:none;text-align:center;color:#94A3B8;padding:60px 0;font-size:15px;}
    .back{font-size:13px;color:#1E4D8C;text-decoration:none;}
    .back:hover{text-decoration:underline;}
    header{position:sticky;top:0;z-index:50;background:#fff;border-bottom:1px solid #E2E8F0;box-shadow:0 1px 4px rgba(0,0,0,.06);}
    .hinner{max-width:1100px;margin:0 auto;padding:0 16px;height:64px;display:flex;align-items:center;justify-content:space-between;}
    .hlogo{font-size:1rem;font-weight:800;color:#1E4D8C;text-decoration:none;}
    .hnav{display:flex;align-items:center;gap:20px;font-size:0.8rem;font-weight:600;}
    .hnav a{color:#475569;text-decoration:none;transition:color .15s;}
    .hnav a:hover{color:#1E4D8C;}
    .hbtn{padding:8px 18px;border-radius:8px;font-size:0.8rem;font-weight:700;background:#1E4D8C;color:#fff;text-decoration:none;transition:background .15s;}
    .hbtn:hover{background:#163870;}
    .hamburger{display:none;flex-direction:column;justify-content:center;gap:5px;width:36px;height:36px;cursor:pointer;background:none;border:none;padding:4px;}
    .hamburger span{display:block;height:2px;background:#1E293B;border-radius:2px;transition:transform .25s,opacity .25s;}
    .hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg);}
    .hamburger.open span:nth-child(2){opacity:0;}
    .hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
    .mobile-menu{display:none;flex-direction:column;background:#fff;border-top:1px solid #E2E8F0;padding:12px 16px 16px;}
    .mobile-menu a{padding:12px 4px;font-size:0.9rem;font-weight:600;color:#1E293B;text-decoration:none;border-bottom:1px solid #F1F5F9;}
    .mobile-menu a:last-child{border-bottom:none;}
    .mobile-menu .mbtn{margin-top:12px;display:block;text-align:center;padding:12px;border-radius:8px;background:#1E4D8C;color:#fff;font-weight:700;text-decoration:none;}
    .mobile-menu.open{display:flex;}
    @media(max-width:640px){.hnav{display:none;}.hbtn{display:none;}.hamburger{display:flex;}}
  </style>
</head>
<body>
<header>
  <div class="hinner">
    <a href="index.html" class="hlogo">지텔프IBT 대학컨설팅</a>
    <nav class="hnav">
      <a href="index.html#about">서비스 소개</a>
      <a href="index.html#process">진행 방법</a>
      <a href="library.html">홍보문구 라이브러리</a>
      <a href="library-pdf.html">채용공고 자료실</a>
      <a href="index.html#faq">FAQ</a>
      <a href="index.html#university-news">대학소식</a>
    </nav>
    <div style="display:flex;align-items:center;gap:8px;">
      <a href="index.html#consultation-form" class="hbtn">무료 신청하기</a>
      <button class="hamburger" id="hamburger" onclick="toggleMenu()" aria-label="메뉴">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
  <div class="mobile-menu" id="mobile-menu">
    <a href="index.html#about">서비스 소개</a>
    <a href="index.html#process">진행 방법</a>
    <a href="library.html">홍보문구 라이브러리</a>
    <a href="library-pdf.html">채용공고 자료실</a>
    <a href="index.html#faq">FAQ</a>
    <a href="index.html#university-news">대학소식</a>
    <a href="index.html#consultation-form" class="mbtn">무료 신청하기</a>
  </div>
</header>
<div class="wrap">
  <h1>채용공고 자료실</h1>
  <p class="subtitle">공공기관·공기업·연구원 채용공고 ''' + str(len(data)) + '''개 — 검색 후 바로 다운로드</p>
  <input id="search" type="text" placeholder="기관명 또는 공고 제목 검색..." oninput="filterCards()"/>
  <div class="filters">''' + filter_btns + '''</div>
  <p id="count">''' + str(len(data)) + '''개 표시 중</p>
  <div id="grid">''' + cards_html + '''</div>
  <p id="empty">검색 결과가 없습니다.</p>
</div>
<script>
  function toggleMenu() {
    const m = document.getElementById('mobile-menu');
    const h = document.getElementById('hamburger');
    m.classList.toggle('open');
    h.classList.toggle('open');
  }
  let currentCat = '전체';
  function setCategory(btn, cat) {
    currentCat = cat;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterCards();
  }
  function filterCards() {
    const q = document.getElementById('search').value.toLowerCase();
    const cards = document.querySelectorAll('.card');
    let n = 0;
    cards.forEach(c => {
      const catOk = currentCat === '전체' || c.dataset.category === currentCat;
      const txtOk = !q || c.dataset.institution.toLowerCase().includes(q) || c.dataset.title.toLowerCase().includes(q);
      if (catOk && txtOk) { c.classList.remove('hidden'); n++; }
      else c.classList.add('hidden');
    });
    document.getElementById('count').textContent = n + '개 표시 중';
    document.getElementById('empty').style.display = n === 0 ? 'block' : 'none';
  }

  // 분류 버튼 순차 깜빡임 (전체 제외)
  (function() {
    const allBtns = Array.from(document.querySelectorAll('.filter-btn'));
    const catBtns = allBtns.filter(b => b.textContent.trim() !== '전체');
    if (catBtns.length === 0) return;
    let cur = 0;
    setInterval(() => {
      catBtns.forEach(b => b.classList.remove('pulse'));
      if (currentCat === '전체') {
        catBtns[cur].classList.add('pulse');
      }
      cur = (cur + 1) % catBtns.length;
    }, 1800);
  })();
</script>
</body>
</html>'''

with open('c:/Users/User/Desktop/homepage/library-pdf.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('완료! library-pdf.html 생성 (' + str(len(data)) + '개)')
