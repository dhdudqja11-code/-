from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

# =======================================================
# 1. 요청 바디 (Input Schema)
# =======================================================

class InputData(BaseModel):
    """API에 전달되는 모든 핵심 입력 데이터 구조."""
    # 필수 변수: 사용자의 기본 정보와 데이터를 담는 컨테이너 역할을 합니다.
    client_id: str = Field(..., description="고객 고유 ID (필수)")
    transaction_value: float = Field(..., gt=0, description="현재 트랜잭션 가치")
    data_source: str = Field(..., description="데이터가 발생한 출처 (예: Webhook, Manual)")
    risk_factor_input: Dict[str, Any] = Field({}, description="규제 리스크 관련 추가 데이터 딕셔너리")

class CalculationInputs(BaseModel):
    """손실 계산 로직에 필요한 변수들을 모아둔 스키마."""
    # 행동경제학적 가중치 적용을 위한 핵심 입력 필드들
    emotional_loss_sensitivity: float = Field(..., ge=0.1, le=5.0, description="감정적 손실 민감도 (행동 변수)")
    regulatory_risk_score: float = Field(None, ge=0.0, le=1.0, description="외부 규제 위험 점수")
    data_integrity_penalty: float = Field(..., gt=0, description="데이터 무결성 위반 페널티 가중치")

# =======================================================
# 2. 응답 바디 (Output Schema)
# =======================================================

class LossAnalysisResult(BaseModel):
    """최종적으로 계산되어 반환되는 Avoided Loss 결과."""
    total_avoided_loss: float = Field(..., description="계산된 총 회피 손실액")
    key_risk_area: str = Field(..., description="가장 위험도가 높은 리스크 영역 (예: Data Sovereignty)")
    mitigation_suggestion: str = Field(..., description="위험 완화를 위한 구체적인 해결책 제시")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="분석 결과의 신뢰도 점수")

class ErrorResponse(BaseModel):
    """데이터 누락 또는 상충 관계로 인해 발생하는 구조화된 오류 응답."""
    error_code: str = Field(..., description="구체적인 에러 코드 (예: E4001)")
    message: str = Field(..., description="사용자 친화적 오류 메시지")
    failed_field: Optional[str] = Field(None, description="문제가 발생한 필드명")
    required_action: str = Field(..., description="클라이언트가 취해야 할 조치")

# 최종 응답을 포괄하는 모델
class AvoidedLossResponse(BaseModel):
    """API의 최종 성공 또는 실패 응답 구조를 정의합니다."""
    success: bool = True
    data: Optional[LossAnalysisResult] = None
    error: Optional[ErrorResponse] = None
    timestamp: str = Field(..., description="요청 처리 시간 기록")

# -------------------------------------------------------
# 유효성 검사 커스텀 Validator (예시)
# -------------------------------------------------------
class ValidatedInputData(BaseModel):
    """필수 필드 체크 및 데이터 타입 강제."""
    pass # 현재는 Pydantic의 기본 기능을 사용하며, 복잡한 비즈니스 로직은 서비스 레이어에서 처리합니다.