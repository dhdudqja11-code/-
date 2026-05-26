# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient

# 로컬 모듈 임포트
try:
    from main_api import app, AuditBlock
    from auth_service import create_access_token
except ImportError:
    from .main_api import app, AuditBlock
    from .auth_service import create_access_token

client = TestClient(app)

# ------------------- [1. 테스트용 Mock Data 및 Helper] ------------------- #
def get_auth_headers(user_id: str, roles: list) -> dict:
    """테스트용 유효 JWT 헤더 생성 헬퍼."""
    token_payload = {
        "sub": user_id,
        "roles": roles,
        "active": True
    }
    token = create_access_token(token_payload)
    return {"Authorization": f"Bearer {token}"}

# ------------------- [2. pytest 테스트 케이스 정의] ------------------- #

def test_api_unauthorized_access():
    """🛡️ 토큰 없이 요청 시 403/401 HTTP 인증 거부가 발생하는지 단언합니다."""
    response = client.post(
        "/api/v1/simulate_risk", 
        json={"user_id": "guest_user", "data_source": {"param1": 123}}
    )
    # auto_error=True이므로 Bearer 토큰이 누락되면 403 Forbidden 발생
    assert response.status_code == 403

def test_api_invalid_jwt_token():
    """🛡️ 잘못된 서명 또는 만료된 토큰 전달 시 401 Unauthorized 오류가 나는지 단언합니다."""
    headers = {"Authorization": "Bearer invalid_or_expired_jwt_token_signature"}
    response = client.post(
        "/api/v1/simulate_risk", 
        headers=headers,
        json={"user_id": "test_user", "data_source": {"param1": 123}}
    )
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]

def test_simulate_risk_success():
    """✨ 시나리오 1: 정상적인 JWT 토큰 주입으로 시뮬레이션 성공 및 AuditBlock 생성 검증"""
    headers = get_auth_headers(user_id="manager_user", roles=["ROLE_USER"])
    request_payload = {
        "user_id": "manager_user",
        "data_source": {"risk_metric_a": 10, "risk_metric_b": 20}
    }
    
    response = client.post(
        "/api/v1/simulate_risk",
        headers=headers,
        json=request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "transaction_id" in data
    assert data["audit_details"]["source_api"] == "/api/v1/simulate_risk"
    assert data["audit_details"]["initiator_user_id"] == "manager_user"
    assert data["audit_details"]["audit_payload"]["mini_roi_score"] > 0

def test_simulate_risk_validation_failure():
    """🐛 시나리오 2: 입력 데이터가 비어있을 때 SUCCESS 응답 내 FAILURE 상태의 AuditBlock 보존 검증"""
    headers = get_auth_headers(user_id="manager_user", roles=["ROLE_USER"])
    request_payload = {
        "user_id": "manager_user",
        "data_source": {}  # 빈 데이터 주입
    }
    
    response = client.post(
        "/api/v1/simulate_risk",
        headers=headers,
        json=request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILURE"
    assert "ValueError" in data["message"]
    assert data["audit_details"]["initiator_user_id"] == "manager_user"

def test_check_compliance_success():
    """✨ 시나리오 3: 정상 규제 매칭으로 컴플라이언스 성공 AuditBlock 검증"""
    headers = get_auth_headers(user_id="compliance_officer", roles=["ROLE_ADMIN"])
    request_payload = {
        "transaction_id": "TX_99988",
        "timestamp": 1716710400
    }
    
    response = client.post(
        "/api/v1/check_compliance",
        headers=headers,
        json=request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["audit_details"]["audit_payload"]["compliance_status"] == "COMPLIANT"

def test_check_compliance_failure():
    """🐛 시나리오 4: 특정 위반 패턴 유발 시 SUCCESS 응답 내 FAILURE 감사 로그 보존 검증"""
    headers = get_auth_headers(user_id="compliance_officer", roles=["ROLE_ADMIN"])
    request_payload = {
        "transaction_id": "TX_FAIL_SEQUENCE",  # fail 트리거 패턴
        "timestamp": 1716710400
    }
    
    response = client.post(
        "/api/v1/check_compliance",
        headers=headers,
        json=request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILURE"
    assert "ValueError" in data["message"]
    assert "Invalid transaction ID pattern" in data["message"]

def test_e2e_gateway_to_pdf_generation_pipeline():
    """✨ 시나리오 5: E2E 파이프라인 연동 - 트랜잭션 호출 후 감사 로그를 PDF 보고서로 자동 출력하는 통합 흐름 검증"""
    import os
    import sqlite3
    from main_api import DB_PATH
    
    # 0. 감사 저장소 리셋 (SQLite3 DB 비우기)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audit_blocks")
    conn.commit()
    conn.close()
    
    # 1. 시뮬레이션 성공 호출 (1건 적재)
    headers = get_auth_headers(user_id="e2e_user", roles=["ROLE_USER"])
    client.post(
        "/api/v1/simulate_risk",
        headers=headers,
        json={"user_id": "e2e_user", "data_source": {"metric": 1}}
    )
    
    # 2. 컴플라이언스 실패 호출 (1건 적재)
    client.post(
        "/api/v1/check_compliance",
        headers=headers,
        json={"transaction_id": "TX_FAIL_E2E", "timestamp": 12345}
    )
    
    # 3. PDF 출력 엔드포인트 기동
    pdf_filename = "e2e_pipeline_report.pdf"
    
    # 만약 기존 파일이 있다면 정리
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
        
    response = client.post(
        "/api/v1/generate_legal_report",
        headers=headers,
        json={"filename": pdf_filename}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mapped_records_count"] == 2
    assert "e2e_pipeline_report.pdf" in data["pdf_path"]
    
    # 4. 물리 디스크 파일 생성 여부 단언 및 뒤처리
    assert os.path.exists(pdf_filename)
    try:
        os.remove(pdf_filename)
    except OSError:
        pass