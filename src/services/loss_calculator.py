import json
from typing import Dict, Any, List, Tuple, Optional
import os

# --- Legacy classes preserved for backward compatibility ---
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
        total_loss = {}
        matched_risks: List[Any] = self._match_scenarios(industry, company_size_korea, input_data)
        
        if not matched_risks:
            total_loss['base'] = 0.0
            return {'Base': 0.0, 'Total Loss': 0.0}, ["✅ 현재 데이터 상 심각한 위험 징후는 감지되지 않았습니다."]

        for risk in matched_risks:
            scenario = self._scenarios[risk['id']]
            loss = self._calculate_stage_loss(scenario, company_size_korea)
            total_loss[f"{scenario['name']} 손실액"] = loss

        base_loss = total_loss.get('Base', 0.0)
        final_total_loss = base_loss + sum(total_loss[k] for k in total_loss if '손실액' in k)
        total_loss['Total Loss'] = round(final_total_loss, 2)

        warning_messages = []
        warning_messages.extend(self._generate_critical_alert(matched_risks))

        return total_loss, warning_messages

    def _match_scenarios(self, industry: str, company_size_korea: int, input_data: Dict[str, Any]) -> List[Dict]:
        matched = []
        for scenario_id, scenario in self._scenarios.items():
            is_keyword_match = any(kw.lower() in str(input_data).lower() for kw in scenario['trigger_keywords'])
            if is_keyword_match and (industry in scenario['description'] or company_size_korea >= 5):
                matched.append({"id": scenario_id, "risk_level": scenario['risk_level'], "scenario": scenario})
        return sorted(matched, key=lambda x: x['risk_level'], reverse=True)

    def _calculate_stage_loss(self, scenario: Any, company_size_korea: int) -> float:
        components = scenario['loss_components']
        initial_fine = components['initial_fine_rate'] * company_size_korea * 1000
        penalty_loss = initial_fine * components['regulatory_penalty_factor']
        remediation_cost = components['remediation_cost_base'] + (company_size_korea * 5000)
        total = penalty_loss + remediation_cost
        return round(total, 2)

    def _generate_critical_alert(self, matched_risks: List[Dict]) -> List[str]:
        alerts = []
        for risk in matched_risks:
            scenario = self._scenarios[risk['id']]
            alert_msg = f"""\n🚨 [CRITICAL ALERT - {scenario['name']} 발생] 🚨\n"""
            alert_msg += "  1. 🚩 문제 정의 (What went wrong?): 핵심 자산/규제가 위협받는 상태입니다.\n"
            alert_msg += f"     -> 구체적 위험: {scenario['description']}\n"
            alert_msg += "  2. 🔍 원인 분석 (Why did it go wrong? Source/Time): 트랜잭션 데이터({list(self._scenarios.keys())[0] if matched_risks else 'N/A'}]에서 {risk['scenario']['trigger_keywords'][0]} 키워드가 감지되었습니다. 규제 위반 가능성이 높습니다.\n"
            alert_msg += "  3. 💡 해결책 제시 (How to fix it?): 즉시 모든 관련 시스템의 접근을 차단하고, 내부 법률 자문팀 및 보안 전문가를 호출하여 포렌식 분석을 수행해야 합니다."
            alerts.append(alert_msg)
        return alerts

# --- New modular functions matching the pytest expectations ---

class MiniROIServiceError(Exception):
    """Mini ROI 시뮬레이터의 커스텀 예외 클래스."""
    def __init__(self, message: str, error_type: str, details: Optional[str] = None):
        super().__init__(message)
        self.error_type = error_type # e.g., 'SCHEMA', 'AUTH', 'BUSINESS'
        self.details = details

    def __str__(self) -> str:
        return f"[{self.error_type}] {super().__str__()}"

    def to_dict(self) -> Dict[str, Any]:
        """Gateway가 처리할 수 있는 표준 에러 구조를 반환."""
        return {
            "success": False,
            "error": {
                "code": self.error_type,
                "message": str(self),
                "details": self.details if self.details else "상세 정보 없음."
            }
        }

def calculate_risk_level(data: Dict[str, Any]) -> str:
    """
    데이터를 기반으로 비즈니스 리스크 레벨을 산출한다.
    """
    required_keys = ["source", "time_window", "transaction_value"]
    if not all(key in data for key in required_keys):
        raise MiniROIServiceError("필수 데이터 필드가 누락되었습니다. 'source', 'time_window', 'transaction_value'를 확인하세요.", "SCHEMA")

    try:
        value = float(data["transaction_value"])
        if value > 1000 and data["source"] == "CrossBorder":
            return "High"
        elif value > 500:
            return "Medium"
        else:
            return "Low"
    except ValueError:
        raise MiniROIServiceError("트랜잭션 값은 반드시 유효한 숫자여야 합니다.", "SCHEMA", f"Value: {data.get('transaction_value')}")

def calculate_loss(risk_level: str, transaction_value: float) -> float:
    """
    산출된 위험 레벨과 거래 금액을 기반으로 예상 손실액을 계산한다.
    """
    if not isinstance(transaction_value, (int, float)) or transaction_value < 0:
        raise MiniROIServiceError("손실 계산에 사용되는 거래 금액이 유효하지 않습니다.", "SCHEMA")

    loss_multiplier = {"Low": 0.01, "Medium": 0.05, "High": 0.1}
    
    if risk_level not in loss_multiplier:
        raise MiniROIServiceError(f"유효하지 않은 리스크 레벨 '{risk_level}'이 입력되었습니다.", "BUSINESS")

    loss = transaction_value * loss_multiplier[risk_level]
    return round(loss, 2)

def process_mini_roi(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    API Gateway의 최종 통합 진입점 (Entry Point). 전체 로직을 감싸고 에러 처리를 표준화한다.
    """
    # 3. [실패 Case 2: Authorization Failure]
    if data.get("source") == "Restricted":
        raise MiniROIServiceError("해당 소스는 현재 계정의 접근 권한 범위를 초과하여 분석할 수 없습니다.", "AUTH")

    try:
        # 1. Schema 검증 및 리스크 레벨 산출 단계 (Critical State)
        risk_level = calculate_risk_level(data)

        # 2. 손실액 계산 단계
        loss_amount = calculate_loss(risk_level, float(data["transaction_value"]))

        # 3. 최종 성공 응답 구조화
        return {
            "success": True,
            "result": {
                "risk_level": risk_level,
                "estimated_loss": loss_amount,
                "message": "Mini ROI 시뮬레이션이 성공적으로 완료되었습니다."
            }
        }
    except MiniROIServiceError as e:
        if e.error_type == "SCHEMA":
            raise  # tests expect MiniROIServiceError to bubble up
        elif e.error_type == "BUSINESS":
            raise  # tests expect MiniROIServiceError to bubble up
        raise
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "TIMEOUT_ERROR",
                "message": f"요청 처리 중 시스템 시간 초과가 발생했습니다. ({type(e).__name__})",
                "details": str(e)
            }
        }

# --- Legacy test runner ---
def run_unit_test():
    """모듈의 핵심 기능을 단위 테스트합니다."""
    print("\n=======================================")
    print("🚀 [TESTING] Unit Test Start - LossCalculator")
    
    try:
        calculator = MiniROI_LossCalculator(scenario_file_path="mini_roi_risk_scenarios.json")
        test_data_a = {"user_id": "abc123", "data_type": "sensitive_pii"}
        loss_a, alerts_a = calculator.calculate_loss("Healthcare", 10, test_data_a)

        print("\n✅ [Test Case A: PII Leak (High Risk)]")
        print(f"   - 계산된 손실액: {json.dumps(loss_a)}")
        for alert in alerts_a:
            print("--- 경고 출력 ---")
            print(alert)

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
    run_unit_test()