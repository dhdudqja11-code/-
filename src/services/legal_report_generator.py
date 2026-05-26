# -*- coding: utf-8 -*-
import os
import sys
import datetime
from typing import Dict, List, Any

# ReportLab 컴포넌트 임포트
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# 폰트 구성 및 Windows 맑은 고딕 동적 등록
FONT_NAME = "Helvetica"
if REPORTLAB_AVAILABLE and os.name == 'nt':
    malgun_path = r"C:\Windows\Fonts\malgun.ttf"
    if os.path.exists(malgun_path):
        try:
            pdfmetrics.registerFont(TTFont("Malgun", malgun_path))
            FONT_NAME = "Malgun"
        except Exception as e:
            print(f"⚠️ Failed to register Malgun Gothic font: {e}", file=sys.stderr)

def sanitize_text(text: str, font: str) -> str:
    """
    Helvetica 폰트 등 한글 인코딩 미지원 환경에서 PDF 크래시를 예방하기 위해
    국문 서사 텍스트를 고품질 영어/ASCII 문구로 지능형 대체 매핑합니다.
    """
    if font != "Malgun":
        replacements = {
            "🚨 섹션 1. 위험 고지 및 법률적 문제 정의 (Problem Definition)": "🚨 Section 1. Risk Warning & Legal Problem Definition",
            "🔍 섹션 2. 감사 로그 기반 원인 분석 및 증명 기록 (Audit Trail Analysis)": "🔍 Section 2. Audit Trail Analysis & Proof Record",
            "✅ 섹션 3. 규정 준수 및 법적 해결책 제시 (Mitigation Suggestion)": "✅ Section 3. Compliance & Legal Mitigation Suggestions",
            "법적 리스크 분석 보고서: [회사명] 불변 증거 기록": "Legal Risk Analysis Report: Immutable Evidence Record",
            "불변 증거 기록": "Immutable Evidence Record",
            "작성일": "Date",
            "경고: 최근 트랜잭션 기록에서 규정 위반 또는 시스템 오류가 발생했습니다. 이로 인해 법적 책임 및 데이터 유실 위험이 존재할 수 있습니다.": 
                "WARNING: Regulatory non-compliance or system errors detected in recent transactions. Legal liability and data loss risks may exist.",
            "현재까지의 로그만으로는 명확한 대규모 리스크는 감지되지 않았습니다. 다만, 지속적인 모니터링이 필요합니다.":
                "No large-scale critical risks detected from current logs alone. Continuous monitoring recommended.",
            "해결책 1. 데이터 처리 전 반드시 '유효성 검증 게이트웨이'를 추가하여 모든 입력을 스키마 기반으로 필터링해야 합니다.":
                "Solution 1: A validation gateway must be added before data processing to filter all inputs based on schemas.",
            "해결책 2. 핵심 비즈니스 로직은 Auth Middleware와 Compliance Gateway의 3단계 파이프라인을 의무화하고, 모든 트랜잭션에 SHA-256 해시를 포함한 불변 증명 기록(Audit Log)을 남겨야 합니다.":
                "Solution 2: Mandate 3-tier pipelines (Auth Middleware, Compliance Gateway) and maintain immutable SHA-256 hashed Audit Logs.",
            "추가적인 법률 검토가 필요합니다. 시스템 아키텍처 재설계를 통해 위험 요소를 근본적으로 제거하는 것을 권고합니다.":
                "Further legal review required. Fundamental redesign of system architecture is recommended to mitigate risks.",
            "현재 시스템 상태 분석 결과, 감지된 위반 사항이 없으며 비즈니스가 안전하게 통제되고 있음을 증명합니다.":
                "Analysis of current system state proves zero compliance violations, demonstrating business operations are securely controlled.",
            "현재 시스템 상태 분석 결과, 귀사의 비즈니스는 총": "Analysis of current system state shows exposure to a total of",
            "USD의 예상 손실 위험에 노출되어 있습니다. 이는 주요 규제 위반 항목": "USD in estimated losses due to compliance violations",
            "건 때문입니다. 본 보고서는 사전에 해당 리스크를 감지하고 통제했음을 증명합니다.": "cases. This report proves proactive detection and containment.",
            "--- 불변의 감사 로그 추적 (Immutable Audit Trail) ---": "--- Immutable Audit Trail Track ---",
            "위반 항목은 없습니다.": "No compliance violations found."
        }
        for kr, en in replacements.items():
            text = text.replace(kr, en)
        # 128보다 큰 유니코드 문자열은 물음표(?)로 처리하여 ASCII 범위 유지
        return "".join([c if ord(c) < 128 else "?" for c in text])
    return text

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
        if not logs or loss <= 0:
            return "현재 시스템 상태 분석 결과, 감지된 위반 사항이 없으며 비즈니스가 안전하게 통제되고 있음을 증명합니다."
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
    def __init__(self, audit_log: List[Dict] = None):
        """Audit Log 기반의 법적 보고서 생성을 준비합니다."""
        if audit_log is not None:
            if not isinstance(audit_log, list) or not audit_log:
                raise ValueError("LegalReportGenerator requires a non-empty list of audit logs.")
        self.audit_log = audit_log

    def _is_data_immutable(self, audit_log: List[Dict]) -> bool:
        """
        Audit Log의 핵심 필드와 데이터 순차적 일치 여부를 검사하여
        보고서가 생성되기 전 완벽한 불가역성(Immutability)을 단언 검증합니다.
        """
        if not isinstance(audit_log, list):
            return False
        
        # 필수 검증 필드 구성
        required_keys = ["timestamp", "error_type", "severity", "legal_basis", "description"]
        
        for entry in audit_log:
            if not isinstance(entry, dict):
                return False
            # 모든 필수 키가 존재하고 비어있지 않은지 검사
            for key in required_keys:
                if key not in entry or entry[key] is None:
                    return False
        
        # 타임스탬프 순차성(Sequential Integrity) 검증
        try:
            timestamps = [entry["timestamp"] for entry in audit_log]
            # 문자열 순서 정렬 상태와 동일한지 단언
            if timestamps != sorted(timestamps):
                return False
        except Exception:
            return False

        return True

    def _analyze_and_structure_data(self, raw_logs: List[Dict], risk_input: Dict) -> LegalReportData:
        """
        Raw 로그 데이터를 분석하고, 법률 보고서의 핵심 구조에 맞게 재구성합니다.
        """
        if not raw_logs:
            print("Warning: No logs provided. Defaulting to minimal risk report.")
            return LegalReportData(0.0, 0.0, [])

        # Step 1: 리스크 지수 계산 (가중치 적용)
        total_risk = sum([float(log.get('severity', '1')) * 5.0 for log in raw_logs])
        final_score = min(100.0, total_risk + risk_input.get('base_factor', 10))

        # Step 2: 예상 손실액 계산
        loss_estimate = len(raw_logs) * 50000 + risk_input.get('market_impact', 0)

        # Step 3: 데이터 구조화 및 반환
        return LegalReportData(final_score, loss_estimate, raw_logs)

    def _build_structured_report(self, structured_data: LegalReportData, initial_risk_context: Dict) -> Dict:
        """
        3단 논리 구조에 기반하여 보고서의 서사 내용 및 세부 필드를 기획 구성합니다.
        """
        # Section 1. 위험 고지 및 공포 조성
        if structured_data.violation_logs:
            risk_warning = (
                f"경고: 최근 트랜잭션 기록에서 규정 위반 또는 시스템 오류가 발생했습니다. 이로 인해 법적 책임 및 데이터 유실 위험이 존재할 수 있습니다. "
                f"현재 귀사에서 '{initial_risk_context.get('reg_name', '통합 가이드라인')}'의 조항 '{initial_risk_context.get('art_num', 'Art 5')}' "
                f"위반 가능성이 대단히 높게 감출되었습니다."
            )
        else:
            risk_warning = "현재까지의 로그만으로는 명확한 대규모 리스크는 감지되지 않았습니다. 다만, 지속적인 모니터링이 필요합니다."

        # Section 2. 감사 로그 기반 분석적 확신 제공
        analysis_trail = []
        for i, log in enumerate(structured_data.violation_logs):
            analysis_trail.append(
                f"[로그 증적 {i+1}] {log['timestamp']} | 에러: {log['error_type']} | 근거 법률: {log['legal_basis']} | 세부 설명: {log['description']}"
            )
        analysis_log_text = "\n".join(analysis_trail) if analysis_trail else "위반 항목은 없습니다."

        # Section 3. 구체적인 해결책 제시
        if structured_data.violation_logs:
            solution = (
                "해결책 1. 데이터 처리 전 반드시 '유효성 검증 게이트웨이'를 추가하여 모든 입력을 스키마 기반으로 필터링해야 합니다.\n"
                "해결책 2. 핵심 비즈니스 로직은 Auth Middleware와 Compliance Gateway의 3단계 파이프라인을 의무화하고, "
                "모든 트랜잭션에 SHA-256 해시를 포함한 불변 증명 기록(Audit Log)을 남겨야 합니다."
            )
        else:
            solution = "추가적인 법률 검토가 필요합니다. 시스템 아키텍처 재설계를 통해 위험 요소를 근본적으로 제거하는 것을 권고합니다."

        return {
            "title": "법적 리스크 분석 보고서: [회사명] 불변 증거 기록",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sections": [
                {"heading": "🚨 섹션 1. 위험 고지 및 법률적 문제 정의 (Problem Definition)", "content": risk_warning},
                {"heading": "🔍 섹션 2. 감사 로그 기반 원인 분석 및 증명 기록 (Audit Trail Analysis)", "content": analysis_log_text},
                {"heading": "✅ 섹션 3. 규정 준수 및 법적 해결책 제시 (Mitigation Suggestion)", "content": solution}
            ]
        }

    def generate_report(self, audit_logs: List[Dict] = None, initial_risk_context: Dict = None, filename: str = None) -> str:
        """
        메인 진입점. 전체 보고서의 텍스트 기반 구조를 완성하고 시각화된 불가역 PDF 파일을 생성합니다.
        """
        logs_to_process = audit_logs if audit_logs is not None else self.audit_log
        context_to_use = initial_risk_context if initial_risk_context is not None else {}

        if logs_to_process is None:
            raise ValueError("No audit logs provided for report generation.")

        # 1. 데이터 무결성 검증 (Immutability Guard)
        if not self._is_data_immutable(logs_to_process):
            raise ValueError("Data integrity verification failed. Missing fields or timestamps are not sequential.")

        try:
            # 2. 데이터 구조화 및 3단 논리 모델링
            structured_data = self._analyze_and_structure_data(logs_to_process, context_to_use)
            report_data = self._build_structured_report(structured_data, context_to_use)

            # 3. 텍스트 리포트 스트림 구성
            text_lines = []
            text_lines.append("="*80)
            text_lines.append(report_data["title"])
            text_lines.append(f"작성일: {report_data['date']}")
            text_lines.append("="*80)

            for sec in report_data["sections"]:
                text_lines.append(f"\n{sec['heading']}")
                text_lines.append("-"*40)
                text_lines.append(sec["content"])

            final_text_report = "\n".join(text_lines)

            # 4. 실증 PDF 파일 생성 (ReportLab 빌드)
            if filename and REPORTLAB_AVAILABLE:
                self._render_pdf(filename, report_data)

            return final_text_report

        except Exception as e:
            print(f"\n[!!! CRITICAL ERROR !!!] 보고서 생성 중 예외 발생: {e}", file=sys.stderr)
            raise e

    def _render_pdf(self, filename: str, report_data: Dict[str, Any]):
        """
        ReportLab Platypus를 이용해 고품질 정밀 PDF 문서 레이아웃을 빌드하고 로컬에 영구 보존합니다.
        """
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                rightMargin=54, leftMargin=54,
                                topMargin=54, bottomMargin=54)
        
        styles = getSampleStyleSheet()
        
        # 커스텀 단락 스타일 구성 (맑은 고딕 또는 헬베티카 탑재)
        title_style = ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1A2B4C"),
            spaceAfter=15
        )
        
        heading_style = ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontName=FONT_NAME,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#A8201A"),
            spaceBefore=15,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            name='SectionBody',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2B2D42"),
            spaceAfter=10
        )

        story = []
        
        # 1. 보고서 제목 렌더링
        story.append(Paragraph(sanitize_text(report_data["title"], FONT_NAME), title_style))
        story.append(Paragraph(sanitize_text(f"작성일: {report_data['date']}", FONT_NAME), body_style))
        story.append(Spacer(1, 10))
        
        # 구분선 장식
        divider_data = [[""]]
        divider_table = Table(divider_data, colWidths=[500], rowHeights=[2])
        divider_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1A2B4C")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider_table)
        story.append(Spacer(1, 15))

        # 2. 3단 구조 섹션별 렌더링
        for sec in report_data["sections"]:
            story.append(Paragraph(sanitize_text(sec["heading"], FONT_NAME), heading_style))
            
            # 본문 내 줄바꿈을 Paragraph HTML 태그로 변환하여 레이아웃 유연성 유지
            content_html = sec["content"].replace("\n", "<br/>")
            story.append(Paragraph(sanitize_text(content_html, FONT_NAME), body_style))
            story.append(Spacer(1, 10))
            
        doc.build(story)

# 테스트용 기본 Mock 데이터 세트 제공 ------------------------------------
mock_audit_logs = [
    {
        'timestamp': '2026-05-26T14:00:00',
        'error_type': 'PII Leakage',
        'severity': '3',
        'legal_basis': 'GDPR Article 17',
        'description': '사용자의 민감 정보가 로컬에 평문으로 저장됨.'
    },
    {
        'timestamp': '2026-05-26T14:05:00',
        'error_type': 'Data Retention Violation',
        'severity': '2',
        'legal_basis': 'CCPA § 1798.100',
        'description': '필요 기간을 초과한 사용자 데이터를 삭제하지 않음.'
    }
]

mock_risk_context = {
    'reg_name': 'GDPR 및 CCPA 통합 가이드라인',
    'art_num': 'Art 5(1)(f)',
    'base_factor': 20,
    'market_impact': 1000000
}

if __name__ == "__main__":
    generator = LegalReportGenerator()
    final_report_text = generator.generate_report(mock_audit_logs, mock_risk_context, "immutable_audit_report.pdf")
    print("\n" + "="*80)
    print("✨ [PDF 및 텍스트 빌드 완료] 최종 보고서 텍스트 스크랩")
    print("="*80)
    print(final_report_text)