from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

# 로깅 설정 (시스템 로그 기록의 일관성 유지)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Authority Data Ingestion API", version="3.0.0")

# --- Pydantic Schema 정의: 데이터 무결성을 위한 계약서 ---
class RegulatoryCase(BaseModel):
    """규제 위반 사례 하나에 대한 상세 구조."""
    article_id: str = Field(description="위반된 법률 조항 ID (예: ARTICLE-102)")
    violation_type: str = Field(description="위반 유형 (예: 정보 비대칭, 과장 광고)")
    risk_category: str = Field(description="리스크 카테고리 (재무/법률/운영)")
    severity_score: float = Field(description="심각도 점수 (0.0 ~ 1.0)", ge=0.0, le=1.0)
    estimated_financial_loss: float = Field(description="최소 예상 재무적 손실액 ($A_{LP}$ 기여치)")

# v3.0 신규 글로벌 리스크 입력 스키마
class AIBiasInput(BaseModel):
    is_biased: bool = Field(..., description="AI 편향 존재 여부")
    data_provenance_trace: str = Field(..., description="데이터 세트 수집 경로 추적 ID")
    highest_risk_group: Optional[str] = Field(None, description="가장 편향 노출 가능성이 높은 특정 집단")
    bias_score: float = Field(..., description="편향도 계수 (0.0 ~ 1.0)", ge=0.0, le=1.0)
    compliance_evidence: str = Field(..., description="학습 데이터셋 투명성 증명서 링크/참조")

class SovereigntyInput(BaseModel):
    is_compliant: bool = Field(..., description="국가별 데이터 주권 법규 준수 여부")
    conflict_detected: bool = Field(..., description="지정학적 법규 상충 발생 여부")
    conflicting_jurisdictions: List[str] = Field(..., description="상충 법규 목록 (예: China PIPL, EU GDPR)")
    data_flow_path_used: str = Field(..., description="사용된 우회/안전 데이터 전송 경로")
    legal_proof_attached: bool = Field(..., description="법적 보관/에스크로 증명 첨부 여부")

class ESGInput(BaseModel):
    is_compliant: bool = Field(..., description="ESG 규정 준수 여부")
    primary_violation: Optional[str] = Field(None, description="주요 환경/사회/거버넌스 규정 위반명")
    cso_score: int = Field(..., description="지속 가능성 점수 (0 ~ 100)", ge=0, le=100)
    mitigation_plan_verified: bool = Field(..., description="리스크 완화 계획 검증 여부")
    estimated_financial_impact_usd: float = Field(..., description="정량화된 추정 재무적 영향 (USD)")

class AuthorityCheckRequest(BaseModel):
    """API 요청 본문 전체 스키마 v3.0."""
    regulatory_cases: List[RegulatoryCase] = Field(..., description="분석할 규제 위반 사례 리스트")
    financial_params: Dict[str, Any] = Field(..., description="재무 분석에 필요한 변수들 (예: 매출액, 사용자 수)")
    ai_bias_input: Optional[AIBiasInput] = Field(None, description="AI 편향성 검사 데이터 (선택)")
    sovereignty_input: Optional[SovereigntyInput] = Field(None, description="데이터 주권 충돌 분석 데이터 (선택)")
    esg_input: Optional[ESGInput] = Field(None, description="ESG 리스크 모니터링 데이터 (선택)")

# v3.0 신규 글로벌 리스크 상태 응답 스키마
class AIBiasStatus(BaseModel):
    is_biased: bool
    data_provenance_trace: str
    highest_risk_group: Optional[str]
    bias_score: float
    compliance_evidence: str

class SovereigntyStatus(BaseModel):
    is_compliant: bool
    conflict_detected: bool
    conflicting_jurisdictions: List[str]
    data_flow_path_used: str
    legal_proof_attached: bool

class ESGRiskStatus(BaseModel):
    is_compliant: bool
    primary_violation: Optional[str]
    cso_score: int
    mitigation_plan_verified: bool
    estimated_financial_impact_usd: float

class RiskMetrics(BaseModel):
    ai_bias_status: AIBiasStatus
    sovereignty_status: SovereigntyStatus
    esg_risk_status: ESGRiskStatus

class SummaryReport(BaseModel):
    compliance_status: str = Field(description="기존 v2.0 호환용 요약 컴플라이언스 상태")
    total_risk_score: float = Field(description="기존 v2.0 호환용 종합 리스크 점수")
    authority_warning: Dict[str, Any] = Field(description="기존 v2.0 호환용 권위적 경고 메시지")
    mitigation_plan: List[str] = Field(description="기존 v2.0 호환용 시스템 대응책 목록")

class AuthorityResponse(BaseModel):
    """API 성공 응답 본문 스키마 v3.0."""
    status: str = Field(..., description="최종 컴플라이언스 상태 (COMPLIANT / WARNING / NON_COMPLIANT)")
    timestamp: str = Field(..., description="ISO 8601 타임스탬프 형식의 검증 시간")
    overall_compliance_score: float = Field(..., description="전체 종합 컴플라이언스 점수 (0.0 ~ 1.0)")
    risk_metrics: RiskMetrics = Field(..., description="신규 정의된 세부 글로벌 리스크 데이터")
    summary_report: SummaryReport = Field(..., description="이전 호환성용 요약 리포트 구조")

# --- API 엔드포인트 정의 ---

@app.post("/api/v1/check_authority", response_model=AuthorityResponse)
async def check_authority(request: AuthorityCheckRequest):
    """
    핵심 권위 검증 로직 실행 (v3.0).
    입력 데이터를 기반으로 시스템적 '통제감 회복' 상태 및 3대 신규 글로벌 리스크 통제 능력을 산출합니다.
    """
    logging.info("--- Authority Check API 요청 수신 v3.0 ---")

    # 1. 기존 v2.0 규제 리스크 계산 로직
    total_risk = sum(case.severity_score for case in request.regulatory_cases) / max(1, len(request.regulatory_cases)) * 100
    
    authority_warning_data: Dict[str, Any] = {}
    mitigation_plans: List[str] = []

    critical_violation_found = False
    for case in request.regulatory_cases:
        if case.severity_score > 0.7 or case.estimated_financial_loss > 100000:
            critical_violation_found = True
            logging.warning(f"Critical Violation Detected: {case.article_id}")
            
            authority_warning_data[case.article_id] = {
                "status": "WARNING",
                "description": f"{case.violation_type}로 인한 규정 준수 문제 발생.",
                "severity": case.severity_score,
                "impact_assessment": f"최소 재무 영향 추정치: ${case.estimated_financial_loss:,.0f}"
            }
            mitigation_plans.append(f"[{case.article_id}] {case.violation_type}에 대한 법적 검토 및 데이터 보강이 필요합니다.")

    # 2. 신규 글로벌 리스크 정보 빌드 (요청 데이터가 없을 시 디폴트 값 바인딩)
    ai_status = request.ai_bias_input or AIBiasInput(
        is_biased=False,
        data_provenance_trace="Trace_Default_System",
        highest_risk_group=None,
        bias_score=0.0,
        compliance_evidence="Proof_of_Default_Dataset"
    )

    sovereignty_status = request.sovereignty_input or SovereigntyInput(
        is_compliant=True,
        conflict_detected=False,
        conflicting_jurisdictions=[],
        data_flow_path_used="Standard_Network_Path",
        legal_proof_attached=True
    )

    esg_status = request.esg_input or ESGInput(
        is_compliant=True,
        primary_violation=None,
        cso_score=100,
        mitigation_plan_verified=True,
        estimated_financial_impact_usd=0.0
    )

    # 3. v3.0 전체 컴플라이언스 점수 산출 로직
    # 기본 점수: 1.0에서 total_risk(0.0~1.0 환산)를 차감
    overall_score = 1.0 - (total_risk / 200.0) 

    # 리스크 보정 감점
    if ai_status.is_biased:
        overall_score -= ai_status.bias_score * 0.2
        mitigation_plans.append(f"[AI Bias] AI 데이터 편향(점수: {ai_status.bias_score}) 해소를 위한 편향 완화(Mitigation) 학습 알고리즘 적용 권장.")
    else:
        overall_score -= ai_status.bias_score * 0.05

    if sovereignty_status.conflict_detected:
        overall_score -= 0.15
        mitigation_plans.append(f"[Data Sovereignty] {', '.join(sovereignty_status.conflicting_jurisdictions)} 법규 상충 감지. 우회 경로({sovereignty_status.data_flow_path_used})의 상시 백업 게이트웨이 추가 필요.")

    if not esg_status.is_compliant:
        overall_score -= (100 - esg_status.cso_score) / 100.0 * 0.2
        mitigation_plans.append(f"[ESG Risk] ESG 위반({esg_status.primary_violation}) 식별. 녹색 탄소 상쇄 프로그램 적용 및 검증 계획 승인 필요.")

    overall_score = round(max(0.0, min(1.0, overall_score)), 2)

    # 4. 최종 상태 판단
    # Rule 1: ESG 재무 영향이 $1,000,000 이상인 경우 강제 NON_COMPLIANT
    esg_high_impact = esg_status.estimated_financial_impact_usd >= 1000000.0

    if esg_high_impact or total_risk > 80:
        compliance_status = "NON_COMPLIANT"
        logging.warning("FINAL STATUS SET TO: NON_COMPLIANT due to ESG high impact or excessive general risk.")
    elif critical_violation_found or ai_status.is_biased or sovereignty_status.conflict_detected or overall_score < 0.7:
        compliance_status = "WARNING"
        logging.warning("FINAL STATUS SET TO: WARNING due to moderate risks.")
    else:
        compliance_status = "COMPLIANT"

    # 5. 응답 조립
    return AuthorityResponse(
        status=compliance_status,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        overall_compliance_score=overall_score,
        risk_metrics=RiskMetrics(
            ai_bias_status=AIBiasStatus(
                is_biased=ai_status.is_biased,
                data_provenance_trace=ai_status.data_provenance_trace,
                highest_risk_group=ai_status.highest_risk_group,
                bias_score=ai_status.bias_score,
                compliance_evidence=ai_status.compliance_evidence
            ),
            sovereignty_status=SovereigntyStatus(
                is_compliant=sovereignty_status.is_compliant,
                conflict_detected=sovereignty_status.conflict_detected,
                conflicting_jurisdictions=sovereignty_status.conflicting_jurisdictions,
                data_flow_path_used=sovereignty_status.data_flow_path_used,
                legal_proof_attached=sovereignty_status.legal_proof_attached
            ),
            esg_risk_status=ESGRiskStatus(
                is_compliant=esg_status.is_compliant,
                primary_violation=esg_status.primary_violation,
                cso_score=esg_status.cso_score,
                mitigation_plan_verified=esg_status.mitigation_plan_verified,
                estimated_financial_impact_usd=esg_status.estimated_financial_impact_usd
            )
        ),
        summary_report=SummaryReport(
            compliance_status=compliance_status,
            total_risk_score=round(min(100.0, total_risk), 2),
            authority_warning=authority_warning_data if authority_warning_data else {},
            mitigation_plan=list(set(mitigation_plans))
        )
    )


# --- 테스트용 더미 데이터 예시 (개발/QA 용도) ---
@app.post("/test/dummy-request")
async def test_dummy_check():
    """테스트 목적으로 임의의 데이터를 넣어 API 호출 흐름을 검증합니다."""
    # 정상적인 케이스 시뮬레이션
    return await check_authority(AuthorityCheckRequest(
        regulatory_cases=[
            RegulatoryCase(article_id="ART-001", violation_type="없음", risk_category="법률", severity_score=0.1, estimated_financial_loss=50),
            RegulatoryCase(article_id="ART-999", violation_type="과장 광고", risk_category="재무", severity_score=0.85, estimated_financial_loss=35000)
        ],
        financial_params={"revenue": 100_000_000, "users": 5000},
        ai_bias_input=AIBiasInput(
            is_biased=False,
            data_provenance_trace="Trace_ID_54321",
            highest_risk_group="None",
            bias_score=0.12,
            compliance_evidence="Proof_of_Training_Dataset_V3"
        ),
        sovereignty_input=SovereigntyInput(
            is_compliant=True,
            conflict_detected=False,
            conflicting_jurisdictions=[],
            data_flow_path_used="Anon_Gateway_Singapore",
            legal_proof_attached=True
        ),
        esg_input=ESGInput(
            is_compliant=True,
            primary_violation=None,
            cso_score=85,
            mitigation_plan_verified=True,
            estimated_financial_impact_usd=1200000.0
        )
    ))