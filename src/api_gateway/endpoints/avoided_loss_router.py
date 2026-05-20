from fastapi import APIRouter, Depends, HTTPException
from src.api_gateway.schemas.avoided_loss_schema import AvoidedLossInput
from src.api_gateway.services.avoided_loss_calculator import generate_avoided_loss_report

# FastAPI 라우터 정의 (최종 게이트웨이 엔드포인트)
router = APIRouter(prefix="/v1", tags=["AvoidedLoss"])

@router.post("/avoided_loss", response_model=AvoidedLossOutput, summary="재무적 위험 회피 비용 계산 및 보고서 생성")
async def calculate_and_report_loss(input_data: AvoidedLossInput):
    """
    POST 요청을 받아 'Avoided Loss'를 핵심 로직으로 계산하고 구조화된 보고서를 반환합니다.
    입력 데이터는 반드시 Pydantic 스키마에 의해 유효성 검증됩니다.
    """
    try:
        report = generate_avoided_loss_report(input_data)
        return report
    except Exception as e:
        # 내부 로직 오류를 API 레벨에서 포착하여 500 에러 반환
        print(f"Error processing avoided loss request: {e}") # 로그 기록 위치
        raise HTTPException(status_code=500, detail="API 게이트웨이 처리 중 내부 오류가 발생했습니다. 로직을 재검토해주세요.")