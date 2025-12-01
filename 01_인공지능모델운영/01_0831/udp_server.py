import socket
import datetime
import threading
import signal
import sys

class UDPServer:
    def __init__(self, host='0.0.0.0', port=9998):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
        
        # Ctrl+C 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Ctrl+C 처리를 위한 시그널 핸들러"""
        print("\n[*] 서버를 종료합니다...")
        self.running = False
        self.server_socket.close()
        sys.exit(0)
    
    def get_current_time(self):
        """현재 시간을 문자열로 반환"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def start(self):
        """UDP 서버 시작"""
        try:
            # 소켓 바인딩
            self.server_socket.bind((self.host, self.port))
            print(f"[*] UDP 서버가 {self.host}:{self.port}에서 시작되었습니다.")
            print("[*] 서버를 종료하려면 Ctrl+C를 누르세요.")
            
            self.running = True
            buffer_size = 1024
            
            while self.running:
                try:
                    # 데이터 수신 대기
                    data, client_address = self.server_socket.recvfrom(buffer_size)
                    current_time = self.get_current_time()
                    
                    # 수신한 데이터 처리
                    message = data.decode('utf-8')
                    print(f"\n[{current_time}] {client_address}로부터 수신: {message}")
                    
                    # 클라이언트에게 응답
                    response = f"서버 응답: '{message}' 메시지를 받았습니다."
                    self.server_socket.sendto(response.encode('utf-8'), client_address)
                    
                except Exception as e:
                    print(f"[-] 메시지 처리 중 오류 발생: {e}")
                    
        except Exception as e:
            print(f"[-] 서버 오류 발생: {e}")
            
        finally:
            self.server_socket.close()
    
    def send_broadcast(self, message, port):
        """브로드캐스트 메시지 전송 (옵션)"""
        try:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', port))
            print(f"[*] 브로드캐스트 메시지 전송: {message}")
        except Exception as e:
            print(f"[-] 브로드캐스트 전송 중 오류 발생: {e}")
        finally:
            broadcast_socket.close()

def main():
    print("=== UDP 서버 ===")
    
    # 서버 설정
    HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 수신
    PORT = 9998       # 포트 번호
    
    # 서버 인스턴스 생성 및 시작
    server = UDPServer(HOST, PORT)
    
    try:
        # 브로드캐스트 메시지 전송 (옵션)
        broadcast_thread = threading.Thread(
            target=server.send_broadcast,
            args=("UDP 서버가 시작되었습니다!", PORT)
        )
        broadcast_thread.daemon = True
        broadcast_thread.start()
        
        # 서버 시작
        server.start()
        
    except Exception as e:
        print(f"[-] 메인 스레드 오류: {e}")

if __name__ == '__main__':
    main()
