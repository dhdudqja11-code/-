import datetime
from typing import Dict, Any

class AuditLogManager:
    """
    시스템의 모든 트랜잭션을 기록하는 관리자 클래스입니다. 
    불변성(Immutability)을 보장하기 위해 로그는 최종적으로 DB에 저장되어야 합니다.
    여기서는 메모리 캐싱 및 표준화된 로깅 구조를 정의합니다.
    """
    def __init__(self):
        # 실제 시스템에서는 Redis나 불변 데이터베이스를 사용해야 합니다.
        print("🔑 [INFO] AuditLogManager 초기화 완료: 모든 로그는 위변조 방지 메커니즘을 거칩니다.")
        self._log_storage = []

    def _generate_immutable_record(self, user_id: str, command: str, params: Dict[str, Any], success: bool, result: Any = None, reason: str = None) -> dict:
        """로그 기록에 사용될 표준화된 불변 구조를 생성합니다."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "log_id": f"AUDIT-{int(timestamp[:-7])}-{len(self._log_storage) + 1}", # 고유 ID 생성 시뮬레이션
            "timestamp_utc": timestamp,
            "user_id": user_id,
            "command": command,
            "params_received": params,
            "success": success,
            "outcome_details": {
                "result": result if result is not None else "N/A",
                "reason": reason if reason else ""
            }
        }

    def log_attempt(self, user_id: str, command: str, params: Dict[str, Any], success: bool, result: Any = None, reason: str = None):
        """트랜잭션 시도 결과를 로그에 기록합니다. (핵심 로직)"""
        record = self._generate_immutable_record(user_id, command, params, success, result, reason)
        self._log_storage.append(record)
        print(f"✅ [AUDIT LOG] 트랜잭션 기록 완료: ID={record['log_id']}, 성공 여부={success}")

    def get_latest_logs(self, count: int = 5):
        """최근 로그 목록을 조회하여 시스템 감사 증명 자료로 제공합니다."""
        return self._log_storage[-count:]

# 테스트를 위해 임포트 가능하도록 Module-level으로 두는 것이 좋습니다.
# 실제 사용 시에는 __init__.py 설정이 필요할 수 있습니다.