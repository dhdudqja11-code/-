import json
from typing import Dict, Any, List, Tuple
import os

class LossCalculatorError(Exception):
    """손실 계산 로직에서 발생하는 사용자 정의 예외."""
    pass

class MiniROI_LossCalculator:
    """
    Mini ROI 시뮬레이터의 핵심 손실액 계산 서비스.
    사용자 조건과 리스크 시나리오를 매칭하여 정량적, 단계적 손실액을 산출합니다.
    """
    def __init__(self, scenario_file_path: str = "mini_roi_risk_scenarios.json"):
        print(f"⚙️ [System] 로스 계산 모듈 초기화 중... 파일 경로: {scenario_file_path}")
        if not os.path.exists(scenario_file_path):
            raise FileNotFoundError(f"필수 리스크 시나리오 파일을 찾을 수 없습니다: {scenario_file_path}")
        
        self._scenarios = self._load_scenarios(scenario_file_path)

    def _load_scenarios(self, file_path: str) -> Dict[str, Any]:
        """JSON 파일에서 모든 리스크 시나리오를 로드하고 메모리에 캐싱합니다."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Dictionary 형태로 빠르게 조회할 수 있도록 가공
                scenarios = {}
                for scenario in data.get("scenarios", []):
                    scenarios[scenario['id']] = scenario
                return scenarios
        except json.JSONDecodeError as e:
            raise LossCalculatorError(f"JSON 파일 디코딩 오류 발생: {e}")

    def calculate_loss(self, 
                        industry: str, 
                        company_size_korea: int, 
                        input_data: Dict[str, Any]) -> Tuple[Dict[str, float], List[str]]:
        """
        핵심 손실 계산 로직. 주어진 조건과 데이터를 기반으로 단계별 손실액을 산출합니다.

        Args:
            industry (str): 기업 산업군 (예: 'Healthcare', 'Fintech').
            company_size_korea (int): 회사 규모 (만 단위).
            input_data (Dict[str, Any]): Webhook으로 들어오는 트랜잭션/리스크 데이터.

        Returns:
            Tuple[Dict[str, float], List[str]]: {단계별 손실액}, [경고 메시지 리스트]
        """
        total_loss = {}
        triggered_scenarios = []
        warning_messages = []
        
        # 1. 가장 높은 위험도 점수 계산 및 시나리오 매칭 (가중치 적용)
        matched_risks: List[Any] = self._match_scenarios(industry, company_size_korea, input_data)
        
        if not matched_risks:
            total_loss['base'] = 0.0
            return {'Base': 0.0, 'Total Loss': 0.0}, ["✅ 현재 데이터 상 심각한 위험 징후는 감지되지 않았습니다."]

        # 2. 단계적 손실액 계산 (Staged Loss Calculation)
        for risk in matched_risks:
            scenario = self._scenarios[risk['id']]
            loss = self._calculate_stage_loss(scenario, company_size_korea)
            total_loss[f"{scenario['name']} 손실액"] = loss

        # 3. 최종 총 손실액 및 Critical State 진단
        base_loss = total_loss.get('Base', 0.0)
        final_total_loss = base_loss + sum(total_loss[k] for k in total_loss if '손실액' in k)
        total_loss['Total Loss'] = round(final_total_loss, 2)

        # 4. Critical State 발생 시 경고 메시지 생성 및 에러 핸들링 구조화
        warning_messages.extend(self._generate_critical_alert(matched_risks))

        return total_loss, warning_messages

    def _match_scenarios(self, industry: str, company_size_korea: int, input_data: Dict[str, Any]) -> List[Dict]:
        """입력된 조건과 데이터를 기반으로 가장 높은 위험도를 가진 시나리오 목록을 반환합니다."""
        matched = []
        for scenario_id, scenario in self._scenarios.items():
            # 1차 필터링: 키워드 매칭 및 산업군 적합성 검사
            is_keyword_match = any(kw.lower() in str(input_data).lower() for kw in scenario['trigger_keywords'])
            
            if is_keyword_match and (industry in scenario['description'] or company_size_korea >= 5): # 간단한 가중치 로직 예시
                matched.append({"id": scenario_id, "risk_level": scenario['risk_level'], "scenario": scenario})
        
        # 위험도(risk_level)가 높은 순서로 정렬하여 최악의 시나리오부터 제시
        return sorted(matched, key=lambda x: x['risk_level'], reverse=True)

    def _calculate_stage_loss(self, scenario: Any, company_size_korea: int) -> float:
        """주어진 리스크 시나리오를 기반으로 3단계 손실액을 계산합니다."""
        components = scenario['loss_components']
        
        # 로스 구조: [기본 벌금] * [규제 가중치] + (최소 복구 비용 * 규모 보정)
        
        # 1. 기본 벌금 산출 (Initial Fine): PII 유출 시도 대비 법적 최소 벌금 예상액
        initial_fine = components['initial_fine_rate'] * company_size_korea * 1000 # 단위: 원
        
        # 2. 규제 가중치 적용 (Regulatory Penalty): 산업별 특성 반영
        penalty_loss = initial_fine * components['regulatory_penalty_factor']
        
        # 3. 규모 보정 복구 비용 산출 (Remediation Cost): 회사 규모에 비례하여 증가
        remediation_cost = components['remediation_cost_base'] + (company_size_korea * 5000)

        total = penalty_loss + remediation_cost
        return round(total, 2)

    def _generate_critical_alert(self, matched_risks: List[Dict]) -> List[str]:
        """Critical State 발생 시, [문제 정의 $\to$ 원인 분석 $\to$ 해결책 제시] 구조로 경고 메시지를 생성합니다."""
        alerts = []
        for risk in matched_risks:
            scenario = self._scenarios[risk['id']]
            
            # 🚨 Critical State 출력 포맷 강제 적용 (Must enforce this structure)
            alert_msg = f"""\n🚨 [CRITICAL ALERT - {scenario['name']} 발생] 🚨\n"""
            alert_msg += "  1. 🚩 문제 정의 (What went wrong?): 핵심 자산/규제가 위협받는 상태입니다.\n"
            alert_msg += f"     -> 구체적 위험: {scenario['description']}\n"
            alert_msg += "  2. 🔍 원인 분석 (Why did it go wrong? Source/Time): 트랜잭션 데이터({list(self._scenarios.keys())[0] if matched_risks else 'N/A'}]에서 {risk['scenario']['trigger_keywords'][0]} 키워드가 감지되었습니다. 규제 위반 가능성이 높습니다.\n"
            alert_msg += "  3. 💡 해결책 제시 (How to fix it?): 즉시 모든 관련 시스템의 접근을 차단하고, 내부 법률 자문팀 및 보안 전문가를 호출하여 포렌식 분석을 수행해야 합니다."
            alerts.append(alert_msg)
        return alerts

# --- 테스트 코드 포함: E2E 테스트 가능 확인 ---
def run_unit_test():
    """모듈의 핵심 기능을 단위 테스트합니다."""
    print("\n=======================================")
    print("🚀 [TESTING] Unit Test Start - LossCalculator")
    
    try:
        # 1. 초기화 및 데이터 로딩 테스트
        calculator = MiniROI_LossCalculator(scenario_file_path="mini_roi_risk_scenarios.json")

        # 2. 시나리오 A (PII 유출) 테스트 케이스
        test_data_a = {"user_id": "abc123", "data_type": "sensitive_pii"}
        loss_a, alerts_a = calculator.calculate_loss("Healthcare", 10, test_data_a)

        print("\n✅ [Test Case A: PII Leak (High Risk)]")
        print(f"   - 계산된 손실액: {json.dumps(loss_a)}")
        for alert in alerts_a:
            print("--- 경고 출력 ---")
            print(alert)

        # 3. 시나리오 B (안전한 조건) 테스트 케이스
        test_data_b = {"transaction_id": "xyz987", "status": "success"}
        loss_b, alerts_b = calculator.calculate_loss("E-commerce", 1, test_data_b)

        print("\n✅ [Test Case B: Low Risk / Safe Conditions]")
        print(f"   - 계산된 손실액: {json.dumps(loss_b)}")
        for alert in alerts_b:
            print("--- 경고 출력 ---")
            print(alert)

    except FileNotFoundError as e:
        print(f"\n❌ [FATAL ERROR] 테스트 실패: {e}")
    except Exception as e:
        print(f"\n❌ [ERROR] 예상치 못한 오류 발생: {type(e).__name__}: {e}")
    finally:
        print("=======================================\n")

if __name__ == "__main__":
    # 테스트 실행을 위해 임시로 스크립트를 직접 호출할 수 있도록 main 블록 유지
    run_unit_test()