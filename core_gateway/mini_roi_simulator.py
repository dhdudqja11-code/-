from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid

# ==============================================================
# 1. Pydantic Models (Input/Output Guardrails)
# ==============================================================

class RiskFactor(BaseModel):
    """사용자가 진단하고자 하는 리스크 요인."""
    activity_name: str = Field(..., description="누락된 핵심 활동의 명칭.")
    potential_impact_score: float = Field(..., ge=1.0, le=10.0, description="이슈가 발생했을 때의 상대적 영향도 (1~10).")

class SimulationInput(BaseModel):
    """Mini ROI 시뮬레이션을 위한 전체 입력 데이터."""
    client_id: str = Field(..., description="진단 대상 클라이언트 고유 ID.")
    user_role: str = Field(..., description="사용자의 권한 역할 (e.g., Admin, Viewer).")
    risk_factors: List[RiskFactor] = Field(..., min_items=1, description="분석할 리스크 요인 목록.")

class StructuredReportItem(BaseModel):
    """API 출력의 필수 구조: [문제 정의 -> 원인 분석 -> 해결책 제시]."""
    stage: str = Field(..., description="단계 (Problem/Cause/Solution).")
    detail: str = Field(..., description="해당 단계에 대한 구체적이고 권위적인 설명.")

class SimulationOutput(BaseModel):
    """Mini ROI 시뮬레이션의 최종 출력 구조."""
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="이번 시뮬레이션 고유 ID.")
    total_estimated_loss_usd: float = Field(..., ge=0, description="예상되는 총 손실액 (USD).")
    is_critical_risk: bool = Field(..., description="현재 위험 상태가 임계치(Critical)에 도달했는지 여부.")
    report: List[StructuredReportItem] = Field(..., min_items=1, description="위험 진단 3단계 구조 보고서.")

# ==============================================================
# 2. Core Business Logic (Testable Unit Function)
# ==============================================================

def calculate_mini_roi_loss(input_data: SimulationInput) -> List[StructuredReportItem]:
    """
    핵심 로직: 입력된 리스크 요인을 기반으로 예상 손실액을 계산하고, 
    필수적인 [문제 정의 -> 원인 분석 -> 해결책 제시] 보고서를 생성합니다. (Mock Data 사용)

    Args:
        input_data: SimulationInput 모델로 검증된 위험 요소 목록.

    Returns:
        StructuredReportItem 리스트 형태의 권위적 진단 보고서.
    """
    if not input_data.risk_factors:
        raise ValueError("분석할 리스크 요인이 하나 이상 필요합니다.")

    total_loss = 0.0
    report: List[StructuredReportItem] = []

    # Mock Loss Calculation (위험성 공포 조성 로직)
    for risk in input_data.risk_factors:
        impact = risk.potential_impact_score * 1500  # Impact Score에 가중치 부여
        total_loss += impact
        
        # [문제 정의]
        problem_detail = f"[{risk.activity_name}의 부재]: 해당 활동은 필수적인 컴플라이언스/수익 창출 경로임에도 불구하고 현재 시스템에서 누락되어 있습니다."
        report.append(StructuredReportItem(stage="Problem", detail=problem_detail))

        # [원인 분석] (Mock Cause)
        cause_detail = f"[{risk.activity_name}의 공백]: 데이터 추적 관점이나 규제 준수 측면에서 취약점이 발생할 가능성이 매우 높습니다. 특히 {input_data.user_role} 권한 레벨에서는 치명적입니다."
        report.append(StructuredReportItem(stage="Cause", detail=cause_detail))

        # [해결책 제시] (Mock Solution - 자사 서비스 연결 유도)
        solution_detail = f"[{risk.activity_name} 복구 방안]: 즉시 Core Gateway API를 통해 {input_data.user_role} 권한에 맞는 'Mini ROI 시뮬레이션'을 재실행하여, 누락된 활동의 가치를 정량적으로 측정하고 보완해야 합니다."
        report.append(StructuredReportItem(stage="Solution", detail=solution_detail))

    # 최종 결과값 계산 및 경고 설정 (임계치 로직)
    is_critical = total_loss > 10000 # 예시 임계값
    if is_critical:
        report.append(StructuredReportItem(stage="WARNING", detail="🚨 즉각적인 조치가 필요합니다! 시스템 감사 기록을 재검토해야 합니다."))

    return report, round(total_loss, 2)


# ==============================================================
# 3. FastAPI Router (API Endpoint Skeleton)
# ==============================================================

router = APIRouter()

@router.post("/api/v1/mini-roi/simulate", response_model=SimulationOutput)
async def simulate_mini_roi(input: SimulationInput):
    """
    Mini ROI 시뮬레이션을 실행하여 예상 손실액과 권위적 보고서를 반환합니다.
    이 엔드포인트는 핵심 컴플라이언스 게이트웨이를 통하는 필수 API입니다.
    """
    try:
        # 1. Core Logic 호출 및 결과 받기 (테스트 가능한 함수 활용)
        report, total_loss = calculate_mini_roi_loss(input)

        # 2. 최종 출력 객체 생성
        output = SimulationOutput(
            simulation_id=str(uuid.uuid4()),
            total_estimated_loss_usd=total_loss,
            is_critical_risk=(total_loss > 10000),
            report=report
        )
        return output

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 시스템 에러 발생 시에도 사용자에게는 '위험'으로 포장하여 전달하는 것이 비즈니스 원칙.
        print(f"Critical Error during simulation: {e}") 
        raise HTTPException(status_code=500, detail="시스템 로직 오류. 재시도 후 Core Gateway 로그를 확인해 주십시오.")

# ==============================================================
# END OF FILE mini_roi_simulator.py
# ==============================================================