from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# =========================================
# 🧪 INPUT SCHEMA (클라이언트가 보내는 데이터)
# =========================================

class UserActionSimulation(BaseModel):
    """사용자의 특정 행동 시뮬레이션에 대한 메타데이터."""
    action_type: str = Field(description="시도된 사용자 액션의 유형 (예: data_export, third_party_integration)")
    data_scope: str = Field(description="처리하려는 데이터의 범위 (예: user_profile, financial_record)")
    source_system: str = Field(description="데이터가 유입되는 시스템/서비스 이름")

class AssessmentRequest(BaseModel):
    """전체 리스크 평가를 위한 요청 본문."""
    user_actions: List[UserActionSimulation] = Field(description="평가를 요청하는 모든 사용자 행동 목록.")
    metadata_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="요청이 발생한 시간 (Source/Time 추적용).")

# =========================================
# 🚨 OUTPUT SCHEMA (시스템이 반환해야 할 구조화된 Alert)
# =========================================

class RiskLevel(str, Enum):
    """리스크 심각도 레벨."""
    CRITICAL = "Critical" # 법적 위반, 즉시 중단 필요
    HIGH = "High"         # 정책 위반, 수정 후 진행 필요
    MEDIUM = "Medium"     # 권장 사항, 모니터링 필요
    LOW = "Low"           # 정상

class StructuredRiskAlert(BaseModel):
    """구조화된 리스크 경고 메시지 (메모리 기반 3단계 구조)."""
    risk_level: RiskLevel = Field(description="감지된 리스크의 심각도. Critical, High 등.")
    is_compliant: bool = Field(description="현재 행동이 규제에 부합하는지 여부.")
    
    # [1] 문제 정의 (What went wrong?) - 핵심적으로 사용자에게 충격을 주는 메시지
    problem_definition: str = Field(description="사용자가 인지해야 할 명확한 위반/위험 상황 설명.")
    
    # [2] 원인 분석 (Why did it go wrong? Source/Time) - 권위를 부여하는 법적 근거 및 출처 명시
    root_cause: str = Field(description="위험의 구체적인 기술적 또는 법적 근거. (예: GDPR Art. 17 위반).")
    source_details: dict = Field(description="데이터/행동의 원본 정보 추적지.") # {Source, Time} 등
    
    # [3] 해결책 제시 (How to fix it?) - 즉각적인 조치 가능한 Mitigation Suggestion
    mitigation_suggestion: str = Field(description="위험을 해소하기 위한 구체적이고 단계적인 행동 가이드라인.")

class RiskAssessmentResponse(BaseModel):
    """최종 API 응답 본문."""
    status_code: int = 200
    success: bool = True
    assessment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    alerts: List[StructuredRiskAlert] = Field(description="감지된 모든 리스크 경고 목록.")

# =========================================
# ✅ 정상 응답 (Low Risk / No Alert)
# =========================================
class SuccessfulAssessmentResponse(BaseModel):
    """모든 검증이 통과했을 때의 성공적인 구조화된 응답."""
    status_code: int = 200
    success: bool = True
    assessment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    alerts: List[StructuredRiskAlert] = [] # 알림이 없는 빈 리스트