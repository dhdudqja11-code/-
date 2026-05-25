from typing import Dict, Any
from src.logging.audit_logger import AuditLoggerService

class ComplianceGatewayError(Exception):
    """컴플라이언스 게이트웨이에서 발생하는 오류를 정의합니다."""
    def __init__(self, what: str, why: str, how: str):
        self.what = what
        self.why = why
        self.how = how
        super().__init__(f"Compliance Violation Detected: {what}")

class ComplianceGateway:
    """
    모든 API 요청이 반드시 거쳐야 하는 법적/규제 준수 검증 게이트웨이입니다.
    단순한 기능 호출을 넘어 '재무적 손실 회피' 관점을 강제합니다.
    """
    @staticmethod
    def execute(user_id: str, request_data: Dict[str, Any], endpoint_name: str) -> None:
        """
        요청 데이터를 받아 3단계 구조의 검증을 실행하고, 실패 시 예외를 발생시킵니다.
        """
        print("\n[⚙️ COMPLIANCE GATEWAY] Starting mandatory compliance check...")

        # --- 1. 데이터 무결성 및 출처(Source) 확인 로직 (핵심 규제 준수) ---
        if 'source' not in request_data or not request_data['source']:
            raise ComplianceGatewayError(
                what="Data Source Missing", 
                why="데이터의 출처(Source)가 명시되지 않아 위변조 가능성이 높습니다.", 
                how="외부 시스템 연동 및 데이터 전송 시, 반드시 메타데이터에 '데이터 생성 주체'를 포함해야 합니다."
            )

        # --- 2. 민감 정보 처리 적정성 검증 로직 (HIPAA/GDPR 관점) ---
        if "ssn" in str(request_data).lower() and request_data['source'] != 'secure_internal':
             raise ComplianceGatewayError(
                what="Sensitive Data Handling Violation", 
                why="민감 정보(SSN 등)가 안전한 내부망이 아닌 외부 채널로 전송될 위험이 감지되었습니다.", 
                how="처리 전에 반드시 데이터 마스킹 및 비식별화(De-identification) 절차를 거쳐야 합니다."
            )

        # --- 3. 게이트웨이 통과 시, 감사 로깅을 강제 실행합니다. (최종 증명 기록 생성) ---
        print("[✅ GATEWAY SUCCESS] Compliance check passed.")
        audit_record = AuditLoggerService.log_transaction(
            user_id=user_id, 
            action=endpoint_name, 
            details={"request_data": request_data}
        )
        # 이 audit_record를 호출자에게 반환하거나 상태에 저장하여 후속 처리에 사용합니다.
        return audit_record