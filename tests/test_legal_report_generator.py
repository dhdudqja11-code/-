import pytest
from src.services.legal_report_generator import LegalReportGenerator, mock_audit_logs, mock_risk_context

@pytest.fixture(scope="module")
def generator():
    """테스트용 Generator 인스턴스를 제공합니다."""
    return LegalReportGenerator()

# 1. 정상 데이터 처리 테스트 (Happy Path)
def test_successful_report_generation(generator):
    """모든 컴포넌트가 완벽하게 작동하는 표준 케이스를 검증합니다."""
    report = generator.generate_report(mock_audit_logs, mock_risk_context)
    assert "Executive Summary" in report # 보고서 핵심 구조 확인
    assert "예상 손실 위험에 노출되어 있습니다." in report # 서사적 톤앤매너 확인
    # 중요한 키워드가 포함되었는지 검증 (규제 준수 입증 여부)
    assert "GDPR Article 17" in report

# 2. 경계 조건 테스트 (Boundary Condition: 데이터 부재)
def test_report_generation_with_no_logs(generator):
    """Audit Log가 비어있을 때, 시스템이 크래시되지 않고 안전한 기본 보고서를 생성하는지 검증합니다."""
    empty_logs = []
    empty_context = {'reg_name': 'N/A', 'art_num': 'N/A', 'base_factor': 1}
    report = generator.generate_report(empty_logs, empty_context)
    assert "위반 항목은 없습니다." in report # 안전한 메시지 반환 확인
    # 예상 손실액이 0에 가깝게 설정되었는지 검증 (재무적 피해가 없음을 명시)
    assert "예상 손실 위험에 노출되어 있습니다" not in report

# 3. 에러 핸들링 테스트 (Failure Path: 비정형 데이터 주입)
def test_report_generation_with_malformed_data(generator):
    """로그 데이터가 JSON 형식이 아니거나, 심각도 필드가 숫자가 아닐 때 시스템이 안정적으로 작동하는지 검증합니다."""
    # 'severity' 필드에 문자를 넣어 파싱 에러 유발 시나리오 테스트
    malformed_logs = [
        {'timestamp': '2026-05-26T14:00:00', 'error_type': 'Malformed Data Test', 'severity': 'HIGH!', 'legal_basis': 'N/A', 'description': '가짜 데이터'},
    ]
    # Generator 내부에서 Exception을 잡는 테스트를 통해, 보고서가 깨지는 것을 막고 오류 메시지 반환 로직이 작동하는지 검증합니다.
    report = generator.generate_report(malformed_logs, mock_risk_context)
    assert "오류가 발생했습니다" in report or "Warning: No logs provided" in report 
    # 목표는 크래시 방지 및 사용자 친화적 에러 메시지 반환

# 4. 불변성 검증 테스트 (Immutability Check)
def test_data_integrity_after_generation(generator):
    """데이터가 한 번 처리된 후, 원본 데이터 구조를 오염시키거나 변조하는 일이 없는지 확인합니다."""
    original_logs = list(mock_audit_logs) # 복사본 생성
    report = generator.generate_report(original_logs, mock_risk_context)
    # 보고서 생성 후에도 원본 입력 데이터가 변경되지 않았음을 검증
    assert original_logs == mock_audit_logs