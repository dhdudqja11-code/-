#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 텔레그램 양방향 승인 브릿지 (telegram_approval_bridge.py) - 하이브리드 파일 모니터링 에디션

100% 409 Conflict 오류를 원천 차단하기 위해, getUpdates 롱 폴링 대신
VSCode 익스텐션과 로컬 파일 IPC 핸드셰이크 방식으로 연동합니다.
"""
import os
import sys
import json
import time
import io
import argparse

# 윈도우 터미널 UTF-8 출력 보장 (한글 및 이모지 출력 시 UnicodeEncodeError 방지)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_DIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONFIG_MD = os.path.join(HERE, "..", "config.md")
SETUP_JSON = os.path.join(HERE, "telegram_setup.json")
PENDING_DIR = os.path.join(COMPANY_DIR, "approvals", "pending")
HISTORY_DIR = os.path.join(COMPANY_DIR, "approvals", "history")

def load_credentials():
    """config.md 또는 telegram_setup.json에서 봇 토큰과 chat_id 로드"""
    token, chat_id = "", ""
    if os.path.exists(CONFIG_MD):
        try:
            with open(CONFIG_MD, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TELEGRAM_BOT_TOKEN:"):
                        token = line.split("TELEGRAM_BOT_TOKEN:")[1].strip()
                    elif line.startswith("TELEGRAM_CHAT_ID:"):
                        chat_id = line.split("TELEGRAM_CHAT_ID:")[1].strip()
        except Exception as e:
            print(f"⚠️ [Bridge] config.md 읽기 중 경고: {e}", file=sys.stderr)

    if (not token or not chat_id) and os.path.exists(SETUP_JSON):
        try:
            with open(SETUP_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = cfg.get("TELEGRAM_BOT_TOKEN", "").strip()
                chat_id = cfg.get("TELEGRAM_CHAT_ID", "").strip()
        except Exception as e:
            print(f"⚠️ [Bridge] telegram_setup.json 읽기 중 경고: {e}", file=sys.stderr)
            
    return token, chat_id

def send_telegram_message(token, chat_id, text):
    """표준 라이브러리 urllib 또는 requests를 활용해 결재 메시지 송신"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    headers = {"Content-Type": "application/json"}
    data_bytes = json.dumps(payload).encode("utf-8")

    try:
        import requests
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except ImportError:
        import urllib.request
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise Exception(f"Urllib 전송 실패: {e}")

def create_pending_approval_files(action_id, title, description, agent_id="developer", kind="deploy"):
    """VSCode 익스텐션과 호환되는 pending 파일 (.json + .md) 생성"""
    os.makedirs(PENDING_DIR, exist_ok=True)
    
    json_path = os.path.join(PENDING_DIR, f"{action_id}.json")
    md_path = os.path.join(PENDING_DIR, f"{action_id}.md")
    
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
    
    # 1. JSON 파일 작성
    pending_json = {
        "id": action_id,
        "agentId": agent_id,
        "kind": kind,
        "title": title,
        "description": description,
        "createdAt": now_iso,
        "payload": {
            "action_id": action_id,
            "title": title
        }
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pending_json, f, ensure_ascii=False, indent=4)
        
    # 2. MD 파일 작성
    pending_md = (
        f"# ⏳ 승인 대기 — {title}\n\n"
        f"- **에이전트:** {agent_id}\n"
        f"- **종류:** `{kind}`\n"
        f"- **요청 시각:** {now_iso}\n"
        f"- **id:** `{action_id}`\n\n"
        f"### 상세 업무 설명\n"
        f"{description}\n"
    )
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(pending_md)
        
    print(f"💾 [Bridge] 익스텐션 호환용 결재 파일 생성 완료: {action_id} (.json / .md)")

def monitor_approvals_history(action_id, timeout_seconds=300):
    """getUpdates 롱 폴링 대신 approvals/history 디렉터리의 처리를 감시 (0% 충돌)"""
    print(f"⏳ [Bridge] 사장님의 결재 처리를 대기하는 중... (로컬 파일 모니터링: 제한시간 {timeout_seconds}초)")
    start_time = time.time()
    
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # 마지막 4글자 Suffix 계산 (텔레그램 /approve 커맨드 단축 대응)
    short_id = action_id[-9:] if len(action_id) >= 9 else action_id
    
    while time.time() - start_time < timeout_seconds:
        try:
            # history 디렉터리 스캔
            history_files = os.listdir(HISTORY_DIR)
            for f in history_files:
                if not f.endswith(".json"):
                    continue
                    
                # 겹침 방지 가드: 완벽한 풀 ID 매칭이거나, short_id 길이가 최소 6자 이상인 안전한 단축 매칭인 경우만 인정
                is_match = False
                if f.endswith(f"_{action_id}.json"):
                    is_match = True
                elif len(short_id) >= 6 and f.endswith(f"_{short_id}.json"):
                    is_match = True
                    
                if is_match:
                    if "_OK_" in f:
                        print("🎉 [Bridge] 익스텐션으로부터 결재 승인(OK) 확인 완료! 👍")
                        return "approved"
                    elif "_NO_" in f:
                        print("❌ [Bridge] 익스텐션으로부터 결재 반려(NO) 확인 완료!")
                        return "rejected"
                        
            # 아직 처리가 안 되었으면 2초 대기
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ [Bridge] 파일 스캔 중 오류 발생: {e}", file=sys.stderr)
            time.sleep(3)
            
    # 대기 타임아웃 발생 시 청소 및 반려
    print("⏳ [Bridge] 결재 대기 제한 시간이 초과되었습니다. 자동 반려 청소를 개시합니다.")
    try:
        # pending 폴더에 남아있는 파일 제거
        for ext in [".json", ".md"]:
            p = os.path.join(PENDING_DIR, f"{action_id}{ext}")
            if os.path.exists(p):
                os.remove(p)
    except Exception as e:
         print(f"⚠️ [Bridge] 임시 파일 청소 중 오류: {e}", file=sys.stderr)
         
    return "timeout"

def main():
    parser = argparse.ArgumentParser(description="Telegram 하이브리드 파일 모니터링 승인 브릿지 툴")
    parser.add_argument("--action-id", type=str, default="test_action", help="업무 식별 고유 ID")
    parser.add_argument("--title", type=str, default="테스트 결재 요청", help="승인 요청 제목")
    parser.add_argument("--description", type=str, default="이것은 양방향 승인 테스트입니다.", help="승인 요청 내용")
    parser.add_argument("--timeout", type=int, default=300, help="대기 타임아웃 초")
    parser.add_argument("--test", action="store_true", help="스스로 모바일 자가 테스트 수행")
    
    args = parser.parse_args()
    
    token, chat_id = load_credentials()
    if not token or not chat_id:
        print("❌ [Bridge] 봇 자격증명이 부족합니다. config.md 또는 telegram_setup.json을 기입해주세요.")
        sys.exit(1)
        
    print(f"🚀 [Bridge] 봇 정보 및 로컬 파일 브릿지 가동 완료. Target Chat ID: {chat_id}")
    
    if args.test:
        print("✨ [Test Mode] 하이브리드 결재 연계 자가 테스트를 수행합니다.")
        # VSCode 익스텐션의 _approvalNewId()가 생성하는 것과 유사한 ID 형식 세팅
        stamp = time.strftime("%Y%m%d%H%M%S")
        args.action_id = f"apr-{stamp}-test"
        args.title = "🔥 모바일 텔레그램 승인 장치 자가 테스트"
        args.description = (
            "409 충돌을 원천 회피하는 하이브리드 결재 통신으로 업그레이드되었습니다.\n\n"
            "아래 승인 명령어를 복사하여 채팅창에 텍스트로 즉시 보내주세요."
        )
        args.timeout = 120
        
    # 마지막 9글자 슬라이싱으로 사장님의 타이핑 피로 완화
    short_id = args.action_id[-9:] if len(args.action_id) >= 9 else args.action_id
    
    # 텔레그램 메시지에 인라인 버튼 대신 일반 텍스트 커맨드 가이드 탑재
    approval_instruction = (
        f"🔔 *[결재 대기 승인 요청]*\n\n"
        f"📌 *업무 ID*: `{args.action_id}`\n"
        f"📋 *제목*: {args.title}\n"
        f"📄 *상세*: {args.description}\n\n"
        f"💬 *결재 방법*: 아래 명령어를 그대로 복사해서 채팅창에 텍스트로 보낸 뒤 엔터를 쳐 주십시오.\n"
        f"👉 승인 시: `/approve {short_id}`\n"
        f"👉 반려 시: `/reject {short_id}`"
    )
    
    try:
        # 1단계: 익스텐션과 연동될 pending 파일 (.json + .md) 디스크에 작성
        create_pending_approval_files(args.action_id, args.title, args.description)
        
        # 2단계: 텔레그램으로 텍스트 커맨드 가이드라인 송신
        send_telegram_message(token, chat_id, approval_instruction)
        print("✅ [Bridge] 모바일 텔레그램 결재 가이드라인 발송 완료!")
        
        # 3단계: getUpdates 롱 폴링 대신 로컬 파일 이동 모니터링 돌입 (충돌 방지 100%)
        result = monitor_approvals_history(args.action_id, args.timeout)
        print(f"📊 [Bridge] 결재 최종 흐름 처리 결과: {result.upper()}")
        
        if result == "approved":
            sys.exit(0)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"❌ [Bridge] 프로세스 실행 중 크래시: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
