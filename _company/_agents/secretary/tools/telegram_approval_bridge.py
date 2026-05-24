#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 텔레그램 양방향 승인 브릿지 (telegram_approval_bridge.py)

비서 에이전트(영숙이)가 사장님 모바일로 결재 요청 카드를 발송하고,
getUpdates 롱 폴링을 통해 승인/반려Callback Query를 실시간 수집 및 위임 전파합니다.
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
APPROVALS_DIR = os.path.join(COMPANY_DIR, "approvals")

def load_credentials():
    """config.md 또는 telegram_setup.json에서 봇 토큰과 chat_id 로드"""
    token, chat_id = "", ""
    
    # 1단계: config.md 파싱 시도
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

    # 2단계: 파싱 실패 시 telegram_setup.json 시도
    if (not token or not chat_id) and os.path.exists(SETUP_JSON):
        try:
            with open(SETUP_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = cfg.get("TELEGRAM_BOT_TOKEN", "").strip()
                chat_id = cfg.get("TELEGRAM_CHAT_ID", "").strip()
        except Exception as e:
            print(f"⚠️ [Bridge] telegram_setup.json 읽기 중 경고: {e}", file=sys.stderr)
            
    return token, chat_id

def send_api_request(token, method, payload=None):
    """requests 라이브러리 사용하되, 없을 경우 내장 urllib.request로 안전하게 폴백"""
    url = f"https://api.telegram.org/bot{token}/{method}"
    headers = {"Content-Type": "application/json"}
    data_bytes = json.dumps(payload).encode("utf-8") if payload else None

    # requests 사용 시도
    try:
        import requests
        if payload is not None:
            r = requests.post(url, json=payload, timeout=20)
        else:
            r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except ImportError:
        # urllib 폴백
        import urllib.request
        import urllib.error
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST" if payload else "GET")
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise Exception(f"HTTPError: {e.code} - {err_body}")
        except Exception as e:
            raise Exception(f"urllib Connection Error: {e}")

def send_approval_request(token, chat_id, action_id, title, description):
    """Inline Keyboard가 달린 승인 메시지를 송신하고 message_id 리턴"""
    message_text = (
        f"🔔 *[결재 대기 승인 요청]*\n\n"
        f"📌 *업무 ID*: `{action_id}`\n"
        f"📋 *제목*: {title}\n"
        f"📄 *상세*: {description}\n\n"
        f"⚠️ 아래 버튼을 눌러 승인 혹은 반려를 최종 결정해 주십시오."
    )
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "승인 👍", "callback_data": f"approve:{action_id}"},
                {"text": "반려 ❌", "callback_data": f"reject:{action_id}"}
            ]
        ]
    }
    
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    
    res = send_api_request(token, "sendMessage", payload)
    if res.get("ok"):
        msg_id = res["result"]["message_id"]
        print(f"✅ [Bridge] 승인 요청 송신 성공! (메시지 ID: {msg_id})")
        return msg_id
    else:
        raise Exception(f"메시지 송신 실패: {res}")

def answer_callback(token, callback_query_id, text):
    """모바일 로딩 스피너 종료를 위한 callback 응답"""
    payload = {
        "callback_query_id": callback_query_id,
        "text": text
    }
    try:
        send_api_request(token, "answerCallbackQuery", payload)
    except Exception as e:
        print(f"⚠️ [Bridge] answerCallbackQuery 경고: {e}", file=sys.stderr)

def edit_message(token, chat_id, message_id, text):
    """메시지 상태 업데이트 (Inline Keyboard 제거)"""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        send_api_request(token, "editMessageText", payload)
    except Exception as e:
        print(f"⚠️ [Bridge] editMessageText 경고: {e}", file=sys.stderr)

def record_approval_result(action_id, status, details=""):
    """승인/반려 결과를 _company/approvals/ 내 파일로 보관"""
    if not os.path.exists(APPROVALS_DIR):
        os.makedirs(APPROVALS_DIR, exist_ok=True)
        
    result_path = os.path.join(APPROVALS_DIR, f"{action_id}.json")
    result_data = {
        "action_id": action_id,
        "status": status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": details
    }
    
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
    print(f"💾 [Bridge] 결재 결과 저장 완료: {result_path}")

def wait_for_approval(token, chat_id, action_id, message_id, title, description, timeout_seconds=300):
    """getUpdates를 롱 폴링하면서 버튼 피드백 대기"""
    print(f"⏳ [Bridge] 사장님의 결재를 기다리는 중... (제한시간 {timeout_seconds}초)")
    start_time = time.time()
    offset = None
    
    # 중복 업데이트 수집을 방지하기 위해, 우선 최근 offset 세팅
    try:
        updates = send_api_request(token, "getUpdates", {"limit": 10})
        if updates.get("ok") and updates["result"]:
            offset = updates["result"][-1]["update_id"] + 1
    except Exception as e:
        print(f"⚠️ [Bridge] 초기 offset 조회 경고: {e}", file=sys.stderr)

    while time.time() - start_time < timeout_seconds:
        try:
            payload = {"timeout": 10, "limit": 10}
            if offset is not None:
                payload["offset"] = offset
                
            res = send_api_request(token, "getUpdates", payload)
            if not res.get("ok"):
                time.sleep(3)
                continue
                
            for update in res["result"]:
                offset = update["update_id"] + 1
                
                # Callback Query(인라인 버튼 클릭) 감시
                if "callback_query" in update:
                    cb = update["callback_query"]
                    cb_data = cb.get("data", "")
                    cb_msg = cb.get("message", {})
                    cb_msg_id = cb_msg.get("message_id")
                    cb_id = cb.get("id")
                    
                    # 내가 보낸 메시지 카드이고, 액션 ID가 부합하는지 체크
                    if cb_msg_id == message_id:
                        if cb_data == f"approve:{action_id}":
                            print("🎉 [Bridge] 사장님 결재 승인 수신 완료! 👍")
                            answer_callback(token, cb_id, "결재가 정상 승인되었습니다.")
                            
                            ok_text = (
                                f"🎉 *[결재 승인 완료]*\n\n"
                                f"📌 *업무 ID*: `{action_id}`\n"
                                f"📋 *제목*: {title}\n"
                                f"📄 *상세*: {description}\n\n"
                                f"✅ *결과*: 사장님께서 승인하셨습니다. (결재일: {time.strftime('%Y-%m-%d %H:%M:%S')})"
                            )
                            edit_message(token, chat_id, message_id, ok_text)
                            record_approval_result(action_id, "approved", "사장님 모바일 직접 승인")
                            return "approved"
                            
                        elif cb_data == f"reject:{action_id}":
                            print("❌ [Bridge] 사장님 결재 반려 수신 완료!")
                            answer_callback(token, cb_id, "결재가 반려되었습니다.")
                            
                            fail_text = (
                                f"❌ *[결재 최종 반려]*\n\n"
                                f"📌 *업무 ID*: `{action_id}`\n"
                                f"📋 *제목*: {title}\n"
                                f"📄 *상세*: {description}\n\n"
                                f"⚠️ *결과*: 사장님께서 반려하셨습니다. (반려일: {time.strftime('%Y-%m-%d %H:%M:%S')})"
                            )
                            edit_message(token, chat_id, message_id, fail_text)
                            record_approval_result(action_id, "rejected", "사장님 모바일 직접 반려")
                            return "rejected"
                            
            time.sleep(3)
        except Exception as e:
            err_msg = str(e)
            if "409" in err_msg or "Conflict" in err_msg:
                print("⚠️ [Bridge] 409 Conflict가 감지되었습니다. 로컬 PC 또는 다른 곳에서 동일한 봇 토큰으로 getUpdates를 롱 폴링 중인 다른 터미널/파이썬 프로세스가 있는지 확인하고 종료해주세요! (5초 후 자동 재시도)", file=sys.stderr)
            else:
                print(f"⚠️ [Bridge] 폴링 중 오류 발생 (재시도 중): {e}", file=sys.stderr)
            time.sleep(5)
            
    # 타임아웃 발생 시 처리
    timeout_text = (
        f"⚠️ *[결재 시간 만료]*\n\n"
        f"📌 *업무 ID*: `{action_id}`\n"
        f"📋 *제목*: {title}\n"
        f"📄 *상세*: {description}\n\n"
        f"⏳ *결과*: 대기 시간({timeout_seconds}초) 초과로 자동 반려 처리되었습니다."
    )
    edit_message(token, chat_id, message_id, timeout_text)
    record_approval_result(action_id, "timeout", "승인 대기 시간 초과")
    print("⏳ [Bridge] 결재 승인 대기 시간이 초과되어 자동 반려 처리되었습니다.")
    return "timeout"

def main():
    parser = argparse.ArgumentParser(description="Telegram 양방향 승인 브릿지 툴")
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
        
    print(f"🚀 [Bridge] 봇 정보 확인 완료. Target Chat ID: {chat_id}")
    
    if args.test:
        print("✨ [Test Mode] 즉시 모바일 승인 요청 카드를 보내고 폴링을 대기합니다.")
        args.action_id = f"test_{int(time.time())}"
        args.title = "🔥 모바일 텔레그램 승인 장치 자가 테스트"
        args.description = "아래의 [승인 👍] 혹은 [반려 ❌] 버튼을 직접 눌러서 수신 브릿지가 무결하게 도는지 최종 검증해주세요."
        args.timeout = 120  # 테스트 모드는 2분 대기
        
    try:
        msg_id = send_approval_request(token, chat_id, args.action_id, args.title, args.description)
        result = wait_for_approval(token, chat_id, args.action_id, msg_id, args.title, args.description, args.timeout)
        print(f"📊 [Bridge] 결재 최종 흐름 처리 결과: {result.upper()}")
        
        # 쉘 리턴코드 관리
        if result == "approved":
            sys.exit(0)
        else:
            sys.exit(2) # 반려/타임아웃은 리턴코드 2
            
    except Exception as e:
        print(f"❌ [Bridge] 프로세스 실행 중 크래시: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
