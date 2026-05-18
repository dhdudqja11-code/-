#!/usr/bin/env python3
"""마음을 묻다 - 자율 운영 일일 브리핑 스크립트 (daily_briefing.py)

본 스크립트는 백엔드에 기록된 `traffic_log.json`과 `reviews.json` 데이터를 수집하여,
오늘의 일일 방문자 수와 사용자 피드백(리뷰)을 요약한 뒤 대표님의 텔레그램으로 자동 브리핑을 전송합니다.
"""

import os
import json
import requests
from datetime import datetime

# 경로 설정
HERE = os.path.dirname(os.path.abspath(__file__))
TRAFFIC_FILE = os.path.join(HERE, 'traffic_log.json')
REVIEWS_FILE = os.path.join(HERE, 'reviews.json')

# 텔레그램 설정 파일 경로 (Secretary 에이전트 설정 공유)
TELEGRAM_SETUP_PATH = os.path.join(HERE, '..', '_company', '_agents', 'secretary', 'tools', 'telegram_setup.json')

def load_json(filepath, default_val):
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ {filepath} 읽기 오류: {e}")
        return default_val

def get_telegram_config():
    """텔레그램 봇 토큰 및 챗 ID 로드"""
    if os.path.exists(TELEGRAM_SETUP_PATH):
        try:
            with open(TELEGRAM_SETUP_PATH, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                return cfg.get('TELEGRAM_BOT_TOKEN'), cfg.get('TELEGRAM_CHAT_ID')
        except Exception as e:
            print(f"⚠️ 텔레그램 설정 파일 읽기 실패: {e}")
    
    # 예외 대비 환경 변수 또는 직접 입력 값 대비 (Fallback)
    return None, None

def generate_briefing():
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 트래픽 데이터 요약
    traffic_data = load_json(TRAFFIC_FILE, {})
    today_visits = traffic_data.get(today, 0)
    total_visits = sum(traffic_data.values())
    
    # 2. 리뷰 데이터 요약
    reviews = load_json(REVIEWS_FILE, [])
    today_reviews = []
    
    for r in reviews:
        # timestamp 형식: '2026-05-18T12:34:56.789012'
        try:
            r_date = r.get('timestamp', '').split('T')[0]
            if r_date == today:
                today_reviews.append(r)
        except Exception:
            continue
            
    avg_rating = 0.0
    if today_reviews:
        avg_rating = sum(float(r.get('rating', 5)) for r in today_reviews) / len(today_reviews)
    
    # 3. 브리핑 텍스트 빌드
    brief_lines = [
        "🌅 *마음을 묻다 — 일일 운영 브리핑*",
        f"날짜: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}",
        "",
        "📈 *트래픽 통계*",
        f"• 오늘 방문자 수: `{today_visits}` 명",
        f"• 누적 방문자 수: `{total_visits}` 명",
        "",
        "⭐️ *사용자 피드백 (리뷰)*",
        f"• 오늘 접수된 리뷰: `{len(today_reviews)}` 건",
    ]
    
    if today_reviews:
        brief_lines.append(f"• 오늘 평균 평점: `★ {avg_rating:.1f} / 5.0`")
        brief_lines.append("")
        brief_lines.append("💬 *오늘의 생생한 목소리:*")
        for i, rev in enumerate(today_reviews[:5], 1): # 최대 5개까지만 표시
            rating_stars = "★" * int(float(rev.get('rating', 5)))
            content = rev.get('content', '').replace('\n', ' ').strip()
            if len(content) > 60:
                content = content[:60] + "..."
            brief_lines.append(f"{i}. {rating_stars} | \"{content}\"")
    else:
        brief_lines.append("• _오늘은 아직 접수된 리뷰가 없습니다._")
        
    brief_lines.extend([
        "",
        "✨ *오늘 하루도 고생 많으셨습니다, 대표님!*",
        "무거운 마음에 빛을 밝히는 여정은 계속됩니다."
    ])
    
    return "\n".join(brief_lines)

def send_telegram_briefing(text):
    token, chat_id = get_telegram_config()
    if not token or not chat_id:
        print("❌ 텔레그램 설정(Token 또는 Chat ID)을 찾을 수 없습니다. 브리핑 전송을 취소합니다.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        print("✅ 텔레그램 데일리 브리핑 발송 성공!")
        return True
    except Exception as e:
        print(f"❌ 텔레그램 발송 실패: {e}")
        return False

def main():
    print("--- 마음을 묻다: Daily Briefing Generator ---")
    brief_text = generate_briefing()
    print("\n[생성된 브리핑 미리보기]")
    print(brief_text)
    print("\n-------------------------")
    
    send_telegram_briefing(brief_text)

if __name__ == "__main__":
    main()
