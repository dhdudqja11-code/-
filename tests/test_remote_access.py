import unittest
from src.services.remote_access_service import (
    AccessToken, RemoteConnectionDetails, IntegrationError, run_remote_access_flow
)

class TestRemoteAccessFlow(unittest.TestCase):
    """원격 접근 모듈의 통합 기능을 단위/통합 테스트합니다."""

    def setUp(self):
        # 공통 환경 설정
        self.admin_token = AccessToken(user_id="ceo", role="admin")
        self.standard_token = AccessToken(user_id="userB", role="standard")
        self.guest_token = AccessToken(user_id="temp", role="guest")

    def test_01_success_flow_admin(self):
        """[성공 케이스] Admin 권한으로 모든 단계가 정상적으로 작동하는지 검증."""
        conn_info = RemoteConnectionDetails(ip_address="192.168.1.50", port=22)
        result = run_remote_access_flow(self.admin_token, conn_info, "ls -l /var/log")
        self.assertTrue(result['success'])
        self.assertIn("성공적으로 완료되었습니다", result['report'])

    def test_02_rbac_failure_command(self):
        """[권한 실패] Standard 유저가 Admin 전용 명령을 시도할 때 IntegrationError 발생 확인."""
        conn_info = RemoteConnectionDetails(ip_address="192.168.1.50", port=22)
        result = run_remote_access_flow(self.standard_token, conn_info, "systemctl restart sshd")
        self.assertFalse(result['success'])
        self.assertEqual(result['error_report'].split('(')[1].strip(")."), "PERMISSION_DENIED")

    def test_03_auth_failure_guest(self):
        """[인증 실패] Guest 유저가 접속을 시도할 때 IntegrationError 발생 확인."""
        conn_info = RemoteConnectionDetails(ip_address="192.168.1.50", port=22)
        result = run_remote_access_flow(self.guest_token, conn_info, "echo hello")
        self.assertFalse(result['success'])
        self.assertEqual(result['error_report'].split('(')[1].strip(")."), "AUTH_ERROR")

    def test_04_network_validation_failure(self):
        """[네트워크 실패] 유효하지 않은 IP 포맷을 사용할 때 IntegrationError 발생 확인."""
        conn_info = RemoteConnectionDetails(ip_address="256.1.1.1", port=80) # Invalid IP/Port combination
        result = run_remote_access_flow(self.admin_token, conn_info, "ls -l /")
        self.assertFalse(result['success'])
        self.assertEqual(result['error_report'].split('(')[1].strip(")."), "VALIDATION_ERROR")

    def test_05_execution_failure_command(self):
        """[실행 실패] 명령 자체에 오류가 있어도 시스템은 충돌 없이 처리하는지 검증."""
        conn_info = RemoteConnectionDetails(ip_address="192.168.1.50", port=22)
        result = run_remote_access_flow(self.admin_token, conn_info, "FAIL_CMD");
        self.assertFalse(result['success'])
        self.assertEqual(result['error_report'].split('(')[1].strip(")."), "EXECUTION_ERROR")

if __name__ == "__main__":
    unittest.main()