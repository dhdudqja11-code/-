# -*- coding: utf-8 -*-
import os, sys, shutil, json
import unittest.mock as mock
import pytest
import requests

# 테스트 대상 경로 주입
HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")
sys.path.append(SHARED_DIR)

import llm_adapter

@pytest.fixture(autouse=True)
def setup_decisions_backup(tmp_path):
    """테스트 기동 중 decisions.md의 원본을 임시 백업 및 격리 보호하는 피처입니다."""
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    decisions_bak = os.path.join(SHARED_DIR, "decisions.md.llm_bak")
    decisions_existed = os.path.exists(decisions_orig)

    if decisions_existed:
        shutil.copy2(decisions_orig, decisions_bak)
        with open(decisions_orig, "w", encoding="utf-8") as f:
            f.write("# 📌 테스트용 임시 공용 의사결정 로그\n- 지시사항: 썸네일 카피를 더 직관적으로 뽑아라\n")

    yield

    if decisions_existed:
        if os.path.exists(decisions_bak):
            shutil.copy2(decisions_bak, decisions_orig)
            os.remove(decisions_bak)
    else:
        if os.path.exists(decisions_orig):
            os.remove(decisions_orig)

def test_ollama_successful_gpu_inference():
    """로컬 Ollama 서비스가 정상 작동할 때, 지표 지향형 GPU 추론 응답을 성공적으로 파싱하는지 검증합니다."""
    
    # 가상 Ollama JSON 응답 모사
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "로컬 GPU 가속을 활용한 성공적인 한글 IT 칼럼입니다."}

    with mock.patch("requests.post", return_value=mock_resp) as mock_post:
        res = llm_adapter.generate_text(
            prompt="블로그 IT 칼럼 기획안 작성",
            system_instruction="전문 에반젤리스트 페르소나",
            model="llama3"
        )
        
        # 호출 무결성 및 인자 매핑 검증
        mock_post.assert_called_once()
        assert "로컬 GPU 가속" in res
        
        # RAG 의사결정 로그가 프롬프트 내부에 안전하게 함께 기입되었는지 payload 검증
        called_args = mock_post.call_args[1]
        assert called_args["json"]["model"] == "llama3"
        assert "썸네일 카피" in called_args["json"]["prompt"]

def test_ollama_fallback_robustness():
    """로컬 Ollama 데몬이 꺼져 있거나 연결 장애가 발생할 때, 유료 API 비용을 부과하지 않고 즉각 고품질 한글 로컬 Fallback 모드를 구동하는지 검증합니다."""
    
    # ConnectionError 던지도록 모킹하여 장애 모사
    with mock.patch("requests.post", side_effect=requests.exceptions.ConnectionError()):
        # 1. 네이버 블로그 맥락 검증
        res_blog = llm_adapter.generate_text(
            prompt="네이버 블로그 IT 에반젤리스트 칼럼 기획",
            system_instruction="B2B 전략가",
            model="llama3"
        )
        assert "GPU" in res_blog or "로컬" in res_blog
        assert "연봉" in res_blog or "Expected Loss" in res_blog

        # 2. 인스타 Reels 대본 맥락 검증
        res_reels = llm_adapter.generate_text(
            prompt="인스타그램 Reels 숏폼 비디오 시나리오 대본",
            system_instruction="인플루언서 마케터",
            model="llama3"
        )
        assert "Reels" in res_reels or "릴스" in res_reels
        assert "음성 및 오디오" in res_reels or "비주얼" in res_reels
