import socket
import ipaddress
import netifaces
import requests

def get_private_ip():
    """로컬 시스템의 사설 IP 주소들을 가져옵니다."""
    private_ips = []
    
    # 모든 네트워크 인터페이스 확인
    for interface in netifaces.interfaces():
        try:
            # IPv4 주소 정보 가져오기
            addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
            for addr in addrs:
                ip = addr['addr']
                # 사설 IP 주소인지 확인
                if ipaddress.ip_address(ip).is_private:
                    private_ips.append((interface, ip))
        except Exception as e:
            print(f"인터페이스 {interface} 확인 중 오류 발생: {e}")
    
    return private_ips

def get_public_ip():
    """공인 IP 주소를 가져옵니다."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        return f"공인 IP 확인 중 오류 발생: {e}"

def check_ip_type(ip_str):
    """IP 주소의 종류와 특성을 분석합니다."""
    try:
        ip = ipaddress.ip_address(ip_str)
        
        info = {
            "IP 주소": str(ip),
            "버전": f"IPv{ip.version}",
            "사설 IP 여부": ip.is_private,
            "루프백 여부": ip.is_loopback,
            "링크로컬 여부": ip.is_link_local,
            "멀티캐스트 여부": ip.is_multicast,
            "예약된 주소 여부": ip.is_reserved
        }
        
        # 사설 IP 범위 확인
        if ip.is_private:
            if ipaddress.IPv4Address('10.0.0.0') <= ip <= ipaddress.IPv4Address('10.255.255.255'):
                info["사설 IP 범위"] = "Class A (10.0.0.0/8)"
            elif ipaddress.IPv4Address('172.16.0.0') <= ip <= ipaddress.IPv4Address('172.31.255.255'):
                info["사설 IP 범위"] = "Class B (172.16.0.0/12)"
            elif ipaddress.IPv4Address('192.168.0.0') <= ip <= ipaddress.IPv4Address('192.168.255.255'):
                info["사설 IP 범위"] = "Class C (192.168.0.0/16)"
        
        return info
    except ValueError as e:
        return f"잘못된 IP 주소 형식: {e}"

def main():
    print("=== IP 주소 분석 도구 ===\n")
    
    # 호스트 이름 출력
    print(f"호스트 이름: {socket.gethostname()}")
    
    # 공인 IP 출력
    public_ip = get_public_ip()
    print(f"\n공인 IP 주소: {public_ip}")
    
    # 사설 IP 목록 출력
    print("\n사설 IP 주소 목록:")
    private_ips = get_private_ip()
    for interface, ip in private_ips:
        print(f"인터페이스: {interface}, IP: {ip}")
    
    while True:
        print("\n=== 메뉴 ===")
        print("1. IP 주소 분석")
        print("2. 현재 시스템의 모든 IP 정보 새로고침")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            ip = input("\n분석할 IP 주소를 입력하세요: ").strip()
            info = check_ip_type(ip)
            if isinstance(info, dict):
                print("\nIP 주소 분석 결과:")
                for key, value in info.items():
                    print(f"{key}: {value}")
            else:
                print(info)
        
        elif choice == '2':
            print("\n=== 시스템 IP 정보 새로고침 ===")
            print(f"\n호스트 이름: {socket.gethostname()}")
            public_ip = get_public_ip()
            print(f"공인 IP 주소: {public_ip}")
            print("\n사설 IP 주소 목록:")
            private_ips = get_private_ip()
            for interface, ip in private_ips:
                print(f"인터페이스: {interface}, IP: {ip}")
        
        elif choice == '3':
            print("\n프로그램을 종료합니다.")
            break
        
        else:
            print("\n잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == '__main__':
    main()
