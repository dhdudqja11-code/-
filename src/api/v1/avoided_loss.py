from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from src.services.avoided_loss_calculator import calculate_avoided_loss, calculate_mitigation_strategy

router = APIRouter()

class AvoidedLossRequest(BaseModel):
    """API 요청 본문 스키마 정의"""
    transaction_data: Dict[str, Any] = Field(..., description="경제적/감정적 변수 포함 트랜잭션 데이터")
    regulatory_risk_score: float = Field(..., ge=0.0, le=1.0, description="규제 리스크 점수 (0.0 ~ 1.0)")

class AvoidedLossResponse(BaseModel):
    """API 응답 스키마 정의"""
    avoided_loss_amount: float = Field(..., description="총 계산된 회피 손실액")
    mitigation_suggestion: str = Field(..., description="손실액에 따른 구체적인 완화 전략 제시")

@router.post("/avoided_loss", response_model=AvoidedLossResponse)
async def post_avoided_loss(request: AvoidedLossRequest):
    """
    트랜잭션 데이터와 규제 리스크 점수를 기반으로 회피 손실액을 계산하고 
    구체적인 완화 전략을 제시합니다. (POST /api/v1/avoided_loss)
    """
    try:
        # 1. 핵심 로직 호출 및 실행 (Service Layer 의존)
        total_loss = calculate_avoided_loss(request.transaction_data, request.regulatory_risk_score)

        if total_loss < 0:
            raise HTTPException(status_code=422, detail="계산된 손실액은 음수가 될 수 없습니다.")

        # 2. 완화 전략 제시 (Service Layer 의존)
        mitigation = calculate_mitigation_strategy(total_loss, "규제 위반") # 현재는 임시로 '규제 위반' 고정 처리
        
        return AvoidedLossResponse(
            avoided_loss_amount=total_loss,
            mitigation_suggestion=mitigation
        )

    except Exception as e:
        # 모든 예외를 포착하여 시스템 오류가 아닌 비즈니스 로직 문제로 응답합니다.
        print(f"API Error during avoided loss calculation: {e}")
        raise HTTPException(status_code=500, detail="Avoided Loss 계산 중 내부 서버 오류가 발생했습니다.")