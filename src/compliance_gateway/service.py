import datetime
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, PositiveInt

# ==============================================================
# 🛡️ 1. 데이터 모델 정의 (Immutable Proof Schema)
# 모든 기록은 이 구조를 따릅니다. 변질되면 안 되는 '증거'입니다.
# ==============================================================

class AuditRecord(BaseModel):
    """
    불변 감사 기록 객체 스키마. 시스템의 핵심 증명 요소.
    이 필드들은 데이터 무결성 검증을 위해 필수적입니다.
    """
    record_uuid: uuid.UUID = Field(default_factory=uuid.uuid4, description="고유 트랜잭션 식별자.")
    timestamp_utc: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc), description="기록 생성 시간 (UTC 필수).")
    actor_id: str = Field(description="행위를 수행한 사용자 또는 시스템 ID.")
    action_type: str = Field(description="발생한 행위의 종류 (예: API_CALL, DATA_TRANSFER, COMMAND_EXECUTION).")
    target_resource: str = Field(description="작용 대상 리소스 식별자 (예: user:{id}, api:/data/transfer).")
    status: str = Field(description="행위의 결과 상태 (SUCCESS, FAILURE, PENDING).")
    details: Dict[str, Any] = Field(description="추가적인 상세 정보. (원격 명령 파라미터, 전송 데이터 요약 등)")

# ==============================================================
# 🛡️ 2. Compliance Gateway 서비스 클래스
# 모든 핵심 로직은 이 게이트웨이를 통과해야 합니다.
# ==============================================================

class ComplianceGateway:
    """
    모든 시스템 상호작용을 감지, 기록하고 검증하는 중앙 컴플라이언스 관리자.
    이 객체는 싱글턴(Singleton) 패턴으로 사용되는 것이 이상적입니다.
    """
    def __init__(self):
        # 실제 환경에서는 DB 연결 정보나 캐시 매니저를 여기에 초기화합니다.
        print("✅ ComplianceGateway Initialized: 모든 트랜잭션은 이제 감사 기록을 거칩니다.")

    @staticmethod
    def _validate_and_enrich(raw_record: Dict[str, Any], action_type: str) -> Optional[AuditRecord]:
        """
        Raw 데이터를 받아 Pydantic 모델로 검증하고 필수 정보를 보강합니다.
        데이터 누락이나 형식 오류 시 즉시 실패를 반환하여 시스템 다운을 방지하는 것이 핵심입니다.
        """
        try:
            # 강제적인 데이터 구조화 및 유효성 검사 (Schema Enforcement)
            validated_record = AuditRecord(**raw_record)
            return validated_record
        except Exception as e:
            print(f"🚨 CRITICAL FAILURE: 감사 기록 생성 실패. 입력 데이터 불일치 또는 누락: {e}")
            # 여기서 시스템 오류 로그를 별도로 남겨야 합니다.
            return None

    def capture_audit_record(self, 
                              actor_id: str, 
                              action_type: str, 
                              target_resource: str, 
                              status: str, 
                              details: Dict[str, Any]) -> AuditRecord:
        """
        핵심 함수. 모든 행위가 이 함수를 통해 감지되고 기록됩니다.

        Args:
            actor_id (str): 행위자 ID.
            action_type (str): 수행된 행동의 타입.
            target_resource (str): 대상 자원.
            status (str): 최종 상태 (SUCCESS/FAILURE).
            details (dict): 세부 컨텍스트 정보.

        Returns:
            AuditRecord: 성공적으로 생성되고 검증된 감사 기록 객체.
        """
        print(f"\n⚙️ [Compliance Gateway] 트랜잭션 감지: {action_type} ({status})")
        
        # 1. 데이터 구조화 및 유효성 검사 (MUST DO)
        raw_data = {
            "actor_id": actor_id,
            "action_type": action_type,
            "target_resource": target_resource,
            "status": status,
            "details": details
        }
        validated_record = self._validate_and_enrich(raw_data, action_type)

        if not validated_record:
            # 데이터가 유효하지 않으면 더 이상 진행할 수 없습니다. 이 자체가 기록됩니다.
            return AuditRecord(
                actor_id="SYSTEM", 
                action_type="AUDIT_FAILURE", 
                target_resource=f"Failed_{action_type}", 
                status="CRITICAL_FAIL", 
                details={"error": "Input validation failed."}
            )

        # 2. 불변성 확보 및 영구 저장 (Persistence Layer Simulation)
        try:
            # --- TODO: 실제 DB WRITE 로직이 들어갈 위치입니다. ---
            # 예시: self.database_client.save(validated_record)
            print(f"✅ Audit Record [{validated_record.record_uuid}]가 성공적으로 저장되었습니다.")
            # 로그 레벨, 시점, 주체 등을 기록합니다. 이 과정이 불변성을 보장해야 합니다.
            return validated_record
        except Exception as e:
            # DB 연결 오류 등 시스템 장애는 치명적인 위험입니다. 반드시 로깅하고 알람을 발생시켜야 합니다.
            print(f"❌ CRITICAL ERROR: 영구 저장 실패! {e}")
            raise ConnectionError("Audit Log Persistence Failure.")

# ==============================================================
# 🚀 사용 예시 (Testing the Gateway)
# 이 코드는 테스트를 위해 여기에 남겨둡니다.
# ==============================================================

if __name__ == "__main__":
    gateway = ComplianceGateway()
    print("-" * 50)

    # Case 1: 성공적인 원격 제어 시도 (Remote Command Execution)
    success_details = {"command": "read_file", "path": "/user/profile.txt"}
    record_success = gateway.capture_audit_record(
        actor_id="User-Alpha-789", 
        action_type="REMOTE_COMMAND", 
        target_resource="System Core", 
        status="SUCCESS", 
        details=success_details
    )
    print("--- [성공 기록 요약] ---")
    print(record_success.model_dump_json(indent=2))

    print("\n" + "=" * 50)

    # Case 2: 권한 부족으로 인한 실패 (Unauthorized Access Attempt)
    failure_details = {"attempted_action": "admin_delete", "required_role": "SUPER_ADMIN"}
    record_fail = gateway.capture_audit_record(
        actor_id="User-Beta-123", 
        action_type="API_CALL", 
        target_resource="/user/settings/privacy", 
        status="FAILURE", 
        details=failure_details
    )
    print("--- [실패 기록 요약] ---")
    print(record_fail.model_dump_json(indent=2))

    # Case 3: 유효하지 않은 데이터 입력 (System Test Failure - 자가 검증용)
    bad_data = { # Pydantic 모델이 요구하는 필드가 없거나 형식이 틀림
        "actor_id": "Invalid-User", 
        "action_type": "TEST", 
        # status나 details가 누락됨 (pydantic validation fail 예상)
    }
    print("\n" + "=" * 50)
    gateway._validate_and_enrich(bad_data, "INVALID_INPUT")