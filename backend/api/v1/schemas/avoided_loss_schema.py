from pydantic import BaseModel, Field, condecimal
from typing import Optional

class InputRiskData(BaseModel):
    """API에 입력될 최종 리스크 데이터를 정의합니다. 모든 필수 필드와 타입을 명시합니다."""
    transaction_id: str = Field(..., description="고유 트랜잭션 식별자")
    source_system: str = Field(..., description="데이터가 유입된 시스템 출처 (예: PayPal Webhook)")
    verification_time: Optional[str] = Field(None, description="규제 검증 시간 (ISO 8601 형식 권장)")
    raw_data_payload: dict = Field(..., description="외부에서 수신된 원본 JSON 페이로드")

class AvoidedLossRequest(BaseModel):
    """Avoided Loss 계산 요청의 최상위 모델입니다."""
    input_risk_data: InputRiskData
    user_profile: dict = Field(..., description="사용자 프로필 데이터 (계산에 필요한 기초 정보)")