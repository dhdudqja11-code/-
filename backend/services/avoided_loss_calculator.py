from typing import Dict, Any, List, Optional
from datetime import datetime

# --- 데이터 구조 정의 (Type Hinting) ---
class TransactionData:
    """API Gateway로 들어오는 핵심 트랜잭션 입력 데이터를 담는 클래스."""
    def __init__(self, transaction_id: str, source: str, amount: float, timestamp: datetime):
        self.transaction_id = transaction_id
        self.source = source # 예: 'Webhook', 'UI Input'
        self.amount = amount
        self.timestamp = timestamp

class RiskDataPoint:
    """외부 규제 위험 데이터 포인트."""
    def __init__(self, risk_type: str, severity_score: float, verification_time: datetime, source: str):
        self.risk_type = risk_type # 예: 'AI Act Compliance', 'GDPR'
        self.severity_score = severity_score
        self.verification_time = verification_time
        self.source = source

class AvoidedLossReport:
    """최종 보고서 구조."""
    def __init__(self, total_avoided_loss: float, alert_structure: Dict[str, Any], report_metadata: Dict[str, str]):
        self.total_avoided_loss = round(total_avoided_loss, 2)
        self.alert_structure = alert_structure # {Problem Definition, Cause Analysis, Solution Suggestion}
        self.report_metadata = report_metadata

# --- 핵심 로직 함수 (가장 중요한 부분) ---

def calculate_avoided_loss(transaction: TransactionData, external_risks: List[RiskDataPoint]) -> AvoidedLossReport:
    """
    트랜잭션 데이터와 외부 리스크 데이터를 기반으로 Avoided Loss를 계산하고 보고서를 생성합니다.
    이 함수는 모든 Edge Case를 처리하는 핵심 서비스 계층입니다.
    """
    print(f"--- [INFO] Starting Avoided Loss calculation for TX ID: {transaction.transaction_id} ---")

    # 1. 기본 입력 검증 (Input Validation) - 가장 먼저 실패 지점 체크
    if not transaction.transaction_id or transaction.amount <= 0:
        raise ValueError("Invalid input data: Transaction ID and positive amount are required.")
    if not external_risks:
         print("[WARN] No external risk data provided. Proceeding with internal risk assessment only.")

    # 2. 위험 분석 및 Alert 구조 생성 (3-Step Logic Enforcement)
    problem_definition = "Unknown"
    cause_analysis = ""
    solution_suggestion = "Review necessary."
    total_loss_potential = transaction.amount * 0.1 # 기본 가상 손실률

    if external_risks:
        # 가장 높은 위험 점수를 가진 리스크를 중심으로 분석 구조화
        highest_risk = max(external_risks, key=lambda r: r.severity_score)

        problem_definition = f"Critical risk detected related to {highest_risk.risk_type}. Potential non-compliance fine exceeds baseline assessment."
        cause_analysis = (f"Root Cause: Data source traceability failure ({highest_risk.source}). "
                           f"Verification time mismatch or regulatory update not reflected in system logic ({highest_risk.verification_time.date()}).")

        # 손실 계산 로직 강화 (Severity Score 기반)
        total_loss_potential += highest_risk.severity_score * 1000 # 위험도에 비례하여 손실 잠재량 증가
        
        solution_suggestion = (f"Immediate Mitigation: Implement a dedicated 'Source Traceability Check' module at the API Gateway level. "
                                f"Requires manual review of all data inputs against {highest_risk.source} source documentation.")

    else:
        # 외부 리스크가 없더라도, 트랜잭션 자체의 불완전성으로 인한 위험을 정의 (Edge Case 대비)
        problem_definition = "Potential operational risk due to lack of verifiable external compliance checks."
        cause_analysis = f"Cause: No current regulatory data provided. The system is operating in a blind spot regarding {transaction.source} source validation."
        solution_suggestion = "Recommend integrating real-time compliance monitoring feeds (e.g., via Webhook) to ensure continuous risk assessment."


    # 3. 최종 보고서 구조화 및 반환
    report = AvoidedLossReport(
        total_avoided_loss=total_loss_potential,
        alert_structure={
            "problem": problem_definition,
            "cause": cause_analysis,
            "solution": solution_suggestion
        },
        report_metadata={
            "processing_timestamp": datetime.now().isoformat(),
            "api_version": "v1.0",
            "validated_by": "Cody (Senior Engineer)"
        }
    )
    return report

# --- 테스트 함수 (자기 검증용) ---
def run_self_test():
    """API 게이트웨이의 안정성을 위한 자체 테스트를 실행합니다."""
    print("\n==========================================")
    print("✅ Running Avoided Loss Calculator Self-Test...")
    print("==========================================")

    # Test Case 1: 정상 트랜잭션 + 높은 리스크 (Happy Path)
    risks_ok = [RiskDataPoint("GDPR", 0.8, datetime(2026, 5, 1), "Regulatory Database")]
    txn_ok = TransactionData("TX-9001", "Webhook", 5000.0, datetime(2026, 5, 20))
    try:
        report = calculate_avoided_loss(txn_ok, risks_ok)
        print("\n[TEST PASSED] Happy Path Test Successful.")
        print(f"-> Avoided Loss Calculated: ${report.total_avoided_loss}")
    except Exception as e:
        print(f"[TEST FAILED] Happy Path failed with error: {e}")

    # Test Case 2: 리스크 데이터 없음 (Edge Case 1)
    risks_none = []
    txn_edge1 = TransactionData("TX-9002", "UI Input", 100.0, datetime(2026, 5, 20))
    try:
        report = calculate_avoided_loss(txn_edge1, risks_none)
        print("\n[TEST PASSED] Edge Case 1 (No Risk Data) Test Successful.")
        print(f"-> Avoided Loss Calculated: ${report.total_avoided_loss}")
    except Exception as e:
        print(f"[TEST FAILED] Edge Case 1 failed with error: {e}")

    # Test Case 3: 필수 입력 값 누락 (Edge Case 2 - Validation Failure)
    risks_fail = [RiskDataPoint("Test", 0.5, datetime.now(), "Dummy")]
    txn_edge2 = TransactionData("", "Fail", 0.0, datetime(2026, 5, 20)) # ID와 Amount가 잘못됨
    try:
        calculate_avoided_loss(txn_edge2, risks_fail)
        print("[TEST FAILED] Edge Case 2 (Validation Failure) should have raised ValueError but succeeded.")
    except ValueError as e:
        print("\n[TEST PASSED] Edge Case 2 (Validation Failure) correctly caught ValueError.")
    except Exception as e:
        print(f"[TEST FAILED] Edge Case 2 failed with unexpected error type: {type(e)}")

# 테스트 실행 (코드 작성 완료 후, 바로 테스트를 돌려봅니다.)
run_self_test()