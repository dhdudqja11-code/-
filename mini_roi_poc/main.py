from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any
import datetime

# ----------------------------------------------------
# 1. 데이터 스키마 정의 (Pydantic Models)
# 모든 입력은 이 구조를 따라야 합니다. 규정 준수(Compliance)의 시작입니다.
class RiskInputData(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier.")
    user_data_source: str = Field(..., min_length=3, description="Source of user data (e.g., Website Click, API Call).")
    risk_assessment_score: float = Field(..., ge=-100, le=100, description="Calculated risk score (-100 to 100).")
    data_fields: Dict[str, Any] = Field({}, description="Dictionary containing the actual data points being analyzed.")

# 구조화된 경고 응답 (Immutable Audit Block 표준 준수)
class ComplianceAlert(BaseModel):
    is_compliant: bool
    alert_level: str  # e.g., CRITICAL, WARNING, OK
    report: Dict[str, Any] # [문제 정의], [원인 분석], [해결책 제시] 구조

# API 초기화
app = FastAPI(title="Mini ROI Risk Simulator PoC Gateway")

@app.post("/simulate_risk", response_model=ComplianceAlert)
async def simulate_risk(data: RiskInputData):
    """
    주어진 트랜잭션 데이터를 기반으로 규제 준수 여부를 시뮬레이션합니다.
    결과적으로 경고 보고서 (Immutable Audit Block 구조)를 반환합니다.
    """
    # ----------------------------------------------------
    # 2. 데이터 유효성 및 기본 검증 로직
    # 기본적인 필수 값 체크는 FastAPI와 Pydantic이 처리하지만,
    # 비즈니스 레벨의 '법적/규제' 위반 여부를 여기서 검사합니다.

    data_fields = data.data_fields
    
    # [Rule 1: 데이터 출처(Source) 유효성 검증]
    if "GDPR" not in data.user_data_source and "HIPAA" not in data.user_data_source:
        return ComplianceAlert(
            is_compliant=False,
            alert_level="CRITICAL",
            report={
                "problem": "개인 식별 정보 출처 규정 위반 가능성 (Missing Data Source Context)",
                "cause": f"사용자 데이터 소스가 {data.user_data_source}로 확인되었으나, GDPR 또는 HIPAA와 같은 필수 규제 준수 문맥이 명시적으로 기록되지 않았습니다.",
                "solution": "데이터 수집 단계에서 반드시 '법적 근거(Legal Basis)'를 포함한 메타데이터 태깅을 의무화해야 합니다. (e.g., Consent ID, Purpose)."
            }
        )

    # [Rule 2: 위험 점수와 데이터 필드의 불일치 검증]
    if abs(data.risk_assessment_score) > 80 and "Audit Trail" not in data_fields:
         return ComplianceAlert(
            is_compliant=False,
            alert_level="CRITICAL",
            report={
                "problem": f"높은 위험 점수({data.risk_assessment_score:.2f})에 대한 불완전한 감사 증명 (Missing Audit Trail)",
                "cause": "위험도가 높은 트랜잭션임에도 불구하고, 해당 리스크를 추적하고 검증할 수 있는 '불변의 감사 기록(Audit Trail)'이 데이터 필드에서 발견되지 않았습니다.",
                "solution": "모든 고위험 거래는 반드시 불변성을 보장하는 Audit Block을 생성하고, 최소한 (User ID, Timestamp, Action) 3요소를 포함해야 합니다."
            }
        )

    # [Rule 3: 정상 트랜잭션 시뮬레이션]
    if data.risk_assessment_score < -20 and "Audit Trail" in data_fields:
        return ComplianceAlert(
            is_compliant=True,
            alert_level="OK",
            report={
                "problem": "현재 트랜잭션은 법규 준수 리스크가 낮습니다.",
                "cause": f"데이터 소스({data.user_data_source})와 감사 기록(Audit Trail)이 모두 명확하게 확인되었습니다.",
                "solution": "정기적으로 시스템의 취약점 및 규제 변화를 모니터링하여 '예방적 리스크 관리' 체계를 유지하십시오."
            }
        )

    # 기본 성공 케이스 (위의 조건에 해당하지 않는 경우, 예외 처리 목적)
    return ComplianceAlert(
        is_compliant=True,
        alert_level="OK",
        report={
            "problem": "분석된 리스크는 수용 가능한 범위 내에 있습니다.",
            "cause": "제공된 데이터 스키마와 트랜잭션 로그가 내부 기준을 만족합니다. (추가 검토 필요)",
            "solution": "시스템의 운영 감사 기록(Audit Log) 주기적 점검을 통해 지속적인 무결성을 확보하십시오."
        }
    )

# 헬스 체크 엔드포인트 추가 (테스트 편의성)
@app.get("/health")
def read_root():
    return {"status": "ok", "message": "Mini ROI Simulator Gateway is operational."}