from typing import Dict, Any, Optional
from app.schemas import ErrorResponse, LossAnalysisResult

# 상수 정의 (Why: 하드코딩을 피하고 관리하기 쉬운 곳에 둔다.)
ERROR_CODE_MISSING = "E4001"
ERROR_CODE_CONFLICT = "E4002"

def calculate_avoided_loss(
    input_data: Dict[str, Any],
    calc_inputs: Dict[str, float]
) -> tuple[Optional[LossAnalysisResult], Optional[ErrorResponse]]:
    """
    핵심 비즈니스 로직: Avoided Loss를 계산하고 위험도를 분석합니다.

    Args:
        input_data: 트랜잭션 및 리스크 데이터를 포함한 원본 데이터.
        calc_inputs: 행동경제학 가중치를 담은 입력 변수들.

    Returns:
        (성공 결과, 실패 오류) 튜플 형태. 둘 중 하나만 값이 채워져야 함.
    """
    # --- [STEP 1] 유효성 검증 (Missing Field / Conflicting Data Type 시뮬레이션) ---
    try:
        # 필수 필드 체크 및 타입 강제 실행 (예시: 'transaction_value'가 숫자가 아닌 경우)
        if not isinstance(input_data.get('client_id'), str) or not input_data['client_id']:
            raise ValueError("Client ID는 필수 필드이며 비어있을 수 없습니다.")

        # 데이터 상충 검증 로직 (예: Source가 Webhook인데 트랜잭션 가치가 0인 경우)
        if calc_inputs.get('regulatory_risk_score') is None and input_data['data_source'] == "Webhook":
            raise ValueError("Webhook 기반의 트랜잭션은 반드시 규제 위험 점수(regulatory_risk_score)를 포함해야 합니다.")

    except (ValueError, TypeError) as e:
        # 구조화된 오류 객체 반환 (Requirement 2 충족)
        error = ErrorResponse(
            error_code=ERROR_CODE_MISSING if "필드" in str(e) else ERROR_CODE_CONFLICT,
            message=f"데이터 유효성 검증 실패: {str(e)}",
            failed_field="InputData 또는 CalculationInputs",
            required_action="요청 바디의 필수 필드를 확인하거나 데이터 타입을 수정하십시오."
        )
        return None, error

    # --- [STEP 2] Avoided Loss 계산 로직 골격 (Requirement 1 충족) ---
    try:
        # ① 감정적 손실 변수 및 행동경제학 가중치 적용 (Placeholder)
        base_loss = input_data['transaction_value'] * calc_inputs['emotional_loss_sensitivity']
        regulatory_penalty = base_loss * calc_inputs['regulatory_risk_score'] * 1.5 # 규제 리스크에 큰 가중치 부여
        total_avoided_loss = base_loss + regulatory_penalty

    except KeyError as e:
        # 로직 내부에서 필수 변수가 누락된 경우
        error = ErrorResponse(
            error_code="E4003",
            message=f"내부 계산에 필요한 핵심 변수 {e}가 누락되었습니다.",
            failed_field="Service Logic",
            required_action="API 호출 전 모든 필수 파라미터를 확인하십시오."
        )
        return None, error

    # --- [STEP 3] 결과 분석 및 구조화 (Requirement 1 충족 계속) ---
    if regulatory_penalty > base_loss * 0.5:
        key_risk = "데이터 주권 위반 리스크"
        suggestion = "최신 규제 가이드라인에 맞춰 데이터 출처와 사용 목적을 명확히 분리하고, 동의 절차를 강화해야 합니다."
    else:
        key_risk = "일반적 트랜잭션 위험"
        suggestion = "거래 변수를 다각화하고 내부 감사 프로세스를 주기적으로 점검하십시오."

    result = LossAnalysisResult(
        total_avoided_loss=round(total_avoided_loss, 2),
        key_risk_area=key_risk,
        mitigation_suggestion=suggestion,
        confidence_score=0.95 # 임시 고정값
    )

    return result, None


def run_stress_test(mock_input: Dict[str, Any]) -> tuple[bool, str]:
    """
    E2E 스트레스 테스트 골격 (Requirement 3 충족).
    실제 API 호출이 아닌, 로직의 안정성을 검증하는 독립 함수.
    """
    print("\n--- [STRESS TEST START] ---")
    try:
        # 가상의 필수 파라미터 설정
        mock_calc = {'emotional_loss_sensitivity': 3.0, 'regulatory_risk_score': 0.5, 'data_integrity_penalty': 1.2}
        result, error = calculate_avoided_loss(mock_input, mock_calc)

        if error:
            return False, f"Stress Test Failure: {error.message}"
        else:
            print("✅ Stress Test Passed: Avoided Loss 로직이 성공적으로 실행되었습니다.")
            return True, "Success"
    except Exception as e:
        return False, f"Stress Test Critical Error: {str(e)}"