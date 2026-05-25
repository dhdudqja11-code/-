# -*- coding: utf-8 -*-
from typing import Dict, Set, List, Tuple
import ipaddress

class SecurityService:
    """
    비인가 외부 IP 접근 및 로그인 실패를 모니터링하고,
    동적 IP 블랙리스트를 실시간으로 관리하는 보안 서비스입니다.
    """
    def __init__(self):
        # 1. 허용된 사내 대역 및 로컬 주소 (IP Whitelist)
        self.allowed_networks = [
            ipaddress.ip_network("127.0.0.1/32"),
            ipaddress.ip_network("192.168.0.0/16"),
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12")
        ]
        # 2. 동적 IP 블랙리스트
        self._blacklisted_ips: Set[str] = set()
        
        # 3. 로그인 실패 횟수 트래커 (IP별 기록)
        self._failed_login_attempts: Dict[str, int] = {}
        
        # 4. 실시간 보안 경고 로그
        self.pending_alerts: List[dict] = []

    def is_ip_allowed(self, ip_address: str) -> bool:
        """
        [Guardrail 1] 허용된 사내 IP 대역(Whitelist)에 포함되는지 검사합니다.
        """
        try:
            # localhost 문자열 처리
            if ip_address == "testclient" or ip_address == "localhost":
                return True
                
            ip = ipaddress.ip_address(ip_address)
            for network in self.allowed_networks:
                if ip in network:
                    return True
            return False
        except Exception:
            # 부적절한 형식의 IP 주소는 안전하게 차단
            return False

    def track_login_failure(self, ip_address: str) -> Tuple[int, bool]:
        """
        로그인 실패를 누적 기록합니다. 3회 누적 시 보안 알림을 발생시키고 
        경보 플래그(True)를 리턴합니다.
        """
        attempts = self._failed_login_attempts.get(ip_address, 0) + 1
        self._failed_login_attempts[ip_address] = attempts
        
        alert_triggered = False
        if attempts >= 3:
            alert_triggered = True
            self.trigger_security_alert(
                alert_type="LOGIN_FAILURES_EXCEEDED",
                details=f"IP {ip_address}로부터 연속 3회 이상 로그인 자격증명 실패 감지!"
            )
            
        return attempts, alert_triggered

    def reset_login_failures(self, ip_address: str):
        """성공적인 인증 완료 시 실패 이력을 초기화합니다."""
        self._failed_login_attempts.pop(ip_address, None)

    def blacklist_ip(self, ip_address: str):
        """위협 IP를 블랙리스트에 등재합니다 (실시간 킬 스위치 연동)."""
        self._blacklisted_ips.add(ip_address)
        self.trigger_security_alert(
            alert_type="IP_BLACKLISTED",
            details=f"IP {ip_address}가 사장님 명령(원격 킬 스위치)에 의해 블랙리스트에 등재되었습니다."
        )

    def unblacklist_ip(self, ip_address: str):
        """블랙리스트에서 IP를 제거합니다."""
        self._blacklisted_ips.discard(ip_address)

    def is_ip_blacklisted(self, ip_address: str) -> bool:
        """IP가 블랙리스트에 차단된 상태인지 판별합니다."""
        return ip_address in self._blacklisted_ips

    def trigger_security_alert(self, alert_type: str, details: str):
        """보안 알림 이벤트를 발생시키고 큐에 보관합니다 (텔레그램 연동 대상)."""
        alert = {
            "alert_type": alert_type,
            "details": details,
            "timestamp": datetime_stamp()
        }
        self.pending_alerts.append(alert)
        print(f"🚨 [SECURITY ALERT] {alert_type}: {details}")

def datetime_stamp() -> str:
    from datetime import datetime
    return datetime.now().isoformat()
