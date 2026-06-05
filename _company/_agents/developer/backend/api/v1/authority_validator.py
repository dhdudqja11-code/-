from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
import datetime
import json

# --- [Authority Data Schema 정의 (Mock)] ---
# 실제 프로젝트에서는 ComplianceTypes.ts나 별도의 스키마 파일에서 불러옴
class AuthorityDataSchema:
    """
    시스템이 유효성을 검증해야 하는 핵심 데이터 구조체.
    모든 트랜잭션은 이 형태를 준수해야 합니다.
    """
    def __init__(self, transaction_id: str, source: str, timestamp: datetime.datetime):
        self.transaction_id = transaction_id
        self.source = source  # 예: payment_gateway, manual_input, etc.
        self.timestamp = timestamp

class ValidationReport:
    """
    시스템 검증 보고서 구조체. 반드시 이 포맷을 준수해야 함.
    """
    def __init__(self, is_valid: bool, report_data: Dict[str, Any]):
        self.is_valid = is_valid
        self.report = report_data

# --- [Mock Validation Service] ---

class AuthorityValidator:
    """
    AuthorityDataSchema의 데이터 무결성을 검증하는 핵심 백엔드 서비스 레이어.
    실패 시, 4xx/5xx HTTP 에러를 반환하지 않고 구조화된 시스템 경고 코드를 반환합니다.
    """
    def __init__(self):
        # Mock 저장소: 실제로는 DB 또는 캐시에 접근해야 합니다.
        self.immutable_audit_log = [] # 불변 감사 기록 (Immutable Proof)
        self.bypass_traffic_flow = {}  # 자동 우회 트래픽 흐름 기록

    def _check_immutable_proof(self, data: AuthorityDataSchema) -> bool:
        """불변성 검증 로직: 데이터가 시간적/논리적으로 변조되지 않았는지 체크."""
        # 예시: 데이터에 'Proof-Hash' 필드가 누락되었거나 시간이 과거로 돌아간 경우 실패 처리
        if "Proof-Hash" not in data.report or data.report["Proof-Hash"] == None:
            return False, "IMMUTABILITY_VIOLATION", "데이터의 무결성을 증명하는 Proof Hash가 누락되었습니다."

        # 실제 로직: 현재 보고된 해시값과 기록된 해시값을 비교 (SHA256 등)
        print(f"[Validator] Immutable Check passed for {data.transaction_id}")
        return True, "OK", ""

    def _check_bypass_flow(self, data: AuthorityDataSchema) -> bool:
        """자동 우회 트래픽 흐름 검증 로직: 예상 경로를 벗어났는지 체크."""
        # 예시: Source가 'manual'인데, 필요한 필수 필드 {X}가 누락된 경우 실패 처리
        required_fields = ["source", "amount", "time"]
        if not all(field in data.report for field in required_fields):
            return False, "FLOW_VIOLATION", f"필수 트랜잭션 필드 중 하나({', '.join(required_fields)})가 누락되었습니다."

        print(f"[Validator] Bypass Flow Check passed for {data.transaction_id}")
        return True, "OK", ""


    def validate_authority_data(self, data: AuthorityDataSchema) -> ValidationReport:
        """
        핵심 유효성 검증을 수행하고 보고서를 반환합니다.
        """
        is_valid = True
        errors: List[str] = []

        # 1. 불변성 검사
        immutable_ok, immutability_code, immutability_msg = self._check_immutable_proof(data)
        if not immutable_ok:
            is_valid = False
            errors.append({"code": immutability_code, "message": f"[{immutability_code}] {immutability_msg}"})

        # 2. 트래픽 흐름 검사
        flow_ok, flow_code, flow_msg = self._check_bypass_flow(data)
        if not flow_ok:
            is_valid = False
            errors.append({"code": flow_code, "message": f"[{flow_code}] {flow_msg}"})

        # 3. 최종 보고서 생성 (시스템적 경고 코드를 포함하여 구조화)
        report_data = {
            "status": "SUCCESS" if is_valid else "FAILURE",
            "validation_timestamp": str(datetime.datetime.now()),
            "errors": errors,
            "message": "데이터 유효성 검증이 완료되었습니다." if is_valid else f"{len(errors)}개의 오류가 발견되어 통제권 확보에 실패했습니다."
        }

        return ValidationReport(is_valid, report_data)


router = APIRouter()

@router.post("/api/v1/validate/authority")
async def validate_endpoint(raw_payload: Dict[str, Any]):
    """
    실시간 권위 데이터 무결성 검증 엔드포인트. 
    성공적인 흐름만 허용하며, 실패 시 구조화된 시스템적 경고를 반환합니다.
    """
    try:
        # Payload 파싱 및 스키마 구축 (이 부분은 실제 요청에 맞게 수정 필요)
        data_schema = AuthorityDataSchema(
            transaction_id=raw_payload.get("transactionId", "UNKNOWN"),
            source=raw_payload.get("source", "UNKNOWN"),
            timestamp=datetime.datetime.now() # 서버 시간 기준
        )

        validator = AuthorityValidator()
        report = validator.validate_authority_data(data_schema)

        if not report.is_valid:
            # 🚨 핵심 로직: HTTP 에러를 던지는 대신, 전문적인 실패 리포트를 반환합니다.
            return {
                "status": "SYSTEM_ALERT", # 시스템적 경고 상태 코드 사용
                "http_code": status.HTTP_400_BAD_REQUEST, # 클라이언트에게는 400을 주지만...
                "payload": report.report,
                "message": f"⚠️ WARNING: 데이터 흐름에 문제가 감지되었습니다. 상세 오류 코드를 참조하세요."
            }
        else:
            # 성공 시 통제권 확보 과정 완료 메시지를 반환하여 권위를 높입니다.
             return {
                "status": "SYSTEM_SUCCESS", # 시스템적 성공 상태 코드 사용
                "http_code": status.HTTP_200_OK,
                "payload": report.report,
                "message": "✅ Authority Data Schema 검증 완료. 통제권 확보에 성공했습니다."
            }

    except Exception as e:
        # 예측 불가능한 시스템 오류 발생 시, 최고 수준의 경고를 반환합니다.
         return {
            "status": "CRITICAL_FAILURE", 
            "http_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "payload": {"error_detail": str(e)},
            "message": f"❌ CRITICAL FAILURE: 시스템 내부 오류 발생. 현재는 자동 진단 모드입니다."
        }

# 이 라우터를 사용하여 FastAPI 애플리케이션에 연결해야 합니다.