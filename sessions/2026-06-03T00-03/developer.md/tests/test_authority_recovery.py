import unittest
from src.remote_access_service import connect_remote, execute_command, stream_data

class TestAuthorityRecovery(unittest.TestCase):
    """
    원격 제어 모듈의 복구 플로우를 테스트합니다. 
    단순 에러 발생이 아닌 '권위적 처리'가 핵심입니다.
    """

    def test_connection_failure_recovery(self):
        print("\n--- Testing Connection Failure (Authority Check) ---")
        # 가짜 크리덴셜로 실패 유도
        result = connect_remote("bad-creds:123")
        # 성공 케이스가 아닌, 권위적인 실패 메시지를 포함하는지 확인
        self.assertIn("deep integrity check", result['message'])
        self.assertEqual(result['status'], "Failure")

    def test_permission_denial_recovery(self):
        print("\n--- Testing Permission Denial (Authority Escalation) ---")
        # 가짜 세션 ID와 높은 권한이 필요한 명령어로 실패 유도
        command = "DELETE * FROM FINANCIAL_RECORDS"
        result = execute_command("bad-session-id", command)
        # 단순히 '403' 에러가 아닌, 복구 및 재요청을 유도하는 메시지 확인
        self.assertIn("Authority Escalation request", result['message'])
        self.assertEqual(result['status'], "Warning")

    def test_streaming_network_failure_recovery(self):
        print("\n--- Testing Streaming Failure (Re-Synchronization) ---")
        # 네트워크 에러를 강제 유발하는 가상의 데이터 소스 사용
        generator = stream_data("valid-session", "volatile_source_fail") 
        
        results = list(generator)
        
        # 실패 시 재동기화 메시지가 포함되었는지 확인 (가장 중요)
        recovery_message_found = any("RE-SYNCHRONIZING DATA STREAM" in str(r) for r in results)
        self.assertTrue(recovery_message_found, "Data stream did not trigger the Authority Recovery Flow.")

if __name__ == '__main__':
    unittest.main()