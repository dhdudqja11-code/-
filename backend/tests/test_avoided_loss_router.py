import pytest
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_successful_avoided_loss_calculation():
    """[성공 케이스] 모든 필드가 유효하고 계산이 정상적으로 완료되는지 테스트합니다."""
    # Mock 성공 데이터 설정 (실제 값 사용 필요)
    valid_payload = {
        "input_risk_data": {
            "transaction_id": "txn_12345", 
            "source_system": "PayPal", 
            "verification_time": "2026-05-20T10:00:00Z",
            "raw_data_payload": {"amount": 100, "status": "success"}
        },
        "user_profile": {"tier": "Pro", "history_score": 85}
    }

    # 요청 전송 및 상태 코드 확인 (HTTP 200 OK 예상)
    response = client.post("/api/v1/avoided_loss", json=valid_payload)
    assert response.status_code == 200
    # 응답 본문에서 핵심 리포트 필드가 포함되는지 검증합니다.
    assert "Avoided Loss Report" in response.json().get("report")

def test_e001_missing_required_field():
    """[실패 케이스] 필수 입력 필드(예: source_system)가 누락되었을 때 422 Unprocessable Entity를 반환하는지 테스트합니다."""
    # 'source_system' 필드를 의도적으로 제거한 불완전한 페이로드
    invalid_payload = {
        "input_risk_data": {
            "transaction_id": "txn_12345", 
            # source_system 누락
            "verification_time": "2026-05-20T10:00:00Z",
            "raw_data_payload": {"amount": 100, "status": "success"}
        },
        "user_profile": {"tier": "Pro", "history_score": 85}
    }

    response = client.post("/api/v1/avoided_loss", json=invalid_payload)
    # FastAPI는 Pydantic 유효성 검사 실패 시 일반적으로 422를 반환합니다.
    assert response.status_code == 422
    # 에러 메시지 구조 확인 (어떤 필드가 누락되었는지 명시되어야 함)
    assert "source_system" in str(response.json())

def test_e001_incorrect_data_type():
    """[실패 케이스] 데이터 타입이 잘못된 경우 (예: ID가 숫자로 들어옴) 422를 반환하는지 테스트합니다."""
    invalid_payload = {
        "input_risk_data": {
            "transaction_id": 12345, # 문자열이어야 하는데 정수형으로 전달
            "source_system": "PayPal", 
            "verification_time": "2026-05-20T10:00:00Z",
            "raw_data_payload": {"amount": 100, "status": "success"}
        },
        "user_profile": {"tier": "Pro", "history_score": 85}
    }

    response = client.post("/api/v1/avoided_loss", json=invalid_payload)
    assert response.status_code == 422
# 이 테스트 파일은 라우터가 성공적으로 Pydantic 스키마를 사용하여 검증하는지 확인합니다.