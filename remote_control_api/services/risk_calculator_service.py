import uuid
from typing import Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# -------------------------------------------
# Pydantic 스키마 정의: 입력 데이터 규격화 (엄격한 타입 검증)
# -------------------------------------------
class SimulationInput(BaseModel):
    """Mini ROI 시뮬레이션에 필요한 최소 필수 데이터를 받습니다."""
    user_id: str = Field(..., description="시뮬레이션을 요청한 사용자 식별자")
    revenue_projection: float = Field(..., gt=0, description="예상 매출액 (단위: 원)")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="현재 시스템 컴플라이언스 점수 (0.0 ~ 1.0)")
    regulatory_change_risk: float = Field(..., gt=0, description="최근 규제 변화에 대한 노출 위험도 (0.0 ~ 1.0)")

# -------------------------------------------
# 핵심 서비스 클래스 정의 (단일 책임 원칙 준수)
# -------------------------------------------
class RiskCalculatorService:
    """
    Mini ROI 리스크 시뮬레이션의 핵심 로직을 제공합니다.
    입력 데이터를 기반으로 위험 등급, 예상 손실액 및 개선책을 계산합니다.
    """

    @staticmethod
    def calculate_risk(input_data: SimulationInput) -> Dict[str, Any]:
        """
        사용자 입력 데이터와 내부 규제 모델을 결합하여 리스크 분석을 수행합니다.

        Args:
            input_data: 필수 시뮬레이션 데이터를 담은 스키마 객체.

        Returns:
            분석 결과와 구조화된 피드백 메시지 딕셔너리.
        """
        # 1. 위험 점수 계산 (가중치 기반)
        # 규제 변화 위험도가 높고, 컴플라이언스 점수가 낮을수록 가중치가 높아짐
        risk_score = (input_data.regulatory_change_risk * 0.5 + 
                      (1 - input_data.compliance_score) * 0.3 + 
                      (1 / (input_data.revenue_projection + 1)) * 0.2) * 100

        # 2. 위험 등급 및 예상 손실액 산출
        if risk_score > 75:
            risk_grade = "🔴 Critical"
            loss_estimate = input_data.revenue_projection * (risk_score / 100) * 0.2
            alert_level = "심각한 리스크 노출"
        elif risk_score > 40:
            risk_grade = "🟠 High"
            loss_estimate = input_data.revenue_projection * (risk_score / 100) * 0.1
            alert_level = "주의 깊은 모니터링 필요"
        else:
            risk_grade = "🟢 Low"
            loss_estimate = 0.0
            alert_level = "안정적인 운영 상태 유지 중"

        # 3. 회사 지침에 따른 구조화된 피드백 생성 (가장 중요!)
        feedback = {
            "problem_definition": f"현재 프로젝트는 규제 변화 위험도({input_data.regulatory_change_risk:.2f})와 낮은 컴플라이언스 점수({1 - input_data.compliance_score:.2f})로 인해 시장에서 예상치 못한 법적 손실에 노출될 가능성이 높습니다.",
            "cause_analysis": f"주요 원인은 내부 프로세스의 규제 준수(Compliance) 미흡 및 예측하지 못한 외부 환경 변화(Regulatory Change)입니다. (Source: {datetime.now().strftime('%Y-%m-%d')})",
            "mitigation_suggestion": "즉각적으로 전담팀을 구성하여 법무/기술 검토를 병행하고, 특히 데이터 흐름의 출처(Source)와 모든 결정의 추적 가능성(Traceability) 확보에 자원을 집중해야 합니다.",
        }

        return {
            "simulation_id": str(uuid.uuid4()),
            "risk_score": round(risk_score, 2),
            "risk_grade": risk_grade,
            "estimated_loss_krw": round(max(0, loss_estimate), int(1)), # 손실액은 최소 0원 보장
            "status_alert": alert_level,
            "structured_feedback": feedback
        }

# 테스트용 예시 데이터 (이것을 기반으로 Mock Prototype의 흐름을 설계함)
EXAMPLE_INPUT = SimulationInput(
    user_id="mock-test-user", 
    revenue_projection=500_000_000, 
    compliance_score=0.6, 
    regulatory_change_risk=0.8
)

if __name__ == '__main__':
    print("--- Risk Calculator Service Test Run ---")
    result = RiskCalculatorService.calculate_risk(EXAMPLE_INPUT)
    import json
    print(json.dumps(result, indent=4, ensure_ascii=False))

# -------------------------------------------
# Self-Test: 이 파일은 실행 로직이므로 테스트를 통해 검증해야 함.
# -------------------------------------------