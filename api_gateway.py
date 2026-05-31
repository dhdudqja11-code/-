import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Next.js 프론트엔드 컴포넌트와의 E2E CORS 통신 보장

# 로컬 JSON 데이터베이스 파일 경로 설정
TRAFFIC_LOG_PATH = os.path.join(os.path.dirname(__file__), 'traffic_log.json')
REVIEWS_PATH = os.path.join(os.path.dirname(__file__), 'reviews.json')

def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        return default_data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_data

def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False

@app.route('/api/track/visit', methods=['POST', 'GET'])
def track_visit():
    """
    웹사이트 접속 시 방문자 수를 실시간 기록하는 API 엔드포인트
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    traffic_data = load_json(TRAFFIC_LOG_PATH, {})
    
    # 오늘 날짜 접속자 수 증가
    traffic_data[today_str] = traffic_data.get(today_str, 0) + 1
    
    if save_json(TRAFFIC_LOG_PATH, traffic_data):
        return jsonify({
            "status": "success",
            "date": today_str,
            "today_visits": traffic_data[today_str]
        }), 200
    else:
        return jsonify({"status": "error", "message": "Failed to write traffic log"}), 500

@app.route('/api/track/review', methods=['POST'])
def track_review():
    """
    처방전 발급 완료 후 유저의 별점 및 치유 감상평을 수집하는 API 엔드포인트
    """
    try:
        req_data = request.get_json() or {}
        rating = req_data.get('rating')  # 1 ~ 5 점
        review_text = req_data.get('review', '').strip()
        tier = req_data.get('tier', 'Free')  # Free, Beta, Deep, Recovery, Gift 등
        
        if rating is None:
            return jsonify({"status": "error", "message": "Rating is required"}), 400
            
        reviews_data = load_json(REVIEWS_PATH, [])
        
        new_review = {
            "rating": int(rating),
            "review": review_text,
            "tier": tier,
            "timestamp": datetime.now().isoformat()
        }
        reviews_data.append(new_review)
        
        if save_json(REVIEWS_PATH, reviews_data):
            return jsonify({
                "status": "success",
                "message": "Review recorded successfully",
                "review": new_review
            }), 200
        else:
            return jsonify({"status": "error", "message": "Failed to write review log"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("====================================================")
    print("--- 'Asking the Heart' AI 1-Person Company API Gateway ---")
    print(f"Local DB Paths:")
    print(f"   - Traffic Log: {TRAFFIC_LOG_PATH}")
    print(f"   - Review Log: {REVIEWS_PATH}")
    print("====================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
