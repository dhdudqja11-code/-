# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from typing import Dict, List, Any
import os

# 로컬 모듈 임포트 (타입 안전성 및 사전 검증 스키마 적재)
try:
    from schemas import ConnectionRequest, ScopeValidationResponse, GatekeeperResponse, UserCredentials 
except ImportError:
    from .schemas import ConnectionRequest, ScopeValidationResponse, GatekeeperResponse, UserCredentials 

# --- 보안 장치 1: Rate Limiting 구성 ---
# 클라이언트 IP 기반 속도 조절 인스턴스 생성
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Core Gateway API - Security Layer", 
    description="모든 원격 접속 요청을 통제 및 감사하는 보안 연동 게이트웨이."
)

# FastAPI state에 limiter 등록 및 글로벌 예외 핸들러 바인딩 (글로벌 미들웨어 완착)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- 의존성 함수 (Dependencies): 핵심 보안 인증 및 인가 로직 ---

def authenticate_user(credentials: UserCredentials = Depends()):
    """
    PoC 사용자 인증 (Authentication).
    환경 변수 GATEWAY_API_KEY 조회를 우선하며, 부재 시 하드코딩 키로 안전 폴백합니다.
    """
    expected_api_key = os.getenv("GATEWAY_API_KEY", "SUPER_SECRET_HARDCODED_KEY")
    if credentials.api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API Key."
        )
    return credentials

def validate_scope_and_auth(credentials: UserCredentials = Depends(authenticate_user)) -> Dict[str, Any]:
    """
    사용자의 권한 범위(Role)를 기반으로 요청 스코프의 적절성 검사 (Authorization).
    PoLP (Principle of Least Privilege)을 강력히 강제합니다.
    """
    user_role = "ADMIN" if credentials.user_id == "admin_user" else "STANDARD_USER"
    
    # 역할 기반 ACL 정의 
    allowed_scopes = {
        "admin_user": ["READ_FINANCIAL", "WRITE_CONFIG", "VIEW_AUDIT"],
        "standard_user": ["READ_PROFILE", "READ_BASIC_DATA"]
    }
    
    if credentials.user_id not in allowed_scopes:
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN, 
             detail="Unknown or unauthorized user identity."
         )

    return {
        "user_id": credentials.user_id, 
        "role": user_role, 
        "allowed_scopes": allowed_scopes[credentials.user_id]
    }

# --- API 엔드포인트 정의 ---

@app.post(
    "/api/v1/check-connection", 
    response_model=GatekeeperResponse,
    summary="원격 접속 전 사전 게이트웨이 검증 (PoC)"
)
@limiter.limit("10/minute")  # 분당 10회 호출 제한 활성화 (DDoS 방어 레벨)
async def check_connection(
    request: Request,  # SlowAPI 추적 처리를 위한 필수 Request 객체 주입
    conn_req: ConnectionRequest, 
    user_context: dict = Depends(validate_scope_and_auth)
):
    """
    요청된 원격 리소스 스코프와 사용자 권한 목록을 대조하여 접속 통제 판정을 내립니다.
    """
    # 1. Scope 검증 (최소 권한 대조)
    if conn_req.requested_scope not in user_context["allowed_scopes"]:
        return GatekeeperResponse(
            is_authorized=False, 
            message=f"권한 위반: '{conn_req.requested_scope}' 범위에 대한 접근 권한이 없습니다.",
            suggested_action="접근 권한 목록을 다시 확인하거나, 최고 관리자에게 역할 등급 상향을 요청하세요."
        )

    # 2. 호스트 접두사 유효성 검사 (서버 명명 규칙)
    if not conn_req.target_server.startswith("core-"):
         return GatekeeperResponse(
            is_authorized=False, 
            message="잘못된 대상 서버 식별자입니다. 모든 코어 시스템 명칭은 'core-'로 시작해야 합니다.",
            suggested_action="정확한 target_server 호스트명을 스캔 후 재요청 바랍니다."
        )

    # 모든 검증 통과 시 접속 허가 발급
    return GatekeeperResponse(
        is_authorized=True, 
        message=f"접근 허가됨. {conn_req.target_server}에 대해 '{conn_req.requested_scope}' 세션 터널링 진행이 가능합니다.",
        suggested_action="보안 터널링 소켓 통신 모듈을 이어서 호출할 수 있습니다."
    )