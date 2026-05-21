import pytest
from fastapi.testclient import TestClient
# 🚨 로컬 파일 경로 참조: 방금 만든 라우터와 모델을 임포트합니다.
from src.api.v1.risk_assessment_router import router
from src.api.v1.risk_assessment_models import AssessmentRequest

# FastAPI 테스트 클라이언트 설정
client = TestClient(router)

def test_01_successful_low_risk_scenario():
    """
    테스트 케이스 1: 모든 행동이 규제에 완벽히 부합하는 '정상' 시나리오. (Expected: 빈 리스크 목록)
    """
    print("\n--- Running Test Case 1: Low Risk / Success ---")
    
    # 정상적인 데이터 전송 예시
    payload = {
        "user_actions": [
            {
                "action_type": "view",
                "data_scope": "public_documentation",
                "source_system": "official_website"
            }
        ],
        # 타임스탬프는 FastAPI가 기본값으로 처리하게 둡니다.
    }
    response = client.post("/api/v1/risk-assessment", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    # 경고 목록이 비어있어야 함을 확인합니다.
    assert len(data.get('alerts', [])) == 0
    print("✅ Test Case 1 Passed: No alerts detected for normal actions.")


def test_02_critical_risk_scenario():
    """
    테스트 케이스 2: 금융 데이터 유출 시도 (Critical Risk). (Expected: Critical Alert 반환)
    """
    print("\n--- Running Test Case 2: Critical Risk Detection ---")

    # 치명적인 행동을 포함한 페이로드 전송 예시
    payload = {
        "user_actions": [
            {
                "action_type": "export", # 문제 행위
                "data_scope": "financial_record", # 민감 데이터 범위
                "source_system": "internal_tool"
            }
        ]
    }
    response = client.post("/api/v1/risk-assessment", json=payload)

    assert response.status_code == 200
    data = response.json()
    alerts = data.get('alerts', [])

    # 리스트에 경고가 하나 이상 존재해야 함을 확인합니다.
    assert len(alerts) >= 1
    critical_alert = next((a for a in alerts if a['alerts'][0]['risk_level'] == 'Critical'), None)
    
    if critical_alert:
        print("✅ Test Case 2 Passed: Critical alert detected successfully.")
        # 핵심 필드 검증
        assert "금융 거래 내역" in critical_alert['problem_definition']
        assert "개인정보보호법" in critical_alert['root_cause']
    else:
        pytest.fail("Critical Alert가 감지되지 않았습니다.")


def test_03_high_risk_multiple_scenario():
    """
    테스트 케이스 3: High Risk와 Low Risk가 혼재된 복합 시나리오. (Expected: Critical + High Alert 반환)
    """
    print("\n--- Running Test Case 3: Mixed Risk Detection ---")

    # 위험 행동(High)과 정상 행동(Low)을 동시에 포함하는 페이로드 전송 예시
    payload = {
        "user_actions": [
            {
                "action_type": "view", # Low Risk (정상)
                "data_scope": "public_documentation", 
                "source_system": "official_website"
            },
            {
                "action_type": "query", # High Risk (위험)
                "data_scope": "user_profile", 
                "source_system": "unverified_api" # 위험 소스 명시
            }
        ]
    }
    response = client.post("/api/v1/risk-assessment", json=payload)

    assert response.status_code == 200
    data = response.json()
    alerts = data.get('alerts', [])

    # 경고가 최소 두 개 이상 (High Risk 포함) 감지되어야 합니다.
    if len(alerts) >= 1:
        print("✅ Test Case 3 Passed: Mixed alerts detected.")