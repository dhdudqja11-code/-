import pytest
from pydantic import ValidationError
from src.schemas.remote_access_schemas import (
    RemoteConnectionRequest, 
    CommandExecutionRequest, 
    StreamDataRequest
)

# --- Test Case for connect-remote ---
def test_connect_remote_successful_schema():
    """성공적인 연결 요청 스키마 유효성을 검증합니다."""
    data = {
        "user_authority_token": "valid.jwt.token",
        "target_system_id": "CRM_V2",
        "requested_scope": "READ_WRITE_CUSTOMER_PROFILE",
        "duration_minutes": 60
    }
    try:
        request = RemoteConnectionRequest(**data)
        assert request.user_authority_token == "valid.jwt.token"
    except ValidationError as e:
        pytest.fail(f"RemoteConnectionRequest 스키마 유효성 검증 실패: {e}")

def test_connect_remote_missing_field():
    """필수 필드 누락 시 예외 처리가 정상적으로 발생하는지 확인합니다."""
    data = {
        "user_authority_token": "valid.jwt.token",
        # target_system_id가 빠짐
        "requested_scope": "READ_ONLY"
    }
    with pytest.raises(ValidationError):
        RemoteConnectionRequest(**data)

# --- Test Case for execute-command ---
def test_execute_command_successful_schema():
    """성공적인 명령어 실행 요청 스키마 유효성을 검증합니다."""
    data = {
        "connection_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789", # UUID 형식 확인용 가상 ID
        "command_name": "GET_RISK_REPORT",
        "arguments": {"client_id": 123, "report_type": "LEGAL"}
    }
    try:
        request = CommandExecutionRequest(**data)
        assert request.command_name == "GET_RISK_REPORT"
        assert isinstance(request.arguments['client_id'], int)
    except ValidationError as e:
        pytest.fail(f"CommandExecutionRequest 스키마 유효성 검증 실패: {e}")

# --- Test Case for stream-data ---
def test_stream_data_successful_schema():
    """스트리밍 데이터 요청 스키마 유효성을 검증합니다."""
    data = {
        "connection_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
        "data_stream_type": "FINANCIAL_UPDATE",
        "start_timestamp": "2026-06-02T00:00:00Z"
    }
    try:
        request = StreamDataRequest(**data)
        assert request.data_stream_type == "FINANCIAL_UPDATE"
    except ValidationError as e:
        pytest.fail(f"StreamDataRequest 스키마 유효성 검증 실패: {e}")

# 테스트를 통과하는지 확인하기 위해 임시 실행 코드를 추가합니다. (실제 터미널에서 실행될 때)
if __name__ == "__main__":
    print("--- Running Remote Access Schema Tests ---")
    # pytest는 실제 환경에서 사용되므로, 여기서는 단순히 성공 메시지를 출력하는 것으로 대체합니다.
    try:
        test_connect_remote_successful_schema()
        test_execute_command_successful_schema()
        test_stream_data_successful_schema()
        print("✅ 모든 스키마 테스트 케이스가 성공적으로 정의되었습니다.")
    except Exception as e:
        print(f"❌ 스키마 테스트 중 오류 발생: {e}")