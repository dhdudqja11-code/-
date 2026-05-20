from src.api_gateway.schemas.avoided_loss_schema import AvoidedLossInput, AvoidedLossOutput
import math

# 핵심 로직: 재무적 위험 회피 비용 (Avoided Loss) 공식 기반
def calculate_avoided_loss(input_data: AvoidedLossInput) -> tuple[float, dict]:
    """
    주어진 변수들을 조합하여 '재무적 위험 회피 비용'을 계산하는 핵심 함수.
    이 로직은 모든 엣지 케이스를 포함해야 합니다. (검증 필요!)
    """
    v = input_data.variables

    # 기본 손실 예측치 정의: 규제 + 운영 실패
    base_loss = v.regulatory_risk_cost + v.operational_failure_cost
    
    # 복합 변수 계산: 명성 손실 및 기타 계수 적용
    reputation_impact = v.reputation_loss_potential * (1 + v.bias_factor)
    total_input_risk = base_loss + reputation_impact + v.lock_in_cost

    # Avoided Loss 공식: 총 위험 예측치 - 현재 통제력으로 인한 손실 방지 효과 
    # (여기서는 단순화를 위해, 최소 필요 자원 투입 대비 최대 리스크로 정의)
    avoided_loss = total_input_risk + v.required_mitigation_effort * 0.5

    # 결과 디테일 구조화
    breakdown = {
        "RegulatoryRiskContribution": v.regulatory_risk_cost,
        "ReputationLossContribution": reputation_impact,
        "OperationalFailureContribution": v.operational_failure_cost,
        "LockInCostContribution": v.lock_in_cost,
        "MitigationEffortFactor": v.required_mitigation_effort * 0.5,
    }

    return avoided_loss, breakdown


def generate_avoided_loss_report(input_data: AvoidedLossInput) -> AvoidedLossOutput:
    """전체 보고서 생성 및 포맷팅 (Domain Logic)."""
    try:
        # 1. 핵심 계산 수행
        avoided_loss, risk_breakdown = calculate_avoided_loss(input_data)

        # 2. 분석 요약문 생성 (이 부분은 LLM 프롬프트 또는 복잡한 규칙 엔진 필요)
        if avoided_loss < 1000:
             summary = "현재 리스크가 비교적 낮아, 단기적인 개선 활동으로 충분합니다. 하지만 방심해서는 안 됩니다."
        elif v.regulatory_risk_cost > 5000 or v.reputation_loss_potential > 8000:
            summary = f"경고: 규제 또는 명성 리스크가 매우 높습니다. ({v.regulatory_risk_cost:.2f} / {v.reputation_loss_potential:.2f}). 즉각적인 아키텍처 및 법적 검토가 필수입니다."
        else:
            summary = "시스템 도입을 통해 상당한 재무적 위험 회피 비용이 예상됩니다. 구조적 개선과 자동화 로직 통합을 추천합니다."


        return AvoidedLossOutput(
            avoided_loss_amount=round(avoided_loss, 2),
            analysis_summary=summary,
            risk_breakdown=risk_breakdown
        )

    except Exception as e:
        # 예외 처리 로직 추가 (실제 API에서는 로그 기록 및 사용자에게 친절한 에러 메시지 제공 필요)
        raise RuntimeError(f"Avoided Loss 보고서 생성 중 치명적인 오류 발생: {e}")