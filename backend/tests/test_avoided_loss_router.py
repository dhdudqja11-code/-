import pytest
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_successful_avoided_loss_calculation():
    """[성공 케이스] 모든 필드가 유효하고 계산이 정상적으로 완료되는지 테스트합니다."""
    valid_payload = {
        "input_data": {
            "client_id": "test_client_abc", 
            "transaction_value": 10000.0, 
            "data_source": "Manual",
            "risk_factor_input": {"jurisdiction": "EU"}
        },
        "calc_inputs": {
            "emotional_loss_sensitivity": 1.5,
            "regulatory_risk_score": 0.3,
            "data_integrity_penalty": 1.0
        }
    }

    # 요청 전송 및 상태 코드 확인 (HTTP 200 OK 예상)
    response = client.post("/api/v1/avoided_loss", json=valid_payload)
    assert response.status_code == 200
    # 응답 본문에서 핵심 리포트 필드가 포함되는지 검증합니다.
    data = response.json().get("data")
    assert data is not None
    assert "total_avoided_loss" in data
    assert "key_risk_area" in data

def test_e001_missing_required_field():
    """[실패 케이스] 필수 입력 필드(예: client_id)가 누락되었을 때 400 Bad Request (E4001)를 반환하는지 테스트합니다."""
    invalid_payload = {
        "input_data": {
            # client_id 누락
            "transaction_value": 10000.0, 
            "data_source": "Manual",
            "risk_factor_input": {"jurisdiction": "EU"}
        },
        "calc_inputs": {
            "emotional_loss_sensitivity": 1.5,
            "regulatory_risk_score": 0.3,
            "data_integrity_penalty": 1.0
        }
    }

    response = client.post("/api/v1/avoided_loss", json=invalid_payload)
    # app/main.py는 RequestValidationError를 400으로 매핑합니다.
    assert response.status_code == 400
    err = response.json().get("detail", {}).get("error", {})
    assert err.get("error_code") == "E4001"
    assert "client_id" in err.get("failed_field", "")

def test_e001_incorrect_data_type():
    """[실패 케이스] 데이터 타입이 잘못된 경우 (예: client_id가 숫자로 들어옴) 400 (E4002)를 반환하는지 테스트합니다."""
    invalid_payload = {
        "input_data": {
            "client_id": 12345, # 문자열이어야 하는데 정수형으로 전달 (Pydantic V2는 숫자->문자 변환이 되므로 string constraint 혹은 다른 타입 비교)
            "transaction_value": "not-a-number", # 확실히 타입 위반되도록 숫자에 문자열 전달
            "data_source": "Manual",
            "risk_factor_input": {"jurisdiction": "EU"}
        },
        "calc_inputs": {
            "emotional_loss_sensitivity": 1.5,
            "regulatory_risk_score": 0.3,
            "data_integrity_penalty": 1.0
        }
    }

    response = client.post("/api/v1/avoided_loss", json=invalid_payload)
    assert response.status_code == 400
    err = response.json().get("detail", {}).get("error", {})
    assert err.get("error_code") == "E4002"