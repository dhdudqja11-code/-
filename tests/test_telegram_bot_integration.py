# -*- coding: utf-8 -*-
import pytest
import os
import sys
import json
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

def test_telegram_bot_audit_mfa_gating():
    """[텔레그램 봇 - /audit MFA 차단] 인증이 미달된 상태에서 /audit 진입 시 로그인 후 OTP 검증을 요구하는지 단언합니다."""
    mock_resp_login = mock.MagicMock()
    mock_resp_login.status_code = 200
    mock_resp_login.json.return_value = {"access_token": "valid_token_bot_test_123"}
    
    with mock.patch("requests.post", return_value=mock_resp_login) as mock_post, \
         mock.patch("telegram_bot.send_message") as mock_send:
         
        telegram_bot.handle_command("/audit", "fake_token", "fake_chat_id")
        
        # 보류 명령어 적재 및 OTP 요구 단언
        assert telegram_bot.PENDING_SECURE_CMD is not None
        assert telegram_bot.PENDING_SECURE_CMD["cmd_type"] == "audit"
        mock_post.assert_called_once()
        mock_send.assert_called_once()
        assert "MFA 2차 인증 요구" in mock_send.call_args[0][2]

def test_telegram_bot_audit_inline_keyboard_rendering():
    """[텔레그램 봇 - /audit 메뉴 노출] MFA 인증 완료 후 /audit 입력 시 인라인 키보드 메뉴가 정상 송신되는지 단언합니다."""
    telegram_bot.API_TOKEN = "valid_token_bot_test_123"
    telegram_bot.MFA_VERIFIED = True
    
    with mock.patch("telegram_bot.send_message") as mock_send:
        telegram_bot.handle_command("/audit", "fake_token", "fake_chat_id")
        
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        assert "IAG 감사 로그 실시간 원격 관제" in args[2]
        assert "reply_markup" in kwargs
        assert "inline_keyboard" in kwargs["reply_markup"]
        
        # 인라인 키보드 구조에 audit_recent 등 콜백 데이터 유효성 단언
        ik = kwargs["reply_markup"]["inline_keyboard"]
        flat_callbacks = [btn["callback_data"] for row in ik for btn in row]
        assert "audit_recent" in flat_callbacks
        assert "audit_fail_today" in flat_callbacks
        assert "audit_success_0" in flat_callbacks
        assert "audit_close" in flat_callbacks

def test_telegram_bot_callback_query_audit_routing():
    """[텔레그램 봇 - CallbackQuery 스캔] 인라인 버튼 터치 콜백 유입 시 봇이 감사 로그를 조회하고 메시지를 실시간 교체하는지 단언합니다."""
    telegram_bot.API_TOKEN = "valid_token_bot_test_123"
    telegram_bot.MFA_VERIFIED = True
    
    mock_audit_records = [
        {
            "status": "SUCCESS",
            "timestamp_utc": "2026-05-26T20:30:00Z",
            "transaction_id": "TX_MOCK_111222",
            "source_api": "/api/v1/simulate_risk",
            "initiator_user_id": "test_user",
            "result_summary": "Risk simulation completed successfully.",
            "message": "None"
        }
    ]
    
    with mock.patch("telegram_bot._query_audit_logs", return_value=mock_audit_records) as mock_query, \
         mock.patch("telegram_bot.answer_callback_query") as mock_answer, \
         mock.patch("telegram_bot.edit_message_text") as mock_edit:
         
        # 콜백 핸들러 직접 가동
        telegram_bot.handle_callback_query("audit_recent", "fake_query_id", 987, "fake_token", "fake_chat_id")
        
        # 콜백 모래시계 소거 단언
        mock_answer.assert_called_once_with("fake_token", "fake_query_id")
        # SQLite 조회 가동 단언
        mock_query.assert_called_once_with("recent")
        # 메시지 교체 단언
        mock_edit.assert_called_once()
        edit_args = mock_edit.call_args[0]
        assert edit_args[1] == "fake_chat_id"
        assert edit_args[2] == 987
        assert "/api/v1/simulate_risk" in edit_args[3]
        assert "TX_MOCK_" in edit_args[3]

def test_telegram_bot_approve_command_success(tmp_path):
    """[텔레그램 봇 - 결재 승인] /approve [short_id] 명령어 수신 시 pending 결재 건을 history로 OK 이동시키는지 단언합니다."""
    # 디렉터리 구성 (HERE = tmp_path/a/b/c)
    dummy_here = os.path.join(tmp_path, "a", "b", "c")
    os.makedirs(dummy_here, exist_ok=True)
    
    pending_dir = os.path.join(tmp_path, "approvals", "pending")
    os.makedirs(pending_dir, exist_ok=True)
    
    # pending json 파일 생성
    pending_json_path = os.path.join(pending_dir, "apr-20260526-test.json")
    pending_data = {
        "id": "apr-20260526-test",
        "agentId": "developer",
        "kind": "deploy",
        "title": "테스트 배포 결재",
        "description": "코드 결재 검증용",
        "createdAt": "2026-05-26T12:00:00.000Z"
    }
    with open(pending_json_path, "w", encoding="utf-8") as f:
        json.dump(pending_data, f, ensure_ascii=False, indent=4)
        
    pending_md_path = os.path.join(pending_dir, "apr-20260526-test.md")
    with open(pending_md_path, "w", encoding="utf-8") as f:
        f.write("# ⏳ 승인 대기")

    # HERE 경로 모킹
    original_here = telegram_bot.HERE
    telegram_bot.HERE = dummy_here
    
    try:
        with mock.patch("telegram_bot.send_message") as mock_send:
            # /approve test 수행 (test는 apr-20260526-test의 suffix로써 매치됨)
            telegram_bot.handle_command("/approve test", "fake_token", "fake_chat_id")
            
            # pending 파일 삭제 단언
            assert not os.path.exists(pending_json_path)
            assert not os.path.exists(pending_md_path)
            
            # history 파일 생성 단언
            history_dir = os.path.join(tmp_path, "approvals", "history")
            hist_files = os.listdir(history_dir)
            
            # _OK_apr-20260526-test.json 형태 파일 존재 확인
            json_hist_file = [f for f in hist_files if "_OK_apr-20260526-test.json" in f]
            md_hist_file = [f for f in hist_files if "_OK_apr-20260526-test.md" in f]
            
            assert len(json_hist_file) == 1
            assert len(md_hist_file) == 1
            
            # 사장님께 승인 완료 피드백 전송 확인
            mock_send.assert_called_once()
            sent_text = mock_send.call_args[0][2]
            assert "결재 처리 완료 - 승인" in sent_text
            assert "테스트 배포 결재" in sent_text
    finally:
        telegram_bot.HERE = original_here

def test_telegram_bot_reject_command_success(tmp_path):
    """[텔레그램 봇 - 결재 반려] /reject [short_id] 명령어 수신 시 pending 결재 건을 history로 NO 이동시키는지 단언합니다."""
    dummy_here = os.path.join(tmp_path, "a", "b", "c")
    os.makedirs(dummy_here, exist_ok=True)
    
    pending_dir = os.path.join(tmp_path, "approvals", "pending")
    os.makedirs(pending_dir, exist_ok=True)
    
    pending_json_path = os.path.join(pending_dir, "apr-20260526-test.json")
    pending_data = {
        "id": "apr-20260526-test",
        "agentId": "developer",
        "kind": "deploy",
        "title": "테스트 배포 결재",
        "description": "코드 결재 검증용",
        "createdAt": "2026-05-26T12:00:00.000Z"
    }
    with open(pending_json_path, "w", encoding="utf-8") as f:
        json.dump(pending_data, f, ensure_ascii=False, indent=4)
        
    pending_md_path = os.path.join(pending_dir, "apr-20260526-test.md")
    with open(pending_md_path, "w", encoding="utf-8") as f:
        f.write("# ⏳ 승인 대기")

    original_here = telegram_bot.HERE
    telegram_bot.HERE = dummy_here
    
    try:
        with mock.patch("telegram_bot.send_message") as mock_send:
            # /reject test 수행
            telegram_bot.handle_command("/reject test", "fake_token", "fake_chat_id")
            
            assert not os.path.exists(pending_json_path)
            assert not os.path.exists(pending_md_path)
            
            history_dir = os.path.join(tmp_path, "approvals", "history")
            hist_files = os.listdir(history_dir)
            
            json_hist_file = [f for f in hist_files if "_NO_apr-20260526-test.json" in f]
            md_hist_file = [f for f in hist_files if "_NO_apr-20260526-test.md" in f]
            
            assert len(json_hist_file) == 1
            assert len(md_hist_file) == 1
            
            mock_send.assert_called_once()
            sent_text = mock_send.call_args[0][2]
            assert "결재 처리 완료 - 반려" in sent_text
            assert "테스트 배포 결재" in sent_text
    finally:
        telegram_bot.HERE = original_here

def test_telegram_bot_campaign_bgm_sending_success():
    """[텔레그램 봇 - 캠페인 완료 BGM 자동 전송] /campaign 명령어 실행 성공 시 완료 리포트 전송 후 시그니처 BGM mp3 파일이 자동 업로드되는지 단언합니다."""
    # mock subprocess.run for campaign orchestrator
    mock_proc = mock.MagicMock()
    mock_proc.returncode = 0
    # orchestrator stdout containing JSON block with timestamp
    mock_proc.stdout = """
    ==================================================
    {
      "timestamp": "20260526_1800",
      "elapsed_seconds": 15.5,
      "steps": {
        "trend_sniper": "Success",
        "naver_writer": "Success",
        "visual_director": "Success",
        "reels_planner": "Success",
        "naver_publish": {"status": "simulated", "url": ""},
        "instagram_publish": {"status": "simulated", "url": ""}
      }
    }
    """
    
    with mock.patch("subprocess.run", return_value=mock_proc), \
         mock.patch("os.path.exists", return_value=True) as mock_exists, \
         mock.patch("telegram_bot.send_message") as mock_send_msg, \
         mock.patch("telegram_bot.send_audio") as mock_send_audio:
         
        telegram_bot.handle_command("/campaign", "fake_token", "fake_chat_id")
        
        # 1. 완료 리포트 발송 단언 (연쇄 기동 중 메시지 + 완료 요약 메시지 = 2번 호출됨)
        assert mock_send_msg.call_count == 2
        called_texts = [call[0][2] for call in mock_send_msg.call_args_list]
        assert any("연쇄 기동 중" in txt for txt in called_texts)
        assert any("AI 1인 기업 일괄 캠페인 병렬 완수" in txt for txt in called_texts)
        assert any("campaign_20260526_1800" in txt for txt in called_texts)
        
        # 2. mp3 스캔 및 텔레그램 업로드 단언
        mock_send_audio.assert_called_once()
        audio_args = mock_send_audio.call_args[0]
        # BGM 파일명 및 캡션 매치 단언
        assert "05_signature_bgm.mp3" in audio_args[2]
        assert "Campaign BGM" in audio_args[3]


def test_telegram_bot_status_dashboard_sending_success():
    """[텔레그램 봇 - 마케팅 대시보드 시각화] 📊 플래너 상태 또는 /metrics 조회 시, 지표 분석 및 시각화 subprocess를 호출하고 미려한 대시보드 이미지를 자동 전송하는지 단언합니다."""
    # mock subprocess.run for metrics tracker and visualizer
    mock_proc = mock.MagicMock()
    mock_proc.returncode = 0
    
    with mock.patch("subprocess.run", return_value=mock_proc) as mock_sub, \
         mock.patch("os.path.exists", return_value=True), \
         mock.patch("telegram_bot.send_message") as mock_send_msg, \
         mock.patch("telegram_bot.send_photo") as mock_send_photo:
         
        telegram_bot.handle_command("📊 플래너 상태", "fake_token", "fake_chat_id")
        
        # 1. 트래커 및 시각화엔진 서브프로세스 2회 실행 단언
        assert mock_sub.call_count == 2
        called_args = [call[0][0] for call in mock_sub.call_args_list]
        assert any("metrics_tracker.py" in str(arg) for arg in called_args)
        assert any("metrics_visualizer.py" in str(arg) for arg in called_args)
        
        # 2. 분석 중 알림 메시지 + 최종 통합 리포트 메시지 발송 단언
        assert mock_send_msg.call_count == 2
        called_texts = [call[0][2] for call in mock_send_msg.call_args_list]
        assert any("정밀 분석하는 중" in txt for txt in called_texts)
        assert any("마케팅 성과 통합 리포트" in txt for txt in called_texts)
        
        # 3. premium 마케팅 대시보드 이미지 업로드 전송 단언
        mock_send_photo.assert_called_once()
        photo_args = mock_send_photo.call_args[0]
        photo_kwargs = mock_send_photo.call_args[1]
        assert "marketing_dashboard.png" in photo_args[2]
        assert "실시간 마케팅 반응 분석 대시보드" in photo_kwargs["caption"]


def test_telegram_bot_monte_carlo_success():
    """[텔레그램 봇 - 몬테카를로 분석] 🎲 몬테카를로 분석 버튼 조회 시 시뮬레이션을 수행하고 통계 텍스트, 이미지 차트, PDF 보고서를 전부 연쇄 전송하는지 단언합니다."""
    # mock simulate_risk_monte_carlo
    mock_stats = {
        "client_id": "TelegramRemote",
        "trials": 20000,
        "critical_threshold": 15000.0,
        "mean_loss": 18240.50,
        "median_loss": 18100.00,
        "std_dev": 2400.00,
        "var_95": 22400.00,
        "var_99": 24100.00,
        "exceed_prob": 88.5
    }
    mock_result = {
        "status": "CRITICAL",
        "stats": mock_stats,
        "pdf_path": "fake_monte_carlo_report.pdf",
        "mitigation_suggestion": "즉각적인 컴플라이언스 감사 및 decisions.md RAG 자율 통제를 조치하십시오."
    }
    
    with mock.patch("mini_roi_simulator.core_api_service.simulate_risk_monte_carlo", return_value=(mock_result, True)) as mock_sim, \
         mock.patch("os.path.exists", return_value=True), \
         mock.patch("telegram_bot.send_message") as mock_send_msg, \
         mock.patch("telegram_bot.send_photo") as mock_send_photo, \
         mock.patch("telegram_bot.send_document") as mock_send_doc:
         
        telegram_bot.handle_command("🎲 몬테카를로 분석", "fake_token", "fake_chat_id")
        
        # 1. 몬테카를로 시뮬레이션 기동 단언
        mock_sim.assert_called_once()
        
        # 2. 메시지 전송 단언 (수행 개시 안내 + 결과 통계 리포트 = 2회)
        assert mock_send_msg.call_count == 2
        called_texts = [call[0][2] for call in mock_send_msg.call_args_list]
        assert any("몬테카를로 분석" in txt for txt in called_texts)
        assert any("평균 예상 손실액: $18,240.50" in txt for txt in called_texts)
        
        # 3. 몬테카를로 분포 차트(PNG) 전송 단언
        mock_send_photo.assert_called_once()
        photo_args = mock_send_photo.call_args[0]
        photo_kwargs = mock_send_photo.call_args[1]
        assert "monte_carlo_distribution.png" in photo_args[2]
        assert "몬테카를로 리스크 확률밀도 분포 차트" in photo_kwargs["caption"]
        
        # 4. 공식 실물 PDF 보고서(Document) 전송 단언
        mock_send_doc.assert_called_once()
        doc_args = mock_send_doc.call_args[0]
        doc_kwargs = mock_send_doc.call_args[1]
        assert "fake_monte_carlo_report.pdf" in doc_args[2]
        assert "몬테카를로 정량 분석 증명서" in doc_kwargs["caption"]


def test_telegram_bot_cool_ci_success():
    """[텔레그램 봇 - 자율 빌드 검증] ⚡ 자율 빌드 검증 실행 시 쿨링 가드레일 하에서 CI 스크립트를 기동하고 성공 회신을 받는지 검증합니다."""
    mock_proc = mock.MagicMock()
    mock_proc.returncode = 0
    
    mock_report_content = """# ❄️ Thermal-Guard CI/CD 전사 빌드 자동화 리포트
- **검증 일시**: 2026-05-27 23:20:00
- **소요 시간**: 30.50초
- **가드레일 상태**: SUCCESS (BELOW_NORMAL CPU 활성화)
- **통과 여부**: 🟢 Perfect PASS"""
    
    with mock.patch("subprocess.run", return_value=mock_proc) as mock_sub, \
         mock.patch("os.path.exists", return_value=True), \
         mock.patch("builtins.open", mock.mock_open(read_data=mock_report_content)), \
         mock.patch("telegram_bot.send_message") as mock_send_msg:
         
        telegram_bot.handle_command("⚡ 자율 빌드 검증", "fake_token", "fake_chat_id")
        
        # 1. 쿨 CI 러너 서브프로세스 1회 기동 단언
        mock_sub.assert_called_once()
        called_cmd = mock_sub.call_args[0][0]
        assert "cool_ci_runner.py" in called_cmd[1]
        
        # 2. 실행 중 알림 + 완료 통보 메시지 2회 발송 단언
        assert mock_send_msg.call_count == 2
        called_texts = [call[0][2] for call in mock_send_msg.call_args_list]
        assert any("테스트 및 빌드 검증을 쿨링 가드레일 모드로 실행" in txt for txt in called_texts)
        assert any("자율 CI 빌드 통과 성공" in txt for txt in called_texts)
        assert any("Perfect PASS" in txt for txt in called_texts)


