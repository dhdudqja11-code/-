import pytest
import time
from unittest.mock import patch, MagicMock
# 코어 로직이 있는 모듈을 임포트합니다.
from src.api.authority_state_manager import AuthorityStateManager

@pytest.fixture(scope="module")
def authority_manager():
    """테스트를 위해 AuthorityStateManager 인스턴스를 제공하는 Fixture."""
    return AuthorityStateManager()

# Mocking the time delay function to ensure fast, deterministic testing.
# 실제 지연 시간 1초가 걸리는 것을 막고, 로직 흐름만 테스트합니다.
@patch('time.sleep', return_value=None)
def test_e2e_full_state_transition(mock_sleep, authority_manager):
    """
    E2E 전체 상태 전이 (Initial -> Warning -> Solution)를 테스트하고, 
    각 단계의 로깅과 권위적 메시지 출력을 검증합니다.
    """
    print("\n--- STARTING E2E AUTHORITY METER TEST SUITE ---")

    # 1. 초기 상태 (Initial State Check)
    initial_state = authority_manager.initialize_check(data={"source": "Internal", "time": time.time()})
    assert initial_state["status"] == "INITIAL"
    print("✅ Test Passed: Initial state successfully established.")

    # 2. 경고 상태 진입 시뮬레이션 (Warning State Transition)
    # 임의로 위험도가 높은 가상 데이터를 주입합니다.
    warning_data = {"source": "External API", "time": time.time(), "risk_score": 0.85}
    
    # Mocking the logging function to capture 'Glitch' event logs
    with patch('builtins.print') as mock_print:
        warning_result = authority_manager.check_authority(data=warning_data)

    # Assertions for Warning State
    assert warning_result["status"] == "WARNING"
    assert "AuthorityWarning" in str(warning_result["details"]) # 권위적 경고 메시지 포함 확인
    
    # Verify the specific Glitch/Alert log message was emitted
    mock_print.assert_any_call("🚨 [GLITCH ALERT] Authority compromised! System integrity check required.")
    print("✅ Test Passed: Warning state detected and 'Glitch Alert' logged correctly.")

    # 3. 해결 상태로의 복구 시뮬레이션 (Solution State Transition)
    solution_data = {"source": "Manual Override", "time": time.time(), "mitigation_score": 0.95}
    with patch('builtins.print') as mock_print:
        final_result = authority_manager.resolve_check(data=solution_data)

    # Assertions for Solution State
    assert final_result["status"] == "SOLUTION"
    assert "Control Secured" in str(final_result["message"]) # 통제권 확보 메시지 확인
    print("✅ Test Passed: Solution state successfully achieved and 'Control Secured' message emitted.")

    # 4. 최종 검증 (Clean up)
    print("--- E2E AUTHORITY METER TEST SUITE FINISHED ---")


@pytest.mark.parametrize(
    "input_data, expected_status",
    [
        ({"source": "Internal", "time": time.time()}, "INITIAL"), # 기본값 테스트
        (None, "ERROR"), # Null Input 테스트
        ({"source": "Unknown", "time": time.time(), "risk_score": 0.1}, "SOLUTION") # Low Risk = Solution으로 간주되는 로직 가정
    ]
)
def test_edge_case_input(authority_manager, input_data, expected_status):
    """경계 조건 및 데이터 결함 입력 테스트."""
    if input_data is None:
        # Null 처리 시도 (실제 시스템에서는 예외 처리가 필수적임)
        result = authority_manager.check_authority(data=input_data)
    else:
        result = authority_manager.check_authority(data=input_data)

    assert result["status"] == expected_status
    print(f"✅ Test Passed: Edge case input ({input_data}) handled correctly with status {expected_status}.")


# 테스트 완료 후, 이 파일을 실행하는 명령과 보고서를 작성합니다.