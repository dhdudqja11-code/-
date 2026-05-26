import unittest
from typing import Dict, Any
# 실제 구현된 모듈을 임포트합니다. (가정)
from mini_roi_simulator.core_api_service import simulate_risk, simulate_risk_api

class TestMiniROISimulator(unittest.TestCase):
    """
    Mini ROI Simulator의 핵심 API 엔드포인트에 대한 통합 테스트 스위트.
    성공 케이스와 모든 종류의 실패/엣지 케이스를 커버합니다.
    """

    def test_01_happy_path_critical_risk(self):
        """테스트 1: 고위험군 데이터를 입력했을 때, CRITICAL 상태가 정상 반환되는지 확인."""
        print("\n--- Running Test 1: Happy Path (Critical Risk) ---")
        # 리스크 점수를 높게 설정하여 Critical을 유도
        input_data = {"source": "ClientX", "data_points": [8, 9, 7]}
        result, success = simulate_risk(input_data=input_data)

        self.assertTrue(success, "Critical risk test failed to run successfully.")
        self.assertEqual(result['status'], 'CRITICAL', "Expected status CRITICAL for high risk score.")
        self.assertIn("즉각적인 규제 준수 감사", result['mitigation_suggestion'])

    def test_02_happy_path_low_risk(self):
        """테스트 2: 저위험군 데이터를 입력했을 때, LOW 상태가 정상 반환되는지 확인."""
        print("\n--- Running Test 2: Happy Path (Low Risk) ---")
        # 리스크 점수를 낮게 설정하여 Low를 유도
        input_data = {"source": "ClientY", "data_points": [1, 2, 3]}
        result, success = simulate_risk(input_data=input_data)

        self.assertTrue(success, "Low risk test failed to run successfully.")
        self.assertEqual(result['status'], 'LOW', "Expected status LOW for low risk score.")
        self.assertIn("지속적인 모니터링이 권장", result['mitigation_suggestion'])


    def test_03_edge_case_invalid_input(self):
        """테스트 3: 필수 데이터 포인트가 누락되었을 때 (ValueError 유발)의 방어 로직 검증."""
        print("\n--- Running Test 3: Edge Case (Invalid Input) ---")
        # data_points를 아예 제외한 경우
        invalid_data = {"source": "ClientZ", "other_key": "dummy"}

        # simulate_risk 함수가 ValueError를 발생시키고, audit_required가 이를 포착하는지 테스트
        result, success = simulate_risk(input_data=invalid_data)

        self.assertFalse(success, "Expected failure (ValueError) but test succeeded.")
        self.assertIn("cannot be found", result['details']['message'], "Error message should indicate missing data points.")


    def test_04_api_gateway_stress_test(self):
        """테스트 4: 전체 API Gateway 진입점의 안정성 및 오류 포착 능력 테스트."""
        print("\n--- Running Test 4: API Gateway Stress Test (Failure Path) ---")
        # 유효하지 않은 데이터를 넣어 최상위 레이어에서 에러가 발생하는 상황 시뮬레이션
        bad_input = {"source": "CrashTest", "data_points": None}

        api_result = simulate_risk_api(input_data=bad_input)

        self.assertFalse(api_result['success'], "API Gateway should return failure for invalid input.")
        self.assertIn("Internal Server Error", api_result['message'], "Message should reflect a controlled system error.")


if __name__ == '__main__':
    # 테스트 실행 시, 로그 출력을 명확하게 분리하기 위해 unittest 설정을 변경합니다.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)