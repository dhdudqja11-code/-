from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel

# 환경 변수에서 로드한다고 가정 (보안 규칙 준수)
SECRET_KEY = "YOUR_SUPER_SECRET_JWT_KEY" 
ALGORITHM = "RS256" # 사용된 알고리즘 명시
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserPayload(BaseModel):
    """토큰에서 디코딩되어 검증되는 사용자 페이로드 구조."""
    user_id: str
    roles: list[str]
    is_active: bool

async def decode_jwt(token: str) -> UserPayload:
    """
    JWT 토큰을 디코딩하고 유효성을 검사합니다.
    실패 시 명확한 에러를 발생시켜 상위 게이트웨이에서 처리할 수 있게 합니다.
    """
    try:
        # 실제 환경에서는 process.env.SECRET_KEY 등을 사용해야 함
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        roles: list[str] = payload.get("roles", [])
        is_active: bool = payload.get("active", False)

        if user_id is None or not roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing required claims.")

        return UserPayload(user_id=user_id, roles=roles, is_active=is_active)
    except JWTError as e:
        # 토큰 자체가 유효하지 않거나 만료된 경우의 에러 처리
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid or expired token: {e}")

def get_current_user(token: str = Depends(...)) -> UserPayload:
    """
    FastAPI Dependency로 사용될 메인 인증 함수.
    요청 헤더에서 토큰을 받아 유효성을 검사하고 페이로드를 반환합니다.
    """
    try:
        return decode_jwt(token)
    except HTTPException as e:
        # 예외를 다시 발생시켜 FastAPI가 이를 HTTP 에러로 인식하게 함
        raise e

def check_permission(required_role: str):
    """
    특정 권한이 필요한 API 엔드포인트에 사용되는 헬퍼 함수.
    사용자 페이로드와 비교하여 접근 가능 여부를 판단합니다.
    """
    def dependency(user: UserPayload = Depends(get_current_user)):
        if required_role not in user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied. Required role: {required_role}")
        return user
    return dependency

# 타입 힌트 및 사용 예시를 위해 빈 함수 정의 (필요 시 확장 가능)
async def check_read_access(user: UserPayload = Depends(get_current_user)):
    # Read-Only 권한 체크 로직 추가 예정
    pass