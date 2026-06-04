from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any
import logging

# 로깅 설정 (시스템 로그 기록의 일관성 유지)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Authority Data Ingestion API", version="1.0.0")

# --- Pydantic Schema 정의: 데이터 무결성을 위한 계약서 ---
class RegulatoryCase(BaseModel):
    """규제 위반 사례 하나에 대한 상세 구조."""
    article_id: str = Field(description="위반된 법률 조항 ID (예: ARTICLE-102)")
    violation_type: str = Field(description="위반 유형 (예: 정보 비대칭, 과장 광고)")
    risk_category: str = Field(description="리스크 카테고리 (재무/법률/운영)")
    severity_score: float = Field(description="심각도 점수 (0.0 ~ 1.0)", ge=0.0, le=1.0)
    estimated_financial_loss: float = Field(description="최소 예상 재무적 손실액 ($A_{LP}$ 기여치)")

class AuthorityCheckRequest(BaseModel):
    """API 요청 본문 전체 스키마."""
    regulatory_cases: List[RegulatoryCase] = Field(..., description="분석할 규제 위반 사례 리스트")
    financial_params: Dict[str, Any] = Field(..., description="재무 분석에 필요한 변수들 (예: 매출액, 사용자 수)")

class AuthorityResponse(BaseModel):
    """API 성공 응답 본문 스키마. 모든 UI 컴포넌트가 기대하는 구조."""
    compliance_status: str = Field(description="시스템 최종 판단 상태 (COMPLIANT / WARNING / CRITICAL)")
    total_risk_score: float = Field(description="종합 리스크 점수 (0.0 ~ 100.0)", ge=0.0, le=100.0)
    authority_warning: Dict[str, Any] = Field(default_factory=dict, description="권위적 경고 메시지 구조 (필요 시)")
    mitigation_plan: List[str] = Field(description="시스템이 제시하는 해결책 목록")

# --- API 엔드포인트 정의 ---

@app.post("/api/v1/check_authority", response_model=AuthorityResponse)
async def check_authority(request: AuthorityCheckRequest):
    """
    핵심 권위 검증 로직 실행. 입력 데이터를 기반으로 시스템적 '통제감 회복' 상태를 계산합니다.
    이 함수는 실제 데이터 파싱, 리스크 가중치 적용 등의 복잡한 비즈니스 로직을 포함해야 합니다.
    """
    logging.info("--- Authority Check API 요청 수신 ---")

    # 1. 초기 검증 및 집계 (데이터 유효성 체크)
    total_risk = sum(case.severity_score for case in request.regulatory_cases) / max(1, len(request.regulatory_cases)) * 100
    
    authority_warning_data: Dict[str, Any] = {}
    mitigation_plans: List[str] = []

    # 2. 리스크 분석 및 경고 생성 (핵심 비즈니스 로직)
    critical_violation_found = False
    for case in request.regulatory_cases:
        if case.severity_score > 0.7 or case.estimated_financial_loss > 100000: # 임계값 설정 예시
            critical_violation_found = True
            logging.warning(f"Critical Violation Detected: {case.article_id}")
            
            # Authority Warning 구조화 (시스템적 권위를 가진 메시지)
            authority_warning_data[case.article_id] = {
                "status": "WARNING",
                "description": f"{case.violation_type}로 인한 규정 준수 문제 발생.",
                "severity": case.severity_score,
                "impact_assessment": f"최소 재무 영향 추정치: ${case.estimated_financial_loss:,.0f}"
            }
            mitigation_plans.append(f"[{case.article_id}] {case.violation_type}에 대한 법적 검토 및 데이터 보강이 필요합니다.")

    # 3. 최종 상태 판단 (Status determination)
    if critical_violation_found:
        compliance_status = "CRITICAL" if total_risk > 80 else "WARNING"
        logging.warning(f"FINAL STATUS SET TO: {compliance_status}")
    elif request.regulatory_cases and any(c.estimated_financial_loss > 100 for c in request.regulatory_cases):
        compliance_status = "WARNING"
    else:
        compliance_status = "COMPLIANT"

    # 4. 결과 반환 (Final structured response)
    return AuthorityResponse(
        compliance_status=compliance_status,
        total_risk_score=round(min(100.0, total_risk), 2), # 점수는 100을 초과할 수 없음
        authority_warning=authority_warning_data if authority_warning_data else {},
        mitigation_plan=list(set(mitigation_plans)) # 중복 제거
    )

# --- 테스트용 더미 데이터 예시 (개발/QA 용도) ---
@app.post("/test/dummy-request")
async def test_dummy_check():
    """테스트 목적으로 임의의 데이터를 넣어 API 호출 흐름을 검증합니다."""
    # 정상적인 케이스 시뮬레이션
    return check_authority(AuthorityCheckRequest(
        regulatory_cases=[
            RegulatoryCase(article_id="ART-001", violation_type="없음", risk_category="법률", severity_score=0.1, estimated_financial_loss=50),
            RegulatoryCase(article_id="ART-999", violation_type="과장 광고", risk_category="재무", severity_score=0.85, estimated_financial_loss=35000)
        ],
        financial_params={"revenue": 100_000_000, "users": 5000}
    ))