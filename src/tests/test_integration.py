import json
from src.processor.authority_checker import AuthorityChecker # 가정

class TestAuthorityIntegration:
    def __init__(self):
        # 테스트 환경 초기화 및 시스템 ID 설정 (권위 확보를 위한 시뮬레이션)
        self.checker = AuthorityChecker(system_id="AI-ARC-20260603") 
        print("=======================================================")
        print("🚀 [통합 테스트 시작] 원격 제어 모듈의 권위적 복구 플로우 검증")
        print("=======================================================")

    def test_1_successful_run(self):
        """[Case 1: 정상 작동] 규제 위반 없음."""
        print("\n--- [TEST CASE 1/3]: 성공적인 데이터 흐름 테스트 ---")
        # Mock 데이터: 아무 문제가 없는 트랜잭션 리스크 데이터 (JSON 형태로 인코딩)
        good_data = json.dumps({"is_violating": False, "violation_type": "None", "legal_article": "N/A"})
        result = self.checker.run_remote_check({'external_risk_payload': good_data})
        print(f"[RESULT] {result}")
        assert "Status OK" in result

    def test_2_authority_violation(self):
        """[Case 2: 권위적 위반] 규제 위반 감지 및 전문 경고 출력 플로우 검증."""
        print("\n--- [TEST CASE 2/3]: 법규 위반 -> Authority Warning Flow 테스트 ---")
        # Mock 데이터: 명백한 법규 위반이 포함된 트랜잭션 리스크 데이터
        bad_data = json.dumps({
            "is_violating": True, 
            "violation_type": "데이터 프라이버시 침해", 
            "legal_article": "GDPR Article 17: Right to Erasure" # 구체적인 법 조항 명시
        })
        result = self.checker.run_remote_check({'external_risk_payload': bad_data})
        print(f"\n[RESULT] {result}")
        assert "SYSTEM AUTHORITY ALERT" in result and "데이터 프라이버시 침해" in result

    def test_3_structural_error(self):
        """[Case 3: 구조적 오류] 외부 데이터의 JSON 파싱 실패 시 처리 (권위 유지)."""
        print("\n--- [TEST CASE 3/3]: 외부 데이터 무결성 에러 테스트 ---")
        # Mock 데이터: JSON 형식이 깨진 문자열을 전달하여 강제 오류 유발
        corrupt_data = "{'is_violating': True, 'type': 'bad', 'article':'A'" # 잘못된 키(따옴표) 사용
        result = self.checker.run_remote_check({'external_risk_payload': corrupt_data})
        print(f"\n[RESULT] {result}")
        assert "structural integrity failure" in result

if __name__ == "__main__":
    test = TestAuthorityIntegration()
    test.test_1_successful_run()
    test.test_2_authority_violation()
    test.test_3_structural_error()