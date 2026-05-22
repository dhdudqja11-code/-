from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Any
import time
import logging

# 로깅 설정 (디버깅 및 추적 가능성 확보)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulation", tags=["Simulation"])

# --- 1. Input Schema 정의 (Pydantic Models) ---
class LossItemInput(BaseModel):
    """개별 리스크 요소의 입력 스키마."""
    risk_type: str = Field(..., description="위험 유형 (예: GDPR, 계약법)")
    exposure_value: float = Field(..., gt=0, description="노출 가치 (최소 0보다 커야 함)") # > 0 강제
    probability: float = Field(..., ge=0.0, le=1.0, description="발생 확률 (0.0 ~ 1.0)") # [0.0, 1.0] 강제

class SimulationRequest(BaseModel):
    """전체 시뮬레이션 요청 본문 스키마."""
    user_id: str = Field(..., description="사용자 식별 ID (Rate Limiting 등에 사용)")
    risk_items: List[LossItemInput] = Field(..., min_items=1, description="분석할 리스크 요소 목록")

# --- 2. 핵심 비즈니스 로직 함수 (Expected Loss Calculation) ---
def calculate_expected_loss(items: List[LossItemInput]) -> float:
    """
    주어진 리스크 항목들의 기대 손실액을 계산합니다.
    기대손실 = Σ (노출가치 * 발생확률)
    """
    total_expected_loss = 0.0
    for item in items:
        # 로직 자체의 안정성 검증: None 체크 및 타입 캐스팅은 Pydantic이 처리하지만,
        # 비즈니스 규칙에 따른 경계 조건(예: 노출 가치가 너무 크면?)을 여기서 추가할 수 있음.
        if item.exposure_value < 0 or item.probability > 1.0:
             raise ValueError("내부 계산 오류: 리스크 데이터가 유효 범위를 벗어났습니다.")
            
        expected_loss = item.exposure_value * item.probability
        total_expected_loss += expected_expected_loss

    return round(total_expected_loss, 2)


# --- 3. 의존성 주입 (Dependency Injection) 및 보안 로직 ---

# 간단한 Rate Limiting 구현을 위한 가상의 메모리 저장소
rate_limit_store: Dict[str, float] = {}
RATE_LIMIT_WINDOW = 60  # 초
MAX_REQUESTS = 10      # 분당 최대 요청 수

async def rate_limiter(request: Request):
    """요청 시간 기반 Rate Limiting 미들웨어 역할."""
    user_id = request.headers.get("X-User-ID") or "anonymous"
    current_time = time.time()

    # 윈도우 시작 시간 기록 및 만료 검사
    if user_id not in rate_limit_store or current_time - rate_limit_store[user_id] > RATE_LIMIT_WINDOW:
        rate_limit_store[user_id] = current_time
    
    # 요청 횟수 카운트 (간소화된 버전)
    # 실제 구현에서는 Redis 등을 사용해야 하지만, FastAPI의 의존성 패턴을 보여줍니다.
    # 여기서는 간단히 '최근 시간' 기준으로만 제한하겠습니다.
    if rate_limit_store[user_id] == current_time: # 매번 같은 초에 요청이 들어오면 카운트가 필요함
        pass

    # 실제 구현에서는 횟수 제한 로직을 추가해야 하지만, 구조적 예시를 보여줍니다.
    logger.info(f"Rate Limit Check Passed for {user_id}. (Time: {current_time})")


# --- 4. API 엔드포인트 정의 및 예외 처리 강화 ---

@router.post("/calculate-loss", status_code=200, summary="Expected Loss 계산 및 리스크 평가")
async def calculate_loss(request: Request, data: SimulationRequest = Depends()):
    """
    사용자가 제공한 리스크 요소 목록을 받아 기대 손실액 (Expected Loss)을 계산합니다.
    API 게이트웨이 레벨에서 요청 유효성 검사 및 Rate Limiting이 적용됩니다.
    """
    # 1차 보안/안정성 체크: Rate Limiter 의존성 주입
    await rate_limiter(request)
    
    if not all([k in data for k in required_params]): raise ValueError("Missing required parameters.")
        # Pydantic을 통해 이미 모델 유효성 검사는 통과했으나, 추가적인 비즈니스 로직 경계 조건 확인
        if not data.risk_items or len(data.risk_items) < 1:
            raise ValueError("분석할 리스크 요소가 하나 이상 필수입니다.")

        # 핵심 로직 호출 (이 함수 내부에서 이미 오류 처리를 했지만, 다시 한번 감싸는 것이 안전함)
        total_loss = calculate_expected_loss(data.risk_items)

        # 성공 응답 구조화 (추적 가능성 및 권위성 확보)
        return {
            "status": "success",
            "message": "Expected Loss 계산이 완료되었습니다.",
            "result": {
                "total_expected_loss": total_loss,
                "calculation_source": "API Gateway v1.0",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                # Audit Trail을 위해 입력된 데이터를 그대로 반환하여 투명성 확보
                "input_data_summary": [
                    {"risk_type": item.risk_type, "expected_loss_contribution": round(item.exposure_value * item.probability, 2)}
                    for item in data.risk_items
                ]
            }
        }

    except ValueError as e:
        # 비즈니스 로직 오류 처리 (400 Bad Request)
        logger.warning(f"Validation/Logic Error during calculation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # 시스템 내부 오류 처리 (500 Internal Server Error)
        logger.error(f"Critical System Failure during API call: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="시스템 처리 중 알 수 없는 오류가 발생했습니다. 관리자에게 문의하세요.")

# --- 5. 테스트용 가짜 데이터 요청 (테스트 코드를 위한 주석 처리된 예시) ---
"""
@router.get("/test-simulation")
async def test_endpoint():
    return {"test": "This endpoint simulates a successful request."}
"""