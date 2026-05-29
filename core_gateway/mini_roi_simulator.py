from pydantic import BaseModel, Field, validator
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
import random

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

class ChartDataPoint(BaseModel):
    """웹 대시보드 시각화용 단일 차트 데이터 포인트."""
    loss: float = Field(..., description="손실액 구간 기댓값 (USD)")
    density: float = Field(..., description="해당 구간 손실이 발생할 확률 밀도")

class SimulationOutput(BaseModel):
    """Mini ROI 시뮬레이션의 최종 출력 구조."""
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="이번 시뮬레이션 고유 ID.")
    total_estimated_loss_usd: float = Field(..., ge=0, description="예상되는 총 손실액 (USD).")
    is_critical_risk: bool = Field(..., description="현재 위험 상태가 임계치(Critical)에 도달했는지 여부.")
    report: List[StructuredReportItem] = Field(..., min_items=1, description="위험 진단 3단계 구조 보고서.")
    chart_data: List[ChartDataPoint] = Field(default=[], description="웹 대시보드 시각화용 확률 밀도 포인트 배열.")

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

def generate_lightweight_monte_carlo(total_loss: float) -> List[ChartDataPoint]:
    """
    실시간 프론트엔드 출렁임 반응 속도(0.005초)를 보장하기 위해 설계된
    표준 random.triangular 기반 2,000회 경량 몬테카를로 시뮬레이션 및 20개 구간 이산화 밀도 연산기.
    """
    if total_loss <= 0:
        return []
        
    # 삼각분포 범위 산정: 최빈값(total_loss), 최솟값(60%), 최댓값(150%)
    low = total_loss * 0.6
    high = total_loss * 1.5
    
    trials = 2000
    simulated_losses = [random.triangular(low, high, total_loss) for _ in range(trials)]
    
    # 20개 구간으로 이산화(binning)하여 히스토그램 확률 밀도 추출
    num_bins = 20
    min_val, max_val = min(simulated_losses), max(simulated_losses)
    bin_width = (max_val - min_val) / num_bins
    
    if bin_width <= 0:
        return [ChartDataPoint(loss=total_loss, density=1.0)]
        
    counts = [0] * num_bins
    for val in simulated_losses:
        bin_idx = int((val - min_val) / bin_width)
        if bin_idx >= num_bins:
            bin_idx = num_bins - 1
        counts[bin_idx] += 1
        
    # 확률 밀도 연산 (count / (total_samples * bin_width))
    chart_data: List[ChartDataPoint] = []
    for i in range(num_bins):
        bin_center = min_val + (i + 0.5) * bin_width
        density = counts[i] / (trials * bin_width)
        chart_data.append(ChartDataPoint(loss=round(bin_center, 2), density=round(density, 6)))
        
    return chart_data

# ==============================================================
# 3. FastAPI Router (API Endpoint Skeleton)
# ==============================================================

router = APIRouter()

@router.post("/api/v1/mini-roi/simulate", response_model=SimulationOutput)
async def simulate_mini_roi(input: SimulationInput):
    """
    Mini ROI 시뮬레이션을 실행하여 예상 손실액과 권위적 보고서, 그리고 대시보드 시각화용 차트 데이터를 반환합니다.
    이 엔드포인트는 핵심 컴플라이언스 게이트웨이를 통하는 필수 API입니다.
    """
    try:
        # 1. Core Logic 호출 및 결과 받기 (테스트 가능한 함수 활용)
        report, total_loss = calculate_mini_roi_loss(input)

        # 2. 0.005초 내 초고속 경량 몬테카를로 차트 시각화 데이터 생성
        chart_data = generate_lightweight_monte_carlo(total_loss)

        # 3. 최종 출력 객체 생성
        output = SimulationOutput(
            simulation_id=str(uuid.uuid4()),
            total_estimated_loss_usd=total_loss,
            is_critical_risk=(total_loss > 10000),
            report=report,
            chart_data=chart_data
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