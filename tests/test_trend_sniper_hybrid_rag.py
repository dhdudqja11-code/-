# -*- coding: utf-8 -*-
import pytest
import os
import sys
import json
import unittest.mock as mock

# youtube tools 폴더를 sys.path에 추가하여 직접 임포트합니다.
HERE = os.path.dirname(os.path.abspath(__file__))
YOUTUBE_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "youtube", "tools"))
if YOUTUBE_TOOLS not in sys.path:
    sys.path.append(YOUTUBE_TOOLS)

import trend_sniper
import web_search

@pytest.fixture
def temp_decisions_file(tmp_path):
    """테스트 구동 동안 decisions.md의 원본을 오염시키지 않도록 임시 decisions.md 샌드박스를 제공합니다."""
    temp_decisions = tmp_path / "decisions.md"
    temp_decisions.write_text("# 📌 회사 핵심 의사결정 로그 (테스트)\n\n", encoding="utf-8")
    
    # trend_sniper.py 내부의 decisions.md 조회 경로를 이 임시 파일로 강제 모킹합니다.
    with mock.patch("os.path.abspath", side_effect=lambda path: str(temp_decisions) if "decisions.md" in path else os.path.realpath(path)):
        yield temp_decisions

def test_trend_sniper_hybrid_rag_feed_success(temp_decisions_file):
    """[트렌드 스나이퍼 - RAG 피딩] 보고서에 포함된 RAG JSON 블록을 정교하게 추출하여 decisions.md에 등재하는지 단언합니다."""
    sample_report = """🌍 **트렌드 해킹 분석**
- 미디어와 저널리즘 트렌드 분석 완료.

```json
{
  "recommended_niche_keyword": "테스트용 AI 2FA 봇",
  "suggested_thumbnail_copy": "해킹 100% 방어하는 텔레그램 봇 실체",
  "target_topic": "구글 OTP를 텔레그램과 1초 만에 연동하여 원격 PC를 철통 보안하는 법"
}
```
"""
    # RAG 피딩 함수 구동
    trend_sniper._feed_rag_to_decisions(sample_report)
    
    # 임시 decisions.md 내용 검증
    content = temp_decisions_file.read_text(encoding="utf-8")
    assert "### 📡 [RAG Feed] trend_sniper" in content
    assert "추천 틈새 키워드**: `테스트용 AI 2FA 봇`" in content
    assert "해킹 100% 방어하는 텔레그램 봇 실체" in content
    assert "naver_writer.py 및 reels_planner.py는 본 RAG 피드의 키워드와 테마를 최우선 지침" in content

def test_trend_sniper_main_happy_path_hybrid(temp_decisions_file):
    """
    [트렌드 스나이퍼 - 해피 패스 하이브리드 수집]
    YouTube API와 최신 IT 뉴스 RSS 양대 채널에서 병렬로 시장 분석 정보를 무결하게 수집하여,
    최종 decisions.md 적재까지 성공하는 E2E 흐름을 가상 검증합니다.
    """
    # 1. youtube API build 모킹
    mock_youtube = mock.MagicMock()
    mock_search = mock_youtube.search.return_value
    mock_list = mock_search.list.return_value
    mock_list.execute.return_value = {
        "items": [
            {
                "snippet": {
                    "title": "로컬 LLM VRAM 8G 최적화 가이드",
                    "channelTitle": "테크마스터"
                }
            }
        ]
    }
    
    # 2. web_search 및 LLM API 통신 모킹
    mock_news = [
        {
            "title": "Ryzen 9 8945HS 성능 벤치마크 및 발열 분석",
            "url": "https://news.example.com/ryzen9",
            "date": "2026-05-26"
        }
    ]
    
    mock_llm_response = mock.MagicMock()
    mock_llm_response.status_code = 200
    mock_llm_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": """🌍 **트렌드 해킹 분석**
유튜브와 뉴스의 교집합 분석 성공.

```json
{
  "recommended_niche_keyword": "VRAM 8G 로컬 LLM",
  "suggested_thumbnail_copy": "RTX 4060으로 VRAM 8G 로컬 인공지능 속도 5배 올린 썰",
  "target_topic": "VRAM 제한을 뚫고 로컬에서 초광속으로 Ollama 가속하는 최적화 시나리오"
}
```
"""
                }
            }
        ]
    }
    original_open = open
    m_open = mock.mock_open()
    def mock_open_side_effect(file, *args, **kwargs):
        if "decisions.md" in str(file):
            return original_open(file, *args, **kwargs)
        return m_open(file, *args, **kwargs)

    with mock.patch("googleapiclient.discovery.build", return_value=mock_youtube), \
         mock.patch("web_search.scrape_google_news_rss", return_value=mock_news) as mock_rss, \
         mock.patch("requests.get") as mock_get, \
         mock.patch("requests.post", return_value=mock_llm_response), \
         mock.patch("trend_sniper.load_config", return_value={"TARGET_KEYWORDS": ["로컬 AI"]}), \
         mock.patch("trend_sniper.load_account", return_value={"YOUTUBE_API_KEY": "fake_key", "OLLAMA_URL": "http://127.0.0.1:1234/v1"}), \
         mock.patch("builtins.open", side_effect=mock_open_side_effect) as mock_file_write:
         
        # get_models 모킹을 위한 GET 요청
        mock_get_models = mock.MagicMock()
        mock_get_models.status_code = 200
        mock_get_models.json.return_value = {"data": [{"id": "mock-llm-model"}]}
        mock_get.return_value = mock_get_models
        
        # 기동
        trend_sniper.main()
        
        # 3. 단언 검증
        # RSS 스크랩이 병렬 기동되었는지 검증
        mock_rss.assert_called_once()
        
        # decisions.md에 추천 키워드가 피딩 기록되었는지 파일 검증
        content = temp_decisions_file.read_text(encoding="utf-8")
        assert "추천 틈새 키워드**: `VRAM 8G 로컬 LLM`" in content

def test_trend_sniper_api_quota_exhausted_fallback_success(temp_decisions_file):
    """
    [트렌드 스나이퍼 - 쿼터 초과 자율 회복 폴백(Self-Healing)]
    유튜브 API 호출 시 쿼터 한도 초과 예외가 발생하더라도,
    즉시 자율 웹 스카우터(DuckDuckGo)로 동적 폴백 스위칭하여 보고서 완수 및 decisions.md RAG 기입에 성공하는지 검증합니다.
    """
    # 1. 유튜브 API 예외 발생 모킹
    mock_youtube = mock.MagicMock()
    mock_search = mock_youtube.search.return_value
    mock_list = mock_search.list.return_value
    mock_list.execute.side_effect = Exception("YouTube API Quota Exceeded (403 Forbidden)")
    
    # 2. 자율 웹 스카우터(DuckDuckGo) 및 뉴스 RSS 모킹
    mock_ddg = [
        {
            "title": "인터넷 없이 쓰는 로컬 코딩 AI 어시스턴트 실체",
            "snippet": "오프라인 환경에서도 100% Passed 그린을...",
            "url": "https://example.com/offline-ai"
        }
    ]
    mock_news = [
        {
            "title": "NVIDIA VRAM 과열 억제를 위한 쿨링 스케줄러 가드레일",
            "url": "https://news.example.com/vram-cooling",
            "date": "2026-05-26"
        }
    ]
    mock_get_models = mock.MagicMock()
    mock_get_models.status_code = 200
    mock_get_models.json.return_value = {"models": [{"name": "mock-llm-model"}]}

    original_open = open
    m_open = mock.mock_open()
    def mock_open_side_effect(file, *args, **kwargs):
        if "decisions.md" in str(file):
            return original_open(file, *args, **kwargs)
        return m_open(file, *args, **kwargs)

    with mock.patch("googleapiclient.discovery.build", return_value=mock_youtube), \
         mock.patch("web_search.scrape_duckduckgo", return_value=mock_ddg) as mock_scrape_ddg, \
         mock.patch("web_search.scrape_google_news_rss", return_value=mock_news) as mock_rss, \
         mock.patch("requests.get", return_value=mock_get_models) as mock_get, \
         mock.patch("requests.post") as mock_post, \
         mock.patch("trend_sniper.load_config", return_value={"TARGET_KEYWORDS": ["오프라인 AI"]}), \
         mock.patch("trend_sniper.load_account", return_value={"YOUTUBE_API_KEY": "fake_key"}), \
         mock.patch("builtins.open", side_effect=mock_open_side_effect):
         
        # LLM 연결 실패로 인한 mock-model 자동 복구 모드 강제 유발을 위한 예외 처리
        mock_post.side_effect = Exception("Ollama Connection Refused")
        
        # 기동
        trend_sniper.main()
        
        # 3. 단언 검증
        # 유튜브 예외 시 DuckDuckGo 크롤러가 자율 호출되었는지 검증
        mock_scrape_ddg.assert_called_once()
        mock_rss.assert_called_once()
        
        # 자율 폴백 mock-model RAG 데이터가 decisions.md에 피딩 등재 완료되었는지 검증
        content = temp_decisions_file.read_text(encoding="utf-8")
        assert "추천 틈새 키워드**: `AI 페어프로그래밍 샌드박스`" in content
        assert "AI랑 밤새 코딩해서 98개 테스트 한방에 통과한 썰" in content
