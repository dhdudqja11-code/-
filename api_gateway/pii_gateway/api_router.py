from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any
import re

# 로컬 임포트 (방금 만든 모델 사용)
from .models import ComplianceRequestPayload, AuditLogEntry, ComplianceResponseModel, log_audit_event

router = APIRouter(prefix="/pii/gateway", tags=["Compliance Gateway"])

# --- Helper Functions ---

def detect_and_mask_pii(data: Dict[str, Any], user_id: str) -> tuple[Dict[str, Any], AuditLogEntry | None]:
    """
    데이터 딕셔너리에서 PII 패턴을 감지하고 마스킹하며 감사 로그를 생성합니다.
    반복적으로 체크해야 할 모든 민감 필드를 정의해야 합니다.
    """
    masked_data = data.copy()
    detected_pii: Dict[str, Any] = {}

    # 1. PII 패턴 정의 (강화된 정규식 기반 검증)
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"(\d{3}[-\s]?\d{3}[-\s]?\d{4})", # 11자리 전화번호 패턴
        "ssn_like": r"\d{3}-?\d{2}-?\d{4}"   # SSN 유사 패턴
    }

    for key, value in data.items():
        if isinstance(value, str):
            original_value = value
            is_pii = False
            detected_item: str | None = None

            # 2. PII 감지 로직 실행
            for pii_type, pattern in PII_PATTERNS.items():
                if re.search(pattern, original_value):
                    is_pii = True
                    detected_item = pii_type
                    break # 첫 번째 매칭된 PII만으로 간주하고 탈출

            if is_pii:
                # 마스킹 처리 (예: ******** 또는 XXXXX)
                masked_value = original_value[:1] + 'X' * (len(original_value) - 1)
                detected_pii[key] = original_value # 원본 값을 로그에 저장
                masked_data[key] = masked_value   # 마스크된 값을 데이터에 적용

    if detected_pii:
        # 3. 감사 로그 생성 및 반환
        audit_log = AuditLogEntry(
            user_id=user_id,
            violation_type="PII Leakage",
            attempted_pii_item={"keys": list(detected_pii.keys()), "values": detected_pii}
        )
        return masked_data, audit_log
    else:
        # PII가 감지되지 않았을 경우 마스크는 원본 그대로 유지
        return data, None


@router.post("/track", response_model=ComplianceResponseModel)
async def track_compliance(payload: ComplianceRequestPayload, user_id: str = Depends(lambda: "SYSTEM_USER")):
    """
    핵심 엔드포인트: 데이터의 컴플라이언스를 검증하고 PII가 감지되면 마스킹 및 감사 로그를 기록합니다.

    Args:
        payload (ComplianceRequestPayload): 검사할 데이터와 출처 정보.
        user_id (str): 요청을 보낸 사용자 ID (Dependency로 주입).
    """
    raw_data = payload.payload
    print(f"[{datetime.now().isoformat()}] Receiving request for compliance check from User {user_id}.")

    # 1. 데이터 스키마 검증은 Pydantic이 이미 담당하고 있으므로, 여기서 비즈니스 로직에 집중합니다.

    # 2. PII 감지 및 마스킹
    masked_data, audit_log = detect_and_mask_pii(raw_data, user_id)

    is_compliant: bool = (audit_log is None)
    message: str
    
    if not is_compliant:
        message = f"⚠️ Compliance Alert: PII Leakage detected and successfully mitigated. Audit Log recorded."
    else:
        message = "✅ Compliance Check Passed: No critical PII violation found."

    # 3. 감사 로그 기록 (비동기적으로 수행)
    if audit_log:
        await log_audit_event(audit_log)

    # 4. 최종 응답 구조화 및 저장 (DB Write 스텁 호출)
    response = ComplianceResponseModel(
        is_compliant=is_compliant,
        message=message,
        masked_data=masked_data,
        audit_log=audit_log
    )
    await save_compliance_record(payload, response)

    return response

# CRUD Stub (추가적인 컴플라이언스 관련 데이터 관리 엔드포인트 스텁)

@router.get("/status")
async def get_gateway_status():
    """게이트웨이 API의 현재 운영 상태 및 버전 정보를 제공합니다."""
    return {"status": "Operational", "version": "v1.2.0-rc1", "description": "Compliance check is active."}

@router.post("/audit/log")
async def create_manual_audit_record(user_id: str, violation_type: str, details: Dict[str, Any]):
    """수동으로 감사 로그를 기록하는 엔드포인트 스텁 (Admin용)."""
    # 실제로는 권한 체크가 먼저 들어가야 함.
    log_entry = AuditLogEntry(user_id=user_id, violation_type=violation_type, attempted_pii_item={"details": details})
    await log_audit_event(log_entry)
    return {"status": "Manual audit log recorded successfully.", "log_reference": str(log_entry)}