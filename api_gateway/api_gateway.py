import ipaddress
from typing import Dict, Any, Tuple

# 💡 상수 정의 (Guard Config)
ALLOWED_IP_RANGE = "192.168.1.0/24" # 예시: 사내망 IP 대역만 허용
RATE_LIMIT_PER_HOUR = 100          # 시간당 최대 요청 횟수
MIN_REQUIRED_PERMISSION = "PREMIUM_USER" # 최소 권한 레벨

def is_ip_valid(client_ip: str) -> bool:
    """
    [Guard 1] 요청 IP 검증 로직. 주어진 IP가 허용된 범위 내에 있는지 확인한다.
    """
    try:
        client_ip_obj = ipaddress.IPv4Address(client_ip)
        allowed_network = ipaddress.ip_network(ALLOWED_IP_RANGE)
        return client_ip_obj in allowed_network
    except ValueError:
        # IP 형식이 잘못된 경우에도 실패로 처리하여 보안 강화
        print(f"🚨 Validation Failed: Invalid IP format received: {client_ip}")
        return False

def check_rate_limit(user_id: str, current_request_count: int) -> Tuple[bool, float]:
    """
    [Guard 2] 사용량 카운터 체크 로직. 시간당 요청 제한을 초과했는지 확인한다.
    실제 환경에서는 Redis/DB를 사용해야 하지만, 여기서는 Mock으로 처리한다.
    """
    # 실제 구현 시: Cache(user_id, 'request_count') > RATE_LIMIT_PER_HOUR 여부를 체크
    if current_request_count >= RATE_LIMIT_PER_HOUR:
        return False, 3600.0 # Rate Limit 초과 (초)
    return True, 0.0

def check_authorization(user_id: str, user_permission: str) -> bool:
    """
    [Guard 3] 권한 레벨 비교 로직. 요청된 API를 사용하기 위한 최소 권한을 충족하는지 확인한다.
    """
    # 실제 구현 시: Permission Hierarchy (Basic < Premium < Admin)에 따른 계층적 검증 필요
    if user_permission == "ADMIN" or user_permission == "PREMIUM_USER":
        return True
    return False

def get_user_profile(client_ip: str, user_id: str, user_permission: str, current_request_count: int) -> Dict[str, Any]:
    """
    GET /v1/user/profile 엔드포인트의 전처리 로직을 수행하는 핵심 함수.
    세 가지 Guard Logic을 순차적으로 실행하며 실패 시 에러 메시지를 반환한다.
    """
    # 1. IP 주소 검증 (가장 먼저 체크하여 리소스 보호)
    if not is_ip_valid(client_ip):
        raise PermissionError("ACCESS DENIED: Invalid source IP address.")

    # 2. Rate Limiting 검사
    is_rate_ok, wait_time = check_rate_limit(user_id, current_request_count)
    if not is_rate_ok:
        # HTTP 429 Too Many Requests 응답을 유도하는 예외를 발생시킨다.
        raise TimeoutError(f"RATE LIMITED: Please wait {wait_time:.1f} seconds.")

    # 3. 권한 검증 (가장 비싼 로직이므로 마지막에 체크)
    if not check_authorization(user_id, user_permission):
        raise PermissionError("ACCESS DENIED: Insufficient authorization level for this resource.")

    # 모든 Guard를 통과했을 경우의 핵심 비즈니스 로직 실행 (Mock Data 반환)
    return {
        "status": "success",
        "message": f"Profile data retrieved successfully for user {user_id}.",
        "data": {
            "username": f"User_{user_id}",
            "profile_info": "High-value resource accessed.",
            "access_level": user_permission
        }
    }

# 💡 테스트를 위한 더미 설정 값 (실제로는 환경 변수에서 로드되어야 함)
TEST_CONFIG = {
    "IP_SUCCESS": "192.168.1.50",
    "IP_FAILURE": "10.0.0.1",
    "USER_ID_VALID": "user_abc",
    "PERMISSION_ADMIN": "ADMIN",
    "RATE_LIMIT_ZERO": 0,
}

# API Gateway 테스트용 Mock Context 제공 (사용자가 쉽게 호출하도록)
if __name__ == "__main__":
    print("--- [Mock Test Execution] ---")
    try:
        result = get_user_profile(
            client_ip=TEST_CONFIG["IP_SUCCESS"], 
            user_id=TEST_CONFIG["USER_ID_VALID"], 
            user_permission=TEST_CONFIG["PERMISSION_ADMIN"], 
            current_request_count=TEST_CONFIG["RATE_LIMIT_ZERO"]
        )
        print("\n✅ SUCCESS TEST: Gateway passed all guards.")
        import json
        print(json.dumps(result, indent=2))

    except (PermissionError, TimeoutError) as e:
        print(f"\n❌ FAILURE TEST: Guard failed gracefully. Error: {e}")