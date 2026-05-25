# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from services.authentication_service import AuthenticationService
from services.session_manager import SessionManager
from services.security_service import SecurityService

# 💡 초기화 및 의존성 주입 설정
app = FastAPI(title="Remote Control API Gateway", version="0.1.0")

auth_service = AuthenticationService()
session_manager = SessionManager()
security_service = SecurityService()

class Credentials(BaseModel):
    username: str
    password: str

class TokenPayload(BaseModel):
    user_id: str
    device_ip: str

class KillSessionRequest(BaseModel):
    session_id: str

# --- Helper Functions ---

def get_client_ip(request: Request) -> str:
    """X-Forwarded-For 헤더를 우선적으로 참조하여 프록시/게이트웨이 환경에서도 실제 위협 IP를 정확히 획득합니다."""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

# --- Dependency Functions (보안 게이트) ---

def get_current_user_info(request: Request, authorization: str = Header(None)):
    """
    요청 헤더에서 토큰을 추출하고 IP 및 세션의 실시간 유효성을 이중으로 검증하는 보안 가드레일 함수입니다.
    """
    # 1. IP 블랙리스트 검증 (원격 킬 스위치로 차단된 IP 차단)
    client_ip = get_client_ip(request)
    if security_service.is_ip_blacklisted(client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP address has been blacklisted due to security reasons."
        )
        
    # 2. IP 화이트리스트 대역 검증 (비인가 외부 IP 접근 실시간 알림 및 즉각 차단)
    if not security_service.is_ip_allowed(client_ip):
        security_service.trigger_security_alert(
            alert_type="UNAUTHORIZED_IP_ACCESS",
            details=f"비인가 IP {client_ip}로부터 보안 보호 엔드포인트 접근 시도 감지!"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Unauthorized incoming IP address."
        )

    # 3. 토큰 전달 유무 및 Bearer 추출
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired credentials."
        )
        
    token = authorization.split(" ")[1]
    
    # 4. JWT 토큰 해독 및 사용자 ID 획득
    user_id = auth_service.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired credentials."
        )
        
    # 5. [이중 체크] 세션 매니저 내 토큰의 실시간 활성 여부 검증 (Kill Switch 대응 핵심)
    if not session_manager.is_token_active(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied. The session has been revoked or expired."
        )
    
    # 6. 보안 필수 체크: MFA 강제 확인 로직
    if not auth_service.enforce_mfa_check(user_id, token):
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="MFA required or failed."
         )

    return {"user_id": user_id}


# --- API Endpoints ---

@app.post("/auth/login")
def login_for_access_token(credentials: Credentials, request: Request):
    """사용자 로그인 및 JWT Access Token 발급 (IP 추적, 로그인 실패 누적 감지 및 세션 바인딩 포함)."""
    client_ip = get_client_ip(request)
    
    # IP 블랙리스트 선제 차단
    if security_service.is_ip_blacklisted(client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Your IP is blacklisted."
        )
        
    print(f"INFO: Attempting login for {credentials.username} from IP {client_ip}...")
    
    # 테스트 및 검증을 위한 비밀번호 해싱 비교
    admin_hashed_pw = auth_service.get_password_hash("admin_pass")
    
    if credentials.username != "admin" or not auth_service.verify_password(credentials.password, admin_hashed_pw):
        # 로그인 실패 이력 누적
        failures, alert_triggered = security_service.track_login_failure(client_ip)
        print(f"Warning: Login failed for IP {client_ip}. Attempts: {failures}/3")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    # 성공 시 로그인 실패 횟수 초기화
    security_service.reset_login_failures(client_ip)
    user_id = "USER_" + credentials.username 
    
    # 2. Access Token 생성 (30분 유효)
    access_token = auth_service.create_access_token(data={"sub": user_id}, expires_delta=timedelta(minutes=30))

    # 3. 세션 생성 및 등록 (IP 바인딩)
    session_manager.create_session(user_id, access_token, duration_minutes=60, ip_address=client_ip)
    
    return {"access_token": access_token, "token_type": "bearer", "expires_in": 1800}


@app.post("/api/v1/security/kill")
def kill_active_session(req: KillSessionRequest):
    """
    [원격 킬 스위치 API]
    사장님의 텔레그램 명령 또는 보안 대시보드 클릭 시, 
    지정된 세션을 즉각 파괴하고 접속했던 IP를 블랙리스트에 등재합니다.
    """
    session_id = req.session_id
    
    # 1. 세션 조회
    session = session_manager._active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="해당 세션 ID를 찾지 못했습니다.")
        
    client_ip = session.get("ip_address", "127.0.0.1")
    
    # 2. 세션 폭파 (Revocation)
    session_manager.revoke_session(session_id)
    
    # 3. 해당 IP를 즉시 블랙리스트에 등록
    security_service.blacklist_ip(client_ip)
    
    return {
        "success": True,
        "message": f"세션 {session_id}가 즉시 폭파되었으며, IP {client_ip}가 블랙리스트에 등록되었습니다."
    }


@app.get("/api/v1/data/{resource_id}")
def get_protected_data(resource_id: str, user_info: dict = Depends(get_current_user_info)):
    """
    보호된 엔드포인트 예시. 
    사용자 인증과 세션 유효성 검증이 성공해야만 접근 가능합니다.
    """
    user_id = user_info['user_id']
    print(f"SUCCESS: User {user_id} accessed resource {resource_id}. Data processing started.")
    return {
        "status": "success",
        "message": f"Data for {resource_id} retrieved successfully by {user_id}.",
        "data": [1, 2, 3]
    }