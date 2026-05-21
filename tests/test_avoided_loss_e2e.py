import pytest
from unittest.mock import patch, MagicMock
from src.services.avoided_loss_calculator import calculate_avoided_loss

# --- 테스트 케이스 그룹: 성공 및 정상 작동 (Happy Path) ---

def test_happy_path_normal_loss():
    """정상적인 데이터 입력 시 적절한 손실액이 계산되는지 검증합니다."""
    sample_data = {"amount": 1000, "recovery_rate": 0.5, "emotional": {"anxiety": 50, "disappointment": 30}}
    risk_score = 0.5
    # 예상 값은 로직 구현에 따라 달라지지만, 기본적인 작동 확인이 목적입니다.
    assert calculate_avoided_loss(sample_data, risk_score) > 0

def test_high_risk_scenario():
    """규제 리스크가 높을 때 (엣지 케이스 아님), 손실액이 크게 증가하는지 검증합니다."""
    # 규제 점수 최대치와 높은 경제적 손실 상황 가정
    sample_data = {"amount": 1000, "recovery_rate": 0.0, "emotional": {"anxiety": 50, "disappointment": 50}}
    risk_score = 1.0 # 최고 위험도
    result = calculate_avoided_loss(sample_data, risk_score)
    # 규제 리스크가 지배적으로 작용하여 높은 값이 나와야 합니다. (임계값 설정)
    assert result > 450 

# --- 테스트 케이스 그룹: 에지 케이스 및 실패 시나리오 (Stress Test Focus) ---

def test_edge_case_zero_data():
    """모든 변수가 0일 때 손실액이 정확히 0인지 검증합니다."""
    sample_data = {"amount": 0, "recovery_rate": 1.0, "emotional": {"anxiety": 0, "disappointment": 0}}
    risk_score = 0.0
    assert calculate_avoided_loss(sample_data, risk_score) == 0

def test_edge_case_missing_keys():
    """필수 키가 누락되었을 때 (예: 'amount'나 'emotional'), 프로그램이 깨지지 않고 기본값으로 처리하는지 검증합니다."""
    # 'amount' 키를 완전히 제거한 상황 시뮬레이션
    bad_data = {"recovery_rate": 0.5, "emotional": {"anxiety": 10, "disappointment": 20}} # amount 누락
    risk_score = 0.1
    # 오류가 발생하지 않고 계산이 정상적으로 진행되어야 함 (robustness)
    assert calculate_avoided_loss(bad_data, risk_score) >= 0

def test_stress_case_invalid_input_type():
    """'amount'에 문자열 등 잘못된 타입이 들어왔을 때, 예외 처리가 되고 손실액 계산이 중단되는지 검증합니다."""
    # amount 자리에 'N/A' 같은 문자열 삽입 시도
    bad_data = {"amount": "N/A", "recovery_rate": 0.5, "emotional": {"anxiety": 10, "disappointment": 20}}
    risk_score = 0.1
    # 이 테스트는 내부적으로 try-except가 작동하여 계산을 우회하거나 0으로 처리해야 합니다.
    result = calculate_avoided_loss(bad_data, risk_score)
    assert result == pytest.approx(0.0) # 데이터 파싱 오류 발생 시 안전하게 0 반환 예상

def test_stress_case_out_of_range_risk():
    """규제 리스크 점수가 유효 범위를 벗어났을 때 (예: 1.5), 로직이 이를 처리하는지 검증합니다."""
    sample_data = {"amount": 100, "recovery_rate": 0.5, "emotional": {"anxiety": 10, "disappointment": 20}}
    risk_score = 1.5 # 최대치(1.0) 초과
    # 내부 로직에서 점수를 1.0으로 클리핑하거나 에러를 발생시켜야 합니다. 여기서는 안정성 확보를 위해 경고만 출력되고 결과가 나오는지 확인합니다.
    result = calculate_avoided_loss(sample_data, risk_score)
    assert result >= 0 # 오류로 인해 프로그램이 멈추지 않아야 함