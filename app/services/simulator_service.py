from typing import List, Dict
from ..models.simulation_input import SimulationInput, RiskFactor, SimulationResult
# NOTE: 실제 환경에서는 외부 라이브러리(예: pandas)가 필요할 수 있습니다.

class SimulatorService:
    """
    Mini ROI 시뮬레이션의 핵심 비즈니스 로직을 담당하는 서비스 클래스.
    모든 계산 및 데이터 검증은 이 레이어에서만 이루어져야 합니다 (SRP).
    """

    @staticmethod
    def _calculate_individual_loss(risk: RiskFactor) -> float:
        """
        개별 리스크에 대한 손실액을 추정하는 로직입니다.
        [WHY] 단순 곱셈이 아니라, 업종과 자산 규모의 가중치를 적용해야 현실적입니다.
        """
        # (잠재적 영향 점수 * 발생 가능성) * 데이터 자산 개수 * 기본 계수
        base_loss = risk.potential_impact_score * risk.likelihood_of_occurrence
        return round(base_loss * 1000 * 5, 2) # 임시 계산 상수 적용

    @staticmethod
    def run_simulation(input_data: SimulationInput) -> SimulationResult:
        """
        전체 시뮬레이션을 실행하고 결과를 구조화하여 반환합니다.
        [HOW] 모든 비즈니스 로직의 시작점입니다. 
        """
        if not input_data.risks:
            raise ValueError("시뮬레이션에 진단할 리스크 요소가 최소 하나 필요합니다.")

        total_loss = 0.0
        risk_summaries: List[Dict] = []
        critical_factors: List[str] = []

        for risk in input_data.risks:
            # 1. 개별 손실 계산 및 총합 누적
            individual_loss = SimulatorService._calculate_individual_loss(risk)
            total_loss += individual_loss

            # 2. 리스크 경고 플래그 (임계값 설정의 예시)
            is_high_risk = individual_loss > 10000 or risk.likelihood_of_occurrence >= 0.8
            if is_high_risk:
                critical_factors.append(f"{risk.factor_name} (손실액 과다 또는 발생 가능성 높음)")

            # 3. 요약 리포트 작성
            risk_summaries.append({
                "factor": risk.factor_name,
                "loss": round(individual_loss, 2),
                "warning": "🚨 고위험군 감지됨" if is_high_risk else "✅ 안정적 범위",
                "detail": f"임팩트: {risk.potential_impact_score}, 확률: {risk.likelihood_of_occurrence}"
            })

        # 4. 최종 결과 구조화
        is_critical = bool(critical_factors)
        suggested_cta = "즉시 내부 규정 검토 및 데이터 거버넌스 강화가 필요합니다." if is_critical else "현재 상태는 양호하나, 정기적인 감사 주기를 권장합니다."

        return SimulationResult(
            total_estimated_loss=round(total_loss, 2),
            risk_summary=risk_summaries,
            is_critical_state=is_critical,
            suggested_cta=suggested_cta
        )