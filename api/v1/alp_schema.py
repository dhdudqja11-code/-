from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Optional, Dict
from datetime import date

# 1. 핵심 규제 위반 세부 모델 (L_reg의 가장 깊은 레벨)
class MaxFineDetails(BaseModel):
    """규제 위반에 따른 최대 벌금액 정보를 담는 구조."""
    amount: float = Field(..., description="최대 벌금액 숫자. 반드시 양수여야 함.")
    currency: str = Field(..., max_length=3, pattern="^[A-Z]{3}$", description="통화 단위 (예: EUR, USD).")
    range_description: str = Field(..., description="최대 ~ 최소 범위 설명.")
    basis: Optional[str] = Field(None, description="벌금액 증감의 법적 근거 요약.")

# 2. 개별 규제 위반 데이터 모델 (Input Item)
class RegulatoryViolationData(BaseModel):
    """단일 규제 위반 사례가 담긴 표준화된 데이터 구조."""
    id: str = Field(..., description="규제 위반 고유 ID (예: R001).")
    regulation_name: str = Field(..., description="규정명 (예: GDPR).")
    jurisdiction: str = Field(..., description="관할 지역 (예: EU).")
    core_principle: Optional[str] = Field(None, description="핵심 원칙.")
    violation_type: str = Field(..., description="구체적 위반 유형. 반드시 정의된 코드를 사용해야 함.")
    legal_article: str = Field(..., description="구체적 규정 조항 또는 섹션.")
    max_fine_details: MaxFineDetails = Field(..., description="벌금 세부 정보.")
    impact_description: str = Field(..., description="규제 위반이 초래하는 핵심 비즈니스 리스크 요약.")

# 3. 전체 요청 본문 모델 (Request Body)
class AlpCalculationRequest(BaseModel):
    """A_LP 계산을 위한 모든 규제 위반 데이터 세트."""
    data_set_name: str = Field(..., description="데이터셋 이름.")
    source_date: date = Field(default_factory=date.today, description="데이터 수집 기준 날짜.")
    regulations: List[RegulatoryViolationData] = Field(..., min_items=1, description="위반 데이터 리스트.")

    @validator('regulations')
    def validate_minimum_regulation_count(cls, v):
        # 최소 2개 이상의 규제 위반 사례가 있어야 유의미한 A_LP 계산 가능 (비즈니스 가설)
        if len(v) < 2:
            raise ValueError("A_LP 계산을 위해 최소 2가지 이상의 독립적인 규제 위반 데이터 세트가 필요합니다.")
        return v

# 4. API 응답 본문 모델 (Response Body)
class AlpCalculationResult(BaseModel):
    """A_LP 계산의 최종 결과 및 사용된 로직 요약."""
    input_data_count: int = Field(..., description="처리된 규제 위반 데이터 세트의 총 개수.")
    calculation_date: date = Field(default_factory=date.today, description="계산이 수행된 날짜.")
    calculated_alp: float = Field(..., description="최종 산출된 A_LP (불확실성 제거 권한).")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="계산의 신뢰도 점수.")
    used_regulations: List[str] = Field(..., description="A_LP 계산에 영향을 준 주요 규제 목록.")

# 5. 유효성 검증 테스트 함수 (예시)
def run_validation_test(payload: dict):
    """실제 API 게이트웨이에서 호출될 Mock Validation Flow."""
    print("--- [Validation Flow Start] ---")
    try:
        validated_request = AlpCalculationRequest(**payload)
        print("✅ 성공: Payload가 AlpCalculationRequest 스키마를 통과했습니다. 데이터 무결성 확보.")
        # 여기에 A_LP 계산 로직을 호출하는 다음 단계의 비즈니스 로직이 연결됩니다.
        return validated_request
    except ValidationError as e:
        print(f"❌ 실패: Payload가 유효성 검증에 실패했습니다. 오류 상세:")
        for error in e.errors():
            # 오류가 발생한 필드와 이유를 명확히 출력합니다.
            loc = ".".join(map(str, error['loc']))
            print(f"  - [Field: {loc}] 문제 유형: '{error['msg']}' (타입: {error['type']})")
        return None

if __name__ == '__main__':
    # 🧪 테스트 케이스 1: 정상 데이터 (가상의 payload)
    valid_payload = {
        "data_set_name": "Mock_EU_AI_Compliance",
        "source_date": date.today(),
        "regulations": [
            {
                "id": "R001",
                "regulation_name": "GDPR",
                "jurisdiction": "EU",
                "core_principle": "Data Subject Rights",
                "violation_type": "Consent Failure",
                "legal_article": "Article 5(1)(a)",
                "max_fine_details": {"amount": 85000000.0, "currency": "EUR", "range_description": "최대 €85M", "basis": "위반 규모 및 기간에 따라 증감 가능함."},
                "impact_description": "개인 정보 유출로 인한 법적 소송 리스크."
            },
            {
                "id": "R002",
                "regulation_name": "HIPAA",
                "jurisdiction": "US",
                "core_principle": "Protected Health Information",
                "violation_type": "Lack of Encryption",
                "legal_article": "45 CFR § 164.302",
                "max_fine_details": {"amount": 10000000.0, "currency": "USD", "range_description": "$~ 수백만 달러", "basis": "위반 기간 및 고의성 기반."},
                "impact_description": "민감 의료 정보 유출로 인한 환자 신뢰 상실."
            }
        ]
    }
    print("\n==================== Test Case 1: Valid Data ====================")
    run_validation_test(valid_payload)

    # 🧪 테스트 케이스 2: 데이터 타입/규칙 위반 (Amount가 문자열이고, 규제가 하나만 있는 경우)
    invalid_payload = {
        "data_set_name": "Mock_Failed_Compliance",
        "source_date": date.today(),
        "regulations": [
            {
                "id": "R999",
                "regulation_name": "TestFail",
                "jurisdiction": "TEST",
                "core_principle": None,
                "violation_type": "BadInput",
                "legal_article": "T.1",
                # amount를 float이 아닌 문자열로 넣어서 실패 유도
                "max_fine_details": {"amount": "N/A", "currency": "XXX", "range_description": "Test Range", "basis": None},
                "impact_description": "의도적인 테스트 위반."
            }
        ]
    }
    print("\n==================== Test Case 2: Invalid Data ====================")
    run_validation_test(invalid_payload)