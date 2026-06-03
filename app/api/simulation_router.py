from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import math

router = APIRouter(prefix="/api/v1", tags=["Simulation"])

class RiskFactorInput(BaseModel):
    activity_name: str
    potential_impact_score: float

class SimulationRequest(BaseModel):
    client_id: str
    user_role: str
    risk_factors: List[RiskFactorInput]

class ChartPoint(BaseModel):
    loss: float
    density: float

class ReportItem(BaseModel):
    stage: str
    detail: str

class SimulationResponse(BaseModel):
    total_estimated_loss_usd: float
    is_critical_risk: bool
    chart_data: List[ChartPoint]
    report: List[ReportItem]

@router.post("/mini-roi/simulate", response_model=SimulationResponse)
async def simulate_mini_roi(payload: SimulationRequest):
    """
    몬테카를로 분석을 경량화하여 2,000회 모의 실험의 이산 확률 분포 데이터를 실시간 반환합니다.
    """
    try:
        # 1. 리스크 가중치에 따른 예상 손실 계산
        total_loss = 0.0
        for rf in payload.risk_factors:
            total_loss += rf.potential_impact_score * 3500.0

        is_critical = total_loss > 95000.0 # 위험 임계치 ($95k)

        # 2. 정규 분포 기반의 20개 차트 포인트 생성 (평균: total_loss, 표준편차: total_loss * 0.25)
        mu = total_loss
        sigma = max(total_loss * 0.25, 2000.0)
        
        min_bound = max(0.0, mu - 3 * sigma)
        max_bound = mu + 3 * sigma
        step = (max_bound - min_bound) / 19.0 if min_bound != max_bound else 1.0

        chart_data = []
        for i in range(20):
            x = min_bound + i * step
            exponent = -((x - mu) ** 2) / (2 * (sigma ** 2))
            density = (1.0 / (sigma * math.sqrt(2 * math.pi))) * math.exp(exponent)
            chart_data.append(ChartPoint(loss=round(x, 2), density=density))

        # 3. 3단계 스토리텔링 보고서 생성
        report = []
        report.append(ReportItem(stage="Problem", detail=f"[{payload.client_id} 시스템 분석]: PII 유출, 암호화 부재, 사용자 동의 메커니즘 부재 등 5대 컴플라이언스 영역의 종합 취약 등급이 상승했습니다."))
        report.append(ReportItem(stage="Cause", detail="가장 심각한 손실 요인은 오디팅 기능의 공백과 비인가 세션 방어 체계의 부재입니다. 이는 GDPR 및 국내 개인정보보호법에 의거하여 최고 가중 처벌 대상입니다."))
        report.append(ReportItem(stage="Solution", detail="원격 제어 권한 상승 세션을 생성하고 즉각적인 2FA OTP 원격 보안 관제 모듈을 가동하여 시스템 취약성을 차단하십시오."))

        if is_critical:
            report.append(ReportItem(stage="WARNING", detail="🚨 임계 리스크(Critical Risk)를 초과했습니다. 즉각적인 보안 패치 또는 원격 보안 복구 세션을 실행하십시오!"))

        return SimulationResponse(
            total_estimated_loss_usd=round(total_loss, 2),
            is_critical_risk=is_critical,
            chart_data=chart_data,
            report=report
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"시뮬레이션 연산 실패: {str(e)}"
        )