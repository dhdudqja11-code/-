# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import datetime

# Core Gateway API의 요청 페이로드 스키마 (WebSocket 연결 시 초기 핸드셰이크에 사용)
class WebSocketAuthPayload(BaseModel):
    """
    클라이언트가 웹소켓 연결을 시작할 때 함께 보내야 하는 인증 정보.
    JWT Token과 Nonce를 포함하여 무결성을 검증하는 데 사용됩니다.
    """
    jwt_token: str = Field(..., description="OAuth 2.0 Bearer Token.")
    nonce: str = Field(..., description="일회성 난수 (Nonce). Replay Attack 방지용.")

# 사용자 정보 스키마 (JWT 디코딩 후 추출되는 핵심 데이터)
class UserIdentity(BaseModel):
    user_id: str = Field(..., description="고유 식별자")
    scope: List[str] = Field(default=[], description="사용자가 접근 가능한 권한 범위 목록.")
    is_active: bool = True

# 응답 메시지 구조 (Gateway가 클라이언트에게 보내는 표준 메시지)
class GatewayMessage(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None

# ========================================================
# [main.py 및 E2E 테스트에서 요구되는 추가 핵심 스키마 명세]
# ========================================================

class ConnectionRequest(BaseModel):
    """원격 접속 검증 요청 페이로드."""
    requested_scope: str = Field(..., description="요청하는 접근 권한 범위")
    target_server: str = Field(..., description="대상 원격 서버 식별자")

class GatekeeperResponse(BaseModel):
    """사전 게이트키퍼 검증 응답."""
    is_authorized: bool = Field(..., description="인증 및 승인 여부")
    message: str = Field(..., description="진단 검사 결과 세부 피드백")
    suggested_action: str = Field(..., description="사용자 권장 조치 가이드라인")

class UserCredentials(BaseModel):
    """PoC 검증용 사용자 자격 증명 스키마."""
    api_key: str = Field(..., description="검증에 필요한 게이트웨이 API Key")
    user_id: str = Field(..., description="요청 사용자 고유 식별자")

class ScopeValidationResponse(BaseModel):
    """스코프 검증 결과."""
    user_id: str
    role: str
    allowed_scopes: List[str]