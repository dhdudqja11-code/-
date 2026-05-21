import requests
import json
from typing import Dict, Any

# --- 설정 상수 (실제 환경에 맞게 수정 필요) ---
API_URL = "http://localhost:8000/api/v1/avoided_loss" # 가정된 FastAPI 엔드포인트
HEADERS = {"Content-Type": "application/json"}

def run_test_case(description: str, payload: Dict[str, Any]):
    """
    주어진 페이로드로 Avoided Loss API를 호출하고 결과를 출력합니다.
    API 응답 구조화 및 오류 처리를 시연하는 핵심 함수입니다.
    """
    print("=" * 70)
    print(f"🔍 [테스트 케이스]: {description}")
    print("-" * 70)

    try:
        # API 호출 실행
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        # 응답 상태 코드 확인 (HTTP 레벨 검증)
        if response.status_code == 200:
            result = response.json()
            print("✅ [성공]: API 호출 성공 (Status 200)")
            print(f"   -> 계산된 Avoided Loss: {result.get('avoided_loss', 'N/A'):,.0f} 원")
            print("\n--- 구조화된 응답 JSON ---")
            print(json.dumps(result, indent=4, ensure_ascii=False))
        else:
            # 2xx 외의 모든 실패 케이스 (Validation Error 등) 처리
            try:
                error_details = response.json()
            except json.JSONDecodeError:
                 error_details = {"detail": "Non-JSON Response Body"}

            print(f"❌ [실패]: API 호출 실패 (Status {response.status_code})")
            print("   -> 서버가 반환한 오류 구조:")
            # FastAPI의 Pydantic Validation Error는 리스트 형태를 띱니다. 이를 명확히 보여줍니다.
            if isinstance(error_details, list) and error_details:
                 print(json.dumps(error_details, indent=4, ensure_ascii=False))
            else:
                print(json.dumps(error_details, indent=4, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("🚨 [FATAL ERROR]: API 서버에 연결할 수 없습니다. (HTTP 503 Service Unavailable)")
        print("   -> 이 코드를 실행하려면 'app/main.py'가 정상적으로 구동되어야 합니다.")


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Avoided Loss API E2E 통합 시연 클라이언트 시작")
    print(f"   (대상 엔드포인트: {API_URL})")
    print("=" * 80 + "\n")

    # 1. 성공 케이스 (Happy Path): 모든 필수 변수가 완벽하게 주입된 경우
    success_payload = {
        "financial_loss": 500000,  # 예: 규제 벌금 예상액
        "emotional_stress_factor": 0.7, # 예: 데이터 유출로 인한 신뢰도 하락 계수 (0~1)
        "time_urgency_score": 0.9, # 예: 시장 변화 속도에 따른 긴급성 점수 (0~1)
        "asset_value": 12000000    # 예: 현재 자산 가치 (기준점)
    }
    run_test_case("🟢 Case 1: 정상 작동 (Success Path)", success_payload)

    print("\n\n" + "#" * 80)

    # 2. 실패 케이스 A: 필수 필드 누락 (Data Missing Validation)
    failure_missing_payload = {
        "financial_loss": 500000,  # 'emotional_stress_factor' 누락
        "time_urgency_score": 0.9,
        "asset_value": 12000000
    }
    run_test_case("🟡 Case 2: 필수 필드 누락 (Missing Field Error)", failure_missing_payload)

    print("\n\n" + "#" * 80)

    # 3. 실패 케이스 B: 데이터 타입 불일치 (Type Mismatch Validation)
    failure_type_payload = {
        "financial_loss": "Five hundred thousand", # 문자열을 넣음 -> 숫자여야 함
        "emotional_stress_factor": 0.7,
        "time_urgency_score": 0.9,
        "asset_value": 12000000
    }
    run_test_case("🔴 Case 3: 데이터 타입 불일치 (Type Error)", failure_type_payload)

# 스크립트의 목적은 API 계약과 예외 처리 구조를 완벽히 시연하는 것입니다.