# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 로컬 모듈 임포트
try:
    from main_api import app
    from auth_service import create_access_token
except ImportError:
    from .main_api import app
    from .auth_service import create_access_token

client = TestClient(app)

# ------------------- [1. 테스트 Helper 함수] ------------------- #
def get_auth_headers(user_id: str, roles: list, active: bool = True) -> dict:
    """테스트 전용 JWT 토큰 헤더 생성 (active 클레임을 동적으로 주입)"""
    token_payload = {
        "sub": user_id,
        "roles": roles,
        "active": active
    }
    token = create_access_token(token_payload)
    return {"Authorization": f"Bearer {token}"}

# ------------------- [2. Dashboard 테스트 스위트] ------------------- #

def test_dashboard_stats_endpoint():
    """✨ 대시보드 종합 지표 조회 API (/api/v1/dashboard/stats) 성공 검증"""
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "success_blocks" in data
    assert "failure_blocks" in data
    assert "total_campaigns" in data
    assert "cumulative_views" in data
    assert "planner_suspended" in data

def test_dashboard_audit_logs_endpoint():
    """✨ 대시보드 실시간 감사 로그 체인 API (/api/v1/dashboard/audit_logs) 성공 검증"""
    response = client.get("/api/v1/dashboard/audit_logs")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)

def test_dashboard_campaigns_endpoint():
    """✨ 대시보드 캠페인 이력 API (/api/v1/dashboard/campaigns) 성공 검증"""
    response = client.get("/api/v1/dashboard/campaigns")
    assert response.status_code == 200
    campaigns = response.json()
    assert isinstance(campaigns, list)

def test_dashboard_login_success():
    """✨ 대시보드 로그인 성공 및 임시 Bearer 토큰(active=False) 발급 검증"""
    credentials = {"username": "admin", "password": "admin_pass"}
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_dashboard_login_bad_credentials():
    """🛡️ 틀린 자격 증명 제출 시 401 Unauthorized 오류 검증"""
    credentials = {"username": "admin", "password": "wrong_password"}
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 401

def test_dashboard_mfa_verify_success():
    """✨ 구글 OTP 실시간 2FA 검증 및 액티브 세션 토큰 승격(active=True) 검증"""
    # 1. 2FA Secret에 일치하는 올바른 OTP 코드를 생성하도록 TOTPService 모킹
    with patch("main_api.TOTPService.verify_totp_code", return_value=True):
        headers = get_auth_headers(user_id="USER_admin", roles=["ROLE_ADMIN"], active=False)
        payload = {"otp_code": "123456"}
        response = client.post("/auth/mfa/verify", headers=headers, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert "성공" in data["message"]

def test_dashboard_mfa_verify_bad_otp():
    """🛡️ 잘못된 OTP 제출 시 403 Forbidden 및 승격 차단 거부 검증"""
    with patch("main_api.TOTPService.verify_totp_code", return_value=False):
        headers = get_auth_headers(user_id="USER_admin", roles=["ROLE_ADMIN"], active=False)
        payload = {"otp_code": "000000"}
        response = client.post("/auth/mfa/verify", headers=headers, json=payload)
        
        assert response.status_code == 403
        assert "failed" in response.json()["detail"]

def test_trigger_campaign_mfa_gated_blocked():
    """🛡️ MFA 2차인증을 마치지 않은 토큰(active=False)으로 수동 캠페인 실행 요청 시 403 차단 검증"""
    headers = get_auth_headers(user_id="USER_admin", roles=["ROLE_ADMIN"], active=False)
    response = client.post("/api/v1/dashboard/trigger_campaign", headers=headers)
    assert response.status_code == 403
    assert "MFA" in response.json()["detail"]

def test_trigger_campaign_success():
    """✨ MFA 2차인증이 완료된 토큰(active=True)으로 캠페인 정상 가동 및 Subprocess 호출 검증"""
    headers = get_auth_headers(user_id="USER_admin", roles=["ROLE_ADMIN"], active=True)
    
    # subprocess.run 모킹하여 1인 기업 오케스트레이터의 가상 출력을 단언 검증
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        mock_proc.stdout = '{\n  "timestamp": "20260526_2330",\n  "elapsed_seconds": 11.2\n}'
        mock_run.return_value = mock_proc
        
        response = client.post("/api/v1/dashboard/trigger_campaign", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["timestamp"] == "20260526_2330"
        assert mock_run.called
