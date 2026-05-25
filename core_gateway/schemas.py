from pydantic import BaseModel, Field, validator
from typing import Optional
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
    scope: list[str] = Field(default=[], description="사용자가 접근 가능한 권한 범위 목록.")
    is_active: bool = True

# 응답 메시지 구조 (Gateway가 클라이언트에게 보내는 표준 메시지)
class GatewayMessage(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None