from typing import Dict, Optional
import time

class SessionManager:
    """
    사용자의 활성 세션(Active Session) 및 권한 상태를 관리합니다.
    실제로는 Redis나 DynamoDB 같은 인메모리 DB가 적합합니다.
    """
    def __init__(self):
        # 가상의 메모리 저장소 (Production에서는 절대 사용 금지!)
        self._active_sessions: Dict[str, dict] = {}

    @staticmethod
    def generate_session_id() -> str:
        """세션 고유 ID 생성. UUID 등을 사용하는 것이 안전합니다."""
        return f"SESSION_{int(time.time())}_UNIQUE"

    def create_session(self, user_id: str, token: str, duration_minutes: int = 60) -> bool:
        """새로운 세션을 등록하고 유효성을 체크합니다."""
        session_id = self.generate_session_id()
        expiry_time = time.time() + (duration_minutes * 60)
        
        self._active_sessions[session_id] = {
            "user_id": user_id,
            "token": token,
            "created_at": time.time(),
            "expires_at": expiry_time
        }
        print(f"INFO: Session created for User {user_id}. ID: {session_id}")
        return True

    def is_session_valid(self, session_id: str) -> bool:
        """세션의 유효성을 검사하고 만료 여부를 확인합니다."""
        if session_id not in self._active_sessions:
            return False
        
        session = self._active_sessions[session_id]
        is_expired = time.time() > session["expires_at"]
        
        if is_expired:
            print(f"WARNING: Session {session_id} expired.")
            del self._active_sessions[session_id] # 만료 시 자동 제거
            return False
        return True

    def revoke_session(self, session_id: str) -> bool:
        """사용자 요청 또는 비정상 종료 시 세션을 즉시 무효화합니다."""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            return True
        return False

# 테스트용 초기 데이터 주입 (필요없으면 삭제)