import json
from typing import Dict, Any
from datetime import datetime
from pydantic import ValidationError

# 로컬 모듈 불러오기 (가정)
try:
    from compliance_models import ViolationEvidencePayload, LegalEvidence, ComplianceGateResult
except ImportError:
    print("🚨 ERROR: compliance_models.py 파일을 먼저 실행하여 모델을 정의해야 합니다.")
    exit()


def simulate_compliance_check(input_data: Dict[str, Any], violation_details: Dict[str, Any]) -> ComplianceGateResult:
    """
    주어진 입력 데이터와 위반 세부 정보를 바탕으로 컴플라이언스 게이트웨이를 시뮬레이션합니다.
    실제 시스템에서 이 함수는 외부 API 호출 및 DB 조회를 포함하게 됩니다.
    """
    print("⚙️ [Compliance Guardrail] Input Validation 시작...")
    
    try:
        # 1. 법적 증거 Payload 생성 (가장 먼저 구조화)
        legal_evidence = LegalEvidence(**violation_details['legal_evidence'])

        # 2. 위반 페이로드 생성
        violation_payload = ViolationEvidencePayload(
            severity_level=violation_details['severity'],
            violation_summary=violation_details['summary'],
            legal_evidence=legal_evidence,
            # timestamp는 기본값 사용
        )
        print(f"✅ [Compliance Guardrail] 위반 Payload 생성 완료: {violation_payload.violation_id}.")

    except ValidationError as e:
        print(f"❌ [Compliance Guardrail] 치명적 오류! Violation Evidence 구조체 유효성 검증 실패.")
        # 구조 자체가 깨지면, 가장 낮은 수준의 에러를 기록하고 프로세스를 중단해야 합니다.
        return ComplianceGateResult(
            simulation_success=False, 
            raw_input_data=input_data, 
            compliance_violations=[violation_payload] # 가짜 Payload로 오류 구조화
        )

    # 3. 최종 게이트웨이 결과물 구성 (성공 케이스 시뮬레이션)
    print("✅ [Compliance Guardrail] 전체 검증 프로세스 완료.")
    return ComplianceGateResult(
        simulation_success=True,
        raw_input_data=input_data,
        compliance_violations=[violation_payload], # 성공적으로 생성된 Payload를 포함
        audit_log="Data passed all compliance checks."
    )


if __name__ == "__main__":
    # --- 🟢 테스트 시나리오 1: 일반적인 개인정보 유출 위반 (성공 케이스) ---
    print("\n" + "="*50)
    print("✨ [TEST] 시나리오 1: 데이터 규제 위반 감지 및 기록")
    print("="*50)

    test_input = {
        "user_id": "U-9876",
        "action": "profile_update",
        "data": {"email": "test@example.com", "phone": "010-xxxx-xxxx"}
    }

    violation_details_success = {
        'severity': 'HIGH',
        'summary': '개인 식별 정보(PII)를 목적 외 부서에 전송함.',
        'legal_evidence': {
            'applicable_law': '개인정보보호법',
            'legal_article': '제18조 (개인정보의 목적 외 이용·제공 제한)',
            'violation_clause': '개인정보는 수집 시 명시한 목적 내에서만 사용되어야 한다.'
        }
    }

    result_success = simulate_compliance_check(test_input, violation_details_success)
    print("\n[FINAL RESULT] Simulation Success:", result_success.simulation_success)
    # 실제 환경에서는 이 결과를 API 응답으로 반환합니다.
    print(json.dumps({"status": "SUCCESS", "data": result_success.dict()}, indent=2))


    # --- 🔴 테스트 시나리오 2: 법적 근거 미비로 인한 구조체 유효성 검증 실패 (실패 케이스) ---
    print("\n" + "="*50)
    print("🚨 [TEST] 시나리오 2: 필수 필드 누락으로 인한 Validation Failure")
    print("="*50)

    # legal_evidence에서 applicable_law를 제거하여 의도적으로 실패 유발
    violation_details_fail = {
        'severity': 'CRITICAL',
        'summary': '데이터 전송 과정에 법적 근거가 명시되지 않은 비인가 트랜잭션 발생.',
        'legal_evidence': { # applicable_law 누락
            'legal_article': '제3조 (개인정보 처리의 원칙)',
            'violation_clause': '데이터 전송은 반드시 문서화된 법적 근거를 가져야 한다.'
        }
    }

    result_failure = simulate_compliance_check(test_input, violation_details_fail)
    print("\n[FINAL RESULT] Simulation Success:", result_failure.simulation_success)
    # 실패 시에도 시스템은 다운되지 않고, 이 Failure Payload를 기록합니다.
    if not result_failure.simulation_success:
        print("⚠️ [FAILURE HANDLED] System did not crash. Compliance failure recorded.")
        print(json.dumps({"status": "FAILURE", "data": result_failure.dict()}, indent=2))