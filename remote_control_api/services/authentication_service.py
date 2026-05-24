from datetime import timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# TODO: 실제 환경 변수에서 로드해야 함 (JWT Secret Key)
SECRET_KEY = "YOUR_SUPER_SECRET_KEY" 
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthenticationService:
    """
    시스템의 모든 인증 로직을 전담하는 서비스 계층.
    이 클래스는 외부 라이브러리 의존성을 최소화하며, 
    실제 MFA/OAuth 플로우를 통합할 핵심 게이트웨이 역할을 합니다.
    """

    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해시 생성 (bcrypt 사용)."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """제공된 비밀번호와 저장된 해시 비교."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except ValueError:
            # 잘못된 형식의 hash가 들어올 경우 방어 로직 추가
            print("Warning: Invalid hash format provided.")
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """접근 토큰을 생성합니다. (JWT 표준 사용)."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
            to_encode.update({"exp": expire})
        else:
            expire = datetime.utcnow() + timedelta(minutes=30) # 기본 30분 만료
            to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return str(encoded_jwt)

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """토큰을 디코딩하여 사용자 ID를 추출합니다."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            # TODO: 여기에서 토큰이 유효한지 DB를 통해 추가 검증 필요 (Revocation Check)
            return user_id
        except JWTError as e:
            print(f"Authentication Error: {e}")
            return None

    @staticmethod
    def enforce_mfa_check(user_id: str, token: str) -> bool:
        """
        [CRITICAL]: MFA/2FA 강제 검증 플래그. 
        실제 구현 시 TOTP 라이브러리 등을 사용하여 OTP를 체크해야 함.
        현재는 골격만 유지합니다.
        """
        print(f"INFO: Performing Multi-Factor Authentication check for User {user_id}...")
        # Placeholder Logic: 실제 로직은 API Gateway 레벨에서 처리되어야 함
        return True # 일단 통과로 가정

from datetime import datetime, timedelta