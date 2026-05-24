import redis
from fastapi import Request, HTTPException
from typing import Dict, Any
from time import time

# --- [가정] Redis 연결 및 클라이언트 정의 ---
# 실제 운영 환경에서는 API Key와 Secret을 사용해야 합니다.
try:
    # 로컬 테스트를 위해 Mocking 또는 실제 연결 시도 (실제 환경에 맞게 수정 필요)
    redis_client = redis.Redis(decode_responses=True, host='localhost', port=6379, db=0)
    redis_client.ping() # 연결 확인
except Exception:
    # 연결 실패 시 Mock 객체 사용 (테스트 환경을 가정)
    class MockRedisClient:
        def __init__(self):
            self.data = {}
        def incr(self, key, *args, **kwargs):
            self.data[key] = self.data.get(key, 0) + 1
            return self.data[key]
        def expire(self, *args, **kwargs): pass
        def get(self, key, *args, **kwargs): return self.data.get(key, "mock_value")
        def delete(self, key, *args, **kwargs):
            self.data.pop(key, None)
    redis_client = MockRedisClient()


class RateLimitExceeded(HTTPException):
    """Rate Limit 초과 시 발생하는 커스텀 예외."""
    def __init__(self):
        super().__init__(status_code=429, detail="Rate limit exceeded. Please wait before making more requests.")

class QuotaExceeded(HTTPException):
    """사용량 할당량 초과 시 발생하는 커스텀 예외."""
    def __init__(self):
        super().__init__(status_code=429, detail="Quota limit exceeded for this period. Upgrade your plan to increase limits.")


def check_rate_limit(redis: redis.Redis, user_id: str, endpoint: str, window_seconds: int = 60, max_requests: int = 10) -> bool:
    """
    [Rate Limit] 지정된 시간 창(Window) 내 요청 횟수를 체크합니다. (Sliding Window 또는 Fixed Window 방식 사용 권장)

    Args:
        redis: Redis 클라이언트 인스턴스.
        user_id: 사용자 식별자.
        endpoint: 접근하려는 API 엔드포인트 경로.
        window_seconds: 요청 카운터를 유지할 시간(초).
        max_requests: 허용되는 최대 요청 횟수.

    Returns:
        True: 제한을 초과하지 않음.
        False: 제한을 초과함.
    """
    key = f"rate:{user_id}:{endpoint}"
    
    # INCR을 사용하여 카운트를 증가시키고, TTL(만료 시간)을 설정합니다.
    current_count = redis.incr(key)
    redis.expire(key, window_seconds) # 키가 만료되는 시간을 설정하여 자동 정리

    if current_count > max_requests:
        # 카운트 초과 시 예외 발생 유도
        raise RateLimitExceeded()
    
    print(f"✅ Rate Check Passed for User {user_id} at {endpoint}. Count: {current_count}/{max_requests}")
    return True


def check_quota(redis: redis.Redis, user_id: str, quota_type: str = "monthly", max_limit: int = 1000) -> bool:
    """
    [Quota] 월별/일별 사용량 할당량을 체크하고 소모합니다.

    Args:
        redis: Redis 클라이언트 인스턴스.
        user_id: 사용자 식별자.
        quota_type: 'monthly' 또는 'daily'.
        max_limit: 최대 허용 한도.

    Returns:
        True: 할당량 내에 있음.
        False: 할당량을 초과함.
    """
    key = f"quota:{user_id}:{quota_type}"
    
    # 사용량 증가 (INCR) 및 TTL 설정 (월별/일별 기간 끝에 맞춰야 하지만, 단순 시뮬레이션으로 진행)
    current_usage = redis.incr(key)

    if current_usage > max_limit:
        raise QuotaExceeded()
    
    print(f"✅ Quota Check Passed for User {user_id} ({quota_type}). Usage: {current_usage}/{max_limit}")
    return True


async def api_gateway_middleware(request: Request):
    """
    FastAPI 미들웨어로 사용되며, 모든 요청에 대해 Rate Limit과 Quota를 순차적으로 체크합니다.
    """
    # 1. 사용자 ID 추출 (실제 구현에서는 Header나 JWT Payload에서 가져와야 함)
    user_id = request.headers.get("X-User-ID", "anonymous")
    endpoint = request.url.path

    print(f"\n[Middleware Start] Processing Request for User: {user_id}, Endpoint: {endpoint}")

    try:
        # 2. Rate Limit 체크 (예: 분당 10회 제한)
        check_rate_limit(redis_client, user_id, endpoint, window_seconds=60, max_requests=10)

        # 3. Quota Check (예: 월별 1000회 할당량)
        check_quota(redis_client, user_id, quota_type="monthly", max_limit=1000)
        
    except RateLimitExceeded as e:
        # Rate Limit 실패 시 요청 처리 중단 및 429 반환
        raise e
    except QuotaExceeded as e:
        # Quota 실패 시 요청 처리 중단 및 429 반환
        raise e

    print("[Middleware End] All checks passed. Request proceeding.")


# --- [테스트용 더미 API 라우터 (실제 적용 예시)] ---
from fastapi import FastAPI, Depends, APIRouter

router = APIRouter()
app = FastAPI(middleware=[Depends(api_gateway_middleware)]) # 실제 앱에 이 미들웨어를 연결해야 함

@router.get("/api/v1/data")
async def get_protected_data():
    """보호된 API 엔드포인트."""
    return {"message": "Welcome! Access granted."}

# 테스트를 위해 FastAPI 인스턴스를 직접 노출하지는 않습니다. (테스트 파일에서 사용할 것이기 때문)
print("✅ middleware_utils.py: Rate Limit 및 Quota 관리 로직 구현 완료.")