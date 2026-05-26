from fastapi.testclient import TestClient
from datetime import datetime
import unittest
import os

# 로컬 경로에서 FastAPI 앱을 임포트합니다. (실제 프로젝트 구조에 맞게 조정 필요)
try:
    from src.api.audit_router import app, TransactionData, AuditBlock
except ImportError:
    print("Warning: Could not import API components. Assuming local execution context.")

client = TestClient(app)


class TestAuditGatewayAPI(unittest.TestCase):
    """
    Immutable Audit Gateway의 전체 흐름 (성공/실패/보안 위협)을 테스트합니다.
    """

    @unittest.skip("Mock JWT 토큰이 필요하며, 실제 환경 변수 설정 후 실행 권장.")
    def test_01_successful_transaction(self):
        """[CASE 1] 정상적인 트랜잭션 데이터가 들어왔을 때의 성공 케이스 검증."""
        # 가짜 Bearer Token (성공 케이스 시뮬레이션)
        fake_token = "Bearer secure.jwt.token" 
        payload = {"item_id": 456, "price": 99.99}
        data = {"source": "Webhook", "data_payload": payload, "user_action": "purchase"}

        # FastAPI TestClient는 의존성 주입(Depends)을 오버라이드할 수 있어야 합니다.
        # 여기서는 Mocking을 가정하고 요청을 보냅니다. (실제 테스트 환경에서 구현 필요)
        response = client.post(
            "/v1/audit/process", 
            json={"source": data["source"], "data_payload": data["data_payload"], "user_action": data["user_action"]},
            headers={"Authorization": fake_token} # 인증 헤더 전달 시도
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertIn('TX-', result['transaction_id'])
        print("✅ Test Case 1: Success Check Passed.")


    @unittest.skip("Mock JWT 토큰이 필요하며, 실제 환경 변수 설정 후 실행 권장.")
    def test_02_security_alert_illegal_action(self):
        """[CASE 2] 시스템에 법적 리스크가 있는 비정상적인 트랜잭션 케이스 검증."""
        # 'illegal_action'을 포함하여 IAG 로직에서 실패하도록 유도합니다.
        fake_token = "Bearer secure.jwt.token"
        payload = {"item_id": 999, "risk_level": "high"}
        data = {"source": "ManualAPI", "data_payload": payload, "user_action": "illegal_action"}

        response = client.post(
            "/v1/audit/process", 
            json={"source": data["source"], "data_payload": data["data_payload"], "user_action": data["user_action"]},
            headers={"Authorization": fake_token}
        )

        self.assertEqual(response.status_code, 200) # API 자체는 200을 반환하지만, 내용은 실패여야 함.
        result = response.json()
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 403) # IAG 내부에서 정의된 실패 코드
        self.assertIn("SECURITY ALERT", result['message'])
        print("✅ Test Case 2: Security Alert Check Passed.")


    @unittest.skip("Mock JWT 토큰이 필요하며, 실제 환경 변수 설정 후 실행 권장.")
    def test_03_invalid_jwt_authentication(self):
        """[CASE 3] 인증(JWT) 실패 케이스 검증 (401 Unauthorized)."""
        # 유효하지 않은/누락된 토큰을 사용합니다.
        response = client.post(
            "/v1/audit/process", 
            json={"source": "ManualAPI", "data_payload": {}, "user_action": "test"},
            headers={"Authorization": "Bearer invalid_token"} # 유효하지 않은 토큰 전달
        )

        # FastAPI의 HTTPException이 걸러지므로, status code가 달라야 합니다.
        self.assertEqual(response.status_code, 401)
        result = response.json()
        self.assertIn("Authentication failed", result['detail'])
        print("✅ Test Case 3: JWT Auth Fail Check Passed.")


if __name__ == "__main__":
    # 테스트 실행 방법 (터미널에서 pytest 또는 python test_audit_api.py)
    unittest.main()