from typing import List, Dict, Any
from pydantic import BaseModel, Field, validator
import datetime
import hashlib

class RemoteDiagnosisRequest(BaseModel):
    """
    사용자 환경 진단 및 데이터 전송 요청 본문 스키마. 
    모든 민감 정보는 반드시 메타데이터를 통해 증명되어야 함.
    """
    user_id: str = Field(..., description="진단을 수행하는 사용자 고유 ID")
    device_fingerprint: str = Field(..., description="클라이언트 장치 식별자 (UUID 기반)")
    diagnosis_data: Dict[str, Any] = Field(..., description="수집된 환경 진단 데이터 (OS 버전, 라이브러리 등)")
    
    # --- 필수 메타데이터 필드 ---
    immutable_audit_log: str = Field(..., description="모든 트랜잭션 변경 이력의 해시값 (SHA-256).")
    bias_audit_trail: List[Dict[str, Any]] = Field(..., description="진단 과정에서 발견된 잠재적 편향/제한 요인 기록.")

    @validator('immutable_audit_log', pre=True)
    def validate_audit_hash(cls, v):
        """임시 유효성 검사: 해시가 올바른 형식인지 확인."""
        if not isinstance(v, str):
            raise ValueError("Audit Log는 문자열 형태의 SHA-256 해시여야 합니다.")
        return v

    @validator('bias_audit_trail')
    def validate_bias_trail(cls, v):
        """Bias Audit Trail은 빈 리스트 또는 유효한 구조여야 함."""
        if not isinstance(v, list) or any(not isinstance(item, dict) for item in v):
             raise ValueError("Bias Audit Trail은 '타입'과 '설명'을 가진 딕셔너리 리스트여야 합니다.")
        return v

class DiagnosisResponse(BaseModel):
    """API 응답 스키마. 진단 결과와 함께 항상 규제 준수 상태를 포함해야 함."""
    status: str = Field(..., description="진단 성공/실패 상태 (SUCCESS, FAILED_AUTH, ALERT)")
    result_data: Dict[str, Any] = Field(..., description="요청된 진단 결과 데이터")
    compliance_alert: List[Dict[str, Any]] = Field(default=[], description="규제 위반 또는 잠재적 위험 경고 목록.")

# JSON Schema를 위한 임시 변환 (실제 사용 시 Pydantic 모델을 활용)
SCHEMA_JSON = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "device_fingerprint": {"type": "string"},
        "diagnosis_data": {"type": "object"},
        "immutable_audit_log": {"type": "string", "description": "SHA-256 해시가 요구됨."},
        "bias_audit_trail": {"type": "array", "items": {"type": "object"}}
    }
}