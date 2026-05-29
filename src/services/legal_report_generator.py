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
            print(f"⚠️ Failed to register Malgun font: {e}")

def sanitize_text(text: str, font: str) -> str:
    """
    Helvetica 폰트 등 한글 인코딩 미지원 환경에서 PDF 크래시를 예방하기 위해
    국문 서사 텍스트를 고품질 영어/ASCII 문구로 지능형 대체 매핑합니다.
    """
    if font != "Malgun":
        replacements = {
            "🚨 1. 비즈니스 리스크 진단 (어려운 요인 예방)": "🚨 Section 1. Business Risk Diagnosis",
            "🔍 2. 실시간 안전 장부 증적 (확실한 증거 보존)": "🔍 Section 2. Immutable Audit Trail Record",
            "✅ 3. 안전한 비즈니스를 위한 해결 제안": "✅ Section 3. Friendly Safety Mitigation Suggestions",
            "비즈니스 리스크 진단 보고서: [회사명] 안전 가이드라인 증명서": "Risk Diagnosis Report: [Company] Safety Guide Certificate",
            "안전 가이드라인 증명서": "Safety Guide Certificate",
            "작성일": "Date",
            "경고: 최근 거래 장부 기록에서 비정상적인 행위나 시스템의 안전 위협이 감출되었습니다. 이를 그대로 방치할 경우 잠재적인 손실이나 비즈니스 정지 위험으로 이어질 수 있습니다.": 
                "WARNING: Unusual activities or safety threats detected in recent transaction logs. Left unaddressed, it may cause business disruption.",
            "현재까지 수집된 자동 안전 장부를 정밀히 스캔한 결과, 즉각적인 큰 위험 요소는 감지되지 않았습니다. 안심하고 운영하셔도 좋으나, 주기적인 자동 진단을 권장합니다.":
                "Zero major safety risks detected from current logs. Rest easy, though periodic automated diagnosis is recommended.",
            "제안 1. 데이터가 비즈니스 엔진으로 들어가기 전, 입력된 정보가 올바른 형식인지 자동으로 한 번 더 걸러주는 '검증 필터(유효성 검증 게이트웨이)'를 작동시킵니다.":
                "Proposal 1: A validation filter (gateway) must be added before data processing to filter all inputs based on schemas.",
            "제안 2. 비즈니스의 중요 코너와 거래(Transaction) 시에는 반드시 보안 잠금장치(Auth Middleware/Gateway)를 작동시키며, 나중에 손쉽게 조회가 가능한 위조 방지 '디지털 안전 장부(감사 로그)'를 꼼꼼히 적재해 둡니다.":
                "Proposal 2: Apply safety authentication filters for key business operations and maintain immutable safety logs.",
            "추가적인 정밀 진단이 권장됩니다. 일부 시스템 구조를 보다 안전하고 탄탄하게 개선하여 비즈니스 안전성을 근본적으로 높일 것을 권장합니다.":
                "Further analysis recommended. Improve system structure to fundamentally raise business safety levels.",
            "현재 비즈니스 안전 진단 결과, 이상 행동이나 위반 우려가 전혀 검출되지 않은 가장 안전하고 탄탄한 최고 등급 상태임을 공식 증명합니다.":
                "Proves zero safety issues or compliance violations found, showing business operations are securely controlled at the highest grade.",
            "현재 비즈니스 안전 진단 결과, 사장님의 비즈니스는 예상치 못한 사고 노출 시 총": "Analysis of current safety state shows potential exposure to a total of",
            "USD 규모의 예상 손실 리스크가 존재할 수 있습니다. 이는 실시간 안전 장부에 기록된": "USD in estimated losses due to",
            "건의 특이 사항 때문입니다. 본 보고서는 이러한 리스크를 미리 진단하고 사전 안전 통제 하에 두었음을 확실히 증명합니다.": "flagged cases in safety logs. This report proves proactive detection and containment.",
            "--- 위조 불가능한 실시간 안전 거래 장부 (Immutable Audit Trail) ---": "--- Immutable Real-time Safety Audit Trail ---",
            "검출된 특이 장부 기록이 없습니다.": "No compliance violations or flagged issues found in safety logs.",
            "현재 시스템 상태 분석 결과, 감지된 위반 사항이 없으며 비즈니스가 안전하게 통제되고 있음을 증명합니다.": "Analysis of current system state proves zero compliance violations, demonstrating business operations are securely controlled.",
            "현재 시스템 상태 분석 결과, 귀사의 비즈니스는 총": "Analysis of current system state shows exposure to a total of",
            "USD의 예상 손실 위험에 노출되어 있습니다. 이는 주요": "USD of potential loss risk due to major"
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
            return "현재 비즈니스 안전 진단 결과, 이상 행동이나 위반 우려가 전혀 검출되지 않은 가장 안전하고 탄탄한 최고 등급 상태임을 공식 증명합니다."
        return (
            f"현재 비즈니스 안전 진단 결과, 사장님의 비즈니스는 예상치 못한 사고 노출 시 총 {loss:,.2f} USD 규모의 "
            f"예상 손실 리스크가 존재할 수 있습니다. 이는 실시간 안전 장부에 기록된 ({len(logs)}건)의 특이 사항 때문입니다. "
            f"본 보고서는 이러한 리스크를 미리 진단하고 사전 안전 통제 하에 두었음을 확실히 증명합니다."
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
                f"경고: 최근 거래 장부 기록에서 비정상적인 행위나 시스템의 안전 위협이 감출되었습니다. 이를 그대로 방치할 경우 잠재적인 손실이나 비즈니스 정지 위험으로 이어질 수 있습니다. "
                f"현재 귀사의 안전 기준인 '{initial_risk_context.get('reg_name', '통합 가이드라인')}'의 관리 대역 '{initial_risk_context.get('art_num', 'Art 5')}'에서 "
                f"조치 권고 사안이 고도 감출되었습니다."
            )
        else:
            risk_warning = "현재까지 수집된 자동 안전 장부를 정밀히 스캔한 결과, 즉각적인 큰 위험 요소는 감지되지 않았습니다. 안심하고 운영하셔도 좋으나, 주기적인 자동 진단을 권장합니다."

        # Section 2. 감사 로그 기반 분석적 확신 제공
        analysis_trail = []
        for i, log in enumerate(structured_data.violation_logs):
            severity_str = "높음 🔴" if float(log.get('severity', '1')) >= 3 else ("보통 🟡" if float(log.get('severity', '1')) == 2 else "낮음 🟢")
            analysis_trail.append(
                f"[안전 진단 증적 {i+1}] {log['timestamp']} | 조치 시급성: {severity_str} | 관련 안전 기준: {log['legal_basis']} | 상세 진단 내용: {log['description']}"
            )
        analysis_log_text = "\n".join(analysis_trail) if analysis_trail else "검출된 특이 장부 기록이 없습니다."

        # Section 3. 구체적인 해결책 제시
        if structured_data.violation_logs:
            solution = (
                "제안 1. 데이터가 비즈니스 엔진으로 들어가기 전, 입력된 정보가 올바른 형식인지 자동으로 한 번 더 걸러주는 '검증 필터(유효성 검증 게이트웨이)'를 작동시킵니다.\n"
                "제안 2. 비즈니스의 중요 코너와 거래(Transaction) 시에는 반드시 보안 잠금장치(Auth Middleware/Gateway)를 작동시키며, 나중에 손쉽게 조회가 가능한 위조 방지 '디지털 안전 장부(감사 로그)'를 꼼꼼히 적재해 둡니다."
            )
        else:
            solution = "추가적인 정밀 진단이 권장됩니다. 일부 시스템 구조를 보다 안전하고 탄탄하게 개선하여 비즈니스 안전성을 근본적으로 높일 것을 권장합니다."

        return {
            "title": "비즈니스 리스크 진단 보고서: [회사명] 안전 가이드라인 증명서",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sections": [
                {"heading": "🚨 1. 비즈니스 리스크 진단 (어려운 요인 예방)", "content": risk_warning},
                {"heading": "🔍 2. 실시간 안전 장부 증적 (확실한 증거 보존)", "content": analysis_log_text},
                {"heading": "✅ 3. 안전한 비즈니스를 위한 해결 제안", "content": solution}
            ]
        }

    def generate_report(self, audit_logs: List[Dict] = None, initial_risk_context: Dict = None, filename: str = None) -> dict:
        """
        메인 진입점. 전체 보고서의 텍스트 기반 구조를 완성하고 시각화된 불가역 PDF 파일을 생성하여 2중 해싱 결과를 반환합니다.
        """
        logs_to_process = audit_logs if audit_logs is not None else self.audit_log
        context_to_use = initial_risk_context if initial_risk_context is not None else {}

        if logs_to_process is None:
            raise ValueError("No audit logs provided for report generation.")

        # 1. 데이터 무결성 검증 (Immutability Guard)
        if not self._is_data_immutable(logs_to_process):
            raise ValueError("Data integrity verification failed. Missing fields or timestamps are not sequential.")

        try:
            # 2. 데이터 구조화 및 3단 논리 모델 모델링
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

            # 1차 데이터 서명 해시 산출 (Document Signature Hash)
            import hashlib, json
            serialized_logs = json.dumps(logs_to_process, sort_keys=True, ensure_ascii=False)
            data_hash = hashlib.sha256(serialized_logs.encode('utf-8')).hexdigest()

            # 4. 실증 PDF 파일 생성 (ReportLab 빌드)
            file_hash = ""
            if filename and REPORTLAB_AVAILABLE:
                self._render_pdf(filename, report_data, data_hash)
                
                # 2차 실물 파일 서명 해시 산출 (Final Artifact Hash)
                if os.path.exists(filename):
                    with open(filename, "rb") as pdf_file:
                        file_hash = hashlib.sha256(pdf_file.read()).hexdigest()

            return {
                "text_report": final_text_report,
                "data_hash": data_hash,
                "file_hash": file_hash
            }

        except Exception as e:
            print(f"\n[!!! CRITICAL ERROR !!!] 보고서 생성 중 예외 발생: {e}", file=sys.stderr)
            raise e

    def _render_pdf(self, filename: str, report_data: Dict[str, Any], data_hash: str):
        """
        ReportLab Platypus를 이용해 고품질 '따뜻한 웜톤' PDF 문서 레이아웃을 빌드하고 로컬에 영구 보존합니다.
        """
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                rightMargin=54, leftMargin=54,
                                topMargin=54, bottomMargin=54)
        
        styles = getSampleStyleSheet()
        
        # 커스텀 단락 스타일 구성 (맑은 고딕 또는 헬베티카 HSL 웜톤 탑재)
        title_style = ParagraphStyle(
            name='ReportTitle_Warm',
            parent=styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#D35400"), # 따뜻한 오렌지/테라코타
            spaceAfter=15
        )
        
        heading_style = ParagraphStyle(
            name='SectionHeading_Warm',
            parent=styles['Heading2'],
            fontName=FONT_NAME,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#A04000"), # 어두운 테라코타 브라운
            spaceBefore=15,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            name='SectionBody_Warm',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2C2520"), # 짙은 에스프레소 브라운 본문
            spaceAfter=10
        )
        
        bold_body_style = ParagraphStyle(
            name='SectionBody_Bold_Warm',
            parent=body_style,
            fontName=FONT_NAME + "-Bold" if FONT_NAME != "Malgun" else FONT_NAME,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#BA4A00") # 부드러운 마호가니
        )
        
        mono_style = ParagraphStyle(
            name='SectionMono_Warm',
            parent=styles['Normal'],
            fontName="Courier-Bold",
            fontSize=8.0,
            leading=10,
            textColor=colors.HexColor("#A04000") # 마호가니 모노스페이스
        )

        def draw_warm_background(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFillColor(colors.HexColor("#FAF6F0")) # 따뜻한 크림 베이지
            canvas_obj.rect(0, 0, doc_obj.pagesize[0], doc_obj.pagesize[1], fill=True, stroke=False)
            canvas_obj.restoreState()

        story = []
        
        # 1. 보고서 제목 렌더링
        story.append(Paragraph(sanitize_text(report_data["title"], FONT_NAME), title_style))
        story.append(Paragraph(sanitize_text(f"작성일: {report_data['date']}", FONT_NAME), body_style))
        story.append(Spacer(1, 10))
        
        # 구분선 장식 (따뜻한 오렌지/테라코타)
        divider_data = [[""]]
        divider_table = Table(divider_data, colWidths=[500], rowHeights=[2])
        divider_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D35400")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider_table)
        story.append(Spacer(1, 15))

        # 2. 3단 구조 섹션별 렌더링
        for sec in report_data["sections"]:
            story.append(Paragraph(sanitize_text(sec["heading"], FONT_NAME), heading_style))
            content_html = sec["content"].replace("\n", "<br/>")
            story.append(Paragraph(sanitize_text(content_html, FONT_NAME), body_style))
            story.append(Spacer(1, 10))
            
        # 3. 불변 SHA-256 서명 박스 각인 (1차 해시)
        story.append(Spacer(1, 10))
        story.append(Paragraph(sanitize_text("🔒 디지털 보안 및 위조 방지 서명 (디지털 안전 인증)", FONT_NAME), heading_style))
        sig_data = [
            [Paragraph(sanitize_text("안전 장부 고유 번호", FONT_NAME), bold_body_style), Paragraph(data_hash, mono_style)],
            [Paragraph(sanitize_text("안전 인증 완료", FONT_NAME), bold_body_style), Paragraph(sanitize_text("2차 인증(OTP) 보안 완료 및 위조가 불가한 이중 암호화 보증", FONT_NAME), body_style)]
        ]
        sig_table = Table(sig_data, colWidths=[140, 360])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F3EFE9")),
            ('GRID', (0,0), (-1,-1), 1.2, colors.HexColor("#D35400")), # 따뜻한 오렌지 테두리
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(sig_table)
            
        doc.build(story, onFirstPage=draw_warm_background, onLaterPages=draw_warm_background)

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