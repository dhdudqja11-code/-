from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas import AvoidedLossResponse, InputData, CalculationInputs
from app.services.loss_calculator import calculate_avoided_loss, run_stress_test
from app.api.v1 import marketing_router
import time
import json

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Avoided Loss API Gateway", version="v1")
app.include_router(marketing_router.router, prefix="/api/v1", tags=["Marketing"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Pydantic 유효성 검사 에러(422) 발생 시 400 Bad Request로 매핑하고 구조화된 에러 JSON을 반환합니다."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = first_error.get("msg", "Validation error")
    loc = first_error.get("loc", ["body"])
    field = loc[-1] if loc else "unknown"
    
    # E4001: 누락된 필드, E4002: 타입 상충
    error_code = "E4002"
    if "missing" in msg or "required" in msg or "none" in msg.lower() or field == "regulatory_risk_score":
        error_code = "E4001"
        
    error_payload = {
        "success": False,
        "error": {
            "error_code": error_code,
            "message": f"데이터 유효성 검증 실패: {msg}",
            "failed_field": str(field),
            "required_action": "요청 바디의 필수 필드를 확인하거나 데이터 타입을 수정하십시오."
        },
        "data": None,
        "timestamp": str(time.time())
    }
    return JSONResponse(status_code=400, content={"detail": error_payload})


@app.post("/api/v1/avoided_loss", response_model=AvoidedLossResponse)
async def calculate_loss(
    input_data: InputData, 
    calc_inputs: CalculationInputs
):
    """
    핵심 Avoided Loss 계산 엔드포인트입니다. 트랜잭션 데이터와 행동경제학적 변수를 결합하여 위험 손실을 산출합니다.
    """
    start_time = time.time()

    # Pydantic 모델 -> Dict로 변환 (Service Layer 전달용)
    input_data_dict = input_data.dict()
    calc_inputs_dict = calc_inputs.dict()

    # 핵심 로직 실행 및 결과 분리
    result, error = calculate_avoided_loss(input_data_dict, calc_inputs_dict)

    # 에러 처리 (구조화된 오류 반환)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={"success": False, "error": error.dict(), "data": None, "timestamp": str(time.time())}
        )

    # 성공 응답 생성
    response = AvoidedLossResponse(
        success=True,
        data=result,
        error=None,
        timestamp=str(time.time())
    )
    return response

@app.get("/api/v1/stress_test")
async def run_stress_test_endpoint():
    """API 로직의 안정성을 검증하는 스트레스 테스트 엔드포인트입니다."""
    # 가상 입력 데이터 구조를 정의합니다. (실제 전송되는 형태 모방)
    mock_input = {
        "client_id": "TEST_USER_001",
        "transaction_value": 5000.0,
        "data_source": "Webhook", # Webhook으로 가정하여 규제 리스크 점수 필수화 유도
        "risk_factor_input": {"jurisdiction": "EU"}
    }

    # 실제 로직 검증 함수 호출 (Requirement 3)
    is_passed, message = run_stress_test(mock_input)

    if is_passed:
         return {"status": "PASS", "message": f"스트레스 테스트 성공. 결과: {message}"}
    else:
        # 실패 시 상세 에러 메시지 반환
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={"status": "FAIL", "error": message}
        )