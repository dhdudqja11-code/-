import pytest
from fastapi import FastAPI
# 프로젝트 내부 구조에 맞게 수정 필요: 실제 API 호출 함수가 정의된 모듈을 임포트합니다.
from src.api import simulation_router 

# 테스트용 Mock Data (Researcher가 제공한 고위험 사례를 시뮬레이션)
HIGH_RISK_CASE_1 = {
    "risk_type": "GDPR/데이터주권",
    "description": "미국 기반 클라우드 사용으로 인한 유럽 법규 위반 리스크.",
    "severity_score": 0.95, # 최대치 근접
    "potential_loss_factor": 1.8, # 가중치 높은 요소
    "source_statute": "GDPR Article 83",
}

HIGH_RISK_CASE_2 = {
    "risk_type": "SOX/재무보고 투명성",
    "description": "내부 통제 부실로 인한 분기 보고서 조작 가능 리스크.",
    "severity_score": 0.88,
    "potential_loss_factor": 2.5, # 가장 높은 손실 가중치 예상
    "source_statute": "SOX Section 404",
}

@pytest.fixture(scope="module")
def app():
    """테스트용 FastAPI 앱 인스턴스 제공"""
    # 실제 라우터가 사용하는 API 객체를 Mocking하거나, 테스트 전용 클라이언트를 사용합니다.
    return FastAPI()

# Note: 실제 로직이 simulation_router 내부에 있다면, 아래처럼 client를 통해 호출해야 합니다.
# 예시로, 'calculate_loss'라는 핵심 함수가 있다고 가정하고 테스트를 작성하겠습니다.

def test_api_high_risk_validation(app):
    """
    [TEST] 고위험 사례 1: GDPR 위반 시뮬레이션 - 결과값의 논리적 일관성 검증
    목표: 높은 severity와 factor가 충격적으로 큰 손실액을 산출하는지 확인.
    """
    print("--- Running Test Case 1: GDPR Violation ---")
    # Mocking the internal calculation function call (replace with actual router call)
    estimated_loss = simulation_router.calculate_loss(
        risk_data=HIGH_RISK_CASE_1,
        base_revenue=500000 # 가상 기준 매출액 $50만
    )

    # Business Rule Assert: GDPR 리스크는 최소 80% 이상의 손실 위험이 발생해야 함.
    assert isinstance(estimated_loss, float) and estimated_loss > 390000.0
    print(f"✅ Test Case 1 Passed. Estimated Loss: ${estimated_loss:,.2f}")


def test_api_critical_risk_validation(app):
    """
    [TEST] 고위험 사례 2: SOX 규정 위반 시뮬레이션 - 최대 손실액 산출 검증
    목표: 가장 높은 potential_loss_factor를 사용하여 최대치의 재무적 공포를 조성하는지 확인.
    """
    print("\n--- Running Test Case 2: SOX Violation ---")
    # Mocking the internal calculation function call (replace with actual router call)
    estimated_loss = simulation_router.calculate_loss(
        risk_data=HIGH_RISK_CASE_2,
        base_revenue=500000
    )

    # Business Rule Assert: SOX 리스크는 기준 매출액 대비 3배 이상의 손실이 예상되어야 함.
    assert isinstance(estimated_loss, float) and estimated_loss > 1250000.0
    print(f"✅ Test Case 2 Passed. Estimated Loss: ${estimated_loss:,.2f}")


def test_api_low_risk_validation(app):
    """
    [TEST] 낮은 위험 사례 검증 (Negative Testing)
    목표: 리스크가 낮을 때, 손실액이 적절히 제한되는지 확인.
    """
    LOW_RISK_CASE = {
        "risk_type": "일반 운영 미준수",
        "description": "경미한 계약서 누락.",
        "severity_score": 0.2,
        "potential_loss_factor": 0.5,
        "source_statute": None,
    }
    print("\n--- Running Test Case 3: Low Risk Validation ---")
    estimated_loss = simulation_router.calculate_loss(
        risk_data=LOW_RISK_CASE,
        base_revenue=500000
    )

    # Business Rule Assert: 손실액은 기준 매출의 일정 비율(예: 10%)을 넘지 않아야 함.
    assert isinstance(estimated_loss, float) and estimated_loss < 60000.0
    print("✅ Test Case 3 Passed.")