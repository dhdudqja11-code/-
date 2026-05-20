from pydantic import BaseModel, Field
from typing import List, Optional

# 1. 입력 데이터 스키마 (Pydantic Validation)
class RiskVariables(BaseModel):
    """API 게이트웨이에 들어오는 모든 리스크 변수들을 정의합니다."""
    regulatory_risk_cost: float = Field(..., description="규제 준수 미비로 인한 예상 비용 ($C_{reg}$)")
    reputation_loss_potential: float = Field(..., description="명성 손실 가능성으로 인한 비용 ($C_{rep}$) (스코어 기반)")
    operational_failure_cost: float = Field(..., description="운영상의 실패 또는 장애로 인한 예상 최대 손실액")
    bias_factor: float = Field(default=0.0, description="내부 편향성이나 가정으로 인한 비용 증가 계수 ($C_{bias}$) (0~1)")
    lock_in_cost: float = Field(default=0.0, description="대체 불가능성에 갇히는 비용($C_{lock}$)")
    required_mitigation_effort: float = Field(..., description="필요한 완화 노력 수준에 따른 내부 자원 투입 예상 비용")

class AvoidedLossInput(BaseModel):
    """최종 'Avoided Loss' 계산을 위한 통합 입력 모델."""
    variables: RiskVariables
    user_context_id: str = Field(..., description="계산을 요청한 사용자 또는 프로젝트 ID (트래킹용)")


# 2. 출력 데이터 스키마 (API Response)
class AvoidedLossOutput(BaseModel):
    """API 게이트웨이가 반환하는 최종 구조화된 결과입니다."""
    avoided_loss_amount: float = Field(..., description="계산된 총 위험 회피 비용 (Avoided Loss)")
    analysis_summary: str = Field(..., description="전문가 관점의 요약 분석 및 제언")
    risk_breakdown: dict[str, float] = Field(description="각 변수별 기여도와 계산 결과를 구조화하여 제공합니다.")