from typing import Optional, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

# --- 1. 핵심 법적 증거 구조체 (Legal Evidence) ---
class LegalEvidence(BaseModel):
    """
    위반과 관련된 구체적인 법률 근거를 담는 컴플라이언스 모듈의 핵심 데이터 구조.
    '불변의 증명 가능성' 확보가 최우선 목표입니다.
    """
    applicable_law: str = Field(..., description="위반과 관련된 구체적인 법규명 (예: '개인정보보호법', 'GDPR Article 5').")
    legal_article: str = Field(..., description="직접 위반된 조항/항목 번호 및 제목.")
    violation_clause: str = Field(..., description="해당 법규에서 요구하는 핵심 원칙 또는 금지 사항 (예: '최소 수집 원칙').")

# --- 2. 규정 위반 Payload (Violation Evidence) ---
class ViolationEvidencePayload(BaseModel):
    """
    시스템 내에서 규정 위반이 감지될 때 발생하는 모든 법적 증거를 담는 구조체.
    모든 외부 입력 검증 시 반드시 이 형태의 데이터를 생성해야 합니다.
    """
    violation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="고유한 위반 감지 ID.")
    timestamp_utc: datetime = Field(default_factory=datetime.utcnow, description="위반이 발생한 UTC 시점.")
    severity_level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(..., description="위반의 심각도 (법적 책임에 미치는 영향 기반).")
    violation_summary: str = Field(..., description="사용자 친화적인 위반 요약 설명 (예: '개인정보 목적 외 이용 감지').")
    
    # 핵심 법률 증거 구조체 포함
    legal_evidence: LegalEvidence

# --- 3. 통합 컴플라이언스 게이트웨이 출력 모델 ---
class ComplianceGateResult(BaseModel):
    """
    Mini ROI 시뮬레이션의 최종 결과를 담는 컨테이너. 
    성공/실패 여부와 관계없이, 모든 법적 검증 결과가 기록되어야 합니다.
    """
    simulation_success: bool = True
    raw_input_data: dict
    # 성공적으로 처리되었거나, 위반 사항이 감지된 Payload를 모두 포함합니다.
    compliance_violations: list[ViolationEvidencePayload] = []
    audit_log: str = "Simulation process completed successfully."

@validator('simulation_success', pre=True)
def check_success(cls, v):
    # 임시 검증 로직 (필요하다면 추가 가능)
    return bool(v)