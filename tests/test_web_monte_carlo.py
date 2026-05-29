# -*- coding: utf-8 -*-
"""test_web_monte_carlo.py
Unit and E2E tests for Option C real-time lightweight Monte Carlo charting API
and dashboard CTA routing integrity.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HERE, ".."))
CORE_GATEWAY = os.path.join(ROOT_DIR, "core_gateway")

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if CORE_GATEWAY not in sys.path:
    sys.path.append(CORE_GATEWAY)

from core_gateway.main_api import app
from core_gateway.mini_roi_simulator import generate_lightweight_monte_carlo

def test_generate_lightweight_monte_carlo_function():
    """generate_lightweight_monte_carlo 헬퍼 함수가 정확하게 20개 구간의 차트 좌표를 연산해내는지 검증."""
    total_loss = 15000.0
    chart_data = generate_lightweight_monte_carlo(total_loss)
    
    assert isinstance(chart_data, list)
    assert len(chart_data) == 20
    
    for pt in chart_data:
        assert hasattr(pt, "loss")
        assert hasattr(pt, "density")
        assert isinstance(pt.loss, float)
        assert isinstance(pt.density, float)
        # 삼각분포 범위(최소 60% ~ 최대 150%) 안에 구간 손실액이 매핑되는지 단언
        assert total_loss * 0.5 <= pt.loss <= total_loss * 1.6

def test_simulate_mini_roi_api_with_chart_data():
    """FastAPI simulate_mini_roi API 엔드포인트가 Recharts용 chart_data를 정상 송출하는지 검증."""
    client = TestClient(app)
    
    # 5대 위협 요소를 모킹한 입력 페이로드 (임계치 $10,000 초과 세팅)
    payload = {
        "client_id": "ClientDashboardTest",
        "user_role": "Admin",
        "risk_factors": [
            {"activity_name": "PII Leakage", "potential_impact_score": 8.0},
            {"activity_name": "Lack of Audit Logs", "potential_impact_score": 9.0}
        ]
    }
    
    # POST API 호출
    response = client.post("/api/v1/mini-roi/simulate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # 스키마 단언
    assert "simulation_id" in data
    assert "total_estimated_loss_usd" in data
    assert "is_critical_risk" in data
    assert "report" in data
    assert "chart_data" in data
    
    # 예상 손실액 및 임계치 검증
    expected_loss = (8.0 * 1500) + (9.0 * 1500)
    assert data["total_estimated_loss_usd"] == expected_loss
    assert data["is_critical_risk"] is True
    
    # Recharts 시각화용 20개 데이터 포인트 무결성 검증
    chart_pts = data["chart_data"]
    assert isinstance(chart_pts, list)
    assert len(chart_pts) == 20
    
    # 각 포인트가 loss와 density를 정상 함유하고 있는지 검증
    first_pt = chart_pts[0]
    assert "loss" in first_pt
    assert "density" in first_pt
    assert isinstance(first_pt["loss"], (int, float))
    assert isinstance(first_pt["density"], (int, float))
