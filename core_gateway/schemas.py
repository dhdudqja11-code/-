from pydantic import BaseModel, Field, validator
from typing import Optional

# --- 1. 인증 토큰 및 사용자 정보 스키마 ---
class UserCredentials(BaseModel):
    """접근을 요청하는 사용자의 기본 자격 증명."""
    user_id: str = Field(..., description="고유 사용자 식별자")
    api_key: str = Field(..., description="API 접근에 사용되는 고정 키 (실제로는 JWT가 사용되어야 함)")

# --- 2. 연결 요청 스키마 ---
class ConnectionRequest(BaseModel):
    """원격 접속을 시도할 때 필요한 핵심 정보."""
    target_server: str = Field(..., description="접속 목표 서버의 호스트명 또는 IP")
    requested_scope: str = Field(..., description="요청하는 최소 권한 범위 (예: 'READ_FINANCIAL', 'WRITE_CONFIG')")
    reason: Optional[str] = Field(None, description="작업 수행의 비즈니스적 근거 (감사 추적용)")

# --- 3. 응답 스키마 ---
class GatekeeperResponse(BaseModel):
    """게이트웨이 통과 후 최종 사용자에게 제공되는 결과."""
    is_authorized: bool = Field(..., description="접근 권한 여부")
    message: str = Field(..., description="처리 결과 메시지 (성공/실패 사유)")
    suggested_action: Optional[str] = Field(None, description="위험 발견 시 제시하는 해결책 또는 다음 단계 조치")

# --- 4. Scope 검증 응답 스키마 ---
class ScopeValidationResponse(BaseModel):
    """권한 검증 로직 실행 후의 상세 결과."""
    can_access: bool = Field(..., description="요청된 Scope가 현재 권한으로 허용되는지 여부")
    allowed_scopes: list[str] = Field(..., description="사용자가 실제로 접근 가능한 모든 Scope 목록")
    violation_reason: Optional[str] = Field(None, description="접근 거부 시 상세 원인 (예: '최소 권한 원칙 위반')")