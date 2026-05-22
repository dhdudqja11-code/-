from fastapi import APIRouter, Depends, HTTPException, status
from ..models.simulation_input import SimulationInput, SimulationResult
from ..services.simulator_service import SimulatorService

# FastAPI Router 정의 (API 엔드포인트 담당)
router = APIRouter(prefix="/api/v1", tags=["Simulation"])

@router.post("/simulation", response_model=SimulationResult)
async def run_mini_roi_simulation(input_data: SimulationInput):
    """
    Mini ROI 시뮬레이션을 실행하는 엔드포인트입니다.
    요청 바디의 데이터를 받아 비즈니스 로직을 호출합니다.
    """
    try:
        # 1. 입력 데이터 검증은 FastAPI/Pydantic이 자동으로 처리합니다 (422).

        # 2. 핵심 서비스 호출
        result = SimulatorService.run_simulation(input_data)
        return result

    except ValueError as e:
        # 비즈니스 로직에서 발생하는 유효성 검증 오류 처리
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # 예측하지 못한 서버 내부 에러 (가장 중요하게 처리)
        print(f"FATAL ERROR in simulation API: {e}") # 로깅 필수
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="서버에서 예상치 못한 오류가 발생했습니다.")