import pytest
from api_gateway.core_gateway import APIGateway, QuotaExceededError, APIError, handle_webhook_request

@pytest.fixture(scope="module")
def gateway():
    """API Gateway 인스턴스를 테스트 픽스처로 제공합니다."""
    return APIGateway()

# --- 성공 경로 테스트 (Happy Path) ---
def test_successful_request(gateway):
    """유효한 키와 충분한 쿼터를 가진 사용자의 정상 요청 처리 검증."""
    api_key = "secure_test_key123"
    user_id = "admin_user" # 쿼터가 남아있는 사용자
    
    result = gateway.process_request(api_key, user_id)
    assert result['status'] == 'SUCCESS'
    # 쿼터는 반드시 감소했는지 확인 (로직의 사이드 이펙트 검증)
    assert result['remaining_quota'] == 99 

# --- 인증 실패 테스트 (Authentication Guard Test) ---
def test_invalid_api_key(gateway):
    """유효하지 않은 API 키를 사용했을 때, Quota 체크 전에 차단되는지 확인."""
    user_id = "admin_user" # 쿼터는 남아있음.
    invalid_key = "short"
    
    with pytest.raises(APIError) as excinfo:
        gateway.process_request(invalid_key, user_id)
    # 반드시 인증 에러 메시지가 포함되어야 함.
    assert "유효하지 않은 API 키입니다." in str(excinfo.value)

# --- 쿼터 초과 테스트 (Quota Guard Test - Critical Path) ---
def test_quota_exceeded(gateway):
    """사용량 할당량이 0 이하일 때, QuotaExceededError가 발생하며 로직이 안전하게 차단되는지 검증."""
    user_id = "guest_user" # 초기 쿼터가 0인 사용자
    api_key = "valid_test_key123"
    
    with pytest.raises(QuotaExceededError) as excinfo:
        gateway.process_request(api_key, user_id)
    # QuotaExceededError 타입과 메시지 확인
    assert isinstance(excinfo.value, QuotaExceededError)
    assert "사용량 할당량을 초과했습니다." in str(excinfo.value)

def test_unknown_user_id(gateway):
    """존재하지 않는 user_id를 사용할 경우 에러가 발생하는지 확인."""
    api_key = "valid_test_key123"
    unknown_user = "non_existent_user"
    
    with pytest.raises(APIError) as excinfo:
        gateway.process_request(api_key, unknown_user)
    assert "알 수 없는 사용자 ID입니다." in str(excinfo.value)

# --- Webhook 통합 시나리오 테스트 (End-to-End Simulation Test) ---
def test_webhook_successful_processing():
    """Webhook을 통해 성공적으로 트랜잭션 데이터를 처리하는 시뮬레이션."""
    payload = {"user_id": "admin_user", "source_key": "secure_test_key123"}
    # Webhook 로직이 QuotaExceededError를 잡아서 Alert를 출력하도록 설계됨을 검증.
    result = handle_webhook_request(payload)
    assert result and result['status'] == 'SUCCESS'

def test_webhook_quota_failure_handling():
    """Webhook으로 들어온 데이터가 쿼터 초과 시, 안전하게 Alert를 발생시키는지 확인."""
    # 가상의 쿼터 제로 사용자를 강제 주입하여 테스트
    original_quotas = {"guest_user": 0}
    gateway = APIGateway()
    gateway._user_quotas = original_quotas

    payload = {"user_id": "guest_user", "source_key": "secure_test_key123"}
    result = handle_webhook_request(payload)
    # 쿼터 초과 시, Alert가 발생하며 에러 구조를 반환해야 함.
    assert result and 'error' in result