import pytest
from httpx import AsyncClient
# 실제로는 app 객체를 가져와야 하지만, 골격이므로 Mocking으로 가정합니다.
from src.core.api_gateway.gateway import app 

@pytest.mark.asyncio
async def test_successful_data_read():
    """테스트 케이스 1: 일반 사용자가 데이터를 읽는 성공 경로 (Basic Role)"""
    # 가상의 토큰 구조: valid_jwt_{user_id}:{role}
    token = "valid_jwt_testuserbasic:basic" 
    headers = {
        "X-User-Id": "TestRunner", # Rate Limit User ID
        "Authorization": token
    }
    # FastAPI 클라이언트를 사용한다고 가정하고 테스트합니다.
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/data/read", headers=headers)
        assert response.status_code == 200
        assert "Data read success" in response.json()['message']

@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    """테스트 케이스 2: Rate Limit 초과 시 강제 실패 검증 (Critical Security Test)"""
    # 이 테스트는 rate_limit_checker의 로직을 여러 번 호출하여 429를 유발해야 합니다.
    # 실제 구현에서는 Mocking이나 반복적인 요청이 필요합니다. 여기서는 구조만 정의합니다.
    token = "valid_jwt_rateuser:basic"
    headers = {
        "X-User-Id": "RateTester", # 고정된 사용자 ID로 제한 테스트
        "Authorization": token
    }

    # 🚨 주의: Rate Limit을 강제 초과시키기 위해 여러 번의 요청 시뮬레이션이 필요합니다.
    # 현재는 구조적 테스트를 위해 429 에러 메시지 존재 여부를 확인하는 로직만 정의합니다.
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 임시 요청 (실제 테스트에서는 반복 호출 필요)
        response = await ac.get("/api/v1/data/read", headers=headers) 
        # 만약 RateLimit이 구현되었다면, 특정 시점 이후에 429가 나와야 합니다.
        pass # 이 부분은 실제 환경에서 요청 카운트를 조작하여 테스트해야 완벽합니다.

@pytest.mark.asyncio
async def test_polp_violation_write():
    """테스트 케이스 3: PoLP 위반 시도 검증 (Basic Role -> Write Attempt)"""
    # Basic 역할은 write_data를 할 권한이 없습니다. 403 Forbidden이 나와야 합니다.
    token = "valid_jwt_basicuser:basic" 
    headers = {
        "X-User-Id": "TestRunner",
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {"key": "value"}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/data/write", headers=headers, json=payload)
        assert response.status_code == 403
        assert "Forbidden" in response.json()['detail']

@pytest.mark.asyncio
async def test_polp_violation_admin():
    """테스트 케이스 4: 비관리자 역할이 관리 엔드포인트에 접근 시도 (Non-Admin -> Admin Endpoint)"""
    token = "valid_jwt_premiumuser:premium" # Premium은 admin 권한이 없음
    headers = {
        "X-User-Id": "TestRunner",
        "Authorization": token
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/admin/manage", headers=headers)
        assert response.status_code == 403
        assert "Only 'admin' can access this endpoint" in response.json()['detail']

@pytest.mark.asyncio
async def test_authn_token_failure():
    """테스트 케이스 5: 유효하지 않은 토큰으로 접근 시도 (Missing AuthN)"""
    headers = {
        "X-User-Id": "TestRunner",
        "Authorization": "invalid_jwt_format" # 가짜 토큰
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/data/read", headers=headers)
        assert response.status_code == 401
        assert "Invalid or missing authentication token" in response.json()['detail']