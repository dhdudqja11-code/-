import pytest
from fastapi.testclient import TestClient
from app.main import app # main 모듈 임포트

# TestClient를 사용하여 API 테스트 환경을 준비합니다.
client = TestClient(app)


def test_successful_avoided_loss_calculation():
    """[SUCCESS] 모든 파라미터가 정상적으로 전달되었을 때의 정상 계산 흐름 검증."""
    payload = {
        "client_id": "TEST_VALID_USER",
        "transaction_value": 1000.0,
        "data_source": "Manual Input", # 규제 리스크가 필수 아님
        "risk_factor_input": {"jurisdiction": "US"}
    }
    calc = {
        "emotional_loss_sensitivity": 2.5,
        "regulatory_risk_score": 0.1,
        "data_integrity_penalty": 0.8
    }

    response = client.post("/api/v1/avoided_loss", json={"input_data": payload, "calc_inputs": calc})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["success"] is True
    # 계산 결과가 0보다 커야 함 (최소한의 손실액)
    assert data["total_avoided_loss"] > 100


def test_error_missing_field_client_id():
    """[FAILURE] 필수 필드(Client ID) 누락 시, 구조화된 오류 메시지 반환 검증."""
    payload = {
        "client_id": "", # 빈 값으로 설정하여 실패 유도
        "transaction_value": 50.0,
        "data_source": "Manual Input",
        "risk_factor_input": {}
    }
    calc = {
        "emotional_loss_sensitivity": 1.0,
        "regulatory_risk_score": 0.0,
        "data_integrity_penalty": 0.5
    }

    response = client.post("/api/v1/avoided_loss", json={"input_data": payload, "calc_inputs": calc})
    assert response.status_code == 400 # Bad Request
    error_detail = response.json()["detail"]["error"]
    # 구조화된 오류 코드와 필드가 반환되는지 확인
    assert error_detail["error_code"] == "E4001"


def test_error_conflicting_data_type():
    """[FAILURE] 데이터 타입이 상충하는 경우 (예: transaction_value에 문자열 전달) 검증."""
    payload = {
        "client_id": "TYPE_ERROR",
        "transaction_value": "NON_FLOAT_DATA", # 잘못된 타입으로 실패 유도
        "data_source": "Manual Input",
        "risk_factor_input": {}
    }
    calc = {
        "emotional_loss_sensitivity": 1.0,
        "regulatory_risk_score": 0.0,
        "data_integrity_penalty": 0.5
    }

    response = client.post("/api/v1/avoided_loss", json={"input_data": payload, "calc_inputs": calc})
    assert response.status_code == 400 # Bad Request
    error_detail = response.json()["detail"]["error"]
    # 구조화된 오류 코드와 필드가 반환되는지 확인
    assert error_detail["error_code"] == "E4002"

def test_error_business_logic_conflict():
    """[FAILURE] 비즈니스 로직상 필수 변수 누락 (Webhook + Risk Score 없음) 검증."""
    payload = {
        "client_id": "WEBHOOK_TEST",
        "transaction_value": 500.0,
        "data_source": "Webhook", # Webhook이므로 risk_factor_input에 점수가 필요함
        "risk_factor_input": {} # 핵심 변수 누락 유도
    }
    calc = {
        "emotional_loss_sensitivity": 2.0,
        # 이 부분이 테스트의 초점: calc_inputs에서 regulatory_risk_score를 None으로 전달
        "regulatory_risk_score": None, 
        "data_integrity_penalty": 1.0
    }

    response = client.post("/api/v1/avoided_loss", json={"input_data": payload, "calc_inputs": calc})
    assert response.status_code == 400 # Bad Request
    error_detail = response.json()["detail"]["error"]
    # 비즈니스 로직 오류 코드가 반환되는지 확인
    assert error_detail["error_code"] == "E4001"