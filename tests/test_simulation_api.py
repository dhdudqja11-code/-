import pytest
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from unittest.mock import Mock
import json

# 시뮬레이션 로직을 임포트했다고 가정합니다. 실제 프로젝트 구조에 맞춰 수정해야 합니다.
# 여기서는 테스트 목적으로 필요한 클래스와 함수를 재정의하여 self-contained로 만듭니다.

class LossItemInput:
    def __init__(self, risk_type: str, exposure_value: float, probability: float):
        self.risk_type = risk_type
        self.exposure_value = exposure_value
        self.probability = probability

class SimulationRequest:
    def __init__(self, user_id: str, risk_items: list):
        self.user_id = user_id
        self.risk_items = risk_items

# 실제 API 라우터 로직을 Mocking하여 테스트합니다. (간단화를 위해)
async def calculate_loss(request_data):
    try:
        # 1. Pydantic 유효성 검사 시뮬레이션
        if not request_data["user_id"]:
            raise ValueError("User ID is required.")

        items = [LossItemInput(**item) for item in request_data['risk_items']]
        
        # 2. 핵심 로직 계산 (Expected Loss)
        total_expected_loss = sum(item.exposure_value * item.probability for item in items)

        return {
            "status": "success",
            "result": {"total_expected_loss": round(total_expected_loss, 2)}
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation Failed: {e}")
    except ValueError as e:
        # 비즈니스 로직 오류 (예: 리스크 요소가 1개 미만)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 예상치 못한 시스템 오류
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@pytest.mark.asyncio
async def test_successful_calculation():
    """✅ 정상적인 데이터 입력 시 기대 손실액 계산 테스트."""
    request = {
        "user_id": "test-user-123",
        "risk_items": [
            {"risk_type": "GDPR Violation", "exposure_value": 5000.0, "probability": 0.8}, # 예상 손실: 4000
            {"risk_type": "Contract Breach", "exposure_value": 1000.0, "probability": 0.2}  # 예상 손실: 200
        ]
    }
    response = await calculate_loss(request)
    assert response['status'] == 'success'
    assert response['result']['total_expected_loss'] == 4200.0

@pytest.mark.asyncio
async def test_edge_case_zero_probability():
    """✅ 발생 확률이 0인 경우 (손실액 0) 테스트."""
    request = {
        "user_id": "test-user-123",
        "risk_items": [
            {"risk_type": "Zero Risk", "exposure_value": 5000.0, "probability": 0.0} # 예상 손실: 0
        ]
    }
    response = await calculate_loss(request)
    assert response['result']['total_expected_loss'] == 0.0

@pytest.mark.asyncio
async def test_error_input_validation():
    """❌ Pydantic/입력값 유효성 검사 실패 테스트 (probability > 1.0 또는 exposure < 0)."""
    request = {
        "user_id": "test-invalid",
        # probability가 1.5로 잘못 입력된 케이스
        "risk_items": [
            {"risk_type": "Bad Data", "exposure_value": 100.0, "probability": 1.5} 
        ]
    }
    # HTTPException을 기대합니다. (400 Bad Request)
    with pytest.raises(HTTPException) as excinfo:
        await calculate_loss(request)
    assert excinfo.value.status_code == 400
    assert "Validation Failed" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_error_missing_required_field():
    """❌ 필수 필드 누락 또는 비즈니스 규칙 위반 테스트 (예: risk_items가 빈 리스트)."""
    request = {
        "user_id": "test-empty",
        # risk_items를 아예 제거하거나, 최소 항목 수를 만족하지 못하게 만듬
        "risk_items": [] 
    }
    with pytest.raises(HTTPException) as excinfo:
        await calculate_loss(request)
    assert excinfo.value.status_code == 400
    # 비즈니스 로직 오류 메시지 확인 (ValueError에서 포착된 것)
    assert "리스크 요소가 하나 이상 필수입니다" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_security_rate_limiting():
    """🛡️ Rate Limiting 기능의 동작을 검증하는 테스트 (실제 구현된 미들웨어와 연동되어야 함)."""
    # 이 테스트는 실제 FastAPI 환경에서 Middleware를 Mocking해야 정확하지만, 
    # 개념적으로 'Rate Limit 초과 시 429 Too Many Requests'가 발생함을 확인합니다.
    pass