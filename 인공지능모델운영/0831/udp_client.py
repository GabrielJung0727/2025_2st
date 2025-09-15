import socket
import threading
import datetime
import sys

class UDPClient:
    def __init__(self, server_host='localhost', server_port=9998):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
        
        # 브로드캐스트 수신을 위한 설정
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.broadcast_socket.bind(('', server_port))
    
    def receive_broadcast(self):
        """브로드캐스트 메시지 수신"""
        while self.running:
            try:
                data, addr = self.broadcast_socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"\n[브로드캐스트] {addr}로부터 수신: {message}")
            except Exception as e:
                if self.running:  # 정상 종료가 아닌 경우만 에러 출력
                    print(f"[-] 브로드캐스트 수신 중 오류 발생: {e}")
    
    def receive_response(self):
        """서버로부터의 응답 수신"""
        try:
            data, _ = self.client_socket.recvfrom(1024)
            response = data.decode('utf-8')
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] {response}")
        except Exception as e:
            print(f"[-] 응답 수신 중 오류 발생: {e}")
    
    def start(self):
        """클라이언트 시작"""
        self.running = True
        
        # 브로드캐스트 수신 스레드 시작
        broadcast_thread = threading.Thread(target=self.receive_broadcast)
        broadcast_thread.daemon = True
        broadcast_thread.start()
        
        print(f"=== UDP 클라이언트 ===")
        print(f"서버 주소: {self.server_host}:{self.server_port}")
        print("'quit' 또는 'exit'를 입력하면 프로그램이 종료됩니다.")
        
        try:
            while self.running:
                message = input("\n전송할 메시지를 입력하세요: ")
                
                if message.lower() in ['quit', 'exit']:
                    self.running = False
                    break
                
                # 메시지 전송
                self.client_socket.sendto(
                    message.encode('utf-8'),
                    (self.server_host, self.server_port)
                )
                
                # 응답 수신
                self.receive_response()
                
        except KeyboardInterrupt:
            print("\n[*] 클라이언트를 종료합니다...")
        except Exception as e:
            print(f"[-] 오류 발생: {e}")
        finally:
            self.running = False
            self.client_socket.close()
            self.broadcast_socket.close()

def main():
    # 서버 설정
    SERVER_HOST = 'localhost'  # 서버 호스트
    SERVER_PORT = 9998         # 서버 포트
    
    # 명령행 인자로 서버 주소를 받을 수 있음
    if len(sys.argv) > 1:
        SERVER_HOST = sys.argv[1]
    
    # 클라이언트 시작
    client = UDPClient(SERVER_HOST, SERVER_PORT)
    client.start()

if __name__ == '__main__':
    main()
