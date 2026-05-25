from fastapi import FastAPI, Depends, HTTPException, status, Header
from slowapi.limiter import Limiter
from slowapi import apirouter
from typing import Annotated
import time
import hashlib

# 로컬 모듈 임포트 (타입 안전성 확보)
from .schemas import ConnectionRequest, ScopeValidationResponse, GatekeeperResponse, UserCredentials 

app = FastAPI(title="Core Gateway API", description="모든 원격 접속 요청을 통제하는 게이트웨이.")

# --- 보안 장치 1: Rate Limiting 적용 ---
limiter = Limiter(app)
router = apirouter()


# --- 의존성 함수 (Dependencies): 핵심 보안 로직 구현 ---

@limiter.limit("10/minute") # 분당 10회 요청 제한 설정
async def rate_limit_checker():
    """Rate Limiting Middleware 역할을 수행하는 Dependency."""
    pass # 실제 slowapi가 처리함


def authenticate_user(credentials: UserCredentials = Depends(UserCredentials)):
    """
    사용자 인증 (Authentication). 
    실제 운영 환경에서는 JWT Bearer Token을 사용해야 합니다.
    여기서는 PoC를 위해 Body에 포함된 API Key 검증으로 대체합니다.
    """
    if credentials.api_key != "SUPER_SECRET_HARDCODED_KEY": # TODO: Environment Variable로 대체 필요
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key.")
    return credentials

def validate_scope_and_auth(credentials: UserCredentials = Depends(authenticate_user)):
    """
    Scope 검증 및 인증 (Authorization). 
    사용자의 권한 범위(Role)를 기반으로 요청된 Scope가 적절한지 확인합니다.
    PoLP (Principle of Least Privilege)을 강제합니다.
    """
    # PoC 로직: 가상의 역할 기반 접근 제어 목록 (ACL) 시뮬레이션
    user_role = "ADMIN" if credentials.user_id == "admin_user" else "STANDARD_USER"
    
    # 가상 ACL 정의 
    allowed_scopes = {
        "admin_user": ["READ_FINANCIAL", "WRITE_CONFIG", "VIEW_AUDIT"],
        "standard_user": ["READ_PROFILE", "READ_BASIC_DATA"]
    }
    
    if user_role not in allowed_scopes:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown User Role.")

    return {
        "user_id": credentials.user_id, 
        "role": user_role, 
        "allowed_scopes": allowed_scopes[user_role]
    }


# --- API 엔드포인트 정의 ---

@router.post(
    "/v1/check-connection", 
    response_model=GatekeeperResponse,
    summary="원격 접속 전 사전 게이트웨이 검증 (PoC)",
    dependencies=[Depends(rate_limit_checker), Depends(validate_scope_and_auth)] # Rate Limit & Scope Check 적용!
)
async def check_connection(
    request: ConnectionRequest, 
    user_context: dict = Depends(validate_scope_and_auth)
):
    """
    요청된 자원과 사용자의 권한을 비교하여 접속 가능 여부를 판단합니다.
    이 엔드포인트는 실제 SSH 연결 전의 '진단 단계'입니다.
    """
    # 1. Scope 검증 (핵심 로직)
    if request.requested_scope not in user_context["allowed_scopes"]:
        return GatekeeperResponse(
            is_authorized=False, 
            message=f"권한 위반: '{request.requested_scope}' 범위에 대한 접근 권한이 없습니다.",
            suggested_action="접근할 수 있는 스코프 목록을 재확인하거나, 관리자에게 역할 상향 조정을 요청하세요."
        )

    # 2. 기타 검증 (예: 서버 이름 규칙 확인 등)
    if not request.target_server.startswith("core-"):
         return GatekeeperResponse(
            is_authorized=False, 
            message="잘못된 대상 서버 접두사입니다. 모든 핵심 시스템은 'core-'로 시작해야 합니다.",
            suggested_action="정확한 target_server 이름을 확인 후 재요청 바랍니다."
        )

    # 모든 검증 통과 시 성공 응답
    return GatekeeperResponse(
        is_authorized=True, 
        message=f"접근 허가됨. {request.target_server}에 대해 '{request.requested_scope}' 권한으로 연결을 진행할 수 있습니다.",
        suggested_action="실제 SSH 터널링 로직을 이 단계 이후에 구현해야 합니다."
    )

# 메인 앱에 라우터 등록
app.include_router(router, prefix="/api")