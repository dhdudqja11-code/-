from pydantic import BaseModel, ValidationError
from src.schemas.v1_authority import AuthorityMetadata, AlpCalculationRequest

class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

def process_risk_data(input_risk_data: dict) -> float:
    # input_risk_data에서 기본 점수를 추출하거나 기본값 10 반환
    return float(input_risk_data.get("data", 10.0))

def calculate_authority_boost(metadata: AuthorityMetadata) -> float:
    """Authority Metadata를 분석하여 A_LP에 적용할 '권위 보강 계수'를 산출한다."""
    if len(metadata.primary_legal_categories) >= 3 and len(metadata.risk_mitigation_strategies) >= 2:
        # 권위가 충분히 증명되었을 경우, 기본 점수에 적용할 추가적인 가중치 부여 (예: 0.15~0.25 사이)
        return 0.15 + (len(metadata.primary_legal_categories) - 3) * 0.01
    else:
        # 권위 증명이 부족할 경우, 보정 계수 적용 불가 또는 최소 가중치만 부여
        print("Warning: Authority Metadata가 불완전합니다. 기본 보정 계수 적용.")
        return 0.0

def calculate_alp(request: AlpCalculationRequest):
    try:
        # 1. 유효성 검증 (Pydantic이 스키마 레벨에서 처리)
        authority_meta = request.metadata # 이미 스키마를 통과했으므로 유효하다고 간주
        
        # 2. A_LP 기본 계산 로직 실행
        base_score = process_risk_data(request.input_risk_data)
        
        # 3. 메타데이터 기반의 '권위 증명 보정 계수' 산출 (핵심 비즈니스 로직)
        authority_boost = calculate_authority_boost(authority_meta)
        
        final_alp = base_score * (1 + authority_boost)
        return {"alp": final_alp, "status": "success", "metadata_used": authority_meta.model_dump()}

    except ValidationError as ve:
        # Pydantic 스키마 실패 시 발생하는 명시적인 에러 처리
        raise HTTPException(status_code=400, detail=f"Validation Error: {ve}")
    except Exception as e:
        # 기타 시스템 오류 처리
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
