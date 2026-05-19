import random
import time
import json
from typing import Dict, Any, List, Tuple

# Assume this is the actual core logic we are testing/simulating calls to
# We simulate calling the external avoided_loss_calculator module
def calculate_avoided_loss(risk_exposure: float, control_effort_cost: float, source: str, verification_time: str) -> Dict[str, Any]:
    """
    가상의 Avoided Loss 계산 로직. 실제 모듈의 역할을 시뮬레이션합니다.
    정상적으로 작동할 경우 성공적인 결과를 반환해야 합니다.
    """
    if not all(isinstance(x, (int, float)) and x >= 0 for x in [risk_exposure, control_effort_cost]):
        raise ValueError("Risk Exposure와 Control Effort Cost는 음수가 될 수 없습니다.")
    
    if risk_exposure == 0:
        return {"success": False, "error": "위험 노출도가 0이므로 Avoided Loss 계산 불가.", "details": {}}

    # 핵심 로직 시뮬레이션: (Exposure - Cost) * Safety Factor
    safety_factor = max(1.0, abs(source) / 100.0) # Source를 기반으로 가중치 부여한다고 가정
    avoided_loss = round((risk_exposure - control_effort_cost) * safety_factor, 2)
    
    return {
        "success": True,
        "calculated_value": avoided_loss,
        "message": f"{source} 기반으로 회피 손실액이 성공적으로 산출되었습니다.",
        "data_integrity_check": "Passed",
        "inputs_used": {"risk": risk_exposure, "cost": control_effort_cost, "source": source, "time": verification_time}
    }

def run_stress_test(test_cases: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    """
    전달받은 테스트 케이스 리스트를 순회하며 E2E 스트레스 테스트를 수행합니다.
    성공 및 실패 결과를 분리하여 반환합니다.
    """
    successful_runs = []
    failed_runs = []

    print("===============================================================")
    print(f"🚀 Starting Central API Gateway Stress Test ({len(test_cases)} cases)")
    print("===============================================================\n")

    for i, case in enumerate(test_cases):
        test_id = f"Test Case {i+1}: {case['description']}"
        print(f"\n[--- START ---] {test_id}...")
        start_time = time.time()
        
        try:
            # 1. 입력 변수 유효성 검사 (Pydantic/Schema Level Check 시뮬레이션)
            required_keys = ['risk', 'cost', 'source', 'time']
            if not all(k in case for k in required_keys):
                raise KeyError(f"필수 변수가 누락되었습니다. 필요한 키: {required_keys}")

            # 2. 핵심 로직 호출 (API Gateway가 내부적으로 Calling)
            result = calculate_avoided_loss(
                risk_exposure=case['data']['risk'],
                control_effort_cost=case['data']['cost'],
                source=case['data']['source'],
                verification_time=case['data']['time']
            )
            
            # 3. 성공 처리 로직 (Response Schema Validation)
            successful_runs.append({
                "test_id": test_id,
                "status": "PASS",
                "result": result,
                "elapsed_time": round(time.time() - start_time, 4),
                "summary": f"✅ Success: {result['message']}"
            })

        except (ValueError, KeyError, TypeError) as e:
            # 4. 예외 처리 로직 검증 및 기록
            error_message = str(e)
            failed_runs.append({
                "test_id": test_id,
                "status": "FAIL",
                "error_type": type(e).__name__,
                "error_message": error_message,
                "elapsed_time": round(time.time() - start_time, 4),
                "summary": f"❌ Failure: {error_message[:50]}..."
            })
        except Exception as e:
            # 5. 예상치 못한 시스템 오류 처리 (Critical Failures)
            failed_runs.append({
                "test_id": test_id,
                "status": "CRITICAL FAIL",
                "error_type": type(e).__name__,
                "error_message": f"예상치 못한 심각한 시스템 오류 발생: {str(e)}",
                "elapsed_time": round(time.time() - start_time, 4),
                "summary": "🚨 Critical Failure detected in the Gateway."
            })

    return successful_runs, failed_runs


if __name__ == "__main__":
    # ===============================================================
    # 🧠 스트레스 테스트 케이스 정의 (Critical Path Coverage)
    # ===============================================================
    test_cases = [
        # 1. Happy Path: 정상적인 성공 시나리오 (최적 조건)
        {"description": "Happy Path - Optimal Loss Calculation", "data": {"risk": 1500.0, "cost": 300.0, "source": "SEC_FILING_A", "time": "2024-06-01T10:00:00Z"}},
        # 2. Boundary Case: 위험 노출도가 제로일 때 (시스템 실패 방지 테스트)
        {"description": "Boundary - Zero Risk Exposure (Should Fail)", "data": {"risk": 0.0, "cost": 100.0, "source": "API_CALL", "time": "2024-06-01T10:05:00Z"}},
        # 3. Failure Case: 필수 변수 누락 (KeyError 테스트)
        {"description": "Failure - Missing Required Input Variable (Cost)", "data": {"risk": 500.0, "source": "API_CALL", "time": "2024-06-01T10:10:00Z"}},
        # 4. Failure Case: 데이터 타입 에러 - 음수 입력 (ValueError 테스트)
        {"description": "Failure - Negative Cost Input (Type Error)", "data": {"risk": 800.0, "cost": -50.0, "source": "API_CALL", "time": "2024-06-01T10:15:00Z"}},
        # 5. Edge Case: 통제 노력 비용이 위험 노출도를 초과하는 경우 (논리적 Fail)
        {"description": "Edge Case - Cost > Risk (Loss = 0)", "data": {"risk": 100.0, "cost": 200.0, "source": "API_CALL", "time": "2024-06-01T10:20:00Z"}},
        # 6. Critical Failure: 아예 잘못된 형식의 데이터 입력 (TypeError 테스트)
        {"description": "Critical Fail - Non-numeric Input Type (Type Error)", "data": {"risk": "High", "cost": 50.0, "source": "API_CALL", "time": "2024-06-01T10:25:00Z"}},
        # 7. Success Case: 높은 가중치(Source)를 가진 경우 (성공 확인)
        {"description": "Happy Path - High Source Weighting Test", "data": {"risk": 1000.0, "cost": 100.0, "source": "REGULATORY_BODY_XYZ", "time": "2024-06-02T11:00:00Z"}}
    ]

    successful, failed = run_stress_test(test_cases)

    # -------------------------------------------------------------
    # 📊 최종 검증 보고서 출력 (Simulation of Report Generation)
    # -------------------------------------------------------------
    print("\n\n===============================================================")
    print("             📈 E2E 스트레스 테스트 종합 검증 보고서")
    print("===============================================================")

    print(f"\n✅ 총 실행 케이스 수: {len(test_cases)}개")
    print(f"🟢 성공적으로 처리된 케이스: {len(successful)}개 (PASS)")
    print(f"🔴 실패 또는 경고가 발생한 케이스: {len(failed)}개 (FAIL/CRITICAL FAIL)")

    if failed:
        print("\n[🚨 핵심 발견 사항 요약]")
        for failure in failed:
            print(f"  -> [{failure['status']}] '{failure['test_id']}': 원인({failure['error_type']}) -> {failure['summary']}")
        print(">>> 결론: Gateway는 모든 종류의 입력 변수 오류에 대한 방어 로직이 필요합니다. 특히, 비숫자형 데이터 및 필수 필드 누락 처리를 강화해야 합니다.")
    else:
        print("\n[👍 시스템 상태]")
        print("모든 테스트 케이스가 성공적으로 통과했습니다. 현재 아키텍처의 견고성이 매우 높습니다.")

    if successful:
        print("\n[🧪 주요 성공 시나리오 검증 결과 (Avoided Loss)]")
        for success in successful:
            result = success['result']
            if result['success']:
                print(f"  - {success['test_id']} -> 최종 $CoA$: {result['calculated_value']} | 메시지: {result['message']}")
    
    # -------------------------------------------------------------