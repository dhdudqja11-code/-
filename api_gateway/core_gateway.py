# api_gateway/core_gateway.py - 핵심 API Gateway 모듈 (임시 구조)

from typing import Dict, Any

class APIError(Exception):
    """공통 API 처리 오류."""
    def __init__(self, message: str = "API 호출에 실패했습니다.", code: int = 500):
        super().__init__(message)
        self.code = code
        self.error_details = {"status": "ERROR", "message": message}

class QuotaExceededError(APIError):
    """사용량 제한 초과 오류."""
    def __init__(self, remaining_quota: int = 0):
        super().__init__("사용량 할당량을 초과했습니다. 재시도 전 유료 결제가 필요합니다.", code=429)
        self.error_details = {"status": "QUOTA_EXCEEDED", "remaining": remaining_quota}

class APIGateway:
    """
    API 게이트웨이 서비스 클래스. 
    인증, 권한 검사(ACL), 사용량 제한을 통합적으로 처리하는 핵심 로직.
    """
    def __init__(self):
        # 가상의 사용자별 할당량 데이터 (Source of Truth)
        self._user_quotas: Dict[str, int] = {
            "admin_user": 100,
            "standard_user": 5,
            "guest_user": 0
        }

    def authenticate(self, api_key: str) -> bool:
        """API 키를 기반으로 인증 여부를 검증합니다."""
        # 실제로는 DB 조회 및 복잡한 키 매칭 로직이 필요함.
        return api_key and len(api_key) > 5

    def check_quota(self, user_id: str) -> int:
        """사용자의 현재 할당량을 반환합니다."""
        if user_id not in self._user_quotas:
            raise APIError("알 수 없는 사용자 ID입니다.")
        return self._user_quotas[user_id]

    def process_request(self, api_key: str, user_id: str) -> Dict[str, Any]:
        """
        API 요청을 처리하는 메인 진입점. 
        AuthN -> Quota Check -> ACL/Logic Flow 순서로 진행됩니다.
        """
        # 1. 인증 검증 (Authentication Guard)
        if not self.authenticate(api_key):
            raise APIError("유효하지 않은 API 키입니다. 접근이 차단되었습니다.")

        # 2. 사용량 제한 검사 (Quota Guard)
        current_quota = self.check_quota(user_id)
        if current_quota <= 0:
            # QuotaExceededError 발생 시 안전하게 처리되어야 함.
            raise QuotaExceededError()

        # 3. 요청 로직 수행 (Core Logic - 임시 성공)
        print(f"✅ 사용자 {user_id}의 요청을 성공적으로 처리했습니다. 남은 쿼터: {current_quota - 1}")
        return {"status": "SUCCESS", "message": "요청 처리가 완료되었습니다.", "remaining_quota": current_quota - 1}

# 엔드포인트 시뮬레이션 함수 (실제 Webhook 수신 지점)
def handle_webhook_request(payload: Dict[str, Any]):
    """Webhook으로 들어오는 트랜잭션 데이터를 처리하는 예시 함수."""
    user_id = payload.get("user_id")
    api_key = payload.get("source_key")
    if not user_id or not api_key:
        print("❌ 필수 파라미터 누락으로 트랜잭션 처리가 실패했습니다.")
        return None

    try:
        gateway = APIGateway()
        result = gateway.process_request(api_key, user_id)
        return result
    except QuotaExceededError as e:
        print(f"🚨 [ALERT] 트랜잭션 처리 실패: {e.error_details['message']} (재무적 손실 경고)")
        # 여기에 문제 정의/원인 분석/해결책 제시 로직이 추가되어야 함.
        return {"error": e.error_details}
    except APIError as e:
        print(f"🛑 [FATAL] 트랜잭션 처리 실패: {e.error_details['message']}")
        return {"error": e.error_details}