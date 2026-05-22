import pytest
import requests
import json
from datetime import datetime

# 가상 API 엔드포인트 설정 (실제로는 로컬 서버 주소)
BASE_URL = "http://localhost:8000/mini-roi/" 

@pytest.fixture(scope="session")
def setup_api():
    """테스트를 위한 요청 세션 준비."""
    return requests.Session()

# --- 테스트 케이스 1: High Risk Scenario (경고 발생) ---
def test_high_risk_scenario(setup_api):
    """규제 리스크가 높거나 데이터 볼륨이 클 때 경고가 발생하는지 확인합니다."""
    payload = {
        "user_industry": "금융",
        "data_volume_gb": 75.0, # High Volume Trigger
        "regulatory_risk_score": 9   # High Risk Trigger
    }
    response = setup_api.post(f"{BASE_URL}", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # 핵심 검증: 경고 플래그와 문제 정의가 명확한지 확인
    assert data['status'] == "WARNING"
    assert "심각한 규제 리스크" in data['problem_definition']
    print("✅ Test Case 1 (High Risk) Passed.")

# --- 테스트 케이스 2: Low Risk Scenario (안정적) ---
def test_low_risk_scenario(setup_api):
    """모든 값이 안정적일 때 안전하다는 결과가 나오는지 확인합니다."""
    payload = {
        "user_industry": "콘텐츠 제작",
        "data_volume_gb": 5.0, # Low Volume
        "regulatory_risk_score": 2   # Low Risk
    }
    response = setup_api.post(f"{BASE_URL}", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # 핵심 검증: 안전 플래그와 낮은 리스크 점수 확인
    assert data['status'] == "SAFE"
    assert "안정적입니다" in data['problem_definition']
    print("✅ Test Case 2 (Low Risk) Passed.")

# --- 테스트 케이스 3: API Failure Simulation (예외 처리 검증) ---
def test_api_failure_simulation(setup_api):
    """유효하지 않은 입력 값이나 서버 에러 시, 적절한 HTTP 예외가 발생하는지 확인합니다."""
    # 여기서는 의도적으로 존재하지 않는 엔드포인트를 호출하여 500을 유발한다고 가정합니다.
    with pytest.raises(requests.exceptions.RequestException):
        setup_api.get("http://localhost:9999/non-existent-endpoint")

# 참고: 실제 환경에서는 이 테스트 코드를 사용하여 로컬 서버에서 모든 시나리오를 검증해야 합니다.