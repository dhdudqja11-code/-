from pydantic import BaseModel, Field
from typing import Optional, Dict

from enum import Enum

# ========================================
# [Authentication & Authorization Schemas]
# ========================================

class Token(BaseModel):
    access_token: str = Field(description="JWT Access Token")
    token_type: str = "bearer"
    expires_to: int

class UserCredentials(BaseModel):
    username: str = Field(description="사용자 식별명")
    password: str = Field(description="비밀번호 (실제로는 패스워드 해싱 검증 필요)")

# RBAC 역할을 정의하는 기본 모델
class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

# ========================================
# [Core Service Schemas]
# ========================================

class SessionDetails(BaseModel):
    session_id: str = Field(description="고유 세션 식별자 (Audit Trail의 핵심)")
    user_role: Role = Field(description="세션을 시작한 사용자의 권한 등급")
    is_active: bool = True

class CommandInput(BaseModel):
    command: str = Field(description="원격 제어할 명령 문자열 (예: 'get user list')")
    parameters: Optional[Dict[str, str]] = None

# 명령어 실행 결과 (Audit Trail 및 데이터 파기 로직을 고려한 구조)
class CommandResult(BaseModel):
    success: bool
    output_data: str | None = Field(description="명령어 실행의 최종 출력 데이터")
    error_message: Optional[str] = None
    # 이 필드는 필수적으로 기록되어야 하지만, 보안 정책에 따라 세션 종료 시 파기 대상임을 명시
    audit_log_entry: Dict[str, str]