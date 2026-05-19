from pydantic import BaseModel, Field
from typing import List
from .purpose_analyzer import PurposeVector
from .risk_data_service import RiskReport

class AssuranceIndexResult(BaseModel):
    index: float = Field(description="계산된 확신 지수 (0.0 ~ 1.0). 높을수록 신뢰도가 높음.")
    is_compliant: bool = Field(description="현재 상태가 규제 요건을 충족하는지 여부.")
    # 3단계 구조의 최종 출력 객체입니다.
    feedback_report: Dict[str, str] = Field(description={
        "Problem": "사용자가 직면한 근본적 문제 정의.",
        "Cause": "위험 발생의 구체적인 원인 및 출처.",
        "Solution": "문제 해결을 위한 명확하고 실행 가능한 제안."
    })

class AssuranceCalculatorService:
    """
    Purpose Vector와 Risk Report를 결합하여 확신 지수를 계산하고, 3단계 피드백 보고서를 생성하는 핵심 서비스.
    """
    def calculate(self, purpose_vector: PurposeVector, risk_reports: List[RiskReport]) -> AssuranceIndexResult:
        print("--- [AssuranceCalculatorService] Calculating final index and report...")

        # 1. 가중치 기반 지수 계산 로직 (가정):
        # Index = 1 - (평균 리스크 점수 * 목적 정렬 불일치 페널티)
        avg_risk = sum(r.risk_score for r in risk_reports) / max(1, len(risk_reports))
        
        # 만약 Purpose와 Risk Domain이 크게 다르면 패널티 부과 (가정 로직)
        penalty = 0.2 if purpose_vector.target_domain != "Finance" else 0.0
        
        final_index = max(0.0, 1.0 - (avg_risk * 1.5 + penalty))

        # 2. Compliance 및 피드백 보고서 생성 로직:
        is_compliant = final_index > 0.7
        feedback = self._generate_feedback(purpose_vector, risk_reports, is_compliant)

        return AssuranceIndexResult(
            index=round(final_index, 4),
            is_compliant=is_compliant,
            feedback_report=feedback
        )

    def _generate_feedback(self, purpose: PurposeVector, reports: List[RiskReport], compliant: bool) -> Dict[str, str]:
        """3단계 구조의 피드백을 생성하는 private 메소드."""
        if not reports:
            return {"Problem": "정보 부족", "Cause": "위험 데이터를 찾을 수 없습니다.", "Solution": "데이터 소스를 추가해주세요."}

        latest_report = reports[0] # 최신 리포트 기준
        
        # [1] 문제 정의 (What went wrong?)
        problem_definition = f"현재 {purpose.target_domain} 도메인에서 '{purpose.primary_intent}'를 목표로 할 때, 규제적 불확실성(Regulatory Uncertainty)이 주요 문제입니다."

        # [2] 원인 분석 (Why did it go wrong? Source/Time)
        cause_analysis = f"원인은 {latest_report.source}에서 감지된 높은 위험 점수({latest_report.risk_score:.2f}) 때문입니다. 구체적으로: '{latest_report.warning_details}'에 해당합니다."

        # [3] 해결책 제시 (How to fix it?)
        if compliant:
            solution = "현재 구조는 충분히 안전하며, 시장 확장을 위한 추가적인 테스트와 검증이 필요합니다."
        else:
            solution = f"최소한 다음 두 가지 조치가 필수적입니다. 1) 데이터 출처를 {latest_report.source}로 명시하고, 2) 사용자 동의(Consent) 프로세스를 강화하여 '서사적 가치' 증명을 필수로 해야 합니다."

        return {
            "Problem": problem_definition,
            "Cause": cause_analysis,
            "Solution": solution
        }


# 테스트용 인스턴스 준비 및 의존성 검증을 위해 전역으로 사용합니다.
assurance_calculator = AssuranceCalculatorService()