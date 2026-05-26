# -*- coding: utf-8 -*-
import pytest
import os
import sys
import unittest.mock as mock

# 봇 도구 폴더를 sys.path에 추가하여 직접 임포트합니다.
HERE = os.path.dirname(os.path.abspath(__file__))
YOUTUBE_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "youtube", "tools"))
if YOUTUBE_TOOLS not in sys.path:
    sys.path.append(YOUTUBE_TOOLS)

import telegram_bot

@pytest.fixture(autouse=True)
def clean_bot_state():
    """매 테스트 케이스 실행 전에 봇의 전역 연동 상태값을 깔끔하게 초기화합니다."""
    telegram_bot.API_TOKEN = None
    telegram_bot.MFA_VERIFIED = False
    telegram_bot.PENDING_SECURE_CMD = None
    yield

def test_telegram_bot_api_login_success():
    """[텔레그램 봇 - API 로그인] admin 자격으로 API 게이트웨이에 로그인하여 임시 토큰을 정상 발급받는지 확인합니다."""
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "valid_token_bot_test_123"}
    
    with mock.patch("requests.post", return_value=mock_resp) as mock_post:
        success = telegram_bot._api_login("fake_bot_token", "fake_chat_id")
        
        assert success is True
        assert telegram_bot.API_TOKEN == "valid_token_bot_test_123"
        assert telegram_bot.MFA_VERIFIED is False
        mock_post.assert_called_once()
        # 헤더에 X-MFA-Test 헤더가 올바르게 주입되어 나갔는지 확인
        called_headers = mock_post.call_args[1]["headers"]
        assert called_headers["X-MFA-Test"] == "true"

def test_telegram_bot_api_verify_otp_success():
    """[텔레그램 봇 - OTP 2차 검증] 발급된 임시 토큰과 OTP 코드를 싣고 API 서버에 제출하여 인증 승격에 성공하는지 검증합니다."""
    telegram_bot.API_TOKEN = "valid_token_bot_test_123"
    
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"success": True}
    
    with mock.patch("requests.post", return_value=mock_resp) as mock_post:
        success = telegram_bot._api_verify_otp("fake_bot_token", "fake_chat_id", "999888")
        
        assert success is True
        assert telegram_bot.MFA_VERIFIED is True
        mock_post.assert_called_once()
        # Bearer 토큰이 정상 바인딩되었는지 검증
        called_headers = mock_post.call_args[1]["headers"]
        assert "Bearer valid_token_bot_test_123" in called_headers["Authorization"]

def test_telegram_bot_secure_command_interception_mfa_required():
    """[텔레그램 봇 - 보안 차단] 인증되지 않은 상태에서 /kill 등을 입력 시, 보류 명령어로 적재하고 OTP를 요구하는지 검증합니다."""
    # 모킹
    mock_resp_login = mock.MagicMock()
    mock_resp_login.status_code = 200
    mock_resp_login.json.return_value = {"access_token": "valid_token_bot_test_123"}
    
    with mock.patch("requests.post", return_value=mock_resp_login) as mock_post, \
         mock.patch("telegram_bot.send_message") as mock_send:
         
        telegram_bot.handle_command("/kill sess_attack_111", "fake_token", "fake_chat_id")
        
        # 보류 명령어에 올바르게 적재되었는지 검증
        assert telegram_bot.PENDING_SECURE_CMD is not None
        assert telegram_bot.PENDING_SECURE_CMD["cmd_type"] == "kill"
        assert telegram_bot.PENDING_SECURE_CMD["args"] == ["sess_attack_111"]
        
        # 임시 로그인이 유발되었는지 검증
        mock_post.assert_called_once()
        
        # 사장님께 OTP 요청 메시지가 전달되었는지 검증
        mock_send.assert_called_once()
        sent_text = mock_send.call_args[0][2]
        assert "MFA 2차 인증 요구" in sent_text

def test_telegram_bot_verify_otp_and_execute_pending_command_success():
    """
    [텔레그램 봇 - OTP 연쇄 실행 성공 흐름]
    1. /kill 명령이 인증 미달로 보류 상태로 대기합니다.
    2. 사장님이 OTP 번호 6자리("123456")를 전송합니다.
    3. 봇은 OTP 검증 성공 즉시 세션을 활성화하고, 보류 중이던 킬 스위치를 API 서버에 쏘아 폭파시킵니다.
    """
    # 초기 보류 명령 적재
    telegram_bot.API_TOKEN = "valid_token_bot_test_123"
    telegram_bot.MFA_VERIFIED = False
    telegram_bot.PENDING_SECURE_CMD = {"cmd_type": "kill", "args": ["sess_attack_111"]}
    
    # OTP 검증 성공 응답 + 세션 폭파 성공 응답 연이어 모킹
    mock_resp_verify = mock.MagicMock()
    mock_resp_verify.status_code = 200
    mock_resp_verify.json.return_value = {"success": True}
    
    mock_resp_kill = mock.MagicMock()
    mock_resp_kill.status_code = 200
    mock_resp_kill.json.return_value = {"success": True, "message": "세션 sess_attack_111이 즉시 폭파되었습니다."}
    
    def side_effect_post(url, *args, **kwargs):
        if "/auth/mfa/verify" in url:
            return mock_resp_verify
        elif "/security/kill" in url:
            return mock_resp_kill
        return mock.MagicMock(status_code=404)
        
    with mock.patch("requests.post", side_effect=side_effect_post) as mock_post, \
         mock.patch("telegram_bot.send_message") as mock_send:
         
        # 사장님이 OTP 전송
        telegram_bot.handle_command("123456", "fake_token", "fake_chat_id")
        
        # MFA 활성화 완료 검증
        assert telegram_bot.MFA_VERIFIED is True
        assert telegram_bot.PENDING_SECURE_CMD is None # 소모 완료되어야 함
        
        # /auth/mfa/verify 와 /security/kill 이 연달아 정상 호출되었는지 확인
        assert mock_post.call_count == 2
        
        # 최종적으로 원격 킬 스위치 성공 안내 메시지가 사장님께 가갔는지 검증
        called_messages = [call[0][2] for call in mock_send.call_args_list]
        assert any("MFA 인증 성공" in m for m in called_messages)
        assert any("원격 킬 스위치 완료" in m for m in called_messages)

def test_telegram_bot_mitigate_action_trigger_success():
    """[텔레그램 봇 - 위험 완화 원격 제어] 이미 MFA가 검증 통과된 상태에서 /mitigate 를 내렸을 때 X-2FA 헤더와 함께 올바르게 트리거하는지 검증합니다."""
    telegram_bot.API_TOKEN = "valid_token_bot_test_123"
    telegram_bot.MFA_VERIFIED = True
    
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "SUCCESS",
        "transaction_id": "TXN-MOCK-777",
        "message": "위험 완화 조치 성공"
    }
    
    with mock.patch("requests.post", return_value=mock_resp) as mock_post, \
         mock.patch("telegram_bot.send_message") as mock_send:
         
        # 완화 조치 명령
        telegram_bot.handle_command("/mitigate RESTART db_primary", "fake_token", "fake_chat_id")
        
        mock_post.assert_called_once()
        called_headers = mock_post.call_args[1]["headers"]
        # 이중 인증 승인 헤더 확인
        assert called_headers["X-2FA-Authenticated"] == "true"
        
        # 사장님께 조치 성공 보고 메시지가 갔는지 확인
        mock_send.assert_called_once()
        sent_text = mock_send.call_args[0][2]
        assert "위험 완화 조치 트리거 완료" in sent_text
        assert "TXN-MOCK-777" in sent_text

def test_telegram_bot_simulate_risk_sandbox_success():
    """[텔레그램 봇 - 위험 시뮬레이션] 이미 MFA가 통과된 상태에서 /simulate 를 내렸을 때 올바르게 샌드박스 결과를 요약 회신하는지 검증합니다."""
    telegram_bot.API_TOKEN = "valid_token_bot_test_123"
    telegram_bot.MFA_VERIFIED = True
    
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "SIMULATION_REPORT",
        "context": "hipaa_medical",
        "risk_level": "CRITICAL",
        "potential_loss_usd": 250000.0,
        "violation_details": ["HIPAA Rule 위반"],
        "mitigation_steps": ["익명화 암호화 처리 필수"],
        "transparency_report": {"formula": "potential_loss = base_loss * regulatory_weight"}
    }
    
    with mock.patch("requests.get", return_value=mock_resp) as mock_get, \
         mock.patch("telegram_bot.send_message") as mock_send:
         
        # 시뮬레이션 명령
        telegram_bot.handle_command("/simulate hipaa_medical backup_export", "fake_token", "fake_chat_id")
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        # GET 파라미터 확인
        assert "target_context=hipaa_medical" in called_url
        assert "hypothetical_action=backup_export" in called_url
        
        # 샌드박스 위험 분석 보고서 요약본 전송 확인
        mock_send.assert_called_once()
        sent_text = mock_send.call_args[0][2]
        assert "격리 Sandbox 위험 시뮬레이션 결과" in sent_text
        assert "CRITICAL" in sent_text
        assert "$250,000.00" in sent_text
