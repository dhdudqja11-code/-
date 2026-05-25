# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from main import app, security_service, session_manager, auth_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_security_state():
    """매 테스트 케이스 실행 전에 보안 서비스 및 세션 상태를 공정하게 초기화합니다."""
    security_service._blacklisted_ips.clear()
    security_service._failed_login_attempts.clear()
    security_service.pending_alerts.clear()
    session_manager._active_sessions.clear()
    yield

def test_unauthorized_ip_whitelist_blocking():
    """
    [Guardrail 1] 허용되지 않은 외부 IP(예: 203.0.113.8)가 보안 엔드포인트에 
    접속을 시도할 시, 즉각 차단(403) 및 텔레그램 보안 알람 큐 적재를 검증합니다.
    """
    headers = {
        "Authorization": "Bearer dummy_token",
        "X-Forwarded-For": "203.0.113.8"
    }
    response = client.get(
        "/api/v1/data/system_status",
        headers=headers
    )
    
    assert response.status_code == 403
    assert "Unauthorized" in response.json()["detail"]
    
    # 보안 알림이 큐에 쌓였는지 검사
    alerts = security_service.pending_alerts
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "UNAUTHORIZED_IP_ACCESS"
    assert "203.0.113.8" in alerts[0]["details"]


def test_login_failure_threshold_alerts():
    """
    [NFR-3] 연속 3회 로그인 틀린 비밀번호 입력 시, 로그인 실패 카운터가 동작하고
    3회 도달 즉시 텔레그램 경고 알림(LOGIN_FAILURES_EXCEEDED)이 트리거되는지 검증합니다.
    """
    login_data = {
        "username": "admin",
        "password": "wrong_password"
    }
    headers = {
        "X-Forwarded-For": "192.168.1.50"
    }
    
    # 1회 실패
    resp1 = client.post("/auth/login", json=login_data, headers=headers)
    assert resp1.status_code == 401
    assert len(security_service.pending_alerts) == 0
    
    # 2회 실패
    resp2 = client.post("/auth/login", json=login_data, headers=headers)
    assert resp2.status_code == 401
    assert len(security_service.pending_alerts) == 0
    
    # 3회 실패 -> 임계치 도달 및 경고 트리거
    resp3 = client.post("/auth/login", json=login_data, headers=headers)
    assert resp3.status_code == 401
    
    # 알림 큐 검사
    alerts = security_service.pending_alerts
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "LOGIN_FAILURES_EXCEEDED"
    assert "192.168.1.50" in alerts[0]["details"]


def test_active_session_kill_switch_e2e():
    """
    [원격 킬 스위치 & 이중 체크 E2E]
    1. 정상 접속한 세션의 토큰으로 보호 자원에 성공 접근(200)합니다.
    2. 킬 스위치 API를 통해 해당 세션을 즉시 폭파하고 접속 IP를 블랙리스트에 올립니다.
    3. 무효화된 토큰으로 다른 클린 IP에서 재접근할 시 이중 체크 가드에 의해 즉각 401 Unauthorized 처리됩니다.
    4. 블랙리스트에 등재된 IP이므로 해당 IP로 접근 시 403 Forbidden으로 완전 봉쇄됩니다.
    """
    # 1. 로그인 수행 (성공)
    login_data = {
        "username": "admin",
        "password": "admin_pass"
    }
    client_ip = "192.168.1.10"
    headers = {
        "X-Forwarded-For": client_ip
    }
    
    login_resp = client.post("/auth/login", json=login_data, headers=headers)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # 세션 매니저에서 방금 등록된 활성 세션 ID 가져오기
    active_sessions = session_manager._active_sessions
    assert len(active_sessions) == 1
    session_id = list(active_sessions.keys())[0]
    
    # 2. 토큰을 이용해 보호 리소스 성공적인 접근 검증 (200 OK)
    auth_headers = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": client_ip
    }
    data_resp = client.get(
        "/api/v1/data/confidential_db",
        headers=auth_headers
    )
    assert data_resp.status_code == 200
    assert data_resp.json()["status"] == "success"
    
    # 3. 🚨 사장님의 원격 킬 스위치 가동 (세션 폭파 및 IP 블랙리스트 등재)
    kill_resp = client.post(
        "/api/v1/security/kill",
        json={"session_id": session_id}
    )
    assert kill_resp.status_code == 200
    assert kill_resp.json()["success"] is True
    
    # 4. 동일한 토큰으로 다른 (허용된) IP에서 재접근 시 차단 검증 (이중 체크 작동 -> 401 Unauthorized)
    auth_headers_other_ip = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": "192.168.1.11" # 차단되지 않은 허용된 다른 사내 IP
    }
    data_resp2 = client.get(
        "/api/v1/data/confidential_db",
        headers=auth_headers_other_ip
    )
    # 토큰 자체 해독은 되나 활성 세션 풀 매칭에 실패하므로 401 반환
    assert data_resp2.status_code == 401
    
    # 5. 블랙리스트 IP 차단 검증 (403 Forbidden)
    # 원래 차단된 IP로 요청을 날리면 세션 상태와 무관하게 IP 차단에 의해 403 반환
    data_resp_blacklisted = client.get(
        "/api/v1/data/confidential_db",
        headers=auth_headers
    )
    assert data_resp_blacklisted.status_code == 403
    assert "blacklisted" in data_resp_blacklisted.json()["detail"].lower()
