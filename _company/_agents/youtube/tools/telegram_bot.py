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

# 📱 7대 핵심 제어 이모지 단축 키보드 레이아웃 개편
KEYBOARD = {
    "keyboard": [
        [{"text": "🎯 트렌드 분석"}, {"text": "🔭 경쟁사 분석"}],
        [{"text": "✍️ 블로그 칼럼"}, {"text": "📊 플래너 상태"}],
        [{"text": "🎨 비주얼 가이드"}, {"text": "📱 릴스 대본"}],
        [{"text": "❓ 도움말 안내"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

def handle_command(cmd, token, chat_id):
    """명령어와 이모지 단축키 버튼을 맵핑하여 에이전트를 자율 기동시킵니다."""
    import requests
    
    NAVER_WRITER_PATH = os.path.join(HERE, "naver_writer.py")
    VISUAL_DIRECTOR_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "designer", "tools", "visual_director.py"))
    REELS_PLANNER_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "instagram", "tools", "reels_planner.py"))

    if cmd in ("/help", "❓ 도움말 안내"):
        help_text = """🤖 [1인 기업 유튜브 에이전트 원격 제어 비서]

아래 채팅창의 이모지 버튼을 터치하거나 명령어를 전송하여 툴들을 원터치 조종할 수 있습니다:

🎯 [트렌드 분석] : 트렌드 스나이퍼(trend_sniper.py) 즉시 실행 및 요약 회신.
🔭 [경쟁사 분석] : 경쟁 채널 브리프(competitor_brief.py) 즉시 실행 및 지시문 회신.
✍️ [블로그 칼럼] : 네이버 라이터(naver_writer.py) 즉시 실행 및 상위 노출 최적화 포스팅 회신.
📊 [플래너 상태] : 24시간 오토 플래너(auto_planner.py) 구동 상황 실시간 요약 조회.
🎨 [비주얼 가이드] : 비주얼 디렉터(visual_director.py) 즉시 실행 및 디자인 지시서 회신.
📱 [릴스 대본] : 릴스 플래너(reels_planner.py) 즉시 실행 및 숏폼 비디오 스크립트 회신.
❓ [도움말 안내] : 현재 가이드라인 및 조종법 안내."""
        send_message(token, chat_id, help_text, reply_markup=KEYBOARD)

    elif cmd in ("/trend", "🎯 트렌드 분석"):
        send_message(token, chat_id, "📡 [에이전트 기동] 트렌드 스나이퍼(trend_sniper.py)를 즉시 실행합니다. 약 10~30초 소요됩니다...")
        last_size = os.path.getsize(SNIPER_REPORT_PATH) if os.path.exists(SNIPER_REPORT_PATH) else 0
        
        try:
            proc = subprocess.run([sys.executable, SNIPER_PATH], capture_output=True, text=True, timeout=180)
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
            proc = subprocess.run([sys.executable, BRIEF_PATH], capture_output=True, text=True, timeout=240)
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
            proc = subprocess.run([sys.executable, NAVER_WRITER_PATH], capture_output=True, text=True, timeout=240)
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
            proc = subprocess.run([sys.executable, VISUAL_DIRECTOR_PATH], capture_output=True, text=True, timeout=240)
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
            proc = subprocess.run([sys.executable, REELS_PLANNER_PATH], capture_output=True, text=True, timeout=240)
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

    elif cmd in ("/status", "📊 플래너 상태"):
        if not os.path.exists(PLANNER_STATE_PATH):
            status_text = "📊 [상태 조회] 현재 오토 플래너가 작동 중이 아니거나 상태 정보 파일(planner_state.json)이 존재하지 않습니다."
            send_message(token, chat_id, status_text, reply_markup=KEYBOARD)
            return
        
        try:
            with open(PLANNER_STATE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            status_text = f"""📊 [24시간 오토 플래너 구동 현황]

● 가동 상태: {state.get('status', 'UNKNOWN')}
● 누적 분석 회차: {state.get('loop_count', 0)}회차 완료
● 시작 시간: {state.get('start_time', 'N/A')}
● 총 가동 시간: {state.get('elapsed_hours', 0.0)}시간 경과
● 마지막 실행 일시: {state.get('last_run_time', 'N/A')}
● 다음 실행 예정: {state.get('next_run_time', 'N/A')}

🤖 1인 기업 에이전트 엔진은 백그라운드에서 정상 가동 및 감시 루프 대기 중입니다."""
            send_message(token, chat_id, status_text, reply_markup=KEYBOARD)
        except Exception as e:
            send_message(token, chat_id, f"❌ 상태 정보 로딩 중 오류 발생: {e}", reply_markup=KEYBOARD)
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

