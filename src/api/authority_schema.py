from typing import Dict, Any, Literal, Optional
from pydantic import BaseModel, Field

# 1. 입력 데이터 스키마: 시스템에 던져지는 모든 정보는 구조화되어야 함 (Authority Schema)
class AuthorityCheckRequest(BaseModel):
    """시스템 진단에 필요한 원본 트랜잭션 및 리스크 데이터를 담는 요청 본문."""
    transaction_id: str = Field(..., description="분석 대상의 고유 거래 ID.")
    source_data: Dict[str, Any] = Field(..., description="데이터 출처 (Source) 정보를 포함한 원본 데이터 딕셔너리.")
    timestamp: float = Field(..., description="데이터 수집 시점의 타임스탬프.")

# 2. 출력 상태 전이 스키마: 시스템적 권위를 담은 구조화된 응답 (The Single Source of Truth)
class AuthorityCheckResponse(BaseModel):
    """시스템 진단 결과. 반드시 '문제 정의 -> 원인 분석 -> 해결책 제시'의 논리적 흐름을 따른다."""
    status_code: Literal["INITIAL", "WARNING", "BREACHED", "RESOLVED"] = Field(..., description="현재 시스템 상태 (Initial, Warning, Breached, Resolved).")
    authority_score: float = Field(..., ge=0.0, le=100.0, description="시스템적 통제권 확보 점수 (Authority Meter 값).")
    loss_estimate: Optional[float] = Field(None, description="예상되는 재무적 손실 규모 (Loss Estimate).")

    # [문제 정의]: 무엇이 잘못되었는지 사용자에게 명확히 전달
    problem_definition: str = Field(..., description="발생한 핵심 문제를 규제/시스템 관점에서 정의.")
    # [원인 분석]: 왜 문제가 발생했는지, 시스템적 결함으로 포장하여 제시
    root_cause_analysis: str = Field(..., description="데이터의 출처 및 흐름을 추적하며 문제 원인을 분석.")
    # [해결책 제시]: 이 문제를 어떻게 해결해야 하는지 구체적인 행동 지침 제공
    mitigation_suggestion: str = Field(..., description="통제권 확보를 위한 단계별/기술적 해결 방안.")

# 3. 에러 전이 스키마 (강제 지연 및 오류 통제): 시스템 장애 시에도 권위를 유지해야 함
class ErrorTransitionResponse(BaseModel):
    """시스템 내부 오류 또는 외부 API 실패 시, 패닉하지 않고 통제권을 상실하지 않음을 알리는 응답."""
    error_code: str = Field(..., description="내부 에러 코드.")
    message: str = Field(..., description="사용자에게 보여줄 경고 메시지.")
    recovery_action: str = Field(..., description="시스템이 현재 취하고 있는 자가 복구 행동 (Authority Recovery).")
    forced_delay_seconds: float = 1.0 # ★ CEO 지시사항 준수: 강제 지연 시간 1초 고정

# 최종 응답 모델은 이 둘 중 하나를 반환해야 함을 명시적으로 지정
ApiResponse = AuthorityCheckResponse | ErrorTransitionResponse