from pydantic import BaseModel, Field, validator
from typing import List, Optional
import datetime

# --- 1. 입력 데이터 스키마 정의 (Pydantic) ---
class RiskFactor(BaseModel):
    """개별 리스크 요소를 정의합니다."""
    factor_name: str = Field(..., description="리스크 요소의 이름 (예: GDPR 위반, 데이터 유출)")
    potential_impact_score: float = Field(..., ge=0.1, le=10.0, description="잠재적 영향 점수 (0.1 ~ 10.0).")
    likelihood_of_occurrence: float = Field(..., gt=0.0, le=1.0, description="발생 가능성 (0.0 ~ 1.0).")

class SimulationInput(BaseModel):
    """시뮬레이션에 필요한 모든 입력 데이터를 통합 정의합니다."""
    company_name: str = Field(..., min_length=3, description="진단 대상 회사 이름.")
    industry_sector: str = Field(..., regex="^[A-Za-z0-9\s]+$", description="업종 분야 (알파벳/숫자만 허용).")
    data_assets_count: int = Field(..., ge=1, description="보유 데이터 자산 개수.")
    risks: List[RiskFactor] = Field(..., min_items=1, description="진단할 리스크 요소 목록.")

    @validator('industry_sector')
    def validate_sector_format(cls, v):
        # 실제 구현 시, 이 부분에 업종 분류 코드가 들어가야 합니다.
        if not v:
            raise ValueError("업종 분야는 필수입니다.")
        return v

# --- 2. 출력 데이터 스키마 정의 (결과물 형식) ---
class SimulationResult(BaseModel):
    """시뮬레이션의 최종 결과를 구조화합니다."""
    total_estimated_loss: float = Field(..., ge=0.0, description="총 추정 손실액 (단위: 원).")
    risk_summary: List[dict] = Field(..., description="요약된 리스크 목록과 경고 여부.")
    is_critical_state: bool = Field(False, description="임계 상태 진입 여부 (True/False).")
    suggested_cta: str = Field("진단 결과에 따른 다음 행동 가이드라인.", description="사용자에게 제시할 CTA 메시지.")

# --- 3. 전역 예외 클래스 정의 (미래를 위한 준비) ---
class SimulationError(Exception):
    """시뮬레이션 로직 실행 중 발생하는 비즈니스 레벨 오류."""
    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code