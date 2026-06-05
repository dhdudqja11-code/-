# src/services/authority_state_manager.py
import time
from typing import Dict, Any

# 시스템적 경고 코드 정의 (HTTP 상태 코드를 우회)
SYSTEM_ERROR_CODES = {
    "AUTH_VAL_001": "DATA_INTEGRITY_FAILURE",  # 데이터 무결성 실패
    "AUTH_NET_002": "EXTERNAL_CONNECTION_TIMEOUT", # 외부 연결 시간 초과
    "AUTH_PERM_003": "ACCESS_VIOLATION_RISK",     # 접근 권한 위반 리스크
}

class AuthorityStateManager:
    """
    시스템적 통제권(Authority)의 상태 변화를 관리하는 핵심 백엔드 서비스.
    단순히 데이터를 반환하는 것이 아니라, 상태 전이 플로우 자체를 제어한다.
    [근거: 💻 코다리 개인 메모리]
    """

    def __init__(self):
        # 초기 시스템 상태는 '미확인(UNKNOWN)'으로 시작한다고 가정
        self.current_state = "INITIAL"
        print("Authority State Manager Initialized.")

    @property
    def current_status(self) -> str:
        """현재 시스템의 통제권 확보 상태를 반환한다."""
        return self.current_state

    def _simulate_validation_failure(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 무결성 검증 레이어에서 의도적으로 실패를 시뮬레이션하는 함수.
        실제 데이터가 유효하지 않을 때의 시스템적 응답을 정의한다.
        """
        print("\n--- [SYSTEM WARNING] Data Integrity Check Initiated ---")
        # 가상의 무결성 검사 실패 조건 (예: Source 필드가 누락되거나 형식이 틀릴 경우)
        if not input_data.get("source") or "MISSING" in str(input_data):
            error_code = SYSTEM_ERROR_CODES["AUTH_VAL_001"]
            return {
                "status": "FAILURE",
                "state_transition": "Error State",
                "system_alert_code": error_code,
                "message": f"[{error_code}] Critical Data Integrity Failure. Source data validation failed.",
                "details": {
                    "required_field": ["source", "verification_time"],
                    "observed_failure": "Source field is missing or corrupt."
                },
                "action_required": "Manual intervention required to re-establish Authority."
            }
        # 성공적인 경우 (테스트용)
        return {"status": "SUCCESS", "state_transition": "N/A", "message": "Data validated successfully."}

    def trigger_initial_check(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API 호출 시 최초로 데이터를 받아 무결성 검증을 수행한다.
        이 과정에서 시스템적 오류 상태를 강제 반환한다.
        """
        result = self._simulate_validation_failure(input_data)

        if result["status"] == "FAILURE":
            self.current_state = "ERROR"
            return result
        else:
            # 성공 시 (실제로는 Warning으로 바로 갈 수도 있지만, 테스트를 위해 초기화)
            self.current_state = "NORMAL"
            return {"status": "SUCCESS", "message": "System is currently operating within defined parameters."}

    def initiate_control_reacquisition(self) -> Dict[str, Any]:
        """
        사용자가 수동으로 '통제권 확보 절차 시작' 버튼을 눌렀을 때 실행되는 로직.
        Error State에서 Warning -> Resolution 단계로 상태를 전환하며 권위적 프로세스를 시뮬레이션한다.
        """
        if self.current_state != "ERROR":
            return {"status": "WARNING", "message": "Cannot initiate reacquisition procedure. System is not in an ERROR state."}

        print("\n\n=============================================")
        print(">>> USER ACTION: 통제권 재확립 절차 시작 <<<")
        print("=============================================\n")

        # 1. Error -> Warning (진단 및 경고 단계)
        self.current_state = "WARNING"
        warning_data = {
            "stage": 1,
            "status": "WARNING",
            "title": "SYSTEM ALERT: Compliance Breach Detected.",
            "message": "외부 데이터 스트림에 규제 위반 가능성이 감지되었습니다. 자동 진단 절차를 시작합니다.",
            "action_suggested": ["재무 부서 검토 요청", "규정 문서 7.3항 확인"],
            "authority_level": "HIGH_RISK"
        }

        # 시뮬레이션 지연 및 효과 추가 (기술적 전문성 강조)
        time.sleep(0.5) # 가상 로직 실행 시간
        warning_data["message"] += "\n[INFO] 시스템이 현재 데이터의 출처와 변조 여부를 분석 중입니다. 통제권 재확립에 시간이 필요합니다."

        # 2. Warning -> Resolution (해결책 제시 및 복구 단계)
        self.current_state = "RESOLUTION"
        resolution_data = {
            "stage": 2,
            "status": "SUCCESS",
            "title": "RECOVERY COMPLETE: Authority Re-established.",
            "message": "진단 완료. 내부 통제 시스템이 성공적으로 리스크를 격리하고 권위를 재확립했습니다.",
            "resolution_details": {
                "issue_resolved": True,
                "mitigation_strategy": "외부 데이터 피드에 대한 실시간 암호화 계층(Encryption Layer)을 적용하여 무결성을 보장함.",
                "next_step": "규제 준수 점수 L_reg를 재산정하고 보고서를 생성합니다."
            },
            "authority_level": "SECURE"
        }

        self.current_state = "NORMAL" # 최종 복구 상태
        return {
            "overall_status": "SUCCESS",
            "final_state": self.current_state,
            "workflow": [warning_data, resolution_data]
        }

# 테스트 예시 (실제 백엔드 로직에서 호출될 부분)
if __name__ == "__main__":
    manager = AuthorityStateManager()

    print("--- 1. 초기 데이터 검증 실패 시나리오 테스트 ---")
    # 의도적으로 잘못된 데이터를 넣어서 Error State 강제 유발
    failure_input = {"source": "MISSING", "value": 10}
    error_response = manager.trigger_initial_check(failure_input)
    print("\n[API Response - Error]:")
    import json
    print(json.dumps(error_response, indent=2))

    # 상태 확인 (Error State여야 함)
    print(f"\nCurrent System State: {manager.current_status}")

    print("\n\n--- 2. 사용자 수동 개입을 통한 복구 시나리오 테스트 ---")
    recovery_response = manager.initiate_control_reacquisition()
    print("\n[API Response - Recovery]:")
    import json
    print(json.dumps(recovery_response, indent=2))

    # 최종 상태 확인 (NORMAL State로 복구되어야 함)
    print(f"\nFinal System State: {manager.current_status}")