import unittest
from typing import Dict, Any

# --- 1. Schema & Constants Definition ---
STATUS = {"SUCCESS": "성공", "WARNING": "경고", "ERROR": "오류"}
KPIs = ["Proof of Erasure Score", "Data Integrity Check", "Compliance Breach Flag"]

class AuthorityCheckResponseSchema:
    """시스템적 권위 응답 스키마를 정의합니다. 모든 API 출력이 이를 따라야 합니다."""
    def __init__(self, status: str, authority_score: float, diagnosis: str, root_cause: str, mitigation_steps: list):
        self.status = status
        self.authority_score = authority_score
        self.diagnosis = diagnosis
        self.root_cause = root_cause
        self.mitigation_steps = mitigation_steps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "authority_score": round(self.authority_score, 4),
            "diagnosis": self.diagnosis,
            "root_cause": self.root_cause,
            "mitigation_steps": self.mitigation_steps
        }

# --- 2. AuthorityClient (API 호출 시뮬레이터) ---
class AuthorityClient:
    """외부 데이터 API 호출을 모방합니다. 실패 주입 로직을 담당합니다."""
    @staticmethod
    def get_authority(data: Dict[str, Any], simulate_failure: bool = False, breach: bool = False) -> AuthorityCheckResponseSchema:
        if simulate_failure:
            print("--- [⚠️ API FAILURE SIMULATION] ---")
            # 통신 시간 초과 또는 서버 내부 에러 시뮬레이션
            return AuthorityCheckResponseSchema(
                status="ERROR", 
                authority_score=0.0, 
                diagnosis="시스템 데이터 연결 실패.", 
                root_cause="외부 서비스 API Timeout (504). 트랜잭션 무결성 검증 불가.", 
                mitigation_steps=["1. 네트워크 환경 점검", "2. 재시도 로직(Retry Logic) 구현"]
            )
        if breach:
            print("--- [🚨 COMPLIANCE BREACH SIMULATION] ---")
            # 규정 위반이 발생했을 때의 구조화된 경고 반환
            return AuthorityCheckResponseSchema(
                status="WARNING", 
                authority_score=0.3, 
                diagnosis="규제 준수 임계치 초과 (Authority Breach).", 
                root_cause=f"KPI 위반: {data['kpi']} 지표가 규정 기준 이하입니다.", 
                mitigation_steps=["1. 데이터 출처 재검토", "2. 권한 확보 보고서 작성"]
            )
        
        # 성공 시뮬레이션 (Success State)
        score = sum(data.get(kpi, 0) for kpi in KPIs) / len(KPIs)
        return AuthorityCheckResponseSchema(
            status="SUCCESS", 
            authority_score=score, 
            diagnosis="권위적 데이터 흐름 정상 진단.", 
            root_cause="모든 KPI가 규제 기준을 충족함. 시스템 통제력 확보됨.", 
            mitigation_steps=["정기적인 시스템 감사 및 모니터링 유지."]
        )

# --- 3. StateManager (상태 전이 로직 핵심) ---
class StateManager:
    """시스템의 상태를 관리하고 경고/해결책을 강제하는 핵심 로직입니다."""
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.current_state = "INITIAL" # 초기 상태 정의

    def run_full_cycle(self, client: AuthorityClient) -> AuthorityCheckResponseSchema:
        """Initial -> Warning/Success -> Resolution 플로우를 강제 수행합니다."""
        print("\n[✅ StateManager]: 1단계. Initial Diagnosis 시작...")
        
        # 1. 초기 진단 (State Transition: INITIAL -> ? )
        initial_result = client.get_authority(self.data)
        
        if initial_result.status == "ERROR":
            print("[⚠️ StateManager]: API 오류 감지. 통제권 재확립 절차 시작.")
            # 에러 발생 시, 해결책 제시 구조를 강제로 생성 (Recovery Logic)
            return AuthorityCheckResponseSchema(
                status="ERROR", 
                authority_score=0.1, 
                diagnosis="시스템 진단 실패. 통제권 재확립 절차 진행 중.", 
                root_cause="외부 API 오류로 인해 완전한 권위 측정 불가. 데이터 무결성 검증 필요.", 
                mitigation_steps=["[Action] 백업 시스템 연동 확인", "[Action] 수동 감사 기록 요청"]
            )
        elif initial_result.status == "WARNING":
            print("[🚨 StateManager]: 경고 상태 감지. 권위적 보고서 생성.")
            # Warning 발생 시, '해결책 제시'에 초점을 맞춘 최종 리포트를 반환 (Warning -> Resolution)
            return AuthorityCheckResponseSchema(
                status="WARNING", 
                authority_score=initial_result.authority_score * 0.8, # 경고로 인해 점수 하향 조정
                diagnosis=f"권위 미달: {initial_result.diagnosis} - 즉각적 조치 필요.", 
                root_cause=initial_result.root_cause, 
                mitigation_steps=initial_result.mitigation_steps + ["[Critical] 리스크 해결을 위한 법률 자문 필수."]
            )
        else: # SUCCESS
            print("[✅ StateManager]: 초기 진단 성공. 권위 확보 완료.")
            return initial_result

# --- 4. Test Suite Runner (실행기) ---
class AuthorityE2ETestSuite(unittest.TestCase):
    """통합 테스트 케이스 스위트입니다. 다양한 실패 시나리오를 커버합니다."""

    def test_01_success_flow(self):
        """[시나리오 1] 모든 KPI 충족 - 성공 플로우 검증 (Initial -> Success)"""
        print("\n=============================================")
        print("✅ 테스트 시작: [Success Flow Test]")
        mock_data = {"Proof of Erasure Score": 0.9, "Data Integrity Check": 0.8, "Compliance Breach Flag": 1}
        client = AuthorityClient()
        manager = StateManager(mock_data)
        result = manager.run_full_cycle(client)
        print("--- [TEST RESULT] ---")
        print(f"Status: {STATUS[result.status]} | Score: {result.authority_score}")
        self.assertEqual(result.status, "SUCCESS", "성공 시나리오 실패: 시스템이 성공을 인식하지 못함.")

    def test_02_compliance_breach_flow(self):
        """[시나리오 2] 규정 위반 발생 - 경고 플로우 검증 (Initial -> Warning)"""
        print("\n=============================================")
        print("⚠️ 테스트 시작: [Compliance Breach Test]")
        mock_data = {"Proof of Erasure Score": 0.5, "Data Integrity Check": 1, "Compliance Breach Flag": 0}
        client = AuthorityClient()
        manager = StateManager(mock_data)
        # 강제로 위반 상태를 주입하여 테스트 (Breach=True)
        result = manager.run_full_cycle(AuthorityClient().get_authority(mock_data, simulate_failure=False, breach=True)) 
        print("--- [TEST RESULT] ---")
        print(f"Status: {STATUS[result.status]} | Score: {result.authority_score}")
        self.assertEqual(result.status, "WARNING", "경고 시나리오 실패: Warning 상태로 전환되지 않음.")

    def test_03_api_failure_flow(self):
        """[시나리오 3] 외부 API 연결 오류 - 통제권 재확보 플로우 검증 (Initial -> Error)"""
        print("\n=============================================")
        print("💣 테스트 시작: [API Failure Test]")
        mock_data = {} # 데이터는 중요하지 않음, 실패 자체가 목적
        client = AuthorityClient()
        manager = StateManager(mock_data)
        # 강제로 API 실패를 주입하여 테스트 (simulate_failure=True)
        result = manager.run_full_cycle(AuthorityClient()) 
        print("--- [TEST RESULT] ---")
        print(f"Status: {STATUS[result.status]} | Score: {result.authority_score}")
        self.assertEqual(result.status, "ERROR", "API 실패 시나리오 실패: Error 상태로 전환되지 않음.")


if __name__ == '__main__':
    # unittest를 실행하면 모든 테스트가 순차적으로 run 됨
    unittest.main(argv=['first-arg-is-ignored'], exit=False)