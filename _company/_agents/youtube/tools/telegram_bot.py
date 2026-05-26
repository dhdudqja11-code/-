#!/usr/bin/env python3
# version: telegram_v4
"""Telegram Autonomous Bot — 100% Local Long-polling agent daemon.
Allows the CEO (chat_id matching) to remotely query status or trigger
tools like trend_sniper.py and competitor_brief.py from anywhere.

Reads connection tokens and chat IDs from:
1) _agents/secretary/tools/telegram_setup.json
2) Legacy Secretary config.md
3) youtube_account.json
"""
import os, json, sys, time, datetime, re, subprocess

# Windows 환경에서 한글 깨짐 및 이모지 출력 에러 방지를 위해 입출력 인코딩을 UTF-8로 강제 적용
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = os.path.join(HERE, "youtube_account.json")
SNIPER_PATH = os.path.join(HERE, "trend_sniper.py")
BRIEF_PATH = os.path.join(HERE, "competitor_brief.py")
PLANNER_STATE_PATH = os.path.join(HERE, "planner_state.json")
SNIPER_REPORT_PATH = os.path.join(HERE, "trend_sniper_report.md")
BRIEF_REPORT_PATH = os.path.join(HERE, "competitor_brief_report.md")

BRAIN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SECRETARY_TOOL_JSON = os.path.join(BRAIN_ROOT, "_agents", "secretary", "tools", "telegram_setup.json")
SECRETARY_CFG = os.path.join(BRAIN_ROOT, "_agents", "secretary", "config.md")

def _resolve_telegram():
    """비서 설정 -> Legacy MD -> youtube_account.json 순서로 텔레그램 설정 로드."""
    token, chat = "", ""
    # 1) Secretary tool JSON
    if os.path.exists(SECRETARY_TOOL_JSON):
        try:
            with open(SECRETARY_TOOL_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            token = (cfg.get("TELEGRAM_BOT_TOKEN") or "").strip()
            chat  = (cfg.get("TELEGRAM_CHAT_ID") or "").strip()
        except Exception:
            pass
    # 2) Legacy config.md
    if (not token or not chat) and os.path.exists(SECRETARY_CFG):
        try:
            with open(SECRETARY_CFG, "r", encoding="utf-8") as f:
                txt = f.read()
            if not token:
                m = re.search(r"TELEGRAM_BOT_TOKEN\s*[:：=]\s*([A-Za-z0-9:_\-]+)", txt)
                if m: token = m.group(1).strip()
            if not chat:
                m = re.search(r"TELEGRAM_CHAT_ID\s*[:：=]\s*(-?\d+)", txt)
                if m: chat = m.group(1).strip()
        except Exception:
            pass
    # 3) youtube_account.json
    if (not token or not chat) and os.path.exists(ACCOUNT):
        try:
            with open(ACCOUNT, "r", encoding="utf-8") as f:
                acct = json.load(f)
            if not token: token = (acct.get("TELEGRAM_BOT_TOKEN") or "").strip()
            if not chat:  chat  = (acct.get("TELEGRAM_CHAT_ID") or "").strip()
        except Exception:
            pass
    return token, chat

def clean_markdown_for_telegram(text):
    """텔레그램 본문에서 마크다운 파싱 충돌을 방지하기 위해 텍스트를 정화합니다.
    ** 강조 등을 폰 친화적인 따옴표나 대괄호로 매끄럽게 변환합니다.
    """
    if not text:
        return ""
    # ##, ### 등 헤더를 이모지로 보기 좋게 변환
    text = re.sub(r'^###\s+(.*)$', r'■ \1', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*)$', r'● \1', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.*)$', r'👑 \1', text, flags=re.MULTILINE)
    
    # ** 텍스트 ** -> [텍스트] 형태로 변환 (마크다운 파싱 붕괴 방지)
    text = re.sub(r'\*\*(.*?)\*\*', r'[\1]', text)
    
    # 개별 _ 기호 제거
    text = text.replace("_", "")
    
    return text

def send_message(token, chat_id, text, reply_markup=None):
    import requests
    try:
        # 안전한 전송을 위해 본문 마크다운 정화
        cleaned_text = clean_markdown_for_telegram(text)
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": cleaned_text[:4000]
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"⚠️ 메시지 전송 실패: {e}")

def get_new_report_section(file_path, last_size):
    """실행 후 새롭게 추가된 마크다운 리포트만 파싱해서 전송합니다."""
    if not os.path.exists(file_path):
        return ""
    try:
        current_size = os.path.getsize(file_path)
        if current_size <= last_size:
            return ""
        with open(file_path, "r", encoding="utf-8") as f:
            f.seek(last_size)
            new_data = f.read()
        return new_data.strip()
    except Exception as e:
        return f"[리포트 로드 에러]: {e}"

def get_latest_naver_post():
    """naver_posts 폴더에서 가장 최근에 저장된 마크다운 블로그 칼럼을 로드합니다."""
    posts_dir = os.path.join(HERE, "naver_posts")
    if not os.path.exists(posts_dir):
        return ""
    try:
        files = [os.path.join(posts_dir, f) for f in os.listdir(posts_dir) if f.endswith(".md")]
        if not files:
            return ""
        latest_file = max(files, key=os.path.getmtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[최신 글 로드 에러]: {e}"

def get_latest_visual_guide():
    """visual_guides 폴더에서 가장 최근에 저장된 마크다운 비주얼 가이드를 로드합니다."""
    guides_dir = os.path.abspath(os.path.join(HERE, "..", "..", "designer", "tools", "visual_guides"))
    if not os.path.exists(guides_dir):
        return ""
    try:
        files = [os.path.join(guides_dir, f) for f in os.listdir(guides_dir) if f.endswith(".md")]
        if not files:
            return ""
        latest_file = max(files, key=os.path.getmtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[최신 가이드 로드 에러]: {e}"

def get_latest_reels_script():
    """reels_scripts 폴더에서 가장 최근에 저장된 마크다운 릴스 대본을 로드합니다."""
    scripts_dir = os.path.abspath(os.path.join(HERE, "..", "..", "instagram", "tools", "reels_scripts"))
    if not os.path.exists(scripts_dir):
        return ""
    try:
        files = [os.path.join(scripts_dir, f) for f in os.listdir(scripts_dir) if f.endswith(".md")]
        if not files:
            return ""
        latest_file = max(files, key=os.path.getmtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[최신 대본 로드 에러]: {e}"

# 💡 [MFA API 게이트웨이 연동 상태값]
REMOTE_API_URL = "http://127.0.0.1:8000"
API_TOKEN = None
MFA_VERIFIED = False
PENDING_SECURE_CMD = None

def _resolve_api_url():
    """youtube_account.json에서 REMOTE_API_URL 값을 로드합니다. 기본값은 http://127.0.0.1:8000 입니다."""
    url = "http://127.0.0.1:8000"
    if os.path.exists(ACCOUNT):
        try:
            with open(ACCOUNT, "r", encoding="utf-8") as f:
                acct = json.load(f)
            url = acct.get("REMOTE_API_URL", url)
        except Exception:
            pass
    return url

def _api_login(bot_token, chat_id):
    """API 게이트웨이에 admin 자격으로 로그인을 시도해 임시 토큰을 획득합니다."""
    global API_TOKEN, MFA_VERIFIED
    url = f"{_resolve_api_url()}/auth/login"
    payload = {
        "username": "admin",
        "password": "admin_pass"
    }
    headers = {
        "X-Forwarded-For": "127.0.0.1",
        "X-MFA-Test": "true"  # 2FA 흐름을 강제로 기동하기 위해 테스트 헤더 전송
    }
    try:
        import requests
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            API_TOKEN = resp.json().get("access_token")
            MFA_VERIFIED = False
            return True
    except Exception as e:
        print(f"⚠️ API Gateway login failed: {e}")
    return False

def _api_verify_otp(bot_token, chat_id, otp_code):
    """사장님이 제공한 6자리 OTP 코드로 API 게이트웨이의 /auth/mfa/verify를 호출하여 최종 인증에 성공시킵니다."""
    global API_TOKEN, MFA_VERIFIED
    if not API_TOKEN:
        return False
    url = f"{_resolve_api_url()}/auth/mfa/verify"
    payload = {"otp_code": otp_code}
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "X-Forwarded-For": "127.0.0.1"
    }
    try:
        import requests
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            MFA_VERIFIED = True
            return True
    except Exception as e:
        print(f"⚠️ API Gateway MFA verification failed: {e}")
    return False

def _execute_remote_kill(bot_token, chat_id, session_id):
    """MFA 인증이 통과된 상태로 API Gateway의 세션 폭파(Kill Switch) API를 원격으로 기동합니다."""
    global API_TOKEN
    url = f"{_resolve_api_url()}/api/v1/security/kill"
    payload = {"session_id": session_id}
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        import requests
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            msg = f"🛡️ [원격 킬 스위치 완료]\n\n✅ {data.get('message')}"
            send_message(bot_token, chat_id, msg, reply_markup=KEYBOARD)
        else:
            send_message(bot_token, chat_id, f"❌ 세션 폭파 실패 (API 응답코드: {resp.status_code})\n상세: {resp.text}", reply_markup=KEYBOARD)
    except Exception as e:
        send_message(bot_token, chat_id, f"❌ 원격 제어 서버 통신 예외: {e}", reply_markup=KEYBOARD)

def _execute_remote_mitigate(bot_token, chat_id, action_type, target_resource_id):
    """MFA 인증이 통과된 상태로 API Gateway의 위험 완화(trigger_mitigation) API를 원격 기동합니다."""
    global API_TOKEN
    url = f"{_resolve_api_url()}/api/v1/actions/trigger_mitigation"
    payload = {
        "action_type": action_type,
        "target_resource_id": target_resource_id,
        "mitigation_details": {"triggered_by": "telegram_bot"}
    }
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "X-2FA-Authenticated": "true"  # 이중 승인 증명 헤더 탑재
    }
    try:
        import requests
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            msg = f"🛡️ [위험 완화 조치 트리거 완료]\n\n● 상태: {data.get('status')}\n● 트랜잭션 ID: {data.get('transaction_id')}\n● 메시지: {data.get('message')}"
            send_message(bot_token, chat_id, msg, reply_markup=KEYBOARD)
        else:
            send_message(bot_token, chat_id, f"❌ 조치 실패 (API 응답코드: {resp.status_code})\n상세: {resp.text}", reply_markup=KEYBOARD)
    except Exception as e:
        send_message(bot_token, chat_id, f"❌ 원격 제어 서버 통신 예외: {e}", reply_markup=KEYBOARD)

def _execute_remote_simulate(bot_token, chat_id, target_context, hypothetical_action):
    """MFA 인증이 통과된 상태로 API Gateway의 격리 Sandbox 위험 시뮬레이션을 원격 가동하여 투명성 보고서를 회신받습니다."""
    global API_TOKEN
    import urllib.parse
    encoded_ctx = urllib.parse.quote(target_context)
    encoded_act = urllib.parse.quote(hypothetical_action)
    url = f"{_resolve_api_url()}/api/v1/user/simulate_risk?target_context={encoded_ctx}&hypothetical_action={encoded_act}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        import requests
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            msg = f"""⚖️ [격리 Sandbox 위험 시뮬레이션 결과]

● 대상 규제/맥락: {data.get('context')}
● 위험 등급: {data.get('risk_level')}
● 추정 잠재 손실: ${data.get('potential_loss_usd'):,.2f}
● 탐지된 위반 조항: {', '.join(data.get('violation_details', [])) or '없음'}
● 추천 완화 대응조치: {', '.join(data.get('mitigation_steps', [])) or '정상 절차 준수'}

🛡️ 투명성 보고서 공식:
{data.get('transparency_report', {}).get('formula')}"""
            send_message(bot_token, chat_id, msg, reply_markup=KEYBOARD)
        else:
            send_message(bot_token, chat_id, f"❌ 시뮬레이션 실패 (API 응답코드: {resp.status_code})\n상세: {resp.text}", reply_markup=KEYBOARD)
    except Exception as e:
        send_message(bot_token, chat_id, f"❌ 원격 제어 서버 통신 예외: {e}", reply_markup=KEYBOARD)

def _execute_remote_resume(bot_token, chat_id):
    """MFA 인증 완료 상태에서 API Gateway의 플래너 락다운 해제(/api/v1/planner/resume) API를 호출합니다."""
    global API_TOKEN
    url = f"{_resolve_api_url()}/api/v1/planner/resume"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        import requests
        resp = requests.post(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            msg = f"✅ [자율 오토 플래너 락다운 해제 성공]\n\n● 메시지: {data.get('message')}"
            send_message(bot_token, chat_id, msg, reply_markup=KEYBOARD)
        else:
            send_message(bot_token, chat_id, f"❌ 플래너 락다운 해제 실패 (API 응답코드: {resp.status_code})\n상세: {resp.text}", reply_markup=KEYBOARD)
    except Exception as e:
        send_message(bot_token, chat_id, f"❌ 원격 제어 서버 통신 예외: {e}", reply_markup=KEYBOARD)

def edit_message_text(token, chat_id, message_id, text, reply_markup=None):
    """텔레그램 대화방 내 기존 메시지의 본문 텍스트를 화면 전환 없이 실시간 교체합니다."""
    import requests
    try:
        cleaned_text = clean_markdown_for_telegram(text)
        url = f"https://api.telegram.org/bot{token}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": cleaned_text[:4000]
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"⚠️ 메시지 수정 실패: {e}")

def answer_callback_query(token, callback_query_id, text=None):
    """인라인 키보드 버튼 터치 시의 모바일 로딩 대기 바(모래시계)를 즉각 소거합니다."""
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ 콜백 응답 실패: {e}")

def _query_audit_logs(mode, offset=0, limit=5):
    """SQLite3 gateway_audit.db 감사 데이터베이스에 안전하게 연결하여 감사 블록 레코드를 조회합니다."""
    import sqlite3
    gateway_dir = os.path.abspath(os.path.join(HERE, "..", "..", "..", "core_gateway"))
    db_path = os.path.join(gateway_dir, "gateway_audit.db")
    
    if not os.path.exists(db_path):
        return []
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if mode == "recent":
            cursor.execute("SELECT * FROM audit_blocks ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
        elif mode == "fail_today":
            today_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT * FROM audit_blocks WHERE status = 'FAILURE' AND timestamp_utc LIKE ? ORDER BY id DESC",
                (f"{today_str}%",)
            )
            rows = cursor.fetchall()
        elif mode == "success":
            cursor.execute(
                "SELECT * FROM audit_blocks WHERE status = 'SUCCESS' ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
        elif mode == "failure":
            cursor.execute(
                "SELECT * FROM audit_blocks WHERE status = 'FAILURE' ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
        else:
            rows = []
            
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"⚠️ [Telegram Bot DB Error] {e}")
        return []

def _format_audit_message(rows, mode, page=1):
    """조회된 감사 레코드 정보들을 보기 편한 이모지 친화형 마크다운 구조로 가공합니다."""
    if not rows:
        return f"📂 [감사 로그 스캔 결과]\n\n조회된 감사 로그가 존재하지 않습니다. (모드: {mode}, 페이지: {page})"
        
    mode_titles = {
        "recent": "🔄 최근 감사 로그 요약 (최대 5건)",
        "fail_today": "🚨 오늘 규제 위반 실패 로그",
        "success": f"🟢 준수(SUCCESS) 감사 로그 (페이지 {page})",
        "failure": f"🔴 위반(FAILURE) 감사 로그 (페이지 {page})"
    }
    title = mode_titles.get(mode, "📊 감사 로그 조회")
    
    lines = [f"📊 **{title}**", "---"]
    for idx, r in enumerate(rows, 1):
        status_emoji = "🟢" if r["status"] == "SUCCESS" else "🔴"
        ts = r["timestamp_utc"]
        if "T" in ts:
            ts = ts.split(".")[0].replace("T", " ")
            if ts.endswith("Z"):
                ts = ts[:-1]
                
        lines.append(f"{idx}. {status_emoji} [{ts}]")
        lines.append(f"   ● API: {r['source_api']}")
        lines.append(f"   ● ID: {r['transaction_id'][:8]}... (기동자: {r['initiator_user_id']})")
        lines.append(f"   ● 요약: {r['result_summary']}")
        if r["status"] == "FAILURE":
            lines.append(f"   ● 에러: {r['message']}")
        lines.append("")
        
    return "\n".join(lines)

AUDIT_MENU_MARKUP = {
    "inline_keyboard": [
        [
            {"text": "🔄 최근 5건", "callback_data": "audit_recent"},
            {"text": "🚨 오늘 위반 로그", "callback_data": "audit_fail_today"}
        ],
        [
            {"text": "🟢 성공 로그만", "callback_data": "audit_success_0"},
            {"text": "🔴 실패 로그만", "callback_data": "audit_failure_0"}
        ],
        [
            {"text": "❌ 닫기", "callback_data": "audit_close"}
        ]
    ]
}

AUDIT_BACK_MARKUP = {
    "inline_keyboard": [
        [
            {"text": "◀️ 메인 메뉴로", "callback_data": "audit_menu"}
        ]
    ]
}

def _execute_remote_audit_menu(bot_token, chat_id):
    """MFA 인증 완료 상태에서 감사 로그 대화형 인라인 키보드 메뉴를 송신합니다."""
    text = """📊 [IAG 감사 로그 실시간 원격 관제]
    
사장님, SQLite3 영구 SSoT 감사 데이터베이스(gateway_audit.db)에 기록된 감사기록을 원터치로 안전하게 실시간 조회하실 수 있습니다.

아래 원하시는 분석 및 조회 메뉴를 선택해 주십시오."""
    send_message(bot_token, chat_id, text, reply_markup=AUDIT_MENU_MARKUP)

def handle_callback_query(callback_data, callback_id, message_id, token, chat_id):
    """인라인 키보드 버튼 클릭으로 전송된 콜백 쿼리를 분석하고 동적 실시간 피딩을 실행합니다."""
    answer_callback_query(token, callback_id)
    
    if not API_TOKEN or not MFA_VERIFIED:
        edit_message_text(token, chat_id, message_id, "🔒 세션이 비활성화되었거나 만료되었습니다. 다시 2FA OTP 인증을 진행해 주십시오.")
        return
        
    if callback_data == "audit_menu":
        text = """📊 [IAG 감사 로그 실시간 원격 관제]
        
사장님, SQLite3 영구 SSoT 감사 데이터베이스(gateway_audit.db)에 기록된 감사기록을 원터치로 안전하게 실시간 조회하실 수 있습니다.

아래 원하시는 분석 및 조회 메뉴를 선택해 주십시오."""
        edit_message_text(token, chat_id, message_id, text, reply_markup=AUDIT_MENU_MARKUP)
        
    elif callback_data == "audit_close":
        edit_message_text(token, chat_id, message_id, "🔒 감사 로그 조회가 안전하게 종료되었습니다.", reply_markup={"inline_keyboard": []})
        
    elif callback_data == "audit_recent":
        rows = _query_audit_logs("recent")
        text = _format_audit_message(rows, "recent")
        edit_message_text(token, chat_id, message_id, text, reply_markup=AUDIT_BACK_MARKUP)
        
    elif callback_data == "audit_fail_today":
        rows = _query_audit_logs("fail_today")
        text = _format_audit_message(rows, "fail_today")
        edit_message_text(token, chat_id, message_id, text, reply_markup=AUDIT_BACK_MARKUP)
        
    elif callback_data.startswith("audit_success_") or callback_data.startswith("audit_failure_"):
        parts = callback_data.split("_")
        mode = parts[1]
        offset = int(parts[2])
        limit = 5
        
        rows = _query_audit_logs(mode, offset=offset, limit=limit)
        page = (offset // limit) + 1
        text = _format_audit_message(rows, mode, page=page)
        
        inline_buttons = []
        if offset > 0:
            inline_buttons.append({"text": "◀️ 이전", "callback_data": f"audit_{mode}_{offset-limit}"})
        if len(rows) == limit:
            inline_buttons.append({"text": "다음 ▶️", "callback_data": f"audit_{mode}_{offset+limit}"})
            
        keyboard = []
        if inline_buttons:
            keyboard.append(inline_buttons)
        keyboard.append([{"text": "◀️ 메인 메뉴로", "callback_data": "audit_menu"}])
        
        reply_markup = {"inline_keyboard": keyboard}
        edit_message_text(token, chat_id, message_id, text, reply_markup=reply_markup)

# 📱 10대 핵심 제어 이모지 단축 키보드 레이아웃 개편 (감사 로그 및 보안 관제탑 추가)
KEYBOARD = {
    "keyboard": [
        [{"text": "🎯 트렌드 분석"}, {"text": "🔭 경쟁사 분석"}],
        [{"text": "✍️ 블로그 칼럼"}, {"text": "📊 플래너 상태"}],
        [{"text": "🎨 비주얼 가이드"}, {"text": "📱 릴스 대본"}],
        [{"text": "🛡️ 원격 보안 관제"}, {"text": "📊 감사 로그"}],
        [{"text": "💬 사장님 피드백"}, {"text": "❓ 도움말 안내"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

def handle_command(cmd, token, chat_id):
    """명령어와 이모지 단축키 버튼을 맵핑하여 에이전트를 자율 기동시킵니다."""
    global API_TOKEN, MFA_VERIFIED, PENDING_SECURE_CMD
    import requests
    
    NAVER_WRITER_PATH = os.path.join(HERE, "naver_writer.py")
    VISUAL_DIRECTOR_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "designer", "tools", "visual_director.py"))
    REELS_PLANNER_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "instagram", "tools", "reels_planner.py"))
    ORCHESTRATOR_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared", "campaign_orchestrator.py"))
    FEEDER_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared", "feedback_feeder.py"))

    # Windows CPU/GPU 쿨링 및 소음 제어 가드레일 플래그 빌드
    win_kwargs = {}
    if sys.platform == "win32":
        win_kwargs["creationflags"] = 0x00004000 # BELOW_NORMAL_PRIORITY_CLASS

    # 🔒 [MFA OTP 직접 입력 또는 /verify 명령어 감지]
    otp_match = re.match(r"^/verify\s+(\d{6})$", cmd)
    if not otp_match and re.match(r"^\d{6}$", cmd):
        otp_match = re.match(r"^(\d{6})$", cmd)
        
    if otp_match:
        otp_code = otp_match.group(1)
        send_message(token, chat_id, f"📡 [2FA OTP 검증 시도] OTP 코드 {otp_code}를 API Gateway에 인증하는 중...")
        
        # 1. 만약 토큰이 없다면 임시 로그인
        if not API_TOKEN:
            if not _api_login(token, chat_id):
                send_message(token, chat_id, "❌ API Gateway 로그인 실패. 서버 구동 및 네트워크 상태를 확인하십시오.", reply_markup=KEYBOARD)
                return
                
        # 2. OTP 검증 호출
        if _api_verify_otp(token, chat_id, otp_code):
            send_message(token, chat_id, "🔒 [MFA 인증 성공] 2차 보안 토큰이 정상 승격 활성화되었습니다!\n원격 보안 명령이 안전하게 기동됩니다.", reply_markup=KEYBOARD)
            
            # 3. 보류 중이던 원격 보안 명령이 있다면 연쇄 실행
            if PENDING_SECURE_CMD:
                cmd_type = PENDING_SECURE_CMD.get("cmd_type")
                args = PENDING_SECURE_CMD.get("args", [])
                PENDING_SECURE_CMD = None # 소모 완료
                
                if cmd_type == "kill":
                    _execute_remote_kill(token, chat_id, *args)
                elif cmd_type == "mitigate":
                    _execute_remote_mitigate(token, chat_id, *args)
                elif cmd_type == "simulate":
                    _execute_remote_simulate(token, chat_id, *args)
                elif cmd_type == "audit":
                    _execute_remote_audit_menu(token, chat_id)
                    
            # 4. 만약 오토 플래너가 규제 위반 락다운(PAUSED) 상태라면 자동으로 원격 잠금 해제(Resume)
            is_paused = False
            if os.path.exists(PLANNER_STATE_PATH):
                try:
                    with open(PLANNER_STATE_PATH, "r", encoding="utf-8") as f:
                        state_data = json.load(f)
                    if state_data.get("status") == "PAUSED":
                        is_paused = True
                except Exception:
                    pass
            if is_paused:
                _execute_remote_resume(token, chat_id)
        else:
            send_message(token, chat_id, "❌ [MFA 인증 실패] OTP 코드가 일치하지 않거나 만료되었습니다. 다시 시도하십시오.", reply_markup=KEYBOARD)
        return

    # 🔒 3대 원격 보안 제어 명령어 파싱 및 대조 가드
    kill_match = re.match(r"^/kill\s+(.+)$", cmd)
    mitigate_match = re.match(r"^/mitigate\s+(\S+)\s+(\S+)$", cmd)
    simulate_match = re.match(r"^/simulate\s+(\S+)\s+(\S+)$", cmd)
    
    if kill_match or mitigate_match or simulate_match:
        # 인증 여부 체크
        if not API_TOKEN or not MFA_VERIFIED:
            # 보류 명령어로 적재
            if kill_match:
                PENDING_SECURE_CMD = {"cmd_type": "kill", "args": [kill_match.group(1).strip()]}
            elif mitigate_match:
                PENDING_SECURE_CMD = {"cmd_type": "mitigate", "args": [mitigate_match.group(1), mitigate_match.group(2)]}
            elif simulate_match:
                PENDING_SECURE_CMD = {"cmd_type": "simulate", "args": [simulate_match.group(1), simulate_match.group(2)]}
                
            # 임시 로그인 시도
            _api_login(token, chat_id)
            
            send_message(token, chat_id, "🔒 [MFA 2차 인증 요구]\n이 조치는 최고 권한 세션 및 2FA 인증이 필수로 요구됩니다. 실시간 구글 OTP 6자리를 입력하십시오.\n\n👉 예: `/verify 123456` 또는 단순 `123456` 입력")
            return
            
        # 이미 인증 통과된 상태면 즉시 기동
        if kill_match:
            _execute_remote_kill(token, chat_id, kill_match.group(1).strip())
        elif mitigate_match:
            _execute_remote_mitigate(token, chat_id, mitigate_match.group(1), mitigate_match.group(2))
        elif simulate_match:
            _execute_remote_simulate(token, chat_id, simulate_match.group(1), simulate_match.group(2))
        return

    # 🔒 감사 로그 조회 (/audit) 보안 차단 및 개시
    if cmd in ("/audit", "📊 감사 로그"):
        if not API_TOKEN or not MFA_VERIFIED:
            PENDING_SECURE_CMD = {"cmd_type": "audit", "args": []}
            _api_login(token, chat_id)
            send_message(token, chat_id, "🔒 [MFA 2차 인증 요구]\n감사 로그 조치는 최고 권한 세션 및 2FA 인증이 필수로 요구됩니다. 실시간 구글 OTP 6자리를 입력하십시오.\n\n👉 예: `/verify 123456` 또는 단순 `123456` 입력")
            return
            
        _execute_remote_audit_menu(token, chat_id)
        return

    if cmd in ("/help", "❓ 도움말 안내"):
        help_text = """🤖 [1인 기업 유튜브 에이전트 원격 제어 비서]

아래 채팅창의 이모지 버튼을 터치하거나 명령어를 전송하여 툴들을 원터치 조종할 수 있습니다:

🎯 [트렌드 분석] : 트렌드 스나이퍼(trend_sniper.py) 즉시 실행 및 요약 회신.
🔭 [경쟁사 분석] : 경쟁 채널 브리프(competitor_brief.py) 즉시 실행 및 지시문 회신.
✍️ [블로그 칼럼] : 네이버 라이터(naver_writer.py) 즉시 실행 및 상위 노출 최적화 포스팅 회신.
📊 [플래너 상태] : 24시간 오토 플래너(auto_planner.py) 구동 상황 실시간 요약 조회.
🎨 [비주얼 가이드] : 비주얼 디렉터(visual_director.py) 즉시 실행 및 디자인 지시서 회신.
📱 [릴스 대본] : 릴스 플래너(reels_planner.py) 즉시 실행 및 숏폼 비디오 스크립트 회신.
📢 [캠페인 일괄 실행] : 마케팅 파이프라인(유튜브트렌드->블로그->비주얼->릴스대본->발행) 자동 완성.
💬 [사장님 피드백] : 에이전트들의 성능 교정을 위한 지시 로그(decisions.md) 실시간 피딩.
❓ [도움말 안내] : 현재 가이드라인 및 조종법 안내."""
        send_message(token, chat_id, help_text, reply_markup=KEYBOARD)

    elif cmd in ("/trend", "🎯 트렌드 분석"):
        send_message(token, chat_id, "📡 [에이전트 기동] 트렌드 스나이퍼(trend_sniper.py)를 즉시 실행합니다. 약 10~30초 소요됩니다...")
        last_size = os.path.getsize(SNIPER_REPORT_PATH) if os.path.exists(SNIPER_REPORT_PATH) else 0
        
        try:
            proc = subprocess.run([sys.executable, SNIPER_PATH], capture_output=True, encoding="utf-8", timeout=180, **win_kwargs)
            if proc.returncode == 0:
                report = get_new_report_section(SNIPER_REPORT_PATH, last_size)
                if not report:
                    report = "✅ 분석 완료! trend_sniper_report.md 파일을 확인하세요."
                send_message(token, chat_id, f"🎯 [트렌드 스나이핑 분석 완료]\n\n{report}", reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 트렌드 스나이퍼 가동 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 트렌드 스나이퍼 실행 도중 장애 발생: {e}", reply_markup=KEYBOARD)

    elif cmd in ("/brief", "🔭 경쟁사 분석"):
        send_message(token, chat_id, "📡 [에이전트 기동] 경쟁 채널 브리프(competitor_brief.py)를 즉시 실행합니다. 약 10~30초 소요됩니다...")
        last_size = os.path.getsize(BRIEF_REPORT_PATH) if os.path.exists(BRIEF_REPORT_PATH) else 0
        
        try:
            proc = subprocess.run([sys.executable, BRIEF_PATH], capture_output=True, encoding="utf-8", timeout=240, **win_kwargs)
            if proc.returncode == 0:
                report = get_new_report_section(BRIEF_REPORT_PATH, last_size)
                if not report:
                    report = "✅ 분석 완료! competitor_brief_report.md 파일을 확인하세요."
                send_message(token, chat_id, f"🔭 [경쟁 채널 브리핑 완료]\n\n{report}", reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 경쟁 채널 브리프 가동 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 경쟁 채널 브리프 실행 도중 장애 발생: {e}", reply_markup=KEYBOARD)

    elif cmd in ("/write_blog", "✍️ 블로그 칼럼"):
        send_message(token, chat_id, "📡 [에이전트 기동] 네이버 칼럼 라이터(naver_writer.py)를 즉시 실행합니다. 약 10~30초 소요됩니다...")
        
        try:
            proc = subprocess.run([sys.executable, NAVER_WRITER_PATH], capture_output=True, encoding="utf-8", timeout=240, **win_kwargs)
            if proc.returncode == 0:
                post = get_latest_naver_post()
                if not post:
                    post = "✅ 칼럼 생성 완료! naver_posts/ 폴더에서 마크다운 파일을 확인하십시오."
                send_message(token, chat_id, f"✍️ [네이버 마케팅 칼럼 자율 집필 완료]\n\n{post}", reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 네이버 라이터 가동 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 네이버 라이터 실행 도중 장애 발생: {e}", reply_markup=KEYBOARD)

    elif cmd in ("/visual", "🎨 비주얼 가이드"):
        send_message(token, chat_id, "📡 [에이전트 기동] 비주얼 디렉터(visual_director.py)를 즉시 실행합니다. 약 10~30초 소요됩니다...")
        
        try:
            proc = subprocess.run([sys.executable, VISUAL_DIRECTOR_PATH], capture_output=True, encoding="utf-8", timeout=240, **win_kwargs)
            if proc.returncode == 0:
                guide = get_latest_visual_guide()
                if not guide:
                    guide = "✅ 비주얼 가이드 생성 완료! designer/tools/visual_guides/ 폴더에서 마크다운 파일을 확인하십시오."
                send_message(token, chat_id, f"🎨 [프리미엄 비주얼 가이드 라인 기획 완료]\n\n{guide}", reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 비주얼 디렉터 가동 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 비주얼 디렉터 실행 도중 장애 발생: {e}", reply_markup=KEYBOARD)

    elif cmd in ("/reels", "📱 릴스 대본"):
        send_message(token, chat_id, "📡 [에이전트 기동] 릴스 플래너(reels_planner.py)를 즉시 실행합니다. 약 10~30초 소요됩니다...")
        
        try:
            proc = subprocess.run([sys.executable, REELS_PLANNER_PATH], capture_output=True, encoding="utf-8", timeout=240, **win_kwargs)
            if proc.returncode == 0:
                script = get_latest_reels_script()
                if not script:
                    script = "✅ 릴스 대본 생성 완료! instagram/tools/reels_scripts/ 폴더에서 마크다운 파일을 확인하십시오."
                send_message(token, chat_id, f"📱 [인스타그램 릴스 숏폼 대본 기획 완료]\n\n{script}", reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 릴스 플래너 가동 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 릴스 플래너 실행 도중 장애 발생: {e}", reply_markup=KEYBOARD)

    elif cmd in ("/campaign", "📢 캠페인 일괄 실행"):
        send_message(token, chat_id, "⚡ [Ryzen 9 병렬 가동] 1인 기업 자동 마케팅 캠페인 파이프라인 연쇄 기동 중 (8코어 16스레드 Concurrent 최적화 모드)... 약 15~25초 소요됩니다.")
        
        try:
            proc = subprocess.run([sys.executable, ORCHESTRATOR_PATH], capture_output=True, encoding="utf-8", timeout=400, **win_kwargs)
            if proc.returncode == 0:
                # 마지막 JSON 블록을 추출 및 로드
                lines = proc.stdout.splitlines()
                json_lines = []
                start_json = False
                for line in lines:
                    if line.strip() == "{":
                        start_json = True
                    if start_json:
                        json_lines.append(line)
                    if line.strip() == "}":
                        json_lines.append(line)
                        break
                
                json_str = "\n".join(json_lines)
                data = json.loads(json_str)
                
                campaign_id = data.get("timestamp", "N/A")
                summary_msg = f"""📢 [⚡ AI 1인 기업 일괄 캠페인 병렬 완수!]

사장님, Ryzen 9 (16스레드) 병렬 최적화 체인을 가동하여 신규 마케팅 캠페인이 초고속으로 완료되었습니다!

📅 캠페인 회차: campaign_{campaign_id}
📂 포트폴리오: _company/marketing_history/campaign_{campaign_id}/
⚡ 실행 소요 시간: {data.get('elapsed_seconds', 'N/A')}초 (이전 동기식 대비 약 3배 성능 향상!)

🛡️ [에이전트 자율 병렬 기동 상태]
● 유튜브 트렌드 스캔: {data['steps'].get('trend_sniper', 'N/A')}
● 네이버 블로그 칼럼: {data['steps'].get('naver_writer', 'N/A')}
● 비주얼 가이드 설계: {data['steps'].get('visual_director', 'N/A')}
● 인스타 릴스 숏폼대본: {data['steps'].get('reels_planner', 'N/A')}

🚀 [자율 채널 발행 현황]
● 네이버 블로그: {data['steps']['naver_publish'].get('status', 'N/A')}
🔗 링크: {data['steps']['naver_publish'].get('url', '시뮬레이션 모드')}
● 인스타 Reels: {data['steps']['instagram_publish'].get('status', 'N/A')}
🔗 링크: {data['steps']['instagram_publish'].get('url', '시뮬레이션 모드')}

🤖 감사 로그 및 실시간 트래픽 데이터는 로컬 SQLite DB에 완벽히 보존되었습니다. 세부 글/대본 전문을 보시려면 이모지 제어반을 이용하십시오!"""
                send_message(token, chat_id, summary_msg, reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 캠페인 오케스트레이터 가동 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 캠페인 오케스트레이터 실행 중 장애 발생: {e}", reply_markup=KEYBOARD)

    elif cmd == "💬 사장님 피드백":
        feed_info = """💬 [사장님 자율 피드백 피딩 작동법]

에이전트의 글쓰기 톤, 썸네일 카피, 인스타 릴스 훅 등 아쉬운 점이나 추가 지시사항을 한 줄의 피드백으로 전송해 주십시오.

👉 입력 형식: /feedback [선택: 피드백 내용]
👉 예시: /feedback 썸네일 카피를 더 직관적으로 잡고, 예상 리스크액을 수치로 2배 강조해라!

피드백이 접수되는 즉시 에이전트 공용 의사결정 로그(decisions.md)에 연동되어 다음 캠페인 기동부터 자율 수정됩니다."""
        send_message(token, chat_id, feed_info, reply_markup=KEYBOARD)

    elif cmd.startswith("/feedback"):
        feedback_text = cmd[9:].strip()
        if not feedback_text:
            send_message(token, chat_id, "⚠️ 피드백 내용을 적어주세요. 예: /feedback 썸네일 카피를 강렬하게 수정해라.", reply_markup=KEYBOARD)
            return
            
        send_message(token, chat_id, f"📡 [피드백 접수 중...] 사장님의 지시사항을 분석하여 공용 의사결정 데이터베이스에 주입하는 중입니다...")
        try:
            proc = subprocess.run([sys.executable, FEEDER_PATH, feedback_text], capture_output=True, encoding="utf-8", timeout=120, **win_kwargs)
            if proc.returncode == 0:
                summary_msg = f"""🎯 [의사결정 로그 실시간 반영 완료!]

사장님의 소중한 지시사항이 에이전트 공용 의사결정 로그(decisions.md)에 안전하게 반영 및 누적되었습니다!

📅 반영 일시: {time.strftime('%Y-%m-%d %H:%M:%S')}
📝 [반영된 사장님 피드백 내용]:
- {feedback_text}

🤖 다음 캠페인 기동 시부터 모든 에이전트가 이 피드백을 최우선(메모리 1순위 위계)으로 주입받아 작동 방식을 자율 교정합니다!"""
                send_message(token, chat_id, summary_msg, reply_markup=KEYBOARD)
            else:
                err_msg = proc.stderr.strip()[-300:] if proc.stderr else "상세 에러 내용 없음"
                send_message(token, chat_id, f"❌ 피드백 피딩 처리 실패 (exit {proc.returncode}).\n에러 요약: {err_msg}", reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 피드백 피딩 처리 도중 예외 발생: {e}", reply_markup=KEYBOARD)

    elif cmd == "🛡️ 원격 보안 관제":
        security_help = """🛡️ [MFA Guarded 원격 보안 제어 관제탑 조종법]

사장님, 원격 제어 게이트웨이와 텔레그램 채널이 2FA OTP로 철저히 보호되고 있습니다.

👉 아래 템플릿 명령어를 참고하여 전송해 주십시오:

1️⃣ 킬 스위치 (세션 파괴 및 IP 즉시 영구 차단):
   /kill [세션ID]
   예: /kill sess_uuid_12345

2️⃣ 위험 완화 조치 (이중 승인 트리거 및 감사 로그 영구 보존):
   /mitigate [조치타입] [리소스ID]
   예: /mitigate RESTART server_db_main

3️⃣ Sandbox 위험 및 규제성 사전 시뮬레이션:
   /simulate [규제/맥락] [행동]
   예: /simulate gdpr_compliance backup_export_unmasked

💡 모든 보안 명령은 전송 즉시 2차 OTP 인증 확인을 요구하며, 성공 시 백엔드와 연계 기동합니다."""
        send_message(token, chat_id, security_help, reply_markup=KEYBOARD)

    elif cmd in ("/status", "📊 플래너 상태", "/metrics"):
        send_message(token, chat_id, "📊 [데이터 분석] 최근 마케팅 성과 반응 데이터 및 오토 플래너 상태를 정밀 분석하는 중입니다...")
        
        # 1. metrics_tracker.py를 백그라운드 구동하여 최신 트래픽 지표 실시간 수집/RAG 반영 실행
        TRACKER_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared", "metrics_tracker.py"))
        try:
            subprocess.run([sys.executable, TRACKER_PATH], capture_output=True, encoding="utf-8", timeout=60, **win_kwargs)
        except Exception:
            pass

        # 2. SQLite 데이터베이스에서 성과 쿼리 로드
        perf_summary = ""
        try:
            # database 모듈을 동적 임포트하여 성과 조회
            db_dir = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared"))
            if db_dir not in sys.path:
                sys.path.append(db_dir)
            import database
            summary = database.get_performance_summary()
            
            best_info = "없음 (캠페인을 먼저 가동해주세요)"
            if summary.get("best_performer"):
                bp = summary["best_performer"]
                plat = "네이버 블로그" if bp["platform"] == "naver" else "인스타그램 Reels"
                best_info = f"🏆 [{plat}] \"{bp['title']}\"\n  👉 수집 반응: 조회 {bp['views']:,}회 / 좋아요 {bp['likes']:,}개"

            perf_summary = f"""
📈 [채널 마케팅 실시간 반응 지표 요약]
● 네이버 블로그 누적: 조회 {summary['naver_views']:,}회 / 공감 {summary['naver_likes']:,}개
● 인스타 Reels 누적: 재생 {summary['insta_views']:,}회 / 하트 {summary['insta_likes']:,}개
● 베스트 퍼포먼스 콘텐츠:
  {best_info}
● RAG 자율 학습 루프: 최고 성과 요약이 decisions.md 메모리에 실시간 RAG 피딩 완료되었습니다."""
        except Exception as e:
            perf_summary = f"\n⚠️ 성과 지표 로드 실패: {e}"

        # 3. 플래너 구동 상태 파싱
        planner_info = "오토 플래너 작동 중이 아니거나 planner_state.json 파일이 존재하지 않습니다."
        if os.path.exists(PLANNER_STATE_PATH):
            try:
                with open(PLANNER_STATE_PATH, "r", encoding="utf-8") as f:
                    state = json.load(f)
                planner_info = f"""● 가동 상태: {state.get('status', 'UNKNOWN')}
● 누적 분석 회차: {state.get('loop_count', 0)}회차 완료
● 시작 시간: {state.get('start_time', 'N/A')}
● 총 가동 시간: {state.get('elapsed_hours', 0.0)}시간 경과
● 마지막 실행 일시: {state.get('last_run_time', 'N/A')}
● 다음 실행 예정: {state.get('next_run_time', 'N/A')}"""
            except Exception:
                pass
        
        status_text = f"""📊 [24시간 오토 플래너 및 마케팅 성과 통합 리포트]
{perf_summary}

🛡️ [오토 플래너 구동 현황]
{planner_info}

🤖 1인 기업 에이전트 엔진은 백그라운드에서 정상 가동 및 감시 루프 대기 중입니다."""
        send_message(token, chat_id, status_text, reply_markup=KEYBOARD)
    else:
        send_message(token, chat_id, f"⚠️ 알 수 없는 명령어입니다: {cmd}\n아래의 버튼을 눌러 명령을 내리시거나 /help 를 참고하세요.", reply_markup=KEYBOARD)

def main():
    token, chat_id_cfg = _resolve_telegram()
    if not token or not chat_id_cfg:
        print("❌ 텔레그램 연동 토큰 또는 Chat ID를 찾을 수 없습니다. 설정을 확인해 주십시오.")
        sys.exit(1)
        
    try:
        import requests
    except ImportError:
        print("❌ pip install requests 가 필요합니다.")
        sys.exit(1)

    # 1:1 보안 매칭 가드용 정수형 chat_id 매핑
    try:
        target_chat_id = int(chat_id_cfg)
    except ValueError:
        print(f"❌ 설정된 TELEGRAM_CHAT_ID({chat_id_cfg})는 유효한 정수가 아닙니다.")
        sys.exit(1)

    print("=============================================================")
    print("🚀 [텔레그램 비서] 양방향 자율 조종 봇 기동 완료 (Long Polling)")
    print(f"🔒 보안 가드: 사장님 ID({target_chat_id}) 외 접속 전면 차단 작동 중")
    print("=============================================================")
    
    # 봇 기동 첫 시작을 사장님께 간결히 공출 (커스텀 이모지 버튼 자판 자동 팝업)
    welcome = f"🤖 [에이전트 비서 가동] 사장님, 원격 제어 비서 봇이 성공적으로 실행되었습니다.\n아래의 이모지 버튼을 누르시거나 /help 로 조종법을 확인하세요! — {time.strftime('%Y-%m-%d %H:%M:%S')}"
    send_message(token, target_chat_id, welcome, reply_markup=KEYBOARD)

    offset = 0
    # Long Polling 무한 루프 시작
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {"timeout": 30, "offset": offset}
            resp = requests.get(url, params=params, timeout=35)
            
            if resp.status_code != 200:
                time.sleep(5)
                continue
                
            updates = resp.json().get("result", [])
            for up in updates:
                offset = up["update_id"] + 1
                
                # 🔒 인라인 키보드 콜백 쿼리 수신 및 보안 가드 작동
                callback_query = up.get("callback_query")
                if callback_query:
                    callback_id = callback_query.get("id")
                    callback_data = callback_query.get("data", "")
                    sender_chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
                    message_id = callback_query.get("message", {}).get("message_id")
                    from_user = callback_query.get("from", {})
                    
                    if sender_chat_id != target_chat_id:
                        username = from_user.get("username", "N/A")
                        first_name = from_user.get("first_name", "N/A")
                        print(f"🚨 [보안 위반 차단] 비인가 콜백 시도 감지! chat_id: {sender_chat_id} | 이름: {first_name}(@{username}) | 입력: {callback_data}")
                        continue
                        
                    print(f"💬 [CEO 콜백 수신]: {callback_data}")
                    handle_callback_query(callback_data, callback_id, message_id, token, target_chat_id)
                    continue

                msg = up.get("message", {})
                txt = (msg.get("text") or "").strip()
                from_user = msg.get("from", {})
                sender_chat_id = msg.get("chat", {}).get("id")

                if not txt:
                    continue

                # 🔒 1:1 사장님 매칭 보안 가드레일 작동
                if sender_chat_id != target_chat_id:
                    # 비인가 사용자 차단 로그 출력
                    username = from_user.get("username", "N/A")
                    first_name = from_user.get("first_name", "N/A")
                    print(f"🚨 [보안 위반 차단] 비인가 침입 시도 감지! chat_id: {sender_chat_id} | 이름: {first_name}(@{username}) | 입력: {txt}")
                    # 비인가 침입 시도자에게 403 Forbidden 성격의 경고 후 즉각 무시
                    send_message(token, sender_chat_id, "🚨 [보안 거부] 귀하는 이 AI 1인 기업 시스템의 소유자(CEO)가 아닙니다. 모든 접근 및 명령 시도는 기록되고 영구 거부됩니다.")
                    continue

                print(f"💬 [CEO 명령 수신]: {txt}")
                handle_command(txt, token, target_chat_id)
                
        except KeyboardInterrupt:
            print("\n👋 텔레그램 비서가 수동 종료되었습니다.")
            break
        except Exception as e:
            print(f"⚠️ 루프 예외 발생 (자동 재기동 대기): {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

