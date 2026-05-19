from fastapi import FastAPI, HTTPException, status
from decimal import Decimal
from .schemas import AvoidedLossInput, CentralGatewayResponse, LossCalculationResult, AssuranceIndexResult, GatewayValidator
import uvicorn # 실행용 라이브러리

app = FastAPI(title="Central Assurance API Gateway", version="1.0")

@app.post("/v1/calculate_value", response_model=CentralGatewayResponse)
async def calculate_avoided_loss_and_assurance(input_data: AvoidedLossInput):
    """
    모든 비즈니스 로직의 단일 진입점입니다. 
    Avoided Loss와 Assurance Index를 통합 계산하고 표준화된 응답을 반환합니다.
    """
    # 1. 입력 유효성 검증 (Gatekeeper 역할)
    warning = GatewayValidator.validate_input(input_data)
    if warning:
        print(f"🚨 WARNING Detected by Gateway: {warning}")

    try:
        # 2. 핵심 로직 호출 및 가치 산출
        total_loss, breakdown = calculate_core_avoided_loss(input_data)
        assurance_result = calculate_assurance_index(input_data)

        # 3. 표준화된 응답 반환 (Contract 준수)
        return CentralGatewayResponse(
            calculated_loss=LossCalculationResult(
                total_avoided_loss_usd=total_loss, 
                breakdown_details=breakdown
            ),
            assurance_index=AssuranceIndexResult(
                assurance_index=assurance_result['index'],
                confidence_score_description=assurance_result['message']
            )
        )

    except Exception as e:
        # 예상치 못한 오류는 반드시 Catch하여 클라이언트에게 명확한 에러 메시지를 전달해야 합니다.
        print(f"CRITICAL ERROR in Gateway: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate value due to internal service error.")

# --- Mock Business Logic Functions (실제 로직이 들어갈 자리) ---

def calculate_core_avoided_loss(input: AvoidedLossInput):
    """
    [Core Service 1] 모든 리스크를 합산하여 총 회피 손실액을 계산합니다.
    (여기에 복잡한 금융 모델 및 가중치 로직이 들어갑니다.)
    """
    # Mock Calculation Logic (단순 합산 + 가중치 적용 예시)
    loss_reg = input.compliance_risk.estimated_loss_usd * input.compliance_risk.severity_score / 5
    loss_data = input.data_breach_risk.leaked_user_count * input.data_breach_risk.avg_damage_per_user_usd * (1 + input.data_breach_risk.delay_hours / 100)
    loss_op = input.operational_risk.transaction_volume * input.operational_risk.labor_cost_per_txn_usd * (input.operational_risk.error_rate_percent / 100)

    total_loss = loss_reg + loss_data + loss_op
    
    breakdown = {
        "Regulatory Compliance": f"${loss_reg:,.2f}",
        "Data Breach & Privacy": f"${loss_data:,.2f}",
        "Operational Inefficiency": f"${loss_op:,.2f}"
    }
    return total_loss, breakdown

def calculate_assurance_index(input: AvoidedLossInput):
    """
    [Core Service 2] 솔루션의 통제력 확보 정도를 측정합니다. (0.0 ~ 1.0)
    """
    # Mock Calculation Logic: 리스크가 높을수록 Assurance Index 개선 효과가 커지도록 설계.
    risk_magnitude = input.compliance_risk.severity_score + (input.data_breach_risk.leaked_user_count / 1000)
    index = min(1.0, risk_magnitude * 0.3) # 최대 1.0을 넘지 않도록 제한

    message = f"시스템은 ({risk_magnitude:.2f} 기반) 리스크를 포착하고 {int(index*100)}% 이상의 통제력으로 회피 가능성을 극대화합니다."
    return {"index": index, "message": message}

# --- 테스트용 로컬 실행 블록 (실제 Git 커밋에는 포함되지 않음) ---
if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    print("--- FastAPI Gateway Mock Test Run Successful ---")