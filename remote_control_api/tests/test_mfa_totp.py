# -*- coding: utf-8 -*-
import pytest
import time
import base64
from fastapi.testclient import TestClient
from main import app, session_manager, security_service
from services.totp_service import TOTPService

client = TestClient(app)

ADMIN_SECRET = "JBSWY3DPEHPK3PXP" # USER_admin base32 secret

@pytest.fixture(autouse=True)
def clean_security_state():
    """매 테스트 케이스 실행 전에 보안 서비스 및 세션 상태를 공정하게 초기화합니다."""
    security_service._blacklisted_ips.clear()
    security_service._failed_login_attempts.clear()
    security_service.pending_alerts.clear()
    session_manager._active_sessions.clear()
    yield

def test_totp_generation_and_verification():
    """[MFA TOTP 기본 검증] 실시간 생성한 TOTP 코드가 verify 메서드를 통해 완벽하게 검증(True)되는지 확인합니다."""
    # 1. 실시간 TOTP 코드 생성
    code = TOTPService.generate_totp_code(ADMIN_SECRET)
    assert len(code) == 6
    assert code.isdigit()
    
    # 2. 검증 수행 (성공해야 함)
    assert TOTPService.verify_totp_code(ADMIN_SECRET, code) is True

def test_totp_verification_invalid_codes():
    """[MFA TOTP 오류 방어] 유효하지 않은 코드(자릿수 오류, 오타 등) 제출 시 검증 거부(False) 처리되는지 확인합니다."""
    assert TOTPService.verify_totp_code(ADMIN_SECRET, "12345") is False
    assert TOTPService.verify_totp_code(ADMIN_SECRET, "1234567") is False
    assert TOTPService.verify_totp_code(ADMIN_SECRET, "abc123") is False
    assert TOTPService.verify_totp_code(ADMIN_SECRET, "999999") is False

def test_totp_verification_window_lag_tolerance():
    """[MFA TOTP 오차 허용] window=1 규격에 의해 +-30초 전후의 타임스텝 코드도 안전하게 매칭 통과되는지 확인합니다."""
    current_time = int(time.time())
    
    # 이전 타임스텝(30초 전)의 카운터 수동 코드 생성
    prev_time = current_time - 30
    import struct, hmac, hashlib
    prev_counter = int(prev_time / 30)
    key = base64.b32decode(ADMIN_SECRET)
    msg = struct.pack(">Q", prev_counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_bytes = digest[offset:offset + 4]
    code_int = struct.unpack(">I", code_bytes)[0] & 0x7FFFFFFF
    prev_otp = f"{code_int % 1_000_000:06d}"
    
    # window=1 설정 시, 30초 전의 코드도 통과되어야 함
    assert TOTPService.verify_totp_code(ADMIN_SECRET, prev_otp, window=1) is True

def test_mfa_verification_e2e_flow():
    """
    [MFA 2차 인증 E2E 해피 패스]
    1. 로그인 성공 직후 세션은 mfa_verified=False 상태이며, 보호 자원 접근 시 403 Forbidden 차단됩니다.
    2. 생성한 실시간 TOTP 코드를 /auth/mfa/verify 로 제출하여 세션을 활성화합니다.
    3. 세션이 활성화된 후, 동일한 토큰으로 보호 자원에 정상적으로 성공 접근(200 OK)합니다.
    """
    # 1. 로그인 수행
    login_payload = {
        "username": "admin",
        "password": "admin_pass"
    }
    login_headers = {
        "X-Forwarded-For": "127.0.0.1",
        "X-MFA-Test": "true"
    }
    
    login_resp = client.post("/auth/login", json=login_payload, headers=login_headers)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # 세션 상태 검사 (MFA_VERIFIED = False)
    active_sessions = list(session_manager._active_sessions.values())
    assert len(active_sessions) == 1
    assert active_sessions[0]["mfa_verified"] is False
    
    # 2. MFA 미인증 상태에서 보호 리소스 호출 시 차단 (403 Forbidden)
    auth_headers = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": "127.0.0.1"
    }
    blocked_resp = client.get("/api/v1/data/confidential_db", headers=auth_headers)
    assert blocked_resp.status_code == 403
    assert "MFA" in blocked_resp.json()["detail"]

    # 3. 실시간 TOTP 번호 생성
    realtime_code = TOTPService.generate_totp_code(ADMIN_SECRET)
    
    # 4. MFA 인증 제출 (성공)
    verify_resp = client.post(
        "/auth/mfa/verify",
        json={"otp_code": realtime_code},
        headers=auth_headers
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["success"] is True
    
    # 세션 갱신 확인 (MFA_VERIFIED = True)
    assert list(session_manager._active_sessions.values())[0]["mfa_verified"] is True
    
    # 5. 활성화된 세션 토큰으로 보호 리소스 재호출 시 성공 (200 OK)
    success_resp = client.get("/api/v1/data/confidential_db", headers=auth_headers)
    assert success_resp.status_code == 200
    assert success_resp.json()["status"] == "success"

def test_mfa_verification_e2e_invalid_otp():
    """
    [MFA 2차 인증 E2E 예외 경로]
    틀린 6자리 OTP 코드를 제출하면 /auth/mfa/verify 에서 403 Forbidden 에러가 나며,
    세션은 계속 비활성(False) 상태로 차단 유지됨을 확인합니다.
    """
    # 1. 로그인
    login_payload = {"username": "admin", "password": "admin_pass"}
    login_headers = {
        "X-MFA-Test": "true"
    }
    login_resp = client.post("/auth/login", json=login_payload, headers=login_headers)
    token = login_resp.json()["access_token"]
    
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 틀린 OTP 인증 제출 (실패 -> 403)
    verify_resp = client.post(
        "/auth/mfa/verify",
        json={"otp_code": "000000"},
        headers=auth_headers
    )
    assert verify_resp.status_code == 403
    assert "failed" in verify_resp.json()["detail"].lower()
    
    # 세션 비활성 유지 확인
    assert list(session_manager._active_sessions.values())[0]["mfa_verified"] is False
    
    # 3. 여전히 보호 자원 차단됨 확인 (403)
    blocked_resp = client.get("/api/v1/data/confidential_db", headers=auth_headers)
    assert blocked_resp.status_code == 403
