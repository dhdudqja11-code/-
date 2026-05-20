from fastapi import APIRouter, HTTPException, Depends
from app.services.financial_model import calculate_avoided_loss, VariableInput, AvoidedLossReport
from pydantic import BaseModel

router = APIRouter()

@router.post("/avoided-loss", response_model=AvoidedLossReport)
async def get_avoided_loss(variables: VariableInput):
    """
    POST /api/v1/avoided-loss 엔드포인트입니다.
    사용자가 입력한 변수를 받아, 행동경제학적 가중치를 적용하여
    회피 가능한 최대 손실액을 계산하고 상세 분석 보고서를 반환합니다.
    """
    try:
        # 1. 비즈니스 로직 호출 (핵심 분리)
        report = calculate_avoided_loss(variables)

        # 2. 시스템 검증 및 출력 가드 적용
        if report.calculated_avoided_loss < 0:
            raise HTTPException(status_code=400, detail="산출된 손실액은 물리적으로 음수일 수 없습니다.")

        return report
    except Exception as e:
        # E-001 수준의 강력한 에러 처리
        print(f"API Error Catch: {e}")
        raise HTTPException(status_code=500, detail=f"Backend processing error. Check logs for details.")