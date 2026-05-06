import sys; sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client
from collections import Counter
import os

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

# 1. 순수 페이지뷰 카운트
r1 = sb.table("page_views").select("id", count="exact").eq("page", "evidence/sample.html").execute()
print(f"페이지뷰 (evidence/sample.html): {r1.count}건")

# 2. 이벤트 액션 전체 카운트
r2 = sb.table("page_views").select("id", count="exact").like("page", "evidence/sample.html:%").execute()
print(f"이벤트 액션 전체: {r2.count}건")

# 3. 이벤트별 집계
r3 = sb.table("page_views").select("page").like("page", "evidence/sample.html:%").limit(5000).execute()
rows = r3.data or []
actions = [r["page"].split(":")[1] for r in rows if ":" in r["page"]]
print("이벤트별 집계:")
for k, v in Counter(actions).most_common():
    print(f"  {k}: {v}건")

# 4. 최근 5건
r4 = sb.table("page_views").select("page, visited_at").like("page", "evidence/sample.html%").order("visited_at", desc=True).limit(5).execute()
print("\n최근 5건:")
for r in r4.data or []:
    print(f"  {r['visited_at'][:19]}  {r['page']}")
