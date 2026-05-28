# -*- coding: utf-8 -*-
"""test_auto_planner_cooling.py
E2E and unit testing for new Phase 3 auto_planner.py improvements, including
ctypes Windows kernel priority scaling, Monte Carlo risk evaluation integrations,
and hybrid multi-threshold safeguards.
"""
import os
import sys
import shutil
import pytest
import unittest.mock as mock

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")
YOUTUBE_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "youtube", "tools")

if SHARED_DIR not in sys.path:
    sys.path.append(SHARED_DIR)
if YOUTUBE_TOOLS not in sys.path:
    sys.path.append(YOUTUBE_TOOLS)

import auto_planner

@pytest.fixture(autouse=True)
def setup_test_sandboxing():
    """Isolates the environment to prevent breaking decisions.md or planner state."""
    state_path = os.path.join(YOUTUBE_TOOLS, "planner_state.json")
    state_bak = os.path.join(YOUTUBE_TOOLS, "planner_state.json.bak")
    state_existed = os.path.exists(state_path)
    if state_existed:
        shutil.copy2(state_path, state_bak)
        
    yield
    
    if state_existed:
        if os.path.exists(state_bak):
            shutil.copy2(state_bak, state_path)
            os.remove(state_bak)
    else:
        if os.path.exists(state_path):
            os.remove(state_path)

def test_auto_planner_ctypes_cooling():
    """Verifies that auto_planner calls ctypes.windll.kernel32.SetPriorityClass on Windows."""
    mock_cfg = {"INTERVAL_HOURS": 1, "TOTAL_RUN_HOURS": 0.00001}
    
    with mock.patch("auto_planner.load_config", return_value=mock_cfg), \
         mock.patch("sys.platform", "win32"), \
         mock.patch("sys.exit"), \
         mock.patch("time.sleep"), \
         mock.patch("subprocess.run") as mock_run:
         
        import ctypes
        mock_get_proc = mock.Mock(return_value=999)
        mock_set_priority = mock.Mock()
        
        with mock.patch.object(ctypes, "windll", create=True) as mock_windll:
            mock_windll.kernel32.GetCurrentProcess = mock_get_proc
            mock_windll.kernel32.SetPriorityClass = mock_set_priority
            
            try:
                auto_planner.main()
            except Exception:
                pass
                
            mock_get_proc.assert_called_once()
            mock_set_priority.assert_called_once_with(999, 0x00004000)

def test_auto_planner_monte_carlo_low_risk():
    """Verifies that the planner runs with standard intervals when Monte Carlo risk is low (<= 20%)."""
    mock_cfg = {"INTERVAL_HOURS": 4, "TOTAL_RUN_HOURS": 0.00001}
    
    with mock.patch("auto_planner.load_config", return_value=mock_cfg), \
         mock.patch("auto_planner.get_current_bankruptcy_risk", return_value=12.5), \
         mock.patch("sys.exit"), \
         mock.patch("subprocess.run") as mock_run, \
         mock.patch("time.sleep") as mock_sleep:
         
        try:
            auto_planner.main()
        except Exception:
            pass
            
        # Standard interval sleep should be called
        # standard: 4.0 hours * 3600 seconds = 14400 seconds
        mock_sleep.assert_called_with(4.0 * 3600)

def test_auto_planner_monte_carlo_warn_risk():
    """Verifies that the planner doubles the execution interval when Monte Carlo risk is warm (> 20%)."""
    mock_cfg = {"INTERVAL_HOURS": 3, "TOTAL_RUN_HOURS": 0.00001}
    
    with mock.patch("auto_planner.load_config", return_value=mock_cfg), \
         mock.patch("auto_planner.get_current_bankruptcy_risk", return_value=35.0), \
         mock.patch("sys.exit"), \
         mock.patch("subprocess.run") as mock_run, \
         mock.patch("time.sleep") as mock_sleep:
         
        try:
            auto_planner.main()
        except Exception:
            pass
            
        # The execution interval must be doubled: 3 * 2 = 6 hours (21600 seconds)
        mock_sleep.assert_called_with(6.0 * 3600)

def test_auto_planner_monte_carlo_lockdown_risk():
    """Verifies that the planner triggers 2FA lockdown (PAUSED_RISK) when Monte Carlo risk exceeds 50%."""
    mock_cfg = {"INTERVAL_HOURS": 6, "TOTAL_RUN_HOURS": 0.00001}
    
    # We will simulate a suspension loop that breaks immediately on next check
    # to avoid infinite loops during unit tests.
    side_effects = [75.0, 10.0] # starts high, then goes down to unlock
    
    # We will mock the API calls
    mock_allowed_resp = mock.Mock()
    mock_allowed_resp.status_code = 200
    mock_allowed_resp.json.return_value = {"allowed": True}
    
    with mock.patch("auto_planner.load_config", return_value=mock_cfg), \
         mock.patch("auto_planner.get_current_bankruptcy_risk", side_effect=side_effects), \
         mock.patch("requests.get", return_value=mock_allowed_resp), \
         mock.patch("auto_planner.push_telegram_alert") as mock_alert, \
         mock.patch("sys.exit"), \
         mock.patch("subprocess.run") as mock_run, \
         mock.patch("time.sleep") as mock_sleep:
         
        try:
            auto_planner.main()
        except Exception:
            pass
            
        # A lockdown alert should have been sent to Telegram
        mock_alert.assert_called_once()
        assert "파산 리스크" in mock_alert.call_args[0][0]
        assert "PAUSED_RISK" in mock_alert.call_args[0][0] or "일시정지" in mock_alert.call_args[0][0]
        
        # State file check
        state_path = os.path.join(YOUTUBE_TOOLS, "planner_state.json")
        assert os.path.exists(state_path)
