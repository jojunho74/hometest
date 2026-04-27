"""
F-Visa Jobs API 프록시 서버
실행: python fvisa-proxy.py
포트: 8766
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse, urllib.request

API_KEY = 'fd0e3d05449e164a7c3f2fc5a1c1853e48fbe19516aba543055b1eb60daafac3'
API_BASE = 'https://apis.data.go.kr/B490007/Employment'
PORT = 8766

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        page_no  = params.get('pageNo',  ['1'])[0]
        num_rows = params.get('numOfRows', ['12'])[0]

        url = (f'{API_BASE}?serviceKey={API_KEY}'
               f'&method=getApiEmployment'
               f'&pageNo={page_no}&numOfRows={num_rows}')
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/xml, text/xml, */*',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        print(f'[fvisa-proxy] {fmt % args}')

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'✅ F-Visa 프록시 실행 중: http://127.0.0.1:{PORT}')
    print(f'   테스트: http://127.0.0.1:{PORT}?pageNo=1&numOfRows=3')
    print('   종료: Ctrl+C')
    server.serve_forever()
