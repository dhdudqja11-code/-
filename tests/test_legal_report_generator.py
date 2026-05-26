# -*- coding: utf-8 -*-
import os
import pytest
from src.services.legal_report_generator import (
    LegalReportGenerator,
    LegalReportData,
    sanitize_text,
    mock_audit_logs,
    mock_risk_context
)

# 1. 정상 데이터 처리 및 PDF 실제 생성 테스트 (Happy Path)
def test_successful_report_generation():
    """모든 데이터가 올바르고 PDF 파일이 안전하게 실물 생성되는지 검증합니다."""
    pdf_filename = "test_immutable_audit_report.pdf"
    
    # 생성 시점에 audit_log 주입 (신규 패러다임)
    generator = LegalReportGenerator(mock_audit_logs)
    
    # PDF 생성 기동
    report_text = generator.generate_report(initial_risk_context=mock_risk_context, filename=pdf_filename)
    
    # 텍스트 리포트 구조 및 내용 단언
    assert "법적 리스크 분석 보고서" in report_text
    assert "🚨 섹션 1. 위험 고지 및 법률적 문제 정의" in report_text
    assert "🔍 섹션 2. 감사 로그 기반 원인 분석 및 증명 기록" in report_text
    assert "✅ 섹션 3. 규정 준수 및 법적 해결책 제시" in report_text
    assert "GDPR Article 17" in report_text
    
    # 디스크에 PDF 파일이 생성되었는지 확인 후 뒷정리
    assert os.path.exists(pdf_filename)
    try:
        os.remove(pdf_filename)
    except OSError:
        pass

def test_legacy_constructor_successful_report_generation():
    """하위 호환성 준수를 위해 인자 없는 생성자 및 메서드 직접 주입 흐름을 검증합니다."""
    generator = LegalReportGenerator()
    report_text = generator.generate_report(audit_logs=mock_audit_logs, initial_risk_context=mock_risk_context)
    
    assert "법적 리스크 분석 보고서" in report_text
    assert "GDPR Article 17" in report_text

# 2. 데이터 무결성 및 순차성 오류(ValueError) 검출 검증
def test_report_generation_with_missing_fields():
    """필수 필드(timestamp, error_type 등)가 결손되었을 때 보고서 생성을 즉각 거부하는지 단언합니다."""
    malformed_logs = [
        {
            'timestamp': '2026-05-26T14:00:00',
            'error_type': None,  # 결손 필드
            'severity': '3',
            'legal_basis': 'GDPR Article 17',
            'description': '테스트용 결손 로그'
        }
    ]
    
    generator = LegalReportGenerator(malformed_logs)
    with pytest.raises(ValueError, match="Data integrity verification failed"):
        generator.generate_report(initial_risk_context=mock_risk_context)

def test_report_generation_with_non_sequential_timestamps():
    """감사 로그의 타임스탬프 순서가 시간 역행(Non-sequential)할 때 무결성 위반으로 차단되는지 검증합니다."""
    non_sequential_logs = [
        {
            'timestamp': '2026-05-26T14:10:00',  # 뒤의 시간
            'error_type': 'PII Leakage',
            'severity': '3',
            'legal_basis': 'GDPR Article 17',
            'description': '첫 번째 로그'
        },
        {
            'timestamp': '2026-05-26T14:00:00',  # 앞의 시간 (역행)
            'error_type': 'Data Retention Violation',
            'severity': '2',
            'legal_basis': 'CCPA § 1798.100',
            'description': '두 번째 로그'
        }
    ]
    
    generator = LegalReportGenerator(non_sequential_logs)
    with pytest.raises(ValueError, match="Data integrity verification failed"):
        generator.generate_report(initial_risk_context=mock_risk_context)

def test_constructor_value_error_on_invalid_arguments():
    """생성자에 잘못된 형태(빈 리스트 혹은 Dict가 아닌 구조) 주입 시 즉각 ValueError를 반환하는지 단언합니다."""
    with pytest.raises(ValueError, match="requires a non-empty list of audit logs"):
        LegalReportGenerator([])
        
    with pytest.raises(ValueError, match="requires a non-empty list of audit logs"):
        LegalReportGenerator("invalid_argument_type")

# 3. 폰트 폴백 및 지능형 한글 유무 대응 검증
def test_sanitize_text_fallback_behavior():
    """Helvetica 폰트 환경에서 한글 깨짐 방지를 위해 영어/ASCII로 고품질 변환되는지 검증합니다."""
    kr_warning = "경고: 최근 트랜잭션 기록에서 규정 위반 또는 시스템 오류가 발생했습니다. 이로 인해 법적 책임 및 데이터 유실 위험이 존재할 수 있습니다."
    
    # 1. Malgun Gothic 환경인 경우: 한국어 원본이 유지되어야 합니다.
    sanitized_malgun = sanitize_text(kr_warning, "Malgun")
    assert sanitized_malgun == kr_warning
    
    # 2. Helvetica 폴백 환경인 경우: 고품질 영문 매핑이 수행되어야 합니다.
    sanitized_helvetica = sanitize_text(kr_warning, "Helvetica")
    assert "WARNING: Regulatory non-compliance" in sanitized_helvetica
    # ASCII 범위 내의 글자들로만 정화되었는지 단언
    assert all(ord(c) < 128 for c in sanitized_helvetica)

# 4. 데이터 불변성 보장 검증
def test_raw_data_immutability():
    """보고서 생성 가동이 끝난 이후에도 원본 데이터의 불변 상태가 엄격히 보장되는지 확인합니다."""
    import copy
    original_logs_snapshot = copy.deepcopy(mock_audit_logs)
    
    generator = LegalReportGenerator(mock_audit_logs)
    generator.generate_report(initial_risk_context=mock_risk_context)
    
    assert mock_audit_logs == original_logs_snapshot