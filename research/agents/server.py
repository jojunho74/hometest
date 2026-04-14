"""
웹서버 (server.py)
n8n HTTP Request 노드에서 호출받아 파이프라인 실행
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import sys
import os

# 같은 폴더에서 실행
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import agent_automation
import agent_selector
import agent_collector

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/run':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # 백그라운드에서 파이프라인 실행
            def run():
                os.makedirs('logs', exist_ok=True)
                result = agent_automation.run_pipeline()
                print(f"[완료] {result}")

            t = threading.Thread(target=run)
            t.start()

            self.wfile.write(json.dumps({
                'status': 'started',
                'message': '수집 파이프라인이 시작되었습니다'
            }, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/preview':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            sites = agent_collector.get_active_sites()
            preview = []
            for site in sites:
                posts = agent_collector.collect_from_site(site)
                preview.append({
                    'school_name': site['school_name'],
                    'posts': posts[:5]  # 최대 5개만 미리보기
                })
            self.wfile.write(json.dumps({
                'status': 'ok',
                'preview': preview
            }, ensure_ascii=False).encode('utf-8'))

        elif self.path == '/detect':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            detect_results = {'status': 'running', 'results': []}

            def do_detect():
                detect_results['results'] = agent_selector.run()
                detect_results['status'] = 'done'
                print(f"[감지완료] {len(detect_results['results'])}개")

            t = threading.Thread(target=do_detect)
            t.start()
            t.join(timeout=120)  # 최대 2분 대기

            self.wfile.write(json.dumps({
                'status': 'ok',
                'results': detect_results['results']
            }, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

if __name__ == '__main__':
    port = 8765
    print(f"서버 시작: http://localhost:{port}")
    print(f"수집 실행: POST http://localhost:{port}/run")
    print(f"상태 확인: GET  http://localhost:{port}/health")
    HTTPServer(('', port), Handler).serve_forever()
