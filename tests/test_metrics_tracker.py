# -*- coding: utf-8 -*-
import os, sys, shutil, json, time
import unittest.mock as mock
import pytest

# 테스트 대상 경로 추가
HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, "..", "_company"))
SHARED_DIR = os.path.join(COMPANY_ROOT, "_shared")
sys.path.append(SHARED_DIR)

import database
import metrics_tracker

@pytest.fixture(autouse=True)
def setup_test_db_and_backups(tmp_path):
    """테스트 실행 전/후 데이터베이스와 decisions.md의 원본을 백업하고 복원하는 안전장치 피처입니다."""
    # 1. database.DB_PATH를 테스트 임시 DB 경로로 모킹!
    test_db = tmp_path / "marketing_test.db"
    patcher = mock.patch("database.DB_PATH", str(test_db))
    patcher.start()

    # 2. decisions.md 백업
    decisions_orig = os.path.join(SHARED_DIR, "decisions.md")
    decisions_bak = os.path.join(SHARED_DIR, "decisions.md.test_bak")
    decisions_existed = os.path.exists(decisions_orig)

    if decisions_existed:
        shutil.copy2(decisions_orig, decisions_bak)
        # 테스트 동안 decisions.md 초기화 상태로 시작
        with open(decisions_orig, "w", encoding="utf-8") as f:
            f.write("# 📌 테스트용 임시 공용 의사결정 로그\n")

    # 3. SQLite 데이터베이스 상태 가짜 초기화 수행
    database.init_db()

    yield

    # 4. DB_PATH 패치 중지
    patcher.stop()

    # 5. decisions.md 복구 및 백업 정리
    if decisions_existed:
        if os.path.exists(decisions_bak):
            shutil.copy2(decisions_bak, decisions_orig)
            os.remove(decisions_bak)
    else:
        if os.path.exists(decisions_orig):
            os.remove(decisions_orig)

def test_database_metrics_logging_and_summary():
    """log_metrics와 get_performance_summary가 지표 데이터를 올바르게 기록하고 집계하는지 검증합니다."""
    # SQLite에 캠페인 하나 가짜 적재
    campaign_id = database.log_campaign(
        timestamp="20260525_2100",
        campaign_dir="campaign_20260525_2100",
        status="Success",
        naver=1,
        insta=1
    )
    assert campaign_id is not None

    # 지표 삽입
    database.log_metrics(
        campaign_id=campaign_id,
        platform="naver",
        post_identifier="naver_test_101",
        title="AI 활용법 테크 칼럼",
        url="http://blog.naver.com/test/1",
        views=1500,
        likes=120,
        comments=10
    )

    database.log_metrics(
        campaign_id=campaign_id,
        platform="instagram",
        post_identifier="insta_test_202",
        title="AI 꿀팁 인스타 릴스",
        url="http://instagram.com/test/reels/2",
        views=4500,
        likes=350,
        comments=45
    )

    # 마케팅 성과 누적 요약 쿼리 검증
    summary = database.get_performance_summary()
    assert summary["naver_views"] == 1500
    assert summary["naver_likes"] == 120
    assert summary["insta_views"] == 4500
    assert summary["insta_likes"] == 350
    
    # 최고 조회수 베스트 퍼포머 검증
    best = summary["best_performer"]
    assert best is not None
    assert best["platform"] == "instagram"
    assert best["title"] == "AI 꿀팁 인스타 릴스"
    assert best["views"] == 4500
    assert best["likes"] == 350


def test_metrics_tracker_rag_generation(tmp_path):
    """metrics_tracker.py가 성과가 높은 콘텐츠를 감지하여 decisions.md에 올바른 RAG 포맷으로 추가 기입하는지 검증합니다."""
    # 테스트용 임시 DB 초기화 및 지표 추가
    database.init_db()
    
    campaign_id = database.log_campaign(
        timestamp="20260525_2200",
        campaign_dir="campaign_20260525_2200",
        status="Success"
    )
    
    database.log_metrics(
        campaign_id=campaign_id,
        platform="naver",
        post_identifier="naver_rag_test",
        title="RAG 자율 개선 대전략",
        url="http://blog.naver.com/rag/1",
        views=9900,  # 압도적인 1위 베스트 퍼포머
        likes=880,
        comments=90
    )

    # decisions.md 경로 패치하여 안전 격리
    temp_decisions_file = tmp_path / "decisions.md"
    
    with mock.patch("metrics_tracker.DECISIONS_MD", str(temp_decisions_file)):
        metrics_tracker.run_tracker_cycle()

    # RAG 피드백 내용 확인
    assert os.path.exists(str(temp_decisions_file))
    with open(temp_decisions_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "마케팅 성과 자율 RAG 피드백" in content
    assert "RAG 자율 개선 대전략" in content
    assert "조회(재생) 9,900회" in content
    assert "공감(좋아요) 880개" in content
    assert "실용적인 이점" in content or "직관적인 실용적 가치" in content
