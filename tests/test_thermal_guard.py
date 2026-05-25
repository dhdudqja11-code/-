# -*- coding: utf-8 -*-
import os, sys, shutil
import unittest.mock as mock
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")
YOUTUBE_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "youtube", "tools")

sys.path.append(SHARED_DIR)
sys.path.append(YOUTUBE_TOOLS)

import campaign_orchestrator

@pytest.fixture(autouse=True)
def setup_test_sandboxing(tmp_path):
    """테스트 기동 동안 decisions.md의 원본을 임시 백업 및 격리 보호하는 피처입니다."""
    # decisions.md 격리
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    decisions_bak = os.path.join(SHARED_DIR, "decisions.md.test_bak")
    decisions_existed = os.path.exists(decisions_orig)

    if decisions_existed:
        shutil.copy2(decisions_orig, decisions_bak)
        with open(decisions_orig, "w", encoding="utf-8") as f:
            f.write("# 📌 테스트용 임시 공용 의사결정 로그\n")

    yield

    if decisions_existed:
        if os.path.exists(decisions_bak):
            shutil.copy2(decisions_bak, decisions_orig)
            os.remove(decisions_bak)
    else:
        if os.path.exists(decisions_orig):
            os.remove(decisions_orig)

def test_win_cooling_creation_flag_injection():
    """Windows 환경 하에서 서브프로세스 툴 가동 시 BELOW_NORMAL_PRIORITY_CLASS(0x00004000) 플래그가 주입되는지 검증합니다."""
    
    mock_proc = mock.Mock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Success"
    mock_proc.stderr = ""

    with mock.patch("subprocess.run", return_value=mock_proc) as mock_run:
        # sys.platform을 강제로 win32로 모킹!
        with mock.patch("sys.platform", "win32"):
            campaign_orchestrator.run_tool(script_path="fake_script.py", args=["--test"])
            
            # subprocess.run 호출 여부 단언
            mock_run.assert_called_once()
            
            # 주입된 키워드 인자 획득
            called_kwargs = mock_run.call_args[1]
            assert "creationflags" in called_kwargs
            assert called_kwargs["creationflags"] == 0x00004000 # BELOW_NORMAL_PRIORITY_CLASS

def test_non_win_cooling_safeguard():
    """Linux / macOS 등 비 Windows 환경에서는 creationflags 인자가 누락되어 에러가 나지 않는지 하위 호환성을 검증합니다."""
    
    mock_proc = mock.Mock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Success"
    mock_proc.stderr = ""

    with mock.patch("subprocess.run", return_value=mock_proc) as mock_run:
        # sys.platform을 linux로 모킹!
        with mock.patch("sys.platform", "linux"):
            campaign_orchestrator.run_tool(script_path="fake_script.py", args=["--test"])
            
            mock_run.assert_called_once()
            
            # creationflags 인자가 없음을 단언
            called_kwargs = mock_run.call_args[1]
            assert "creationflags" not in called_kwargs


def test_auto_planner_cooling_creation_flag_injection():
    """auto_planner.py 기동 시 Windows 환경인 경우 BELOW_NORMAL_PRIORITY_CLASS(0x00004000) 플래그가 주입되는지 검증합니다."""
    # 동적 로딩하여 sys.path 무결성 매핑
    import auto_planner
    
    mock_proc = mock.Mock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Success"
    mock_proc.stderr = ""

    with mock.patch("subprocess.run", return_value=mock_proc) as mock_run:
        # sys.platform을 win32로 모킹
        with mock.patch("sys.platform", "win32"):
            mock_cfg = {"INTERVAL_HOURS": 1, "TOTAL_RUN_HOURS": 0.00001}
            with mock.patch("auto_planner.load_config", return_value=mock_cfg):
                with mock.patch("sys.exit") as mock_exit:
                    with mock.patch("time.sleep"):
                        try:
                            auto_planner.main()
                        except Exception:
                            pass
                        
                        assert mock_run.call_count >= 1
                        for call in mock_run.call_args_list:
                            called_kwargs = call[1]
                            assert "creationflags" in called_kwargs
                            assert called_kwargs["creationflags"] == 0x00004000

