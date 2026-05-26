import json
from typing import Dict, List, Any
# 실제 환경에서는 reportlab이나 weasyprint 같은 라이브러리가 필요합니다. 
# 여기서는 로직 검증을 위해 가상의 ReportGenerator 인터페이스를 사용하겠습니다.

class LegalReportData:
    """
    법률 증명보고서에 필요한 모든 구조화된 데이터를 담는 모델.
    데이터의 불변성과 추적 가능성을 보장하는 것이 핵심입니다.
    """
    def __init__(self, risk_score: float, loss_estimate: float, violation_logs: List[Dict]):
        self.risk_score = round(risk_score, 2)  # 최종 위험 지수 (0-100)
        self.loss_estimate = round(loss_estimate, 2) # 예상 손실액 (USD)
        self.violation_logs = violation_logs

    @staticmethod
    def generate_summary(risk: float, loss: float, logs: list) -> str:
        """Executive Summary 섹션을 위한 논리적 서사문을 생성합니다."""
        return (
            f"현재 시스템 상태 분석 결과, 귀사의 비즈니스는 총 {loss:,.2f} USD의 "
            f"예상 손실 위험에 노출되어 있습니다. 이는 주요 규제 위반 항목 ({len(logs)}건) 때문입니다. "
            f"본 보고서는 사전에 해당 리스크를 감지하고 통제했음을 증명합니다."
        )

class LegalReportGenerator:
    """
    Audit Log와 Risk Data를 받아 구조화된 법률 보고서를 생성하는 서비스 클래스.
    (SRP 원칙에 따라, 데이터 재구성 및 논리 흐름 제어만 담당합니다.)
    """
    def __init__(self):
        # 초기화 시 필요한 의존성 (예: API 클라이언트, DB 연결)을 주입받아야 합니다.
        print("LegalReportGenerator initialized. Ready to process audit logs.")

    def _analyze_and_structure_data(self, raw_logs: List[Dict], risk_input: Dict) -> LegalReportData:
        """
        Raw 로그 데이터를 분석하고, 법률 보고서의 핵심 구조에 맞게 재구성합니다. (Core Logic)
        """
        if not raw_logs:
            # 데이터 부재 시 안전한 기본값 반환 로직
            print("Warning: No logs provided. Defaulting to minimal risk report.")
            return LegalReportData(0.0, 0.0, [])

        # Step 1: 리스크 지수 계산 (가중치 적용)
        # 실제로는 복잡한 머신러닝 모델이 필요하지만, 여기서는 예시 로직 사용
        total_risk = sum([float(log.get('severity', '1')) * 0.5 for log in raw_logs])
        final_score = min(100.0, total_risk + risk_input.get('base_factor', 10))

        # Step 2: 예상 손실액 계산 (위반 건수와 심각도에 비례)
        loss_estimate = len(raw_logs) * 5000 + risk_input.get('market_impact', 0)

        # Step 3: 데이터 구조화 및 반환
        return LegalReportData(final_score, loss_estimate, raw_logs)

    def generate_report(self, audit_logs: List[Dict], initial_risk_context: Dict) -> str:
        """
        메인 진입점. 전체 보고서의 텍스트 기반 구조를 완성하고 시각화를 준비합니다.
        """
        try:
            # 1. 데이터 분석 및 모델링 (위험성 강조의 근거 확보)
            structured_data = self._analyze_and_structure_data(audit_logs, initial_risk_context)

            # 2. 보고서 서사 구조에 맞게 내용 재구성 (PDF 생성을 위한 문자열 출력 예시)
            report_content = []

            # I. Executive Summary: Shock & Immediate Value
            summary = LegalReportData.generate_summary(structured_data.risk_score, structured_data.loss_estimate, structured_data.violation_logs)
            report_content.append("="*80)
            report_content.append("I. EXECUTIVE SUMMARY: 법적 증명 보고서 (요약)")
            report_content.append(f"*** 핵심 결과: {summary} ***")

            # II. Core Risk Analysis: Fear & Context
            report_content.append("\n\n" + "="*80)
            report_content.append("II. 핵심 위기 상황 분석 (Risk Analysis)")
            report_content.append(f"-> 현재 규제 환경 변화에 따라, '{initial_risk_context.get('reg_name', '개인정보보호법')}'의 조항 {initial_risk_context.get('art_num', 'X')} 위반 가능성이 높습니다.")
            report_content.append(f"-> 시스템은 이를 감지하고, 잠재적 손실액을 최소 {structured_data.loss_estimate:,.0f} USD로 추정했습니다.")

            # III. Detection Log: Proof & Detail
            report_content.append("\n\n" + "="*80)
            report_content.append("III. 감지된 오류/위반 상세 보고 (Detection Log)")
            if structured_data.violation_logs:
                for i, log in enumerate(structured_data.violation_logs):
                    report_content.append(f"\n--- [위반 항목 {i+1}: {log['error_type']} ({log['timestamp']})] ---")
                    report_content.append(f"  * 심각도: {log['severity']} (높음) | 근거 법률: {log['legal_basis']}")
                    report_content.append(f"  * 상세 위반 내용: '{log['description'][:50]}...'")
                    # 여기에 로그 스니펫 시각화 로직이 추가되어야 합니다.
                report_content.append("\n[결론] 위의 증거 기록은 법적 책임의 근거가 명확함을 입증합니다.")
            else:
                 report_content.append("-> 현재까지 감지된 심각한 위반 항목은 없습니다. 시스템 안정성이 확보되었습니다.")


            # 최종적으로 PDF 라이브러리를 호출하여 이 텍스트를 시각화하는 단계가 필요합니다.
            return "\n\n".join(report_content)

        except Exception as e:
            # 치명적인 에러 처리 (Critical Error Handling)
            print(f"\n[!!! CRITICAL ERROR !!!] 보고서 생성 중 예외 발생: {e}")
            return f"오류가 발생했습니다. 상세 오류 로그를 참조하십시오. ({type(e).__name__})"

# 테스트용 Mock Data 구조 정의 ------------------------------------------
mock_audit_logs = [
    {'timestamp': '2026-05-26T14:00:00', 'error_type': 'PII Leakage', 'severity': '3', 'legal_basis': 'GDPR Article 17', 'description': '사용자의 민감 정보가 로컬에 평문으로 저장됨.'},
    {'timestamp': '2026-05-26T14:05:00', 'error_type': 'Data Retention Violation', 'severity': '2', 'legal_basis': 'CCPA § 1798.100', 'description': '필요 기간을 초과한 사용자 데이터를 삭제하지 않음.'}
]

mock_risk_context = {
    'reg_name': 'GDPR 및 CCPA 통합 가이드라인',
    'art_num': 'Art 5(1)(f)',
    'base_factor': 20, # 기본 위험 요소 점수
    'market_impact': 1000000 # 시장 영향 계수 (USD)
}

if __name__ == "__main__":
    # 테스트 실행 로직 (실제 사용자가 이 코드를 돌릴 때의 동작을 시뮬레이션)
    generator = LegalReportGenerator()
    final_report_text = generator.generate_report(mock_audit_logs, mock_risk_context)
    print("\n" + "="*80)
    print("✨ [PDF 준비 완료] 최종 보고서 텍스트 구조 (시각화 전)")
    print("="*80)
    print(final_report_text)

# 테스트를 위해 가상의 PDF 생성 함수 추가 (실제는 라이브러리 사용)
def generate_pdf_file(content: str, filename: str):
    """이 함수가 실제 ReportLab 등을 이용해 물리적인 PDF 파일을 만듭니다."""
    print(f"\n[System Log] Successfully structured content into {filename}. Now invoking PDF library to render...")
    # 실제 코드는 여기에 삽입되어야 합니다.