# -*- coding: utf-8 -*-
import pytest
import requests
import requests_mock
from src.modules.connectivity.connection_module import (
    establish_secure_connection,
    ConnectionModule,
    AuthenticationFailed,
    MfaRequiredError,
    QuotaExceededError,
    ConnectionError
)

# --- 🧪 pytest & requests-mock 기반의 자급자족형 통합 테스트 ---

BASE_URL = "http://127.0.0.1:8000"

def test_successful_secure_connection():
    """[성공 경로] 올바른 로그인 정보로 토큰을 획득하고, 보호 리소스 데이터까지 정상적으로 조회하는 흐름."""
    with requests_mock.Mocker() as m:
        # 1. 로그인 API 모킹
        m.post(
            f"{BASE_URL}/auth/login", 
            json={"access_token": "mocked_jwt_token_admin", "token_type": "bearer"}, 
            status_code=200
        )
        # 2. 보호 리소스 조회 API 모킹
        m.get(
            f"{BASE_URL}/api/v1/data/system_status",
            json={
                "status": "success",
                "message": "Data retrieved successfully.",
                "data": {"cpu": "22%", "memory": "48%"}
            },
            status_code=200
        )
        
        # 실행 및 검증
        result = establish_secure_connection("admin", "correct_password", "system_status", BASE_URL)
        
        assert result["status"] == "success"
        assert result["data"]["cpu"] == "22%"
        assert m.called
        assert m.call_count == 2
        # 요청 헤더에 Authorization Bearer 토큰이 올바르게 주입되었는지 확인
        assert m.request_history[1].headers["Authorization"] == "Bearer mocked_jwt_token_admin"


def test_failure_authentication_login():
    """[실패 경로 1] 로그인 자격 증명이 틀려 401 Unauthorized 에러를 리턴할 때, AuthenticationFailed 예외 검증."""
    with requests_mock.Mocker() as m:
        # 로그인 실패 모킹
        m.post(
            f"{BASE_URL}/auth/login", 
            json={"detail": "Invalid username or password."}, 
            status_code=401
        )
        
        # 실행 및 예외 확인
        with pytest.raises(AuthenticationFailed) as excinfo:
            establish_secure_connection("baduser", "wrong_pass", "system_status", BASE_URL)
            
        assert "유효하지 않습니다" in str(excinfo.value)
        assert m.called
        assert m.call_count == 1 # 로그인에서 실패했으므로 데이터 호출은 수행하지 않아야 함 (Guardrail)


def test_failure_mfa_required():
    """[실패 경로 2] 로그인엔 성공했으나, 리소스 접근 과정에서 MFA 요구로 403 Forbidden을 리턴할 때, MfaRequiredError 예외 검증."""
    with requests_mock.Mocker() as m:
        # 로그인 성공
        m.post(
            f"{BASE_URL}/auth/login", 
            json={"access_token": "valid_token_but_mfa_needed"}, 
            status_code=200
        )
        # MFA 미통과로 403 Forbidden 리턴 모킹
        m.get(
            f"{BASE_URL}/api/v1/data/sensitive_db", 
            json={"detail": "MFA required or failed."}, 
            status_code=403
        )
        
        # 실행 및 예외 확인
        with pytest.raises(MfaRequiredError) as excinfo:
            establish_secure_connection("admin", "pass", "sensitive_db", BASE_URL)
            
        assert "MFA" in str(excinfo.value)
        assert m.call_count == 2


def test_failure_quota_exceeded():
    """[실패 경로 3] 접근은 허용되었으나 사용량 제한(Rate Limit / Quota)으로 429 Too Many Requests를 리턴할 때, QuotaExceededError 예외 검증."""
    with requests_mock.Mocker() as m:
        # 로그인 성공
        m.post(
            f"{BASE_URL}/auth/login", 
            json={"access_token": "valid_token_admin"}, 
            status_code=200
        )
        # 쿼터 초과로 429 리턴 모킹
        m.get(
            f"{BASE_URL}/api/v1/data/system_status", 
            json={"detail": "Rate limit exceeded."}, 
            status_code=429
        )
        
        # 실행 및 예외 확인
        with pytest.raises(QuotaExceededError) as excinfo:
            establish_secure_connection("admin", "pass", "system_status", BASE_URL)
            
        assert "사용량 한도를 초과했습니다" in str(excinfo.value)
        assert m.call_count == 2


def test_failure_network_connection_error():
    """[실패 경로 4] 게이트웨이 백엔드 서버가 다운되었거나 네트워크 장애 발생 시, ConnectionError 예외 변환 검증."""
    with requests_mock.Mocker() as m:
        # 네트워크 예외 강제 유도
        m.post(f"{BASE_URL}/auth/login", exc=requests.exceptions.ConnectionError("Connection refused"))
        
        # 실행 및 예외 확인
        with pytest.raises(ConnectionError) as excinfo:
            establish_secure_connection("admin", "pass", "system_status", BASE_URL)
            
        assert "연결 실패" in str(excinfo.value)
        assert m.called