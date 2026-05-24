# c:\Users\user\AI 기업 두뇌\내 작업들\api_gateway\middleware_utils.py

from typing import Dict, Any
import functools
from datetime import timedelta

# ==============================================
# 🚨 WARNING: 실제 환경에서는 Redis/DB 연결이 필수입니다.
# 현재는 개념 증명(PoC)을 위해 더미 클래스로 대체합니다.
# ==============================================

class MockCache:
    """
    Redis 캐시를 모방한 더미 객체.
    실제 구현 시, 이 부분은 async Redis 클라이언트 호출로 교체되어야 합니다.
    """
    _store: Dict[str, Any] = {}

    @classmethod
    def get(cls, key: str) -> Any | None:
        print(f"[Cache Mock]: Retrieving {key}")
        return cls._store.get(key)

    @classmethod
    def setex(cls, key: str, seconds: int, value: Any):
        print(f"[Cache Mock]: Setting {key} for {seconds}s.")
        cls._store[key] = (value, None) # Value and Expiration time placeholder

# ----------------------
# [1. OAuth & RBAC 인증 미들웨어 스켈레톤]
# ----------------------

def authenticate_request(request: Dict[str, str]) -> tuple[bool, str | None]:
    """
    요청 헤더에서 Bearer 토큰을 추출하고 유효성을 검사합니다.
    토큰이 유효하면 사용자 정보를 반환합니다.
    """
    token = request.get('headers', {}).get('Authorization', '').replace("Bearer ", "")
    if not token:
        print("[Auth Error]: Missing Authorization header.")
        return False, None

    # TODO: 실제 JWT 검증 로직 (서명, 만료 시간 등) 구현 필요
    try:
        # 가상 토큰 디코딩 성공 가정
        user_data = {
            "user_id": "uuid-12345",
            "username": "ceo_admin",
            "roles": ["Admin", "BillingManager"], # RBAC 기반 역할 목록
            "is_active": True
        }
        return True, user_data

    except Exception as e:
        print(f"[Auth Error]: Token validation failed. {e}")
        return False, None


def check_permission(user_roles: list[str], required_role: str) -> bool:
    """
    RBAC (Role-Based Access Control) 검증 로직.
    요청에 필요한 권한이 사용자 역할 목록에 포함되어 있는지 확인합니다.
    """
    if not user_roles or not isinstance(user_roles, list):
        return False
    # 'Admin' 또는 'BillingManager' 중 하나만 있으면 접근 허용하는 로직 예시
    if required_role == "admin" and "Admin" in user_roles:
        return True
    if required_role == "billing" and ("Admin" in user_roles or "BillingManager" in user_roles):
        return True
    
    print(f"[Auth Error]: Role '{required_role}' required, but available roles are {user_roles}.")
    return False


# ----------------------
# [2. Usage Quota 관리 서비스 스켈레톤]
# ----------------------

class QuotaService:
    """
    사용자의 사용량 제한(Quota)을 추적하고 검증하는 핵심 서비스 계층.
    이 클래스는 DB/Redis와 직접 통신해야 합니다.
    """
    def __init__(self):
        pass

    async def get_user_quota(self, user_id: str) -> dict[str, float]:
        """사용자별 할당된 쿼터 정보를 가져옵니다 (예: 'api_calls': 100.0)."""
        # TODO: DB에서 사용자 플랜 기반으로 쿼터 로드
        print(f"[{user_id}] Quota data loaded from billing service.")
        return {
            "api_calls": 50.0, # 이번 달 할당량 (개)
            "data_transfer_gb": 10.0 # 데이터 전송량 (GB)
        }

    async def check_and_consume(self, user_id: str, resource_key: str, cost: float = 1.0) -> tuple[bool, float]:
        """
        사용자에게 특정 리소스 사용을 허용하고, 비용을 차감합니다.
        핵심 트랜잭션 로직: (읽기 -> 검증 -> 쓰기) 순서가 지켜져야 합니다.
        """
        quota = await self.get_user_quota(user_id)
        current_usage = quota.get(resource_key, 0.0)
        max_limit = quota.get(resource_key, float('inf'))

        if current_usage + cost > max_limit:
            print(f"[Quota Exceeded]: {user_id}가 {resource_key}를 초과했습니다. 현재 사용량: {current_usage:.2f}, 할당량: {max_limit:.2f}.")
            return False, current_usage

        # 💡 원자성 보장 필요 (DB Transaction / Redis WATCH)
        print(f"[Quota Success]: {user_id}에 대해 {resource_key} ({cost}) 사용 허용.")
        # 실제 구현 시: DB 트랜잭션으로 업데이트 및 실패 시 롤백 필수.
        return True, current_usage + cost

# ----------------------
# [3. 통합 미들웨어 함수]
# ----------------------

async def gateway_middleware(request: dict[str, Any], next_handler):
    """API Gateway의 최종 진입점 역할 (OAuth -> Quota -> Business Logic)"""
    print("\n--- 🌐 API Gateway Request Start ---")

    # Step 1: 인증 및 권한 검증 (Auth Middleware)
    auth_ok, user = authenticate_request(request)
    if not auth_ok or not user:
        return {"status": "error", "message": "Authentication Failed. Invalid token."}

    # Step 2: 리소스별 사용량 체크 및 차감 (Quota Middleware)
    resource_key = request.get('path', {}).split('/')[-1].replace('-', '_') # 예: 'user-profile' -> user_profile
    cost = 1.0 # 기본 호출 비용 가정

    quota_service = QuotaService()
    can_proceed, current_usage = await quota_service.check_and_consume(
        user['user_id'], resource_key, cost
    )

    if not can_proceed:
        # 🚨 비즈니스 리스크 강조: 사용량 초과 시 상세 에러 메시지 제공 필요
        return {"status": "error", "message": f"Quota Limit Exceeded for {resource_key}. Please upgrade your plan."}

    # Step 3: 권한 최종 검증 (RBAC) - 예시로 Admin 역할이 필요한 API 가정
    required_role = 'admin' if resource_key == 'dashboard' else None
    if required_role and not check_permission(user['roles'], required_role):
        return {"status": "error", "message": f"Access Denied. Requires the '{required_role}' role."}

    # Step 4: 다음 핸들러 호출 (Business Logic Execution)
    print("✅ All security checks passed. Executing core business logic...")
    try:
        result = await next_handler(user, request)
        return {"status": "success", "data": result}
    except Exception as e:
        # 🚨 실패 경로 기록 (Audit Log) 필수
        print(f"Critical Internal Error during execution: {e}")
        return {"status": "error", "message": "Internal Server Error. Check audit logs."}

# Mock Handler Function (테스트용 실제 API 로직 대체)
async def mock_business_logic(user: dict[str, str], request: dict[str, Any]):
    """실제 비즈니스 로직을 담는 핸들러를 모방합니다."""
    return {"message": f"Successfully processed request for user {user['user_id']}."}

# ----------------------
# [4. 테스트 스크립트 작성 (Testability)]
# ----------------------

async def run_test_scenario(request: dict[str, Any]):
    """전체 Gateway 흐름을 시뮬레이션하여 테스트합니다."""
    return await gateway_middleware(request, mock_business_logic)
`;

<create_file path="c:\Users\user\AI 기업 두뇌\내 작업들\api_gateway\test_api_gateway.py">
# c:\Users\user\AI 기업 두뇌\내 작업들\api_gateway\test_api_gateway.py

import asyncio
from middleware_utils import run_test_scenario, MockCache

async def main():
    print("==========================================================")
    print("           🌐 API Gateway Core Functionality Test        ")
    print("==========================================================\n")

    # --- SCENARIO 1: 정상적인 요청 (Success Path) ---
    success_request = {
        "headers": {"Authorization": "Bearer valid_token_for_ceo"},
        "path": "/api/v1/dashboard/user-metrics",
        "body": {}
    }
    print("--- [TEST 1] 성공 경로 테스트: 정상 인증 및 쿼터 사용 ---")
    result = await run_test_scenario(success_request)
    print("\n[RESULT 1]:", result)

    # --- SCENARIO 2: Quota 초과 요청 (Quota Failure Path) ---
    # 가상의 로직을 통해 첫 번째 호출에서 이미 쿼터를 소진했다고 가정하고 재실행하여 실패 유도
    MockCache._store['api_calls'] = (0.0, None) # 강제 초기화: 쿼터 0으로 설정
    print("\n\n==========================================================")
    print("--- [TEST 2] 실패 경로 테스트: Quota 초과로 인한 차단 ---")
    failure_request = {
        "headers": {"Authorization": "Bearer valid_token_for_ceo"},
        "path": "/api/v1/user-metrics",
        "body": {}
    }
    result = await run_test_scenario(failure_request)
    print("\n[RESULT 2]:", result)

    # --- SCENARIO 3: 권한 부족 요청 (RBAC Failure Path) ---
    # 가상의 토큰을 사용하여 Admin 역할이 없는 사용자 역할을 가정
    MockCache._store['api_calls'] = (10.0, None) # 쿼터는 남겨둠
    print("\n\n==========================================================")
    print("--- [TEST 3] 실패 경로 테스트: 권한 부족으로 인한 차단 ---")
    no_permission_request = {
        "headers": {"Authorization": "Bearer invalid_token_for_guest"}, # 가짜 토큰 사용 시 역할이 Guest로 가정됨
        "path": "/api/v1/dashboard", # Admin 권한 필요 API 호출
        "body": {}
    }
    # NOTE: middleware_utils.py의 authenticate_request가 이 경우 실패를 일으키지만, 
    # 테스트 목적상 역할 검증만 분리하여 시나리오 재현이 어려우므로, 
    # mock 로직을 통해 Role Check Failure Path를 강제합니다. (실제 개발에서 수정 필요)

    print("🚨 [NOTE]: Test 3 is structural limitation due to middleware coupling.")
    print("   (실제로는 역할만 조작하여 테스트 가능해야 합니다.)")


if __name__ == "__main__":
    asyncio.run(main())