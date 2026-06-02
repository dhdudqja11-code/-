import os
import unittest
import json
from content_simulator import ContentSimulator

class TestContentSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.config_path = os.path.join(cls.workspace_dir, 'simulator_v1', 'config.json')
        cls.simulator = ContentSimulator(cls.config_path)

    def test_scenario_1_high_quality_content(self):
        """시나리오 1: 최고 점수 콘텐츠 시뮬레이션 (Upload Go 판정 및 매출 정상 발생)"""
        scores = {
            "hooking_score": 90,
            "empathy_score": 95,
            "sales_connection": 90,
            "seo_score": 85,
            "cta_score": 90,
            "spam_risk": 10
        }
        decision, avg_score, report = self.simulator.evaluate_content(scores)
        self.assertEqual(decision, "upload_go")
        self.assertGreaterEqual(avg_score, 80)
        self.assertEqual(report['spam_risk'], 10)

        sim_result = self.simulator.run_revenue_simulation(decision, scores, baseline_traffic=100)
        self.assertEqual(sim_result['status'], "success")
        self.assertGreater(sim_result['total_predicted_revenue'], 0)
        print(f"[Scenario 1 Pass] Decision: {decision}, Total Revenue: KRW {sim_result['total_predicted_revenue']:,}")

    def test_scenario_2_high_spam_risk_content(self):
        """시나리오 2: 스팸 위험 초과 콘텐츠 (Discard 판정 및 매출 0원 종결)"""
        scores = {
            "hooking_score": 80,
            "empathy_score": 80,
            "sales_connection": 85,
            "seo_score": 70,
            "cta_score": 80,
            "spam_risk": 55
        }
        decision, avg_score, report = self.simulator.evaluate_content(scores)
        self.assertEqual(decision, "discard")

        sim_result = self.simulator.run_revenue_simulation(decision, scores)
        self.assertEqual(sim_result['status'], "discarded")
        self.assertEqual(sim_result['total_predicted_revenue'], 0)
        print(f"[Scenario 2 Pass] Decision: {decision}, Total Revenue: KRW {sim_result['total_predicted_revenue']}")

    def test_scenario_3_revision_needed_content(self):
        """시나리오 3: 보완 필요 콘텐츠 (Revision Needed 판정 및 패널티 매출 시뮬레이션)"""
        scores = {
            "hooking_score": 70,
            "empathy_score": 75,
            "sales_connection": 68,
            "seo_score": 70,
            "cta_score": 65,
            "spam_risk": 35
        }
        decision, avg_score, report = self.simulator.evaluate_content(scores)
        self.assertEqual(decision, "revision_needed")

        sim_result = self.simulator.run_revenue_simulation(decision, scores, baseline_traffic=100)
        self.assertEqual(sim_result['status'], "success")
        
        # Revision penalty가 적용되어 Perfect 버전보다 효율이 낮아야 함을 검증
        perfect_scores = {
            "hooking_score": 90,
            "empathy_score": 90,
            "sales_connection": 90,
            "seo_score": 90,
            "cta_score": 90,
            "spam_risk": 10
        }
        perfect_decision, _, _ = self.simulator.evaluate_content(perfect_scores)
        perfect_sim_result = self.simulator.run_revenue_simulation(perfect_decision, perfect_scores, baseline_traffic=100)
        
        self.assertLess(sim_result['total_predicted_revenue'], perfect_sim_result['total_predicted_revenue'])
        print(f"[Scenario 3 Pass] Decision: {decision}, Total Revenue: KRW {sim_result['total_predicted_revenue']:,} (Perfect: KRW {perfect_sim_result['total_predicted_revenue']:,})")

    def test_scenario_4_baseline_traffic_integration(self):
        """시나리오 4: 로컬 DB 연동 Baseline 시뮬레이션"""
        # _get_baseline_traffic() 호출이 예외 없이 올바른 값을 반환하는지 테스트
        baseline = self.simulator._get_baseline_traffic()
        self.assertGreater(baseline, 0)
        
        # Baseline을 통한 시뮬레이션 동작 검증
        scores = {
            "hooking_score": 85,
            "empathy_score": 85,
            "sales_connection": 85,
            "seo_score": 85,
            "cta_score": 85,
            "spam_risk": 15
        }
        decision, _, _ = self.simulator.evaluate_content(scores)
        sim_result = self.simulator.run_revenue_simulation(decision, scores)
        self.assertEqual(sim_result['status'], "success")
        print(f"[Scenario 4 Pass] Baseline Traffic: {baseline}, Total Revenue: KRW {sim_result['total_predicted_revenue']:,}")

    def test_scenario_5_input_validation_guard(self):
        """시나리오 5: 예외 입력값에 대한 무결성 가드 테스트"""
        invalid_scores_high = {
            "hooking_score": 150, # 범위 초과
            "empathy_score": 80,
            "sales_connection": 80,
            "seo_score": 80,
            "cta_score": 80,
            "spam_risk": 10
        }
        with self.assertRaises(ValueError):
            self.simulator.evaluate_content(invalid_scores_high)

        invalid_scores_missing = {
            "hooking_score": 80,
            "empathy_score": 80,
            # sales_connection 누락
            "seo_score": 80,
            "cta_score": 80,
            "spam_risk": 10
        }
        with self.assertRaises(ValueError):
            self.simulator.evaluate_content(invalid_scores_missing)
            
        print("[Scenario 5 Pass] Input validation error guards working properly.")

if __name__ == '__main__':
    unittest.main()
