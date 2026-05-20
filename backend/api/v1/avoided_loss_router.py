from fastapi import APIRouter, HTTPException, status
import uvicorn
from datetime import datetime
from ..services.avoided_loss_calculator import calculate_avoided_loss, TransactionData, RiskDataPoint

# 라우터 설정 (API 엔드포인트)
router = APIRouter()

@router.post("/avoided-loss", response_model=dict)
async def get_avoided_loss_report(transaction_data: dict, risk_data: list):
    """
    POST /api/v1/avoided-loss 엔드포인트입니다. 
    트랜잭션 데이터와 외부 리스크 데이터를 받아 Avoided Loss 보고서를 생성합니다.
    """
    try:
        # 1. 입력 파싱 및 타입 강제 변환 (Input Parsing & Type Casting)
        txn = TransactionData(
            transaction_id=str(transaction_data['transaction_id']),
            source=transaction_data['source'],
            amount=float(transaction_data['amount']),
            timestamp=datetime.fromisoformat(transaction_data['timestamp']) # ISO 포맷 가정
        )

        # 리스크 데이터 파싱
        risks = []
        for item in risk_data:
            risks.append(RiskDataPoint(
                risk_type=str(item['risk_type']),
                severity_score=float(item['severity_score']),
                verification_time=datetime.fromisoformat(item['verification_time']),
                source=str(item['source'])
            ))

        # 2. 핵심 로직 실행 (Service Call)
        report = calculate_avoided_loss(txn, risks)

        # 3. 성공 응답 반환
        return {
            "status": "success",
            "message": "Avoided Loss Report generated successfully.",
            "data": report.__dict__
        }

    except ValueError as e:
        # 비즈니스 로직 또는 데이터 타입 오류 처리 (422 Unprocessable Entity)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation Error: {e}")
    except Exception as e:
        # 예측하지 못한 시스템 레벨 에러 처리 (500 Internal Server Error)
        print(f"[CRITICAL ERROR] API Gateway Failure: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during report generation.")

# 테스트용 서버 실행 함수 (실제 환경에서는 별도 관리)
def run_api_server():
    """개발/테스트 목적으로 FastAPI를 로컬에서 구동합니다."""
    print("\n[INFO] Starting temporary API Gateway Server on http://127.0.0.1:8000")
    uvicorn.run("backend.api.v1.avoided_loss_router:router", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # 테스트 시에는 이 함수를 직접 호출하여 동작을 확인합니다.
    pass # 실제 사용은 uvicorn 명령어로 대체됨