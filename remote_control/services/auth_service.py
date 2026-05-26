import time
from typing import Optional, Tuple

# --- 가상의 데이터베이스 역할 ---
USER_CREDENTIALS = {
    "user-A1B2C3": {"role": "ADMIN", "is_active": True}, # 최고 관리자 권한
    "user-D4E5F6": {"role": "BASIC", "is_active": True}  # 일반 사용자
}

SECRET_KEY = "SUPER_SECURE_DEV_KEY_REPLACE_ME" 

def generate_jwt(user_id: str, role: str) -> str:
    """
    사용자 ID와 역할을 포함하는 JWT 토큰을 생성합니다. (실제로는 PyJWT 라이브러리 사용 권장)
    여기서는 단순한 시뮬레이션 문자열로 대체합니다.
    """
    # 실제 환경에서는 만료 시간(exp)과 발행 시간(iat)을 반드시 넣어야 합니다.
    return f"Bearer.{user_id}.{role}.{int(time.time())}"

def validate_token(token: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    토큰의 유효성 및 만료 시간을 검증합니다.
    Args: token (Bearer.<user_id>.<role>.<timestamp>)
    Returns: (is_valid, user_id, role)
    """
    try:
        parts = token.split('.')
        if len(parts) != 4 or parts[0].lower() != "bearer":
            return False, None, None

        user_id = parts[1]
        role = parts[2]
        timestamp = int(parts[3])

        # 토큰 만료 시간 검증 (간단하게 현재 시간과 비교)
        if timestamp < (time.time() - 60): # 예: 60초 이상 지난 경우 무효 처리 가정
            return False, None, None
        
        # DB에서 사용자 활성 상태 확인 로직 추가 필요
        user_info = USER_CREDENTIALS.get(user_id)
        if not user_info or not user_info['is_active']:
             print(f"Auth Failed: User {user_id} is inactive.")
             return False, None, None

        return True, user_id, role
    except Exception as e:
        print(f"Validation Error: {e}")
        return False, None, None

def check_permission(role: str, required_role: str) -> bool:
    """특정 권한이 필요한지 확인하는 게이트 역할을 수행합니다."""
    # Admin >= Basic (가장 간단한 Role Hierarchy 가정)
    if role == "ADMIN": return True
    if required_role == "BASIC" and role in ["ADMIN", "BASIC"]: return True
    return False

print("✅ Auth Service 스캐폴딩 완료. JWT와 ACL 검증 로직 정의됨.")