# -*- coding: utf-8 -*-
import os, sys, shutil, json
import unittest.mock as mock
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")

# 신규 패키징된 에이전트 스킬의 scripts 폴더를 sys.path에 포팅
SKILL_SCRIPTS_DIR = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "..", "config", "plugins", "science", "skills", "single_person_business_orchestrator", "scripts"
))

# 로컬 테스트용 폴백 경로 확보
if not os.path.exists(SKILL_SCRIPTS_DIR):
    # GEMINI APP DATA 내에 경로가 생성될 것이므로 GEMINI APP DATA 경로를 추적함
    # App Data Directory: C:\Users\user\.gemini\antigravity-ide
    SKILL_SCRIPTS_DIR = r"C:\Users\user\.gemini\config\plugins\science\skills\single_person_business_orchestrator\scripts"

sys.path.append(SKILL_SCRIPTS_DIR)
sys.path.append(SHARED_DIR)

import orchestrate

@pytest.fixture(autouse=True)
def setup_decisions_sandboxing():
    """테스트 기동 동안 decisions.md의 원본을 임시 백업 및 격리 보호하는 피스처입니다."""
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    decisions_bak = os.path.join(SHARED_DIR, "decisions.md.test_skill_bak")
    decisions_existed = os.path.exists(decisions_orig)

    if decisions_existed:
        shutil.copy2(decisions_orig, decisions_bak)

    yield

    # 원복 처리
    if decisions_existed:
        if os.path.exists(decisions_bak):
            shutil.copy2(decisions_bak, decisions_orig)
            os.remove(decisions_bak)
    else:
        if os.path.exists(decisions_orig):
            os.remove(decisions_orig)

def test_ensure_decisions_provisioning_self_healing():
    """decisions.md가 유실되었을 때, 템플릿 파일로부터 무중단 자가 복원 프로비저닝이 작동하는지 검증합니다."""
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    if os.path.exists(decisions_orig):
        os.remove(decisions_orig)
        
    orchestrate.ensure_decisions_provisioning()
    
    assert os.path.exists(decisions_orig)
    with open(decisions_orig, "r", encoding="utf-8") as f:
        content = f.read()
    assert "비즈니스 모델" in content
    assert "디자인 및 UX" in content

def test_skill_orchestrate_run_subcommand():
    """run 명령 실행 시 Windows 환경에서 BELOW_NORMAL_PRIORITY_CLASS(0x00004000) 쿨링 플래그가 전역 기동되는지 검증합니다."""
    
    mock_proc = mock.Mock()
    mock_proc.returncode = 0
    mock_proc.stdout = "🎉 [성공] 마케팅 캠페인이 안전하게 완료되었습니다.\n[결과 JSON]\n{\n  \"elapsed_seconds\": 11.19\n}"
    mock_proc.stderr = ""

    # argparse 인자 mock 구성
    class Args:
        keyword = "인공지능 챗봇"
        
    with mock.patch("subprocess.run", return_value=mock_proc) as mock_run:
        with mock.patch("sys.platform", "win32"):
            orchestrate.cmd_run(Args())
            
            mock_run.assert_called_once()
            called_args = mock_run.call_args[0][0]
            called_kwargs = mock_run.call_args[1]
            
            assert "campaign_orchestrator.py" in called_args[1]
            assert "--keyword" in called_args
            assert "인공지능 챗봇" in called_args
            
            assert "creationflags" in called_kwargs
            assert called_kwargs["creationflags"] == 0x00004000

def test_skill_orchestrate_compress_subcommand():
    """compress 명령 실행 시 다이어트 압축기가 쿨링 가드레일 하에서 강제 구동되는지 검증합니다."""
    
    mock_proc = mock.Mock()
    mock_proc.returncode = 0
    mock_proc.stdout = "📡 RAG 메모리 압축 완료: 96.8% 다이어트 성공!"
    mock_proc.stderr = ""

    class Args:
        force = True
        
    with mock.patch("subprocess.run", return_value=mock_proc) as mock_run:
        with mock.patch("sys.platform", "win32"):
            orchestrate.cmd_compress(Args())
            
            mock_run.assert_called_once()
            called_args = mock_run.call_args[0][0]
            called_kwargs = mock_run.call_args[1]
            
            assert "decision_compressor.py" in called_args[1]
            assert "--force" in called_args
            
            assert "creationflags" in called_kwargs
            assert called_kwargs["creationflags"] == 0x00004000

def test_skill_orchestrate_status_subcommand(capsys):
    """status 명령 실행 시 DB 성과와 플래너 상태 정보가 안전한 마크다운 리포트로 인쇄되는지 검증합니다."""
    
    # planner_state.json 테스트용 모킹
    planner_state_file = os.path.join(orchestrate.WORKSPACE_ROOT, "_company", "_agents", "youtube", "tools", "planner_state.json")
    planner_existed = os.path.exists(planner_state_file)
    planner_bak = os.path.join(orchestrate.WORKSPACE_ROOT, "_company", "_agents", "youtube", "tools", "planner_state.json.skill_test_bak")
    
    if planner_existed:
        shutil.copy2(planner_state_file, planner_bak)
        
    mock_state = {
        "status": "RUNNING",
        "loop_count": 42,
        "elapsed_hours": 12.5,
        "last_run_time": "2026-05-25 22:00:00",
        "next_run_time": "2026-05-26 04:00:00"
    }
    
    with open(planner_state_file, "w", encoding="utf-8") as f:
        json.dump(mock_state, f)

    try:
        # database 모듈 성과 조회 모킹
        mock_summary = {
            "naver_views": 1500,
            "naver_likes": 120,
            "insta_views": 8500,
            "insta_likes": 420,
            "best_performer": {
                "platform": "insta",
                "title": "인터넷 선 뽑고 만든 로컬 AI 1인 기업 실체",
                "views": 5000,
                "likes": 300
            }
        }
        
        with mock.patch("database.get_performance_summary", return_value=mock_summary):
            orchestrate.cmd_status(None)
            
            captured = capsys.readouterr()
            assert "1인 AI 기업 자율 마케팅 성과" in captured.out
            assert "누적 채널 성과 및 트래픽 요약" in captured.out
            assert "네이버 블로그 누적" in captured.out
            assert "인스타 Reels 누적" in captured.out
            assert "인터넷 선 뽑고 만든 로컬 AI" in captured.out
            assert "오토 플래너 24시간 자율 가동 현황" in captured.out
            assert "42회차 완료" in captured.out
            assert "12.5시간" in captured.out
            
    finally:
        # planner_state 원복
        if planner_existed:
            if os.path.exists(planner_bak):
                shutil.copy2(planner_bak, planner_state_file)
                os.remove(planner_bak)
        else:
            if os.path.exists(planner_state_file):
                os.remove(planner_state_file)
