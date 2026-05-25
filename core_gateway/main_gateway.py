from fastapi import FastAPI, HTTPException, status
from pydantic import ValidationError
import datetime
import logging

# 로컬 모듈 임포트 (경로에 맞게 수정 필요)
from .compliance_models import ComplianceEvidencePayload, ViolationReport
from typing import Optional, Dict

app = FastAPI(
    title="Core Compliance Gateway", 
    description="모든 비즈니스 트랜잭션 및 데이터 입출력에 대한 규제 준수 게이트웨이."
)

logging.basicConfig(level=logging.INFO)

def _validate_and_process_input(data: Dict) -> Optional[ComplianceEvidencePayload]:
    """
    들어오는 모든 데이터를 ComplianceEvidencePayload 스키마를 통해 강제 검증합니다. 
    검증 실패 시 None을 반환하여 상위 레벨에서 처리하게 합니다.
    """
    try:
        # Pydantic Guardrail을 통한 데이터 구조 및 타입 검사 수행
        validated_data = ComplianceEvidencePayload(**data)
        logging.info(f"✅ [GATEWAY] Input validation successful for transaction.")
        return validated_data
    except ValidationError as e:
        logging.warning(f"❌ [GATEWAY] Data Validation Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail={
                "error_type": "ValidationFailure", 
                "message": "입력 데이터가 요구되는 구조와 타입 규정을 준수하지 않습니다.", 
                "details": e.errors()
            }
        )

def _check_for_compliance_violation(payload: ComplianceEvidencePayload, diagnosis_context: Dict) -> ViolationReport:
    """
    핵심 비즈니스 로직이 호출되기 전에, Payload와 외부 컨텍스트를 기반으로 규정 위반 여부를 체크합니다.
    여기서 복잡한 리스크 분석 및 법적 근거 검토가 이루어집니다.
    """
    # TODO: 실제 복잡한 비즈니스/법규 검증 로직 구현 필요 (예: 외부 API 호출, DB 조회 등)

    transaction_source = payload.transaction_metadata.get("source", "UNKNOWN")
    is_high_risk_action = diagnosis_context.get("attempted_action") == "HighValueWithdrawal" # 예시 로직

    if transaction_source in ["EXTERNAL_UNTRUSTED"] and is_high_risk_action:
        # 규정 위반 발생 시, 표준화된 ViolationReport를 생성하여 반환합니다.
        return ViolationReport(
            violation_level="CRITICAL",
            rule_id="REG-001", 
            description="신뢰할 수 없는 외부 소스에서의 고위험 액션은 규정 위반 가능성이 높습니다.",
            legal_reference="GDPR Article 5: Integrity and Confidentiality"
        )
    
    # 정상 흐름일 경우, 빈(Empty) 보고서를 반환하거나 None을 반환합니다.
    return ViolationReport(
        violation_level="NONE", 
        rule_id="", 
        description="규제 위반 징후 없음.", 
        legal_reference=""
    )


@app.post("/diagnosis/run")
async def run_compliance_diagnosis(data: dict):
    """
    주요 진단 API 엔드포인트입니다. 모든 입력 데이터는 게이트웨이를 거칩니다.
    """
    logging.info("🚀 [GATEWAY] Incoming request detected for /diagnosis/run.")

    # 1. Guardrail (데이터 검증) - Pydantic 스키마를 통해 필수 구조와 타입을 강제합니다.
    try:
        validated_payload = _validate_and_process_input(data)
    except HTTPException as e:
        raise e # Validation Failure는 이미 HTTP Exception으로 처리됨

    # 2. Compliance Check (규정 위반 체크) - 비즈니스 로직 실행 전 필수 단계
    # 임시로 Context 데이터를 구성합니다. 실제로는 게이트웨이 외부에서 주입되어야 합니다.
    dummy_context = {"attempted_action": "HighValueWithdrawal"} 

    violation_report = _check_for_compliance_violation(validated_payload, dummy_context)
    
    # 3. 결과 처리: 규정 위반 여부에 따라 분기 처리합니다. (핵심 인터셉터 역할)
    if violation_report.violation_level != "NONE":
        return {
            "status": "BLOCKED",
            "message": "규제 준수 실패로 인해 진단 요청이 차단되었습니다.",
            "compliance_evidence": violation_report.dict()
        }

    # 4. 성공 로직: 게이트웨이를 통과한 데이터만 다음 비즈니스 서비스로 전달됩니다.
    logging.info("✅ [GATEWAY] Compliance check passed. Proceeding to core business logic.")
    return {
        "status": "SUCCESS",
        "message": "진단 요청이 성공적으로 처리되었으며, 법적 증거(Evidence)가 생성되었습니다.",
        "payload_processed": validated_payload.dict()
    }