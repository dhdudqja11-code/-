# -*- coding: utf-8 -*-
import os, sys, time, shutil
import unittest.mock as mock
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")
sys.path.append(SHARED_DIR)

import campaign_orchestrator
import database

@pytest.fixture(autouse=True)
def setup_test_sandboxing(tmp_path):
    """실제 database와 decisions.md 파일 경로를 임시 폴더로 안전 격리 모킹합니다."""
    test_db = tmp_path / "marketing_parallel_test.db"
    patcher = mock.patch("database.DB_PATH", str(test_db))
    patcher.start()

    # decisions.md 임시 격리
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    decisions_bak = os.path.join(SHARED_DIR, "decisions.md.test_bak")
    decisions_existed = os.path.exists(decisions_orig)

    if decisions_existed:
        shutil.copy2(decisions_orig, decisions_bak)
        with open(decisions_orig, "w", encoding="utf-8") as f:
            f.write("# 📌 테스트용 임시 공용 의사결정 로그\n")

    # DB 초기화
    database.init_db()

    yield

    patcher.stop()
    if decisions_existed:
        if os.path.exists(decisions_bak):
            shutil.copy2(decisions_bak, decisions_orig)
            os.remove(decisions_bak)
    else:
        if os.path.exists(decisions_orig):
            os.remove(decisions_orig)

def test_concurrent_tool_execution_performance():
    """ThreadPoolExecutor 병렬 구동 시, 3개의 툴이 동기식이 아닌 병렬식으로 거의 동시에 완수되는지 시간 벤치마킹 검증을 수행합니다."""
    
    # run_tool 호출 시 각 툴별로 0.5초가 걸리도록 모사
    def mock_run_tool(script_path, args=None):
        time.sleep(0.5)
        # 성공 코드(0), 가상 stdout, 가상 stderr 반환
        # 퍼블리셔의 경우 JSON 파싱을 위해 더미 JSON 블록 반환
        return 0, "==================================================\n{\"status\":\"success\", \"url\":\"http://mock/url\"}\n==================================================", ""

    with mock.patch("campaign_orchestrator.run_tool", side_effect=mock_run_tool), \
         mock.patch("campaign_orchestrator.get_latest_file", return_value=""), \
         mock.patch("shutil.copy2", return_value=True):
        
        start_time = time.time()
        campaign_orchestrator.main()
        total_duration = time.time() - start_time
        
        # 순차적(Sequential) 실행 시 소요 시간:
        # Step 1 (0.5초) + Step 2,3,4 (0.5 * 3 = 1.5초) + Step 5,6 (0.5 * 2 = 1.0초) = 총 3.0초
        #
        # 병렬(Parallel Concurrent) 실행 시 소요 시간:
        # Step 1 (0.5초) + Step 2,3,4 병렬 (0.5초) + Step 5,6 병렬 (0.5초) = 총 1.5초
        #
        # 따라서 병렬화가 올바르게 작동했다면, 아무리 윈도우 스레드 스케줄링 오차가 있다 하더라도 2.2초 미만으로 완수되어야 합니다!
        print(f"⏱️ 병렬화 모사 오케스트레이터 완수 소요 시간: {total_duration:.2f}초")
        assert total_duration < 2.2, f"병렬 오케스트레이션 수행 속도 부족! 총 {total_duration:.2f}초 소요됨 (Sequential로 동작한 의혹 있음)"
