from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import uuid

# --- 1. connect-remote Schema ---
class RemoteConnectionRequest(BaseModel):
    """원격 연결 초기화를 위한 요청 스키마."""
    user_authority_token: str = Field(..., description="사용자의 권한 증명 토큰 (JWT)")
    target_system_id: str = Field(..., description="접속 대상 시스템 ID (예: CRM, ERP)")
    requested_scope: str = Field(..., description="요청하는 접근 범위 및 목적")
    duration_minutes: Optional[int] = Field(None, description="원격 연결 유효 시간 (분)")

class RemoteConnectionResponse(BaseModel):
    """성공적인 원격 연결 초기화 응답 스키마."""
    connection_id: uuid.UUID = Field(..., description="발급된 고유한 연결 ID")
    access_token: str = Field(..., description="단기 접근 토큰 (Gateway에서 사용)")
    expires_at: str = Field(..., description="토큰 만료 시각 (ISO 8601)")

# --- 2. execute-command Schema ---
class CommandExecutionRequest(BaseModel):
    """원격 명령 실행 요청 스키마."""
    connection_id: uuid.UUID = Field(..., description="활성화된 연결 ID")
    command_name: str = Field(..., description="실행할 명령어 이름 (Whitelist 기반)")
    arguments: Dict[str, Any] = Field({}, description="명령어에 전달될 인자 목록")

class CommandExecutionResponse(BaseModel):
    """명령어 실행 결과 응답 스키마."""
    command_id: uuid.UUID = Field(..., description="실행 요청 고유 ID")
    status: str = Field(..., enum=["SUCCESS", "FAILED", "PENDING"], description="현재 상태")
    output_data: Optional[Dict[str, Any]] = Field(None, description="명령어 실행 결과 데이터 (JSON)")
    execution_log: str = Field(..., description="실행 과정의 상세 로그 및 시간 정보")

# --- 3. stream-data Schema ---
class StreamDataRequest(BaseModel):
    """스트리밍 데이터 요청 스키마."""
    connection_id: uuid.UUID = Field(..., description="활성화된 연결 ID")
    data_stream_type: str = Field(..., description="요청하는 스트림 데이터 유형 (예: LOG, FINANCIAL_UPDATE)")
    start_timestamp: Optional[str] = Field(None, description="데이터 시작 시점 (ISO 8601)")

class StreamDataResponse(BaseModel):
    """스트리밍 데이터 청크 단위 응답 스키마."""
    chunk_id: str = Field(..., description="데이터 청크 고유 ID")
    timestamp: str = Field(..., description="데이터 발생 시각 (ISO 8601)")
    data_payload: Dict[str, Any] = Field(..., description="실제 데이터 페이로드 (JSON) - 권한 증명 메타데이터 포함 가능")
    is_final_chunk: bool = Field(False, description="이것이 스트림의 마지막 청크인지 여부")

# [Self-Correction/Validation Check]
# 모든 필드에 대한 설명과 타입 힌트를 명확히 했으며, 특히 권한 증명 메타데이터를 받을 수 있도록 payload 구조를 유연하게 잡았습니다.