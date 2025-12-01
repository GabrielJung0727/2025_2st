import socket
import threading
import datetime

def handle_client(client_socket, addr):
    """클라이언트 연결을 처리하는 함수"""
    print(f"\n[+] 클라이언트 접속: {addr}")
    
    try:
        while True:
            # 클라이언트로부터 데이터 수신
            data = client_socket.recv(1024)
            if not data:
                print(f"[-] 클라이언트 {addr} 연결 종료")
                break
            
            # 수신한 메시지 출력
            msg = data.decode('utf-8')
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] {addr}로부터 수신: {msg}")
            
            # 클라이언트에게 응답 전송
            response = f"서버 응답: '{msg}' 메시지를 받았습니다."
            client_socket.send(response.encode('utf-8'))
            
    except Exception as e:
        print(f"[-] 클라이언트 {addr} 처리 중 오류 발생: {e}")
    
    finally:
        client_socket.close()

def start_server(host='0.0.0.0', port=9999):
    """TCP 서버를 시작하는 함수"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 소켓에 주소 바인딩
        server.bind((host, port))
        # 연결 대기 시작
        server.listen(5)
        print(f"[*] 서버가 {host}:{port}에서 시작되었습니다.")
        
        while True:
            # 클라이언트 연결 수락
            client, addr = server.accept()
            
            # 각 클라이언트를 별도의 스레드에서 처리
            client_handler = threading.Thread(
                target=handle_client,
                args=(client, addr)
            )
            client_handler.start()
            
    except Exception as e:
        print(f"[-] 서버 오류 발생: {e}")
    
    finally:
        server.close()

def main():
    print("=== TCP 서버 ===")
    print("서버를 종료하려면 Ctrl+C를 누르세요.")
    
    # 서버 설정
    HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 연결 수락
    PORT = 9999       # 포트 번호
    
    try:
        start_server(HOST, PORT)
    except KeyboardInterrupt:
        print("\n[*] 서버를 종료합니다...")

if __name__ == '__main__':
    main()
