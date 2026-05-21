from fastapi import APIRouter, HTTPException
from typing import List
import json

# 🚨 로컬 파일 경로 참조: 방금 만든 모델 파일을 임포트해야 합니다.
from .risk_assessment_models import (
    AssessmentRequest, RiskAssessmentResponse, StructuredRiskAlert, 
    SuccessfulAssessmentResponse, RiskLevel, UserActionSimulation
)

router = APIRouter()

# 가상의 핵심 검증 엔진 함수 (실제 로직은 여기에 들어갑니다.)
def _run_validation_engine(request: AssessmentRequest) -> List[StructuredRiskAlert]:
    """
    요청된 사용자 행동 목록을 분석하여 리스크 경고를 생성하는 내부 엔진.
    이곳에 복잡한 법규/데이터 주권 검증 로직이 구현되어야 합니다.
    """
    alerts: List[StructuredRiskAlert] = []

    # --- [Critical Risk Simulation Logic] ---
    for action in request.user_actions:
        if "financial" in action.data_scope and action.action_type == "export":
            # 예시 1: 금융 데이터를 외부로 가져가는 행위는 Critical 위험으로 간주
            alert = StructuredRiskAlert(
                risk_level=RiskLevel.CRITICAL,
                is_compliant=False,
                problem_definition="⚠️ 심각 경고: 고객의 민감한 금융 거래 내역이 제3자 시스템으로 직접 추출되고 있습니다.",
                root_cause="개인정보보호법 및 금융데이터 보호 지침 위반 가능성 (Source/Time 기반 검증 필수).",
                source_details={"action": action.action_type, "data": action.data_scope},
                mitigation_suggestion="❌ 즉시 중단하고, 반드시 시스템 내부의 암호화된 '읽기 전용(Read-Only)' 대시보드를 통해서만 데이터를 확인해야 합니다."
            )
            alerts.append(alert)

        # --- [High Risk Simulation Logic] ---
        elif "user_profile" in action.data_scope and action.source_system == "unverified_api":
            # 예시 2: 출처가 불분명한 API를 통해 개인 프로필을 가져가는 행위는 High 위험으로 간주
            alert = StructuredRiskAlert(
                risk_level=RiskLevel.HIGH,
                is_compliant=False,
                problem_definition="🚨 경고: 검증되지 않은 외부 API를 사용하여 사용자 식별 정보를 수집하고 있습니다.",
                root_cause="개인정보 비식별화 원칙 위반 및 데이터 주권 침해 위험 (GDPR/CCPA 등 근거).",
                source_details={"system": action.source_system, "scope": action.data_scope},
                mitigation_suggestion="✅ 반드시 공식적으로 승인된 API Gateway를 통하거나, 최소한의 정보(Minimization Principle)만 추출해야 합니다."
            )
            alerts.append(alert)

    return alerts


@router.post("/api/v1/risk-assessment", response_model=RiskAssessmentResponse)
async def run_risk_assessment(request: AssessmentRequest):
    """
    사용자 행동 시뮬레이션 데이터를 기반으로 실시간 규제 리스크를 평가합니다.
    입력 검증 -> 내부 엔진 실행 -> 구조화된 JSON 응답 반환 과정을 수행합니다.
    """
    try:
        # 1. 입력 데이터 유효성 검사 (Validation)는 Pydantic이 담당하지만, 추가적인 비즈니스 로직 검사를 합니다.
        if not request.user_actions:
            raise ValueError("AssessmentRequest에는 반드시 평가할 사용자 행동 목록(user_actions)이 포함되어야 합니다.")

        # 2. 핵심 리스크 엔진 실행 (가장 중요한 단계)
        alerts = _run_validation_engine(request)

        if not alerts:
            # 모든 검증 통과 시, 성공 응답을 반환합니다.
            return SuccessfulAssessmentResponse()
        else:
            # 위험도가 감지된 경우, 구조화된 경고 목록과 함께 응답합니다.
            return RiskAssessmentResponse(alerts=alerts)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 예측하지 못한 서버 오류 처리 (Internal Server Error)
        print(f"Critical Backend Error during assessment: {e}") # 로깅 필수
        raise HTTPException(status_code=500, detail="시스템 내부 오류로 리스크 평가를 수행할 수 없습니다.")