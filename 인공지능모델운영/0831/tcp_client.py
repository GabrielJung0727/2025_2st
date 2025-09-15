import socket
import threading
import datetime
import sys

class TCPClient:
    def __init__(self, server_host='localhost', server_port=9999):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
    
    def receive_messages(self):
        """서버로부터 메시지를 수신하는 스레드 함수"""
        while self.running:
            try:
                # 서버로부터 데이터 수신
                data = self.client_socket.recv(1024)
                if not data:
                    print("\n[-] 서버와의 연결이 종료되었습니다.")
                    self.running = False
                    break
                
                # 수신한 메시지 출력
                message = data.decode('utf-8')
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{current_time}] 서버 응답: {message}")
                print("\n전송할 메시지를 입력하세요: ", end='', flush=True)
                
            except Exception as e:
                if self.running:  # 정상 종료가 아닌 경우만 에러 출력
                    print(f"\n[-] 메시지 수신 중 오류 발생: {e}")
                break
    
    def connect_to_server(self):
        """서버에 연결"""
        try:
            print(f"[*] 서버 {self.server_host}:{self.server_port}에 연결 중...")
            self.client_socket.connect((self.server_host, self.server_port))
            print("[+] 서버에 연결되었습니다!")
            return True
        except Exception as e:
            print(f"[-] 서버 연결 실패: {e}")
            return False
    
    def start(self):
        """클라이언트 시작"""
        if not self.connect_to_server():
            return
        
        self.running = True
        
        # 메시지 수신 스레드 시작
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        print("\n=== TCP 클라이언트 ===")
        print("'quit' 또는 'exit'를 입력하면 프로그램이 종료됩니다.")
        
        try:
            while self.running:
                message = input("\n전송할 메시지를 입력하세요: ")
                
                if message.lower() in ['quit', 'exit']:
                    self.running = False
                    break
                
                # 서버로 메시지 전송
                self.client_socket.send(message.encode('utf-8'))
                
        except KeyboardInterrupt:
            print("\n[*] 클라이언트를 종료합니다...")
        except Exception as e:
            print(f"[-] 오류 발생: {e}")
        finally:
            self.running = False
            self.client_socket.close()
    
    def send_file(self, file_path):
        """파일 전송 (추가 기능)"""
        try:
            with open(file_path, 'rb') as f:
                # 파일 이름 전송
                file_name = file_path.split('/')[-1]
                self.client_socket.send(f"FILE:{file_name}".encode('utf-8'))
                
                # 파일 데이터 전송
                data = f.read(1024)
                while data:
                    self.client_socket.send(data)
                    data = f.read(1024)
                
                # 전송 완료 표시
                self.client_socket.send(b"EOF")
                print(f"[+] 파일 {file_name} 전송 완료")
                
        except Exception as e:
            print(f"[-] 파일 전송 중 오류 발생: {e}")

def main():
    # 서버 설정
    SERVER_HOST = 'localhost'  # 기본 서버 호스트
    SERVER_PORT = 9999         # 기본 서버 포트
    
    # 명령행 인자로 서버 주소를 받을 수 있음
    if len(sys.argv) > 1:
        SERVER_HOST = sys.argv[1]
    
    # 클라이언트 시작
    client = TCPClient(SERVER_HOST, SERVER_PORT)
    
    try:
        client.start()
    except Exception as e:
        print(f"[-] 프로그램 실행 중 오류 발생: {e}")

if __name__ == '__main__':
    main()
