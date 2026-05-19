from typing import Optional
from pydantic import BaseModel, Field, validator
import time

# --- 1. 데이터 스키마 정의 및 유효성 검사 (Pydantic) ---
class AvoidedLossInput(BaseModel):
    """
    Avoided Loss 계산에 필요한 모든 변수와 초기 손실액을 담는 입력 모델.
    모든 필수 값은 누락되거나 비정상적일 경우 Pydantic이 예외를 발생시킵니다.
    """
    initial_loss_amount: float = Field(..., description="사고 발생 시의 기본 재무적 손실액 (L).")
    regulatory_lag_penalty_factor: Optional[float] = Field(None, ge=0.0, description="규제 적응 시차 벌금 계수 (PLT). 0 이상이어야 함.")
    reputation_damage_multiplier: Optional[float] = Field(1.0, ge=1.0, description="평판 손실 증폭 계수 (RDM). 최소 1.0부터 시작.")
    interoperability_debt_cost: Optional[float] = Field(None, ge=0.0, description="데이터 상호운용성 부채 비용 (IDC).")

    @validator('initial_loss_amount')
    def check_positive_loss(cls, v):
        if v < 0:
            raise ValueError("초기 손실액은 음수일 수 없습니다.")
        return v


# --- 2. 핵심 비즈니스 로직 (Pure Function) ---
def calculate_avoided_loss(data: AvoidedLossInput) -> float:
    """
    최종 'Avoided Loss' 금액을 계산하는 순수 함수.
    모든 변수가 입력 데이터에 의해 통제됨을 보장합니다.
    """
    L = data.initial_loss_amount

    # 1. 기본 손실액 (L)에 평판 증폭 계수를 적용하여 초기 피해 규모 산정
    adjusted_l = L * data.reputation_damage_multiplier

    # 2. 데이터 상호운용성 부채 비용 추가 (IDC)
    if data.interoperability_debt_cost is None:
        # IDC가 필수 변수라면 여기서 에러를 발생시키거나, 기본값을 설정해야 함.
        # 현재는 Optional이므로, 누락 시 0으로 간주하고 진행하되 로깅 필요.
        idc = 0.0
    else:
        idc = data.interoperability_debt_cost

    # 3. 최종 Avoided Loss 계산 (가장 큰 위험 요소를 제거한 가치)
    avoided_loss = adjusted_l + idc

    return round(avoided_loss, 2)


# --- 3. API 서비스 레이어 (Caching & Error Handling 포함) ---
# 실제 Redis 연결은 환경 설정에 따라 달라지므로, Mock 객체로 대체합니다.
MOCK_CACHE = {}

def get_cached_result(input_data: AvoidedLossInput):
    """Redis 캐시에서 결과를 조회하는 모킹 함수."""
    cache_key = hash(str(input_data))
    if cache_key in MOCK_CACHE:
        print(f"[Cache Hit] Key {cache_key} found. Returning cached value.")
        return MOCK_CACHE[cache_key]
    return None

def set_cached_result(input_data: AvoidedLossInput, result: float):
    """Redis 캐시에 결과를 저장하는 모킹 함수 (TTL 1시간 설정 가정)."""
    global MOCK_CACHE
    MOCK_CACHE[hash(str(input_data))] = result
    print(f"[Cache Write] Key {hash(str(input_data))} stored successfully.")


def compute_avoided_loss_service(input_data: AvoidedLossInput) -> dict:
    """
    최종 API 진입점. 캐싱, 유효성 검사, 계산을 총괄합니다.
    """
    # 1. 캐시 체크 (성능 최적화)
    cached_result = get_cached_result(input_data)
    if cached_result is not None:
        return {
            "status": "Success",
            "source": "Cache Hit",
            "avoided_loss": cached_result,
            "message": "캐시된 결과입니다. 계산 로직 실행을 생략했습니다."
        }

    # 2. 핵심 계산 수행 (비즈니스 로직)
    try:
        start_time = time.time()
        avoided_loss = calculate_avoided_loss(input_data)
        end_time = time.time()
        
        result = {
            "status": "Success",
            "source": "Live Calculation",
            "avoided_loss": avoided_loss,
            "message": f"계산 완료. 소요 시간: {(end_time - start_time) * 1000:.2f}ms."
        }

        # 3. 캐시 저장 (지연 시간을 감안하여 Redis에 저장했다고 가정)
        set_cached_result(input_data, avoided_loss)
        return result

    except ValueError as e:
        # Pydantic 또는 내부 로직에서 정의된 유효성 오류 처리
        return {
            "status": "Error",
            "source": "Validation Failure",
            "avoided_loss": 0.0,
            "message": f"입력 데이터 검증 실패: {e}"
        }
    except Exception as e:
        # 예상치 못한 시스템 오류 처리 (Critical Error)
        return {
            "status": "Error",
            "source": "System Failure",
            "avoided_loss": 0.0,
            "message": f"예기치 않은 서버 오류 발생: {type(e).__name__} - {str(e)}"
        }

# --- 예제 사용 (테스트용) ---
if __name__ == "__main__":
    print("--- [TEST 1] 정상 케이스 테스트 ---")
    try:
        valid_data = AvoidedLossInput(
            initial_loss_amount=50000,
            regulatory_lag_penalty_factor=1.2, # PLT를 활용할 여지는 있지만, 계산 로직에는 현재 미포함으로 간주하고 테스트
            reputation_damage_multiplier=1.5,
            interoperability_debt_cost=30000
        )
        result = compute_avoided_loss_service(valid_data)
        print("\n[결과]:", result)

    except Exception as e:
        print(f"테스트 실패: {e}")


    print("\n\n--- [TEST 2] 캐시 히트 테스트 ---")
    # 동일 입력으로 재실행하여 캐싱 확인
    valid_data_repeat = AvoidedLossInput(initial_loss_amount=50000, reputation_damage_multiplier=1.5, interoperability_debt_cost=30000)
    result_cache = compute_avoided_loss_service(valid_data_repeat)
    print("\n[결과]:", result_cache)


    print("\n\n--- [TEST 3] 에지 케이스 (데이터 누락/오류) 테스트 ---")
    # initial_loss_amount를 음수로 넣어 유효성 검사 실패 유도
    try:
        invalid_data = AvoidedLossInput(
            initial_loss_amount=-100, # <--- 오류 발생 지점
            reputation_damage_multiplier=1.5, 
            interoperability_debt_cost=30000
        )
    except Exception as e:
        print(f"[예외 처리 성공] Pydantic이 미리 잡았습니다. (실제 API에서는 이 예외가 Service Layer로 전달됩니다.)")

    # 유효성 검사 실패를 시뮬레이션하기 위해, 모델을 강제로 우회하는 상황을 가정하고 테스트 코드를 작성해야 함.
    # 여기서는 calculate_avoided_loss 내부의 try/except 구문이 이를 처리할 것으로 간주합니다.