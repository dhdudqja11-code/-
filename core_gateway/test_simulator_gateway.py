import pytest
from pydantic import ValidationError
from mini_roi_simulator import SimulationInput, RiskFactor, calculate_mini_roi_loss

# --- 테스트 케이스 정의 ---

def test_successful_run():
    """✅ [성공 케이스] 모든 필수 데이터가 완벽하게 포함된 정상 페이로드."""
    print("\n--- 🧪 Running Test: Successful Run (Happy Path) ---")
    valid_payload = {
        "client_id": "CL-12345",
        "user_role": "Admin",
        "risk_factors": [
            {"activity_name": "Database Backup", "potential_impact_score": 8.0},
            {"activity_name": "PII Masking", "potential_impact_score": 5.0}
        ]
    }
    
    # 1. Input Validation 검증
    input_data = SimulationInput(**valid_payload)
    assert input_data.client_id == "CL-12345"
    assert len(input_data.risk_factors) == 2
    
    # 2. 로직 수행 검증
    report, total_loss = calculate_mini_roi_loss(input_data)
    print("✅ Test Passed: Simulation successful.")
    
    # 결과 검증
    assert total_loss == (8.0 * 1500 + 5.0 * 1500)
    assert len(report) == 6 + 1 # 2개 리스크 * 3단계 + WARNING(19500 > 10000)

def test_malformed_payload_missing_field():
    """❌ [Guardrail Test 1] 필수 필드(client_id)가 누락된 경우 Pydantic ValidationError 검출."""
    print("\n--- 🧪 Running Test: Missing Field (Guardrail Test) ---")
    invalid_payload = {
        "user_role": "Admin",
        "risk_factors": [
            {"activity_name": "Database Backup", "potential_impact_score": 8.0}
        ]
    }
    
    with pytest.raises(ValidationError) as exc_info:
        SimulationInput(**invalid_payload)
        
    assert "client_id" in str(exc_info.value)
    print("✅ Test Passed: client_id missing handled by Pydantic.")

def test_type_mismatch_payload():
    """❌ [Guardrail Test 2] 데이터 타입이 잘못 입력된 경우 (e.g., potential_impact_score가 범위를 초과하거나 문자열)."""
    print("\n--- 🧪 Running Test: Type Mismatch (Guardrail Test) ---")
    invalid_payload = {
        "client_id": "CL-12345",
        "user_role": "Admin",
        "risk_factors": [
            {"activity_name": "Database Backup", "potential_impact_score": 15.0} # 1~10 범위를 초과함
        ]
    }
    
    with pytest.raises(ValidationError) as exc_info:
        SimulationInput(**invalid_payload)
        
    assert "potential_impact_score" in str(exc_info.value)
    print("✅ Test Passed: score limit boundary check passed.")

def test_empty_payload():
    """❌ [Guardrail Test 3] 빈 객체 또는 비어있는 risk_factors 리스트 전달 시 예외 발생."""
    print("\n--- 🧪 Running Test: Empty Payload ---")
    with pytest.raises(ValidationError):
        SimulationInput(**{})
        
    invalid_payload = {
        "client_id": "CL-12345",
        "user_role": "Admin",
        "risk_factors": [] # 최소 1개 이상 필요
    }
    with pytest.raises(ValidationError) as exc_info:
        SimulationInput(**invalid_payload)
    
    # min_length (v2) 혹은 min_items (v1) 에러 검출
    assert "risk_factors" in str(exc_info.value)
    print("✅ Test Passed: Empty payload validation rejected.")