from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

# HTML 템플릿 - 중괄호를 이스케이프하여 스타일 부분과 변수 부분을 구분
HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>간단한 웹 서버</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f0f0f0;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>환영합니다!</h1>
        <p>이 페이지는 Python으로 만든 간단한 웹 서버에서 제공됩니다.</p>
        <p>서버 호스트명: {hostname}</p>
        <p>서버 IP: {ip}</p>
    </div>
</body>
</html>
"""

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # 기본 페이지 요청 처리
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                # 서버 정보 가져오기
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                
                # HTML 페이지 생성 및 전송
                response = HTML.format(hostname=hostname, ip=ip)
                self.wfile.write(response.encode('utf-8'))
            else:
                # 404 에러 처리 - 한글 메시지를 ASCII로 변환
                self.send_response(404)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                error_message = "페이지를 찾을 수 없습니다."
                self.wfile.write(f"404 Error: {error_message}".encode('utf-8'))
        except Exception as e:
            print(f"오류 발생: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("500 Internal Server Error".encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHandler)
    print(f"서버가 포트 {port}에서 실행 중입니다...")
    print(f"다음 주소로 접속하세요: http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()