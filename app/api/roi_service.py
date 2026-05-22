from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import json
import random
from typing import List, Dict

router = APIRouter(prefix="/mini-roi", tags=["MiniROI"])

# --------------------
# Pydantic Models (데이터 계약 정의)
# --------------------

class InputData(BaseModel):
    """사용자 입력 데이터 구조체: 분석 대상 정보."""
    user_industry: str = Field(..., description="사용자의 산업군")
    data_volume_gb: float = Field(..., gt=0, description="보유 데이터 볼륨 (GB)")
    regulatory_risk_score: int = Field(..., ge=1, le=10, description="현재 자가 진단 리스크 점수 (1~10)")

class AnalysisResult(BaseModel):
    """API 최종 결과 구조체: 3단계 스토리텔링 강제."""
    status: str # "WARNING" 또는 "SAFE"
    risk_score: int
    # [1] 문제 정의 (What went wrong?)
    problem_definition: str = Field(..., description="구체적인 위기 상황 설명")
    # [2] 원인 분석 (Why did it go wrong? Source/Time)
    cause_analysis: str = Field(..., description="위험 발생의 법적/기술적 근거 및 출처 명시")
    # [3] 해결책 제시 (How to fix it?)
    mitigation_suggestion: str = Field(..., description="실행 가능한 액션 플랜과 다음 단계 가이드")

# --------------------
# Core Logic Implementation
# --------------------

def perform_risk_analysis(input_data: InputData) -> AnalysisResult:
    """
    핵심 리스크 분석 로직. 입력 데이터에 따라 3단계 구조의 결과물을 생성합니다.
    이 함수는 모든 비즈니스 로직을 담고 있으며, 실패 시에도 일관된 출력을 보장해야 합니다.
    """
    # 임시적인 복잡한 위험 판단 로직 (실제로는 DB나 외부 API 연동)
    if input_data.regulatory_risk_score >= 7 or input_data.data_volume_gb > 50:
        status = "WARNING"
        risk_score = input_data.regulatory_risk_score + int(input_data.data_volume_gb / 10)
        
        # 강제된 스토리텔링 출력 로직 (가장 중요한 부분!)
        problem = f"현재 {input_data.user_industry} 산업의 데이터 처리 방식은 법적 규정 {random.choice(['GDPR', 'CCPA', '국내 개인정보보호법'])}에 근거하여 심각한 리스크를 안고 있습니다."
        cause = f"주요 원인은 보유 데이터 볼륨({input_data.data_volume_gb}GB) 대비 데이터 생명주기(Lifecycle Management) 관리가 미흡하기 때문입니다. 출처: {random.choice(['내부 감사팀', '최신 법규 개정안'])}."
        solution = "가장 시급한 것은 전용 API 게이트웨이를 구축하고, 모든 트랜잭션을 중앙에서 검증하는 모듈을 도입하는 것입니다. 즉시 컨설팅이 필요합니다."

    else:
        status = "SAFE"
        risk_score = input_data.regulatory_risk_score
        problem = f"{input_data.user_industry} 산업의 데이터 관리는 현재 법규를 준수하고 있으며 안정적입니다."
        cause = "특정 규제 위반 징후가 포착되지 않았습니다. 다만, 지속적인 모니터링이 필요합니다."
        solution = "현재 프로세스를 유지하되, 비즈니스 성장에 맞춰 데이터 구조화 작업을 진행하는 것을 추천드립니다."

    return AnalysisResult(
        status=status,
        risk_score=min(10, risk_score), # 최대 10으로 제한
        problem_definition=problem,
        cause_analysis=cause,
        mitigation_suggestion=solution
    )


@router.post("/", response_model=AnalysisResult)
async def run_mini_roi_simulation(data: InputData):
    """Mini ROI 시뮬레이션 API 엔드포인트."""
    try:
        # 로직 실행 및 결과 수신
        result = perform_risk_analysis(data)
        return result
    except Exception as e:
        print(f"🚨 [ERROR] Simulation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API 처리 중 예상치 못한 오류가 발생했습니다. 시스템을 점검해 주세요."
        )

# --------------------
# Endpoints Test Stub (개발 단계에서 사용할 스텁)
# --------------------
@router.get("/test")
def test_endpoint():
    return {"message": "Mini ROI Simulation API is operational."}