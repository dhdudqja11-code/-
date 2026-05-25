import pytest
from api_gateway.api_gateway import get_user_profile, is_ip_valid, check_rate_limit, check_authorization, TEST_CONFIG

# --- 1. Guard Logic 단위 테스트 (개별 함수 검증) ---

def test_is_ip_valid_success():
    """IP 유효성 성공 케이스: 허용된 범위 내 IP."""
    assert is_ip_valid(TEST_CONFIG["IP_SUCCESS"]) == True

def test_is_ip_valid_failure_out_of_range():
    """IP 유효성 실패 케이스 1: 범위 외 IP."""
    assert is_ip_valid(TEST_CONFIG["IP_FAILURE"]) == False

def test_is_ip_valid_failure_invalid_format():
    """IP 유효성 실패 케이스 2: 잘못된 포맷의 IP."""
    assert is_ip_valid("not-an-ip") == False

def test_check_rate_limit_ok():
    """Rate Limit 성공 케이스: 요청 횟수가 제한보다 적을 때."""
    is_ok, _ = check_rate_limit("test", 50)
    assert is_ok == True

def test_check_rate_limit_exceeded():
    """Rate Limit 실패 케이스: 요청 횟수가 제한을 초과했을 때."""
    # RATE_LIMIT_PER_HOUR (100)보다 큰 값으로 설정하여 테스트
    is_ok, _ = check_rate_limit("test", 101) 
    assert is_ok == False

def test_check_authorization_success():
    """권한 검증 성공 케이스: ADMIN 권한 보유."""
    assert check_authorization("user", "ADMIN") == True

def test_check_authorization_failure():
    """권한 검증 실패 케이스: 낮은 등급의 권한만 보유."""
    assert check_authorization("user", "BASIC_USER") == False


# --- 2. E2E 통합 Gateway 테스트 (전체 흐름 검증) ---

@pytest.mark.parametrize(
    "ip, user_id, permission, count, expected_status", 
    [
        # Case 1: 성공 케이스 - 모든 게이트 통과
        ("192.168.1.50", "user_abc", "PREMIUM_USER", 50, True),
        # Case 2: IP 실패 -> PermissionError 발생 예상
        ("10.0.0.1", "user_abc", "ADMIN", 1, False),
        # Case 3: Rate Limit 실패 (가정) -> TimeoutError 발생 예상
        ("192.168.1.50", "user_abc", "PREMIUM_USER", 101, False),
        # Case 4: 권한 부족 실패 -> PermissionError 발생 예상
        ("192.168.1.50", "user_abc", "BASIC_USER", 1, False),
    ]
)
def test_get_user_profile_flow(ip, user_id, permission, count, expected_status):
    """다양한 시나리오를 통해 전체 게이트웨이 흐름을 검증한다."""
    try:
        result = get_user_profile(ip, user_id, permission, count)
        # 성공적으로 실행되었다면 결과가 딕셔너리여야 하고, Expected Status도 True여야 함.
        assert isinstance(result, dict) and result["status"] == "success" and expected_status == True
    except (PermissionError, TimeoutError) as e:
        # 예외가 발생했다면, 실패한 게이트에 따른 적절한 에러 메시지를 포함해야 하고, Expected Status도 False여야 함.
        if expected_status == False:
            assert "ACCESS DENIED" in str(e) or "RATE LIMITED" in str(e)
        else:
             pytest.fail(f"Expected success but got unexpected error: {e}")