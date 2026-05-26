# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from main import app, security_service, session_manager, auth_service

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """정상적으로 발급된 JWT 토큰을 획득하고 인증 헤더를 모킹해 리턴합니다."""
    # 세션 강제 생성
    token = auth_service.create_access_token(data={"sub": "USER_admin"})
    session_manager.create_session("USER_admin", token, duration_minutes=30, ip_address="127.0.0.1")
    return {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": "127.0.0.1"
    }

def test_validate_report_success(auth_headers):
    """[보고서 검증 성공] 유효한 ID 및 사유 기입 시 200 OK와 GDPR 증명 리턴."""
    response = client.get(
        "/api/v1/reports/validate/REPORT_GDPR_2026",
        params={"reason_for_access": "재무적 위험 완화 및 데이터 오용 감사", "start_date": "2026-05-01"},
        headers=auth_headers
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "SUCCESS"
    assert res_data["compliance_score"] == 98.5
    assert len(res_data["data_payload"]) == 1
    assert res_data["data_payload"][0]["source"] == "secure_internal"

def test_validate_report_failure_expired(auth_headers):
    """[보고서 검증 실패] 만료/비활성화된 보고서(EXPIRED) 접근 시 403 에러와 3단계(문제->원인->해결) 제안 리턴."""
    response = client.get(
        "/api/v1/reports/validate/EXPIRED_GDPR_REPORT",
        params={"reason_for_access": "법적 규제 리스크 검증"},
        headers=auth_headers
    )
    assert response.status_code == 403
    res_data = response.json()
    assert res_data["status"] == "COMPLIANCE_FAILURE"
    assert "문제 정의" in res_data["message"]
    assert "해결책 제시" in res_data["mitigation_suggestion"]

def test_validate_report_failure_missing_reason(auth_headers):
    """[보고서 검증 실패] 접근 사유(reason_for_access) 누락 시 400 Bad Request 리턴."""
    # reason_for_access 누락
    response = client.get(
        "/api/v1/reports/validate/REPORT_GDPR_2026",
        headers=auth_headers
    )
    assert response.status_code >= 400

def test_trigger_mitigation_success(auth_headers):
    """[위험 완화 성공] 이중 인증(2FA 헤더) 완비 시 200 OK와 트랜잭션 ID 즉시 반환 (비동기 처리)."""
    headers = auth_headers.copy()
    headers["X-2FA-Authenticated"] = "true"
    
    payload = {
        "action_type": "권한 오용 차단",
        "target_resource_id": "RES_CORE_DB_09",
        "mitigation_details": {"action": "revoke_role", "role": "unauthorized_guest"}
    }
    
    response = client.post(
        "/api/v1/actions/trigger_mitigation",
        json=payload,
        headers=headers
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "SUCCESS"
    assert res_data["transaction_id"].startswith("TXN-")
    assert "successfully" in res_data["message"] or "성공적으로" in res_data["message"]

def test_trigger_mitigation_failure_unauthorized(auth_headers):
    """[위험 완화 실패] 2FA 미인증 헤더일 시 이중 승인 미달(401) 및 관리자 승인 제시 리턴."""
    # X-2FA-Authenticated 누락 또는 False
    headers = auth_headers.copy()
    
    payload = {
        "action_type": "데이터 누락 복구",
        "target_resource_id": "RES_CORE_DB_10",
        "mitigation_details": {"action": "restore"}
    }
    
    response = client.post(
        "/api/v1/actions/trigger_mitigation",
        json=payload,
        headers=headers
    )
    assert response.status_code == 401
    res_data = response.json()
    assert res_data["status"] == "FAILURE"
    assert "Two-Factor Auth" in res_data["message"]
    assert res_data["required_action"] == "관리자 개입 필요"

def test_trigger_mitigation_idempotency(auth_headers):
    """[위험 완화 멱등성] 동일 리소스 중복 트랜잭션 트리거 시 캐싱된 동일 결과 반환 검증."""
    headers = auth_headers.copy()
    headers["X-2FA-Authenticated"] = "true"
    
    payload = {
        "action_type": "데이터 복제 차단",
        "target_resource_id": "RES_CORE_DB_IDEMPOTENT",
        "mitigation_details": {"action": "restrict_copy"}
    }
    
    # 1회차 호출 (성공)
    resp1 = client.post(
        "/api/v1/actions/trigger_mitigation",
        json=payload,
        headers=headers
    )
    assert resp1.status_code == 200
    
    # 2회차 호출 (멱등성 작동)
    resp2 = client.post(
        "/api/v1/actions/trigger_mitigation",
        json=payload,
        headers=headers
    )
    assert resp2.status_code == 200
    res_data2 = resp2.json()
    assert res_data2["transaction_id"] == "TXN-IDEMPOTENT-CACHED"
    assert "멱등성" in res_data2["message"]

def test_simulate_risk_success(auth_headers):
    """[시뮬레이터 성공] Sandbox 기반 리스크 예측 및 가중치 투명성 계산 공식 리턴 검증."""
    response = client.get(
        "/api/v1/user/simulate_risk",
        params={"target_context": "HIPAA Medical Records", "hypothetical_action": "third_party_transfer"},
        headers=auth_headers
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "SIMULATION_REPORT"
    assert res_data["risk_level"] == "CRITICAL"
    assert res_data["potential_loss_usd"] == 250000.0
    assert "formula" in res_data["transparency_report"]
    assert res_data["transparency_report"]["weights"]["regulatory_weight"] == 5.0

def test_simulate_risk_failure_xss_protection(auth_headers):
    """[시뮬레이터 실패] XSS/SQL Injection 해킹 문자 삽입 시 즉각적 400 Bad Request 차단 검증."""
    response = client.get(
        "/api/v1/user/simulate_risk",
        params={"target_context": "<script>alert(1)</script>", "hypothetical_action": "malicious_exploit"},
        headers=auth_headers
    )
    assert response.status_code == 400
    res_data = response.json()
    assert res_data["status"] == "ERROR"
    assert "위협 패턴" in res_data["message"]

def test_simulate_risk_failure_missing_params(auth_headers):
    """[시뮬레이터 실패] 파라미터 누락 시 500 Internal Error 시뮬레이션 리턴 검증."""
    response = client.get(
        "/api/v1/user/simulate_risk",
        headers=auth_headers
    )
    assert response.status_code == 500
    res_data = response.json()
    assert res_data["status"] == "ERROR"
