# src/services/assurance_service.py
from pydantic import BaseModel, Field, NonNegativeFloat
from typing import List, Dict
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreCalculationInput(BaseModel):
    """
    Avoided Loss 계산을 위한 핵심 입력 데이터 스키마 정의 (Pydantic 기반).
    모든 외부 API 호출은 이 구조를 따르도록 강제해야 합니다.
    """
    user_purpose: str = Field(..., description="사용자의 서사적 목적 또는 목표.")
    regulatory_risk_data: List[Dict[str, float]] = Field(..., description="관련 규제 위험 데이터 리스트. 예: [{\"type\": \"GDPR\", \"loss_estimate\": 10.5}, ...]")
    current_system_exposure: NonNegativeFloat = Field(..., description="현재 시스템이 노출된 것으로 추정되는 최대 손실액 ($M$).")


class AssuranceCalculationResult(BaseModel):
    """
    최종 계산 결과를 포함하는 스키마.
    """
    avoided_loss_usd_million: float = Field(..., description="계산된 최종 회피 가능 손실액 (단위: 백만 달러).")
    assurance_index: float = Field(..., description="시스템의 확신 지수 (0.0 ~ 1.0). 높을수록 통제력이 우수함을 의미.")
    calculation_details: Dict[str, str] = Field(..., description="계산에 사용된 주요 변수 및 로직 요약.")


class AssuranceService:
    """
    Avoided Loss를 계산하는 핵심 비즈니스 로직 서비스 클래스.
    이 모듈은 재무적 확신(Assurance)을 제공하는 단일 책임 원칙(SRP)을 따릅니다.
    """

    @staticmethod
    def _calculate_assurance_index(risk_data: List[Dict[str, float]]) -> float:
        """
        주어진 규제 위험 데이터를 기반으로 시스템의 통제력 지수를 계산합니다. (Mock Logic)
        -> 로직이 복잡해질수록 외부 모델링 레이어로 분리되어야 함.
        """
        if not risk_data:
            return 0.1  # 최소 기본값 설정

        total_risk = sum(d.get('loss_estimate', 0) for d in risk_data)
        # Mock Logic: 위험 데이터가 많고, 그 값이 크면 (높은 리스크), 해결책이 필요하다는 의미로 지수를 높게 부여 가정.
        # 실제로는 '제공된 통제 메커니즘의 복잡도/효율성'을 측정해야 함.
        return min(1.0, 0.5 + (total_risk / 20.0))


    @staticmethod
    def calculate_avoided_loss(input_data: CoreCalculationInput) -> AssuranceCalculationResult:
        """
        주어진 입력 데이터와 비즈니스 로직을 기반으로 Avoided Loss를 계산합니다.
        """
        logger.info("--- Starting Avoided Loss Calculation ---")

        # 1. 확신 지수 (Assurance Index) 계산 (통제력 측정)
        assurance_index = AssuranceService._calculate_assurance_index(input_data.regulatory_risk_data)

        # 2. 위험 회피 가치 계산 로직 (Avoided Loss Formula Mockup)
        # Avoided Loss = [현재 노출 리스크 - (확신 지수 * 현재 시스템 개입 비용)] * 승수
        # 이 공식은 비즈니스와 협의가 필요하며, 재무적 서사 구조를 반영해야 합니다.

        risk_mitigation_factor = assurance_index * 0.8 # 확신 지수가 높을수록 회피 효과 극대화 (임시 계수)
        avoided_loss = input_data.current_system_exposure - risk_mitigation_factor

        # 손실액이 마이너스가 되는 것은 논리적으로 불가능하므로, 최소값 보장 (Guard Clause)
        if avoided_loss < 0:
            avoided_loss = 0.0

        details = {
            "Purpose Input": input_data.user_purpose[:50] + "...",
            "Assurance Index Used": f"{assurance_index:.4f}",
            "Initial Exposure ($M$)": str(input_data.current_system_exposure),
            "Calculated Avoided Loss ($M$)": f"{avoided_loss:.2f}"
        }

        logger.info(f"Calculation Complete. Final AL: ${avoided_loss:.2f}M")

        return AssuranceCalculationResult(
            avoided_loss_usd_million=max(0.0, avoided_loss),
            assurance_index=assurance_index,
            calculation_details=details
        )

# 예시 사용 (테스트 목적으로 주석 처리)
if __name__ == "__main__":
    sample_input = CoreCalculationInput(
        user_purpose="데이터 사일로로 인한 규제 미준수 위험 해소",
        regulatory_risk_data=[{"type": "GDPR", "loss_estimate": 15.0}, {"type": "CCPA", "loss_estimate": 8.0}],
        current_system_exposure=30.0
    )
    result = AssuranceService.calculate_avoided_loss(sample_input)
    print("\n--- Test Result ---")
    print(result.json(indent=2))