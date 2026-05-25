# -*- coding: utf-8 -*-
import os, sys, shutil, time
import unittest.mock as mock
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")

sys.path.append(SHARED_DIR)

import decision_compressor
import feedback_feeder

@pytest.fixture(autouse=True)
def setup_decisions_sandboxing():
    """테스트 기동 동안 decisions.md의 원본을 임시 백업 및 격리 보호하는 피스처입니다."""
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    decisions_bak = os.path.join(SHARED_DIR, "decisions.md.test_diet_bak")
    decisions_existed = os.path.exists(decisions_orig)

    if decisions_existed:
        shutil.copy2(decisions_orig, decisions_bak)
        
    # 테스트용 임시 decisions.md 파일 빌드
    test_skeleton = """# 📌 회사 핵심 의사결정 로그 (테스트용)

## 1. 비즈니스 모델 및 전략 방향
* **전략**: 고성능 PC 하드웨어 최적화

## 2. 디자인 및 UX
* **UX**: 11초대 병렬 텔레그램 조종반 완수
"""
    with open(decisions_orig, "w", encoding="utf-8") as f:
        f.write(test_skeleton)

    yield

    # 원복 처리
    if decisions_existed:
        if os.path.exists(decisions_bak):
            shutil.copy2(decisions_bak, decisions_orig)
            os.remove(decisions_bak)
    else:
        if os.path.exists(decisions_orig):
            os.remove(decisions_orig)

def test_decision_compressor_skipped_below_threshold():
    """임계 용량(KB) 미만인 경우 압축이 생략되는지 검증합니다."""
    # force=False로 기동
    res = decision_compressor.run_diet_compression(force=False, threshold_kb=10)
    assert res["status"] == "skipped"
    assert "임계값" in res["message"]

def test_decision_compressor_rule_based_fallback():
    """로컬 AI 미기동 상황 시, 중복 문장 필터링 및 최신 지침 추출 룰셋 Fallback이 완벽히 가동되는지 검증합니다."""
    decisions_path = os.path.join(SHARED_DIR, "decisions.md")
    
    # 10줄 이상의 다량의 중복 피드백을 주입하여 강제로 용량 확보 가정을 만듭니다.
    spam_logs = "\n".join([
        f"## [2026-05-25] 세션 로그 {i}\n- 중복지침: 동일한 톤앤매너를 유지한다\n- 지침 {i}: 핵심 변수를 철저히 검증한다"
        for i in range(5)
    ])
    
    with open(decisions_path, "a", encoding="utf-8") as f:
        f.write("\n\n" + spam_logs)
        
    # llm_adapter.generate_text가 offline fallback mockup을 반환하도록 패치
    with mock.patch("llm_adapter.generate_text", return_value="연봉 3배 올리는 법: 로컬 가상 Mock"):
        # force=True로 기동하여 압축 실행 유도
        res = decision_compressor.run_diet_compression(force=True, threshold_kb=1)
        
        assert res["status"] == "success"
        assert res["method"] == "Deterministic Rule-based Fallback"
        assert res["reduction_percentage"] > 0.0
        
        # 파일 내용을 다시 읽어 뼈대는 유지되고 지침이 압축되었는지 확인
        with open(decisions_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "비즈니스 모델" in content
        assert "11초대 병렬 텔레그램" in content
        # 중복 문장 필터링 결과 확인
        assert "동일한 톤앤매너" in content

def test_decision_compressor_ai_online():
    """로컬 AI 온라인 상황 시, llm_adapter가 생성한 지능형 요약 텍스트가 정상 반영되는지 검증합니다."""
    decisions_path = os.path.join(SHARED_DIR, "decisions.md")
    
    spam_logs = "\n".join([
        f"## [2026-05-25] 세션 로그 {i}\n- 지침: 디자인 시 8pt 그리드 채택"
        for i in range(5)
    ])
    with open(decisions_path, "a", encoding="utf-8") as f:
        f.write("\n\n" + spam_logs)
        
    mock_ai_output = "- 로컬 GPU 연동 최적화 지침을 단일화하여 적용한다.\n- 8pt 디자인 컴포넌트 구조를 영구 수호한다."
    
    with mock.patch("llm_adapter.generate_text", return_value=mock_ai_output):
        res = decision_compressor.run_diet_compression(force=True, threshold_kb=0)
        
        assert res["status"] == "success"
        assert res["method"] == "Local AI (GPU/SLM)"
        
        with open(decisions_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "비즈니스 모델" in content
        assert "8pt 디자인 컴포넌트" in content
        assert "로컬 GPU 연동 최적화" in content

def test_feeder_triggers_compressor_subprocess():
    """feedback_feeder.py로 피드백 주입 시, 백그라운드 압축기(subprocess.Popen)가 예외 없이 호출되는지 검증합니다."""
    
    with mock.patch("subprocess.Popen") as mock_popen:
        res = feedback_feeder.feed_feedback("테스트 피드백 지시사항")
        
        assert res["status"] == "success"
        # 백그라운드 스폰 호출이 안전하게 감지되었는지 단언
        mock_popen.assert_called_once()
        
        called_args = mock_popen.call_args[0][0]
        called_kwargs = mock_popen.call_args[1]
        
        assert "decision_compressor.py" in called_args[1]
        if sys.platform == "win32":
            assert "creationflags" in called_kwargs
            assert called_kwargs["creationflags"] == 0x00004000
