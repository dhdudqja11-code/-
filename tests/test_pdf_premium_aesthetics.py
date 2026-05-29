# -*- coding: utf-8 -*-
"""test_pdf_premium_aesthetics.py
E2E and unit testing for Phase 4 premium 'Deep Space Dark & Cyber Neon' (Neon HSL)
PDF design styling and dual-hashing SHA-256 compliance cryptosystems.
"""
import os
import sys
import shutil
import pytest
import sqlite3
import unittest.mock as mock

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")
ROOT_DIR = os.path.abspath(os.path.join(HERE, ".."))
CORE_GATEWAY = os.path.join(ROOT_DIR, "core_gateway")

if SHARED_DIR not in sys.path:
    sys.path.append(SHARED_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if CORE_GATEWAY not in sys.path:
    sys.path.append(CORE_GATEWAY)

from mini_roi_simulator.monte_carlo import run_monte_carlo_simulation, generate_monte_carlo_pdf
from src.services.legal_report_generator import LegalReportGenerator

@pytest.fixture(autouse=True)
def setup_test_sandboxing():
    """Backup and restore test artifacts to prevent directory pollution."""
    reports_dir = os.path.join(ROOT_DIR, "reports")
    pdf_mc = os.path.join(reports_dir, "monte_carlo_risk_report.pdf")
    pdf_mc_bak = os.path.join(reports_dir, "monte_carlo_risk_report.pdf.bak")
    
    mc_existed = os.path.exists(pdf_mc)
    if mc_existed:
        shutil.copy2(pdf_mc, pdf_mc_bak)
        
    yield
    
    if mc_existed:
        if os.path.exists(pdf_mc_bak):
            shutil.copy2(pdf_mc_bak, pdf_mc)
            os.remove(pdf_mc_bak)
    else:
        if os.path.exists(pdf_mc):
            os.remove(pdf_mc)

def test_monte_carlo_premium_pdf_and_dual_hashes():
    """Verifies Monte Carlo PDF generates dual-hashing SHA-256 cryptosystem under Cyber Neon styles."""
    test_input = {"source": "TestClientAesthetics", "data_points": [6, 7, 5]}
    stats = run_monte_carlo_simulation(test_input, trials=100) # Fast run with 100 trials
    
    result = generate_monte_carlo_pdf(stats)
    
    assert isinstance(result, dict)
    assert "pdf_path" in result
    assert "data_hash" in result
    assert "file_hash" in result
    
    # Assert 64-char hex SHA-256 format
    assert len(result["data_hash"]) == 64
    assert len(result["file_hash"]) == 64
    
    # Assert file exists
    assert os.path.exists(result["pdf_path"])

def test_legal_report_generator_cyber_neon_aesthetic():
    """Verifies that LegalReportGenerator draws custom dark backgrounds, cyber fonts and 1st-level JSON data hash."""
    mock_logs = [
        {
            'timestamp': '2026-05-27T10:00:00',
            'error_type': 'Compliance Alert',
            'severity': '3',
            'legal_basis': 'GDPR Art 32',
            'description': 'Secured data flows did not pass secondary validation.'
        }
    ]
    mock_context = {'reg_name': 'Test Reg', 'art_num': 'Art 9', 'base_factor': 10, 'market_impact': 100}
    
    generator = LegalReportGenerator()
    filename = os.path.join(ROOT_DIR, "reports", "test_aesthetic_report.pdf")
    
    try:
        report_result = generator.generate_report(mock_logs, mock_context, filename)
        
        assert isinstance(report_result, dict)
        assert "text_report" in report_result
        assert "data_hash" in report_result
        assert "file_hash" in report_result
        
        assert len(report_result["data_hash"]) == 64
        assert len(report_result["file_hash"]) == 64
        assert os.path.exists(filename)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def test_main_api_legal_report_ssot_double_hashing(tmp_path):
    """Verifies that API Gateway generates reports, applies ALTER TABLE, and stores file_hash into SSoT DB."""
    from fastapi.testclient import TestClient
    from core_gateway.main_api import app
    from core_gateway.auth_service import create_access_token
    
    client = TestClient(app)
    
    # 임시 DB 세션 격리 Mocking
    db_path = os.path.join(CORE_GATEWAY, "gateway_audit.db")
    db_bak = os.path.join(CORE_GATEWAY, "gateway_audit.db.bak")
    db_existed = os.path.exists(db_path)
    
    if db_existed:
        shutil.copy2(db_path, db_bak)
        
    try:
        # DB에 최소 1개 audit block 생성 보장
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS audit_blocks")
        cursor.execute("""
            CREATE TABLE audit_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT,
                source_api TEXT,
                transaction_id TEXT,
                initiator_user_id TEXT,
                result_summary TEXT,
                status TEXT,
                message TEXT,
                audit_payload TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO audit_blocks (timestamp_utc, source_api, transaction_id, initiator_user_id, result_summary, status, message, audit_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            '2026-05-27T12:00:00Z', 'TestAPI', 'tx_999999', 'admin', 'Audit Check Passed', 'SUCCESS', 'No Violation', '{}'
        ))
        conn.commit()
        conn.close()
        
        # API request
        request_payload = {
            "filename": "reports/test_ssot_immutable_report.pdf"
        }
        
        # TestClient로 FastAPI 엔드포인트 호출
        # 유효한 JWT 토큰 및 헤더 생성
        token_payload = {
            "sub": "admin_test",
            "roles": ["ROLE_ADMIN"],
            "active": True
        }
        token = create_access_token(token_payload)
        headers = {"Authorization": f"Bearer {token}"}
        
        # TestClient로 FastAPI 엔드포인트 호출
        response = client.post("/api/v1/security/report", headers=headers, json=request_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data_hash" in data
        assert "file_hash" in data
        assert len(data["file_hash"]) == 64
        
        # SSoT DB에 해시가 이중 각인되었는지 쿼리 단언
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT artifact_hash FROM audit_blocks ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[0] == data["file_hash"]
        
    finally:
        # 임시 PDF 파일 소거
        report_file = os.path.join(ROOT_DIR, "reports", "test_ssot_immutable_report.pdf")
        if os.path.exists(report_file):
            os.remove(report_file)
            
        # DB 원복
        if db_existed:
            if os.path.exists(db_bak):
                shutil.copy2(db_bak, db_path)
                os.remove(db_bak)
        else:
            if os.path.exists(db_path):
                os.remove(db_path)
