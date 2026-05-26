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

def test_autonomous_safeguard_loop():
    """✨ 시나리오 6: 자율 가드레일 및 원격 OTP 해제 - 위반 시 락다운 상태 확인 및 resume API 해제 E2E 검증"""
    # 0. 게이트웨이 글로벌 잠금 상태 리셋
    import main_api
    main_api.PLANNER_SUSPENDED = False
    
    # 1. 고의 규제 위반 실패 유발 (check_compliance -> fail 트리거)
    headers = get_auth_headers(user_id="compliance_officer", roles=["ROLE_ADMIN"])
    client.post(
        "/api/v1/check_compliance",
        headers=headers,
        json={"transaction_id": "TX_FAIL_SEQUENCE", "timestamp": 1716710400}
    )
    
    # 2. 게이트웨이 락다운(Suspended) 전격 활성화 검증
    assert main_api.PLANNER_SUSPENDED is True
    
    # 3. 플래너 allowed GET API를 통해 기동 거부 상태(False) 확인
    allowed_response = client.get("/api/v1/planner/allowed")
    assert allowed_response.status_code == 200
    assert allowed_response.json()["allowed"] is False
    
    # 4. 2FA 승인을 모사한 resume POST API 호출
    resume_response = client.post("/api/v1/planner/resume", headers=headers)
    assert resume_response.status_code == 200
    assert resume_response.json()["success"] is True
    
    # 5. 최종 플래너 잠금 정상 해제(False) 및 allowed 회복(True) 단언
    assert main_api.PLANNER_SUSPENDED is False
    allowed_recovered = client.get("/api/v1/planner/allowed")
    assert allowed_recovered.json()["allowed"] is True

def test_self_correction_rag_pipeline():
    """✨ 시나리오 7: RAG 자가 교정 연동 - 위반 감지 시 차단 원인이 decisions.md 파일 하단에 정상 자동 피딩되는지 검증"""
    import os
    import main_api
    import shutil
    
    # 0. decisions.md 파일 경로 확인 및 임시 백업 구성 (테스트 격리)
    decisions_path = os.path.join(main_api.WORKSPACE, "_company", "_shared", "decisions.md")
    backup_path = decisions_path + ".bak"
    
    # 만약 decisions.md 파일이 있다면 백업
    has_file = os.path.exists(decisions_path)
    if has_file:
        try:
            shutil.copyfile(decisions_path, backup_path)
        except Exception:
            pass
    else:
        # 파일이 없다면 디렉토리 보증 및 더미 생성
        os.makedirs(os.path.dirname(decisions_path), exist_ok=True)
        with open(decisions_path, "w", encoding="utf-8") as f:
            f.write("# Decisions Memory Dummy\n")
            
    try:
        # 1. 고의로 compliance 위반 트랙 유발 (FAILURE)
        headers = get_auth_headers(user_id="compliance_officer", roles=["ROLE_ADMIN"])
        client.post(
            "/api/v1/check_compliance",
            headers=headers,
            json={"transaction_id": "TX_FAIL_SEQUENCE", "timestamp": 1716710400}
        )
        
        # 2. decisions.md 상에 IAG 자율 규제 제어 지침이 피딩 기입되었는지 단언(assert)
        assert os.path.exists(decisions_path)
        with open(decisions_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        assert "[IAG 자율 규제 제어 지침]" in content
        assert "Invalid transaction ID pattern or corrupt timestamp sequence" in content
        
    finally:
        # 3. 사후 청소 및 백업 파일 완벽 롤백
        if has_file:
            if os.path.exists(backup_path):
                try:
                    shutil.move(backup_path, decisions_path)
                except Exception:
                    pass
        else:
            if os.path.exists(decisions_path):
                try:
                    os.remove(decisions_path)
                except Exception:
                    pass

def test_telegram_pdf_delivery():
    """✨ 시나리오 8: 실물 PDF 텔레그램 직접 전송 - 보고서 API 성공 시 send_telegram_pdf 함수가 requests를 통해 sendDocument API를 모킹 찌르는지 검증"""
    import os
    import sqlite3
    from unittest.mock import patch, MagicMock
    from main_api import DB_PATH
    
    # 0. 감사 저장소 리셋
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audit_blocks")
    conn.commit()
    conn.close()
    
    # 1. 시뮬레이션 성공 호출 (데이터 적재)
    headers = get_auth_headers(user_id="e2e_user", roles=["ROLE_USER"])
    client.post(
        "/api/v1/simulate_risk",
        headers=headers,
        json={"user_id": "e2e_user", "data_source": {"metric": 1}}
    )
    
    pdf_filename = "telegram_delivery_test.pdf"
    if os.path.exists(pdf_filename):
        try:
            os.remove(pdf_filename)
        except OSError:
            pass
            
    # 2. requests.post 모킹 통제 가드레일 설치
    with patch("requests.post") as mock_post:
        # 텔레그램 sendDocument 응답 모킹
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 12345}}
        mock_post.return_value = mock_response
        
        # 3. PDF 출력 엔드포인트 기동 (연쇄 텔레그램 직접 발송 트리거)
        response = client.post(
            "/api/v1/generate_legal_report",
            headers=headers,
            json={"filename": pdf_filename}
        )
        
        assert response.status_code == 200
        # 4. 텔레그램 sendDocument API가 최소 1회 이상 정상 호출되었음을 단언
        called_send_doc = False
        for call in mock_post.call_args_list:
            args, kwargs = call
            if args and "sendDocument" in args[0]:
                called_send_doc = True
                assert "files" in kwargs
                assert "document" in kwargs["files"]
                assert "data" in kwargs
                assert "caption" in kwargs["data"]
                
        assert called_send_doc is True
        
    # 5. 사후 클린업
    if os.path.exists(pdf_filename):
        try:
            os.remove(pdf_filename)
        except OSError:
            pass