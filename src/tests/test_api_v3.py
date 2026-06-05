import pytest
from fastapi.testclient import TestClient
from src.api.authority_api import app

client = TestClient(app)

def test_v3_default_compliant():
    """기본적인 정상 컴플라이언스 시나리오 검증."""
    payload = {
        "regulatory_cases": [
            {
                "article_id": "GDPR-17",
                "violation_type": "데이터 삭제 요청 미처리",
                "risk_category": "법률",
                "severity_score": 0.2,
                "estimated_financial_loss": 5000.0
            }
        ],
        "financial_params": {"revenue": 10000000}
    }
    response = client.post("/api/v1/check_authority", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # 스키마 키 확인
    assert "status" in data
    assert "timestamp" in data
    assert "overall_compliance_score" in data
    assert "risk_metrics" in data
    assert "summary_report" in data
    
    # COMPLIANT 상태 확인
    assert data["status"] == "COMPLIANT"
    assert data["overall_compliance_score"] > 0.8
    assert data["risk_metrics"]["ai_bias_status"]["is_biased"] is False
    assert data["risk_metrics"]["sovereignty_status"]["conflict_detected"] is False
    assert data["risk_metrics"]["esg_risk_status"]["is_compliant"] is True

def test_v3_ai_bias_warning():
    """AI Bias 리스크 유입에 따른 WARNING 상태 변환 검증."""
    payload = {
        "regulatory_cases": [],
        "financial_params": {},
        "ai_bias_input": {
            "is_biased": True,
            "data_provenance_trace": "TR-9999",
            "highest_risk_group": "Underrepresented minorities",
            "bias_score": 0.65,
            "compliance_evidence": "Bias_Audit_Reference"
        }
    }
    response = client.post("/api/v1/check_authority", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "WARNING"
    assert data["risk_metrics"]["ai_bias_status"]["is_biased"] is True
    assert data["risk_metrics"]["ai_bias_status"]["bias_score"] == 0.65
    assert "[AI Bias] AI 데이터 편향(점수: 0.65)" in "".join(data["summary_report"]["mitigation_plan"])

def test_v3_sovereignty_warning():
    """데이터 주권 충돌(Sovereignty Conflict) 발생에 따른 WARNING 상태 검증."""
    payload = {
        "regulatory_cases": [],
        "financial_params": {},
        "sovereignty_input": {
            "is_compliant": False,
            "conflict_detected": True,
            "conflicting_jurisdictions": ["China PIPL", "EU GDPR"],
            "data_flow_path_used": "Anon_Gateway_Singapore",
            "legal_proof_attached": True
        }
    }
    response = client.post("/api/v1/check_authority", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "WARNING"
    assert data["risk_metrics"]["sovereignty_status"]["conflict_detected"] is True
    assert "China PIPL, EU GDPR 법규 상충 감지" in "".join(data["summary_report"]["mitigation_plan"])

def test_v3_esg_high_impact_non_compliant():
    """ESG 재무 영향이 $1,000,000 이상일 때 강제 NON_COMPLIANT 처리되는지 검증."""
    payload = {
        "regulatory_cases": [],
        "financial_params": {},
        "esg_input": {
            "is_compliant": False,
            "primary_violation": "Carbon Emission Exceedance",
            "cso_score": 55,
            "mitigation_plan_verified": False,
            "estimated_financial_impact_usd": 1200000.0 # $1,000,000 이상
        }
    }
    response = client.post("/api/v1/check_authority", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # ESG 리스크로 인한 강제 NON_COMPLIANT 상태 및 감점 검증
    assert data["status"] == "NON_COMPLIANT"
    assert data["overall_compliance_score"] < 1.0
    assert data["risk_metrics"]["esg_risk_status"]["estimated_financial_impact_usd"] == 1200000.0

def test_v3_dummy_endpoint():
    """더미 테스트 엔드포인트(/test/dummy-request) 응답 확인."""
    response = client.post("/test/dummy-request")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["risk_metrics"]["esg_risk_status"]["estimated_financial_impact_usd"] == 1200000.0
