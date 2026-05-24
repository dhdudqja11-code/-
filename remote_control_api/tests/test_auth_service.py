import unittest
from services.authentication_service import AuthenticationService
from datetime import timedelta
from jose import jwt # 테스트를 위해 임포트

class TestAuthenticationService(unittest.TestCase):
    """AuthenticationService의 핵심 로직을 검증합니다."""

    def test_create_and_decode_token(self):
        """토큰 생성 및 디코딩이 정상 작동하는지 확인합니다."""
        payload = {"sub": "testuser123"}
        # 1시간짜리 토큰 생성
        access_token = AuthenticationService.create_access_token(payload, timedelta(hours=1))
        self.assertIsInstance(access_token, str)

        # 디코딩하여 payload 검증
        decoded_data = jwt.decode(access_token, "YOUR_SUPER_SECRET_KEY", algorithms=["HS256"])
        self.assertEqual(decoded_data["sub"], "testuser123")

    def test_invalid_token_handling(self):
        """유효하지 않은 토큰에 대한 처리를 테스트합니다."""
        fake_token = "this.is.a.bad.token"
        user_id = AuthenticationService.get_user_id_from_token(fake_token)
        self.assertIsNone(user_id, "Invalid token should return None user ID.")

    def test_password_hashing_and_verification(self):
        """비밀번호 해싱 및 검증 로직이 정상적으로 작동하는지 확인합니다."""
        # 실제 bcrypt가 동작하는 환경에서 테스트 필요 (여기서는 골격만)
        hashed = AuthenticationService.get_password_hash("securepass")
        self.assertTrue(AuthenticationService.verify_password("securepass", hashed))
        self.assertFalse(AuthenticationService.verify_password("wrongpass", hashed))

if __name__ == '__main__':
    unittest.main()