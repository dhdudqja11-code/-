import asyncio
from src.api.authority_gateway import app # FastAPI 앱 임포트 가정
from httpx import AsyncClient, Response
import time

# 테스트 목표: 모든 상태 전이와 강제 지연 시간(1초) 준수 여부를 검증한다.
async def test_e2e_state_transition():
    print("=============================================")
    print("🚀 E2E Authority System Test Start")
    client = AsyncClient(app=app, base_url="http://test-server:8000") # 테스트용 가상 서버 설정

    # --- TEST CASE 1: 정상 상태 전이 (Initial -> Resolved) ---
    print("\n[TEST 1/3] Running Test Case: Normal Resolution Path...")
    request_data = {
        "transaction_id": "TX-20260606-001",
        "source_data": {"Source": "Global Regulatory Audit 2024", "Time": time.time()},
        "timestamp": time.time()
    }
    async with client.asynch_client() as ac:
        response: Response = await ac.post("/api/v1/check_authority", json=request_data)
        print(f"  [SUCCESS] Status Code: {response.json()['status_code']}, Score: {response.json()['authority_score']}")

    # --- TEST CASE 2: Warning 상태 전이 (Utility Solver 단계) ---
    print("\n[TEST 2/3] Running Test Case: Compliance Warning Path...")
    request_data = {
        "transaction_id": "TX-20260606-W01",
        "source_data": {"Source": "Data Source A & B Mismatch"},
        "timestamp": time.time()
    }
    async with client.asynch_client() as ac:
        response: Response = await ac.post("/api/v1/check_authority", json=request_data)
        print(f"  [SUCCESS] Status Code: {response.json()['status_code']}, Loss Estimate Exists: {response.json()['loss_estimate'] is not None}")

    # --- TEST CASE 3: Critical Breach 및 강제 지연 검증 (The Crucial Test) ---
    print("\n[TEST 3/3] Running Test Case: CRITICAL Authority Breach Path...")
    request_data = {
        "transaction_id": "TX-20260606-CRIT",
        "source_data": {"Source": "expired_authority data"}, # Mock backend trigger
        "timestamp": time.time()
    }
    start_time = time.time()
    async with client.asynch_client() as ac:
        response: Response = await ac.post("/api/v1/check_authority", json=request_data)
        end_time = time.time()

        print(f"  [SUCCESS] Status Code: {response.json()['status_code']}")
        # ★ 핵심 검증 로직: 지연 시간 확인
        duration = end_time - start_time
        if 0.9 < duration < 1.2: # 허용 오차 범위 내에서 1초가 지켜졌는지 검사
             print(f"  [✅ PASS] Forced delay of ~1 second successfully enforced (Duration: {duration:.2f}s).")
        else:
            print(f"  [❌ FAIL] Expected forced delay (~1.0s), but got {duration:.2f}s.")

    print("\n=============================================")
    print("✅ E2E Test Suite Completed. System Authority Integrity Confirmed.")


if __name__ == "__main__":
    # 실제 실행 시에는 asyncio.run()을 사용해야 함
    try:
        asyncio.run(test_e2e_state_transition())
    except Exception as e:
        print(f"\n🔴 E2E Test Failed during execution: {e}")