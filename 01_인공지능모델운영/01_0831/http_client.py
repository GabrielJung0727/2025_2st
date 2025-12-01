import requests
import sys
import json

def send_request(url, path='/'):
    """
    지정된 URL로 HTTP GET 요청을 보내고 응답을 처리합니다.
    """
    try:
        # 전체 URL 생성
        full_url = f"{url.rstrip('/')}{path}"
        print(f"\n요청 보내는 중: {full_url}")
        
        # GET 요청 보내기
        response = requests.get(full_url)
        
        # 응답 상태 코드 출력
        print(f"\n응답 상태 코드: {response.status_code}")
        print("응답 헤더:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        # 응답 내용 출력
        print("\n응답 내용:")
        print(response.text)
        
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"오류: 서버 연결 실패. 서버가 실행 중인지 확인하세요.")
        return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def main():
    # 기본 서버 URL
    default_url = "http://localhost:8000"
    
    # 명령행 인자로 URL을 받거나 기본값 사용
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    while True:
        print("\n=== HTTP 클라이언트 메뉴 ===")
        print("1. 메인 페이지 요청 (/)")
        print("2. 존재하지 않는 페이지 요청 (404 에러 테스트)")
        print("3. 사용자 정의 경로 요청")
        print("4. 종료")
        
        choice = input("\n선택하세요 (1-4): ").strip()
        
        if choice == '1':
            send_request(url, '/')
        elif choice == '2':
            send_request(url, '/nonexistent')
        elif choice == '3':
            path = input("요청할 경로를 입력하세요 (예: /test): ").strip()
            send_request(url, path)
        elif choice == '4':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == '__main__':
    main()
