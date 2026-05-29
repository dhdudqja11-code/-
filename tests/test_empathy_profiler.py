# -*- coding: utf-8 -*-
"""
test_empathy_profiler.py
Unit and integration tests for Phase 8 Empathy Profiler Agent and Emotional analysis engine.
"""
import os
import sys
import json
import subprocess
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HERE, ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, "_company", "_agents")

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.append(AGENTS_DIR)

from _company._agents.empathy_profiler import extract_profile_fallback, extract_profile_openai

# 1. 로컬 fallback 심리 분석 규칙 엔진 단위 테스트
def test_empathy_profiler_fallback_anxiety():
    """불안 키워드가 가득한 사연 입력 시, 불안(anxiety) 지수가 지능적으로 상승하는지 단언."""
    story = "미래가 너무 불안해요. 취업 면접과 시험 걱정 때문에 두렵고 매일 앞날 어쩌지 생각뿐입니다."
    profile = extract_profile_fallback(story)
    
    assert isinstance(profile, dict)
    assert "emotions" in profile
    assert "defense_mechanism" in profile
    assert "core_pain_point" in profile
    assert "prescription_guideline" in profile
    
    emotions = profile["emotions"]
    # 불안 수치가 유의미하게 상승했는지 단언 (기본 0.40에서 가중되어 0.85 이상)
    assert emotions["anxiety"] >= 0.80
    assert "불안" in profile["prescription_guideline"] or "관점 전환" in profile["prescription_guideline"]

def test_empathy_profiler_fallback_self_blame():
    """자책 키워드가 담긴 사연 입력 시, 자책(self_blame) 지수가 상승하고 이에 밀착한 가이드라인이 조제되는지 단언."""
    story = "내 잘못인 것 같아요. 내가 왜 이리 바보 같고 부족한지 한심하고 한심해서 매일 후회와 자책만 듭니다."
    profile = extract_profile_fallback(story)
    
    emotions = profile["emotions"]
    # 자책 수치가 유의미하게 가중되었는지 단언
    assert emotions["self_blame"] >= 0.70
    assert "자책" in profile["prescription_guideline"] or "훈계" in profile["prescription_guideline"]

# 2. 파이썬 서브프로세스 기동 E2E 테스트 (Next.js 백엔드가 실제로 호출하는 방식)
def test_empathy_profiler_process_execution():
    """python _agents/empathy_profiler.py 를 쉘상에서 직접 구동 시, 반환값이 깨끗한 JSON 스키마를 만족하는지 검증."""
    profiler_path = os.path.join(AGENTS_DIR, "empathy_profiler.py")
    test_story = "직장 상사와의 관계가 틀어져서 너무 슬프고 힘들어요. 무기력하게 번아웃 온 기분입니다."
    
    # 쿨링 가드레일 (BELOW_NORMAL) 하에서도 프로세스가 무결 구동되는지 실행
    env = os.environ.copy()
    env["PYTHONPATH"] = f".{os.pathsep}{env.get('PYTHONPATH', '')}"
    
    proc = subprocess.run(
        [sys.executable, profiler_path, test_story],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )
    
    assert proc.returncode == 0
    stdout = proc.stdout.strip()
    
    # 파싱 확인
    parsed = json.loads(stdout)
    assert "emotions" in parsed
    assert "defense_mechanism" in parsed
    
    emotions = parsed["emotions"]
    for emotion in ["anxiety", "helplessness", "self_blame", "sadness", "loneliness"]:
        assert emotion in emotions
        assert isinstance(emotions[emotion], (int, float))
        assert 0.0 <= emotions[emotion] <= 1.0
        
    assert isinstance(parsed["prescription_guideline"], str)
    assert len(parsed["prescription_guideline"]) > 10
