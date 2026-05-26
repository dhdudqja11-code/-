# -*- coding: utf-8 -*-
import os
import pytest
from fastapi.testclient import TestClient

# 로컬 main 모듈 임포트 (이름 충돌 방지를 위해 절대 패키지 명시)
try:
    from core_gateway.main import app, limiter
except ImportError:
    try:
        from main import app, limiter
    except ImportError:
        from .main import app, limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """각 테스트 실행 전 SlowAPI 속도 제한 내부 상태를 리셋하여 간섭을 예방합니다."""
    limiter.reset()
    yield

# ------------------- [1. API Key 환경 변수 및 폴백 검증] ------------------- #

def test_gatekeeper_auth_default_fallback_success():
    """✨ 디폴트 폴백 검증: 환경 변수가 없을 때 'SUPER_SECRET_HARDCODED_KEY'로 정상 승인되는지 검증"""
    if "GATEWAY_API_KEY" in os.environ:
        del os.environ["GATEWAY_API_KEY"]

    response = client.post(
        "/api/v1/check-connection",
        params={"api_key": "SUPER_SECRET_HARDCODED_KEY", "user_id": "admin_user"},
        json={"requested_scope": "WRITE_CONFIG", "target_server": "core-backup-db"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_authorized"] is True
    assert "core-backup-db" in data["message"]

def test_gatekeeper_auth_custom_env_key_success():
    """✨ 환경 변수 검증: 커스텀 환경 변수 키 등록 시 해당 값으로 정상 승인되는지 단언"""
    os.environ["GATEWAY_API_KEY"] = "MY_HIGH_SECURITY_TEMP_KEY"
    
    try:
        response = client.post(
            "/api/v1/check-connection",
            params={"api_key": "MY_HIGH_SECURITY_TEMP_KEY", "user_id": "admin_user"},
            json={"requested_scope": "WRITE_CONFIG", "target_server": "core-backup-db"}
        )
        assert response.status_code == 200
        assert response.json()["is_authorized"] is True
    finally:
        # 다른 테스트 영향 방지를 위한 원상복구
        del os.environ["GATEWAY_API_KEY"]

def test_gatekeeper_auth_unauthorized_key_failure():
    """🛡️ 인증 오류 검증: 올바르지 않은 API Key 주입 시 401 Unauthorized 차단을 단언"""
    os.environ["GATEWAY_API_KEY"] = "SECURE_KEY_123"
    
    try:
        response = client.post(
            "/api/v1/check-connection",
            params={"api_key": "WRONG_KEY_ABC", "user_id": "admin_user"},
            json={"requested_scope": "WRITE_CONFIG", "target_server": "core-backup-db"}
        )
        assert response.status_code == 401
        assert "Invalid API Key" in response.json()["detail"]
    finally:
        del os.environ["GATEWAY_API_KEY"]

# ------------------- [2. 글로벌 SlowAPI Rate Limiting 429 검증] ------------------- #

def test_gatekeeper_rate_limit_blocking():
    """🚨 속도 제한 검증: 연속 11회 이상 빠른 속도로 접속 요청 시 429 Too Many Requests가 트리거되는지 단언"""
    payload = {"requested_scope": "WRITE_CONFIG", "target_server": "core-backup-db"}
    params = {"api_key": "SUPER_SECRET_HARDCODED_KEY", "user_id": "admin_user"}

    # 분당 10회 한도이므로, 10회까지는 200 OK 성공을 기대
    for i in range(10):
        response = client.post("/api/v1/check-connection", params=params, json=payload)
        assert response.status_code == 200

    # 11회차 기동 시 SlowAPI에 의해 블로킹되어 429 Too Many Requests 응답 반환을 기대
    blocked_response = client.post("/api/v1/check-connection", params=params, json=payload)
    assert blocked_response.status_code == 429
    assert "Rate limit exceeded" in blocked_response.text
