import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

# 로컬 임포트
from .models import ComplianceRequestPayload, AuditLogEntry
from .api_router import detect_and_mask_pii # 핵심 함수 테스트용으로 분리하여 가져옴

# FastAPI 클라이언트 초기화 (실제 서버 실행 없이 테스트 가능)
client = TestClient() 

@pytest.fixture(scope="module")
def mock_user_id():
    """테스트에서 사용할 가상의 사용자 ID Fixture."""
    return "test_user_123"


# --- 테스트 1: PII 감지 및 마스킹 로직 (가장 중요) ---

def test_detect_and_mask_pii_success(mock_user_id):
    """성공 케이스: 이메일과 전화번호를 포함하여 PII가 성공적으로 감지/마스크되는지 검증."""
    raw_data = {
        "name": "John Doe",
        "email": "john.doe@example.com", # PII 1
        "phone": "010-1234-5678",       # PII 2
        "address": "Seoul, Gangnam"     # Safe Data
    }
    masked_data, audit_log = detect_and_mask_pii(raw_data, mock_user_id)

    assert masked_data["email"] == "jXxx.doe@exampX.com" # 첫 글자만 유지 및 마스킹 확인
    assert masked_data["phone"] == "0XXXXXXXX"          # 전화번호 마스크 확인
    assert audit_log is not None                        # 로그 객체가 생성되었는지 확인

def test_detect_and_mask_pii_no_pii(mock_user_id):
    """성공 케이스: PII가 없을 때 원본 데이터가 그대로 유지되는지 검증."""
    raw_data = {
        "name": "Jane Doe",
        "city": "Busan",
        "age": 30
    }
    masked_data, audit_log = detect_and_mask_pii(raw_data, mock_user_id)

    assert masked_data == raw_data                       # 데이터가 원본과 동일해야 함
    assert audit_log is None                              # 로그 객체가 null이어야 함

def test_detect_and_mask_pii_single_pii(mock_user_id):
    """성공 케이스: SSN 유사 패턴만 있을 때 감지되는지 검증."""
    raw_data = {
        "key": "value",
        "ssn": "999-00-1234" # PII 3
    }
    masked_data, audit_log = detect_and_mask_pii(raw_data, mock_user_id)

    assert masked_data["ssn"] == "Xxx-XX-XXXX"          # SSN 마스킹 확인
    assert audit_log is not None


# --- 테스트 2: API End-to-End 통합 검증 ---

def test_api_endpoint_compliant(mock_user_id):
    """PII가 없는 경우, 엔드포인트 호출 및 성공 응답을 검증합니다."""
    payload = ComplianceRequestPayload(
        request_id="R1", 
        data_source="TestModule", 
        payload={"name": "Tester", "score": 95}
    )
    response = client.post("/pii/gateway/track", json=payload.dict(), headers={"X-User-ID": mock_user_id})

    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] == True
    # audit log 필드는 None이거나 비어 있어야 함 (실제로는 응답 모델에 None으로 포함됨)


def test_api_endpoint_non_compliant(mock_user_id):
    """PII가 있는 경우, 엔드포인트 호출 및 경고/마스킹된 응답을 검증합니다."""
    payload = ComplianceRequestPayload(
        request_id="R2", 
        data_source="UserInputForm", 
        payload={"name": "Violation User", "email": "secret@leak.com"} # PII 포함
    )
    # 헤더를 통해 user_id를 강제 주입하여 테스트 환경을 시뮬레이션합니다.
    response = client.post("/pii/gateway/track", json=payload.dict(), headers={"X-User-ID": mock_user_id})

    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] == False
    # 마스크된 데이터가 응답에 포함되어야 함
    assert "secret@leak.com" not in str(data["masked_data"])