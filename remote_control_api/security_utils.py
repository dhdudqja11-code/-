from fastapi import Depends, HTTPException, Security
from typing import Annotated
import bcrypt
from schemas import Role, UserCredentials

# 🚨 중요: 실제 환경에서는 Redis나 DB에서 토큰/권한을 검증해야 합니다. 여기는 더미 구현입니다.


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 해시하여 검증합니다."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_current_user(credentials: UserCredentials):
    """
    [OAuth 2.0 Dummy] 사용자 인증을 시뮬레이션하고 토큰을 발행하는 로직입니다.
    실제로는 DB에서 유저 정보를 가져와 패스워드 검증 후 JWT를 발급해야 합니다.
    """
    # 더미 검증: username='admin' and password='secure' 일 때만 성공 가정
    if credentials.username != "admin" or credentials.password != "secure":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print("✅ Auth Service: User authenticated successfully.")
    # 실제로는 JWT를 반환해야 하지만, 여기서는 사용자를 직접 반환합니다.
    return {"username": credentials.username, "role": Role.ADMIN}

def get_current_user_with_rbac(
    credentials: Annotated[UserCredentials, Security()], 
    required_role: Role
):
    """
    [RBAC Dummy] 현재 사용자의 역할을 검사하고 필요한 권한이 있는지 확인합니다.
    OAuth 토큰을 통해 유저 정보를 가져오는 과정이 생략되어 있습니다.
    """
    user = get_current_user(credentials) # 먼저 인증 수행
    
    # Role Hierarchy: ADMIN > OPERATOR > VIEWER
    roles_order = {Role.VIEWER: 1, Role.OPERATOR: 2, Role.ADMIN: 3}

    if roles_order[user["role"]] < roles_order[required_role]:
        raise HTTPException(status_code=403, detail=f"Permission Denied. Requires {required_role} role.")
    
    print(f"✅ RBAC Check: User '{user['username']}' passed check for role '{required_role}'.")
    return user

# ⚠️ 주의: 이 함수는 실제 토큰 파싱 및 검증을 수행하는 것이 아니라,
# FastAPI 의존성 주입 테스트를 위해 Dummy로 사용됩니다.