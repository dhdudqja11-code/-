from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional

# A_LP 계산에 필요한 법적 리스크 데이터와 연관된 '권한 증명' 메타데이터 스키마
class AuthorityMetadata(BaseModel):
    """
    A_LP 산출 결과가 단순 숫자가 아님을 증명하는 구조화된 메타데이터. 
    법률 근거, 위험 완화 전략 등을 포함하여 권위(Authority)를 부여한다.
    """
    # 이 서비스의 핵심 가치를 뒷받침하는 주요 법적 규제 카테고리 (최소 3개 필수)
    primary_legal_categories: List[str] = []

    # 리스크 완화 전략에 대한 근거가 되는 구체적인 조치 목록.
    risk_mitigation_strategies: List[str] = []

    # 이 계산 결과가 사용자의 어떤 비즈니스 단계(예: 초기 진단, 법인 확장)와 연관되는지 명시.
    application_context: Optional[str] = None 
    
    # 최종적으로 도출된 '신뢰 상실 가치 계수'의 정량적 해석 (텍스트 설명 필요)
    authority_interpretation: str

    @field_validator('primary_legal_categories', mode='before')
    def validate_min_categories(cls, v):
        """메타데이터 무결성 검사: 최소 3개 이상의 카테고리가 있어야 함."""
        if not isinstance(v, list) or len(v) < 3:
            raise ValueError("AuthorityMetadata는 비즈니스의 권위를 증명하기 위해 최소 3가지의 법적 규제 카테고리를 포함해야 합니다.")
        return v

    @field_validator('risk_mitigation_strategies', mode='before')
    def validate_min_strategies(cls, v):
        """메타데이터 무결성 검사: 리스크 완화 전략은 최소 2가지가 있어야 함."""
        if not isinstance(v, list) or len(v) < 2:
            raise ValueError("AuthorityMetadata는 최소 2가지 이상의 구체적인 위험 완화 전략을 제시해야 합니다.")
        return v

# A_LP 계산 요청 본문 스키마 업데이트 (기존 데이터 + Authority Metadata 포함)
class AlpCalculationRequest(BaseModel):
    """A_LP 계산 API의 전체 Request Body."""
    user_id: str
    input_risk_data: dict # 기존 법적 리스크 입력 데이터
    metadata: AuthorityMetadata # 새로 추가된 권위 증명 메타데이터