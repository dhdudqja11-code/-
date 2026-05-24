import pytest
from unittest.mock import patch, MagicMock
import time
# 로직 파일 경로를 임포트합니다. (실제 프로젝트 구조에 맞게 수정 필요)
from src.modules.connectivity.connection_module import (
    establish_secure_connection, 
    AuthenticationFailed, 
    QuotaExceededError, 
    ConnectionError
)

# --- Mocking 환경 설정 및 Fixtures ---

@pytest.fixture(scope="module")
def mock_dependencies():
    """모든 외부 의존성 함수들을 테스트 세션 전체에 걸쳐 모킹합니다."""
    with (
        patch('src.modules.connectivity.connection_module.validate_credentials') as MockAuth,
        patch('src.modules.connectivity.connection_module.check_quota_and_log') as MockQuotaCheck,
        patch('src.modules.connectivity.connection_module.execute_initial_api_call') as MockAPIExec:
            yield MockAuth, MockQuotaCheck, MockAPIExec

def test_successful_secure_connection(mock_dependencies):
    """[성공 케이스] 인증, 쿼터 확인, API 호출 모두 성공하는 최적의 경로 테스트."""
    MockAuth, MockQuotaCheck, MockAPIExec = mock_dependencies
    
    # 목킹 설정: 모든 함수가 성공적으로 작동한다고 가정
    MockAuth.return_value = True
    MockQuotaCheck.return_value = 100  # 충분한 쿼터
    MockAPIExec.return_value = "SUCCESS_DATA"

    result = establish_secure_connection("admin", "SECURE_TOKEN")

    # 검증: 결과값 확인 및 의존성 함수 호출 여부 확인 (Coverage)
    assert result == "SUCCESS_DATA"
    MockAuth.assert_called_once_with("admin", "SECURE_TOKEN")
    MockQuotaCheck.assert_called_once()
    MockAPIExec.assert_called_once()

def test_failure_authentication(mock_dependencies):
    """[실패 케이스 1] 인증 단계에서 실패했을 때, 후속 로직이 실행되지 않음을 확인."""
    MockAuth, MockQuotaCheck, MockAPIExec = mock_dependencies

    # 목킹 설정: 인증만 실패하도록 강제
    MockAuth.return_value = False

    with pytest.raises(AuthenticationFailed) as excinfo:
        establish_secure_connection("baduser", "wrong_token")

    # 검증 1: 에러 메시지 확인
    assert "유효하지 않습니다" in str(excinfo.value)
    # 검증 2: 중요한 로직 (Quota Check, API Call)이 실행되지 않았는지 확인
    MockQuotaCheck.assert_not_called()
    MockAPIExec.assert_not_called()

def test_failure_quota_exceeded(mock_dependencies):
    """[실패 케이스 2] 인증은 성공했으나, 쿼터 제한에 걸렸을 때의 처리 흐름 테스트."""
    MockAuth, MockQuotaCheck, MockAPIExec = mock_dependencies

    # 목킹 설정: 인증 성공 -> 쿼터 실패 (예외 발생)
    MockAuth.return_value = True
    # QuotaExceededError를 강제 발생시킴
    MockQuotaCheck.side_effect = QuotaExceededError(remaining=0)

    with pytest.raises(QuotaExceededError):
        establish_secure_connection("testuser", "SECURE_TOKEN")

    # 검증 1: 인증은 정상 작동했는지 확인 (이전 단계까지는 성공해야 함)
    MockAuth.assert_called_once()
    # 검증 2: API 호출은 절대 실행되어서는 안 됨 (Guardrail가 잘 작동하는지 테스트)
    MockAPIExec.assert_not_called()

def test_failure_api_connection(mock_dependencies):
    """[실패 케이스 3] 인증과 쿼터까지 통과했으나, 최종 API 호출에서 실패했을 때의 처리 테스트."""
    MockAuth, MockQuotaCheck, MockAPIExec = mock_dependencies

    # 목킹 설정: 성공적으로 AuthN/Quota를 통과하도록 함.
    MockAuth.return_value = True
    MockQuotaCheck.return_value = 50
    # API 호출 시 ConnectionError 발생을 강제
    MockAPIExec.side_effect = ConnectionError("Gateway connection refused.")

    with pytest.raises(ConnectionError) as excinfo:
        establish_secure_connection("admin", "SECURE_TOKEN")

    # 검증 1: 에러 메시지 확인 및 Guardrail 동작 여부 확인
    assert "최종 API 통신 실패" in str(excinfo.value)
    MockAuth.assert_called_once()
    MockQuotaCheck.assert_called_once()
    MockAPIExec.assert_called_once()