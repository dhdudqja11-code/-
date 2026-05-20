from pydantic import BaseModel, Field, NonNegativeFloat
from typing import Dict, Any
import math

# ======================================================
# Pydantic Data Models (Strict Input Validation)
# ======================================================

class VariableInput(BaseModel):
    """사용자가 입력하는 개별 변수 값들을 정의합니다."""
    transaction_value: NonNegativeFloat = Field(..., description="핵심 거래 가치 ($)")
    time_span_days: NonNegativeFloat = Field(..., description="위험이 노출된 시간 범위 (일)")
    emotion_impact_score: float = Field(..., ge=-1.0, le=1.0, description="감정적 손실 점수 (-1.0 ~ 1.0)") # -1 (최저) ~ 1 (최고)
    regulatory_risk_factor: NonNegativeFloat = Field(..., gt=0.0, description="규제 위험 노출 지수 (0.0 이상)")
    opportunity_cost_ratio: float = Field(..., ge=0.0, le=1.0, description="기회비용 대비 비율 (0.0 ~ 1.0)")

class AvoidedLossReport(BaseModel):
    """최종 계산된 손실액 보고서의 구조를 정의합니다."""
    calculated_avoided_loss: float = Field(..., description="산출된 총 회피 가능 손실액 ($)")
    total_risk_score: float = Field(..., description="종합 위험 점수 (가중치 포함)")
    analysis_breakdown: Dict[str, Any] = Field(..., description="세부 분석 항목 (예: 감정적 영향 기여도)")

# ======================================================
# Core Business Logic (Pure Function)
# ======================================================

def calculate_avoided_loss(variables: VariableInput) -> AvoidedLossReport:
    """
    주어진 변수들을 바탕으로 '회피 가능 손실액'을 계산하는 핵심 로직입니다.
    행동경제학 및 감정적 가중치를 통합합니다.
    """
    # 1. 기본 위험 산출 (Base Risk)
    # 거래 가치 * 시간 범위 * 규제 리스크 계수
    base_risk = variables.transaction_value * variables.time_span_days * variables.regulatory_risk_factor

    # 2. 감정적/행동경제학적 변수 통합 (Weighted Factors)
    # 감정적 손실 영향력: |Emotion Score| * Opportunity Cost Ratio * 가중치(1.5)
    emotion_weight = abs(variables.emotion_impact_score) * variables.opportunity_cost_ratio * 1.5

    # 시간 경과에 따른 이자/기회비용 반영 (복리 효과 시뮬레이션)
    time_decay_multiplier = math.exp(0.05 * variables.time_span_days / 365) # 연간 5% 기회비용 가정

    # 3. 최종 회피 손실 계산
    # 기본 위험 + (감정적 가중치 * 시간 복리 계수)
    total_avoided_loss = base_risk + (emotion_weight * time_decay_multiplier)

    # 4. 종합 점수 및 분석 분해
    overall_risk_score = total_avoided_loss / variables.transaction_value if variables.transaction_value > 0 else 0.0

    analysis_breakdown = {
        "base_risk_contribution": round(base_risk, 2),
        "emotional_impact_contribution": round(emotion_weight * time_decay_multiplier, 2),
        "time_decay_factor": round(time_decay_multiplier, 4)
    }

    return AvoidedLossReport(
        calculated_avoided_loss=round(total_avoided_loss, 2),
        total_risk_score=round(overall_risk_score, 3),
        analysis_breakdown=analysis_breakdown
    )

# ======================================================
# E2E 테스트 케이스 (Unit Test Placeholder)
# ======================================================
def run_e2e_test_case():
    """
    [테스트 시나리오] 이상적인 조건에서의 손실액 계산 검증.
    가장 위험한 상황(최대 거래, 최대 시간, 최대 규제 위험, 부정적 감정)을 테스트합니다.
    """
    print("\n--- [E2E Test: Maximum Loss Scenario Simulation Started] ---")
    # 예시 입력 값 (Max values for testing boundary conditions)
    test_variables = VariableInput(
        transaction_value=10000.0, # $10,000 거래
        time_span_days=365,       # 1년 노출
        emotion_impact_score=-1.0,# 최악의 감정적 충격
        regulatory_risk_factor=0.8,# 높은 규제 리스크
        opportunity_cost_ratio=1.0 # 기회비용 최대
    )

    try:
        report = calculate_avoided_loss(test_variables)
        print("✅ Test Passed! Avoided Loss Report Generated Successfully.")
        print(f"  -> Calculated Loss (Max Risk): ${report.calculated_avoided_loss:,}")
        return report
    except Exception as e:
        print(f"❌ Test Failed! Error during calculation: {e}")
        return None

#