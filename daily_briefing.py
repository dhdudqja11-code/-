import os
import json
import requests
from datetime import datetime

# 📱 텔레그램 봇 API 설정 정보 (영숙 비서 전용 config 기준)
TELEGRAM_BOT_TOKEN = "8729092796:AAG9YSMusBSoPh95-QgxC_tqhaPmi97dosA"
TELEGRAM_CHAT_ID = "8834036171"

# 데이터 파일 경로 설정
TRAFFIC_LOG_PATH = os.path.join(os.path.dirname(__file__), 'traffic_log.json')
REVIEWS_PATH = os.path.join(os.path.dirname(__file__), 'reviews.json')

# 요금제별 매출 매핑 테이블
TIER_PRICES = {
    "Free": 0,
    "Random": 0,
    "Beta": 5000,
    "Deep": 9000,
    "Recovery": 29000,
    "Gift": 12000
}

def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        return default_data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_data

def get_day_of_week_korean():
    weeks = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    return weeks[datetime.now().weekday()]

def generate_and_send_briefing():
    print("--- Telegram Daily Briefing System Initiating ---")
    
    # 1. 오늘 날짜 포맷
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_display = f"{today_str} ({get_day_of_week_korean()})"
    
    # 2. 로컬 트래픽 DB 읽기
    traffic_data = load_json(TRAFFIC_LOG_PATH, {})
    today_visits = traffic_data.get(today_str, 0)
    
    # 3. 로컬 리뷰/처방 DB 읽기
    reviews_data = load_json(REVIEWS_PATH, [])
    
    today_reviews = []
    today_revenue = 0
    today_sales_count = 0
    
    for item in reviews_data:
        # timestamp 파싱 및 비교
        timestamp_str = item.get('timestamp', '')
        if timestamp_str:
            try:
                # ISO 포맷 타임스탬프에서 날짜만 추출
                item_date = timestamp_str.split('T')[0]
                if item_date == today_str:
                    today_reviews.append(item)
                    # 요금제 등급별 매출 합계 계산
                    tier = item.get('tier', 'Free')
                    price = TIER_PRICES.get(tier, 0)
                    today_revenue += price
                    if price > 0:
                        today_sales_count += 1
            except Exception as e:
                print(f"Timestamp parsing error: {e}")
                
    # 4. 만족도 지표 및 감상평 요약
    review_count = len(today_reviews)
    avg_rating = 0.0
    valuable_feedbacks = []
    
    if review_count > 0:
        ratings_sum = sum(int(r.get('rating', 5)) for r in today_reviews)
        avg_rating = round(ratings_sum / review_count, 1)
        
        # 4점 또는 5점짜리 감동 피드백 발췌 (최대 5건)
        for r in today_reviews:
            rating = r.get('rating', 5)
            text = r.get('review', '').strip()
            tier = r.get('tier', 'Free')
            if rating >= 4 and text:
                valuable_feedbacks.append(f"• \"{text}\" ({tier} 등급 / ⭐{rating}점)")
                if len(valuable_feedbacks) >= 5:
                    break
                    
    # 5. 브리핑 텍스트 카드 조제 (아날로그 감성)
    message_lines = [
        "🌿 *[마음을 묻다] 오늘의 힐링 비즈니스 브리핑 카드* 💌",
        "",
        "\"오늘도 누군가의 지친 내면에 따뜻한 손을 내밀었습니다.\"",
        "━━━━━━━━━━━━━━━━━━",
        f"📅 *일자*: {today_display}",
        "",
        f"👥 *오늘의 방문자*: `{today_visits}` 명 (마음의 문을 두드린 이들)",
        f"💰 *오늘의 매출*: `₩{today_revenue:,}` 원 ({today_sales_count}건 유료 처방 완료)",
        "",
        f"⭐️ *심리 처방 만족도*: `{avg_rating} / 5.0` ({review_count}명 피드백 참여)",
        ""
    ]
    
    if valuable_feedbacks:
        message_lines.append("🌿 *[생생한 치유의 목소리]*")
        message_lines.extend(valuable_feedbacks)
    else:
        message_lines.append("🌿 *[치유의 소리]*: 오늘 접수된 한줄평이 아직 없습니다.")
        
    message_lines.extend([
        "━━━━━━━━━━━━━━━━━━",
        "💡 _대표님의 시적 철학이 오늘도 누군가의 번아웃을 어루만졌습니다. 평온한 밤 되세요._"
    ])
    
    full_message = "\n".join(message_lines)
    
    # 6. 텔레그램 발송 요청
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": full_message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        if response.status_code == 200:
            print(">>> [SUCCESS] Telegram Daily Briefing Card sent successfully!")
            return True
        else:
            print(f">>> [FAIL] Telegram API error (Code {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f">>> [ERROR] Exception occurred during telegram sending: {e}")
        return False

if __name__ == '__main__':
    generate_and_send_briefing()
