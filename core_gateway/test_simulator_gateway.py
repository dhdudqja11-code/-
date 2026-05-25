import pytest
import json
from mini_roi_simulator import run_mini_roi_analysis # 가정: API 로직을 담은 함수

# --- 테스트 환경 설정 및 가짜 데이터 정의 (Mocking) ---
# 실제 배포 환경에서는 이 부분이 Core Gateway를 통해 호출될 것입니다.

def mock_gateway_call(payload):
    """Mini ROI 시뮬레이터의 핵심 로직을 감싸는 가상 게이트웨이 함수."""
    try:
        # Mini ROI 시뮬레이터 내부에서 Pydantic 유효성 검사가 이루어진다고 가정하고 호출합니다.
        return run_mini_roi_analysis(payload) 
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# --- 테스트 케이스 정의 ---

def test_successful_run():
    """✅ [성공 케이스] 모든 필수 데이터가 완벽하게 포함된 정상 페이로드."""
    print("\n--- 🧪 Running Test: Successful Run (Happy Path) ---")
    valid_payload = {
        "source_system": "WebHook",
        "transaction_id": "TX123456789",
        "data_subject": {"user_id": 100, "email": "test@example.com"},
        "risk_score": 0.85, # High risk score for testing the module's action
    }
    result = mock_gateway_call(valid_payload)
    print("✅ Test Passed: Simulation successful.")
    # 결과 구조 검증 (Assertion Placeholder)
    assert result["status"] == "SUCCESS"

def test_malformed_payload_missing_field():
    """❌ [Guardrail Test 1] 필수 필드(source_system)가 누락된 경우."""
    print("\n--- 🧪 Running Test: Missing Field (Guardrail Test) ---")
    invalid_payload = {
        "transaction_id": "TX999",
        # 'source_system' 키를 의도적으로 제거함. Pydantic은 이를 필수로 간주해야 함.
        "data_subject": {"user_id": 100},
        "risk_score": 0.5,
    }
    result = mock_gateway_call(invalid_payload)
    print("⚠️ Test Result: Malformed payload received.")
    # 핵심 검증 지점: 'Missing Field' 에러가 발생해야 함.
    assert result["status"] == "ERROR" and "source_system" in result["message"]

def test_type_mismatch_payload():
    """❌ [Guardrail Test 2] 데이터 타입이 잘못 입력된 경우 (e.g., user_id가 문자열)."""
    print("\n--- 🧪 Running Test: Type Mismatch (Guardrail Test) ---")
    invalid_payload = {
        "source_system": "Manual",
        "transaction_id": "TX1010",
        "data_subject": {"user_id": "A-B-C"}, # user_id는 정수형이 기대되는데 문자열 전달
        "risk_score": 0.7,
    }
    result = mock_gateway_call(invalid_payload)
    print("⚠️ Test Result: Type mismatch payload received.")
    # 핵심 검증 지점: 'Type Error'가 발생하며 정확한 타입을 명시해야 함.
    assert result["status"] == "ERROR" and "type" in result["message"].lower()

def test_empty_payload():
    """❌ [Guardrail Test 3] 빈 객체를 전달했을 경우."""
    print("\n--- 🧪 Running Test: Empty Payload ---")
    result = mock_gateway_call({})
    print("⚠️ Test Result: Empty payload received.")
    assert result["status"] == "ERROR" and "필수 입력 값" in result["message"]

if __name__ == "__main__":
    # 실제 테스트 실행 시, pytest 프레임워크를 사용하겠지만, 
    # 여기서는 명시적 로그 출력을 위해 main 함수 내에서 순차적으로 호출합니다.
    print("=========================================================")
    print("🚀 Mini ROI Simulator Gateway 통합 안정성 검증 시작 (Staging)")
    print("=========================================================")

    test_successful_run()
    test_malformed_payload_missing_field()
    test_type_mismatch_payload()
    test_empty_payload()
    
    print("\n\n=========================================================")
    print("✅ 모든 테스트 케이스 실행 완료. 디버깅 로그를 확인하세요.")
    print("=========================================================")