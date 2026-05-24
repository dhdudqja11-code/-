import pytest
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
# 로컬 API Gateway의 엔드포인트를 테스트하기 위해 Mocking을 사용한다고 가정합니다.
# 실제 테스트 환경에서는 client를 사용하여 HTTP 요청을 보냅니다.

# 임시로 서비스 모듈만 직접 테스트하는 함수를 정의합니다.
# FastAPI 라우터를 통과하지 않고 순수 비즈니스 로직을 검증하여 안정성을 높입니다.

from services.risk_calculator_service import RiskCalculatorService, SimulationInput

def test_high_risk_scenario():
    """테스트 케이스 1: 규제 변화 위험도와 컴플라이언스 점수가 모두 낮은 Critical State."""
    input_data = SimulationInput(
        user_id="test-crit", 
        revenue_projection=100_000_000, # 비교적 작은 규모로 설정하여 손실액 확인 용이
        compliance_score=0.0, # 0.0으로 낮춰 가중치 상승
        regulatory_change_risk=1.0 # 1.0으로 높여 가중치 상승
    )
    result = RiskCalculatorService.calculate_risk(input_data)
    assert result["risk_grade"] == "🔴 Critical"
    # 예상 손실액이 0보다 크고, 어느 정도 의미 있는 값을 가지는지 확인
    assert result["estimated_loss_krw"] > 1000
    # 피드백 구조가 필수적으로 포함되어야 함을 검증
    assert "problem_definition" in result["structured_feedback"]

def test_low_risk_scenario():
    """테스트 케이스 2: 모든 지표가 완벽하여 Low Risk 상태여야 하는 경우."""
    input_data = SimulationInput(
        user_id="test-safe", 
        revenue_projection=1_000_000_000, # 대규모 매출 예상
        compliance_score=0.95, # 매우 높음
        regulatory_change_risk=0.1 # 낮음
    )
    result = RiskCalculatorService.calculate_risk(input_data)
    assert result["risk_grade"] == "🟢 Low"
    assert result["estimated_loss_krw"] == 0
    # 피드백 구조 검증: 위험성이 낮으므로, 해결책 제시가 '유지'에 초점을 맞춰야 함.
    assert "안정적인 운영 상태 유지 중" in result["status_alert"]

def test_data_validation_failure():
    """테스트 케이스 3: Pydantic 스키마 유효성 검증 실패 (Critical State 방어)."""

    # Pydantic이 자동으로 예외를 던지므로, 이를 포착하는 방식으로 테스트합니다.
    with pytest.raises(ValidationError):
        SimulationInput(
            user_id="test-fail", 
            revenue_projection=-100, 
            compliance_score=0.5, 
            regulatory_change_risk=0.5
        )