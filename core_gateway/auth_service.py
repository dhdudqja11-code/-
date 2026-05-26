# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel

# 환경 변수 대신 PoC용으로 정의된 비밀 대칭 키
SECRET_KEY = "YOUR_SUPER_SECRET_JWT_KEY" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTPBearer 보안 체계 인스턴스 생성 (Depends(...) 오류 완전 해소)
security = HTTPBearer(auto_error=True)

class UserPayload(BaseModel):
    """토큰에서 디코딩되어 검증되는 사용자 페이로드 구조."""
    user_id: str
    roles: List[str]
    is_active: bool

def create_access_token(data: dict, expires_delta_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """테스트 및 실 구동을 위해 유효한 Access Token을 발급하는 헬퍼 함수."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
    to_encode.update({
        "exp": expire,
        "active": data.get("active", True)
    })
    # 테스트 편의성을 위해 기본적으로 HS256으로 서명 인코딩 수행
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def decode_jwt(token: str) -> UserPayload:
    """
    JWT 토큰을 디코딩하고 유효성을 검사합니다.
    HS256과 RS256 두 알고리즘을 하이브리드 지원합니다.
    """
    try:
        # RS256 및 HS256 양대 규격을 모두 수용하도록 디코딩 필터 명시
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256", "RS256"])
        
        # sub(user_id) 추출 및 roles, active 상태 매핑
        user_id: str = payload.get("sub")
        roles: List[str] = payload.get("roles", [])
        is_active: bool = payload.get("active", False)

        if user_id is None or not roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Missing required claims (sub or roles)."
            )

        return UserPayload(user_id=user_id, roles=roles, is_active=is_active)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid or expired token: {str(e)}"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserPayload:
    """
    FastAPI Dependency로 사용되는 비동기 인증 함수.
    HTTP Authorization 헤더에서 Bearer 토큰을 추출하여 검증을 위임합니다.
    """
    token = credentials.credentials
    return await decode_jwt(token)

def check_permission(required_role: str):
    """
    특정 권한이 필요한 API 엔드포인트에 사용되는 헬퍼 권한 검사 장치.
    """
    def dependency(user: UserPayload = Depends(get_current_user)):
        if required_role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Permission denied. Required role: {required_role}"
            )
        return user
    return dependency

async def check_read_access(user: UserPayload = Depends(get_current_user)) -> UserPayload:
    """
    읽기 전용 권한 검사 로직 (PoC 명세).
    ROLE_GUEST, ROLE_USER, ROLE_ADMIN 중 하나라도 가지고 있다면 수용합니다.
    """
    allowed_roles = {"ROLE_GUEST", "ROLE_USER", "ROLE_ADMIN"}
    if not any(role in allowed_roles for role in user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Read access requires at least guest roles."
        )
    return user