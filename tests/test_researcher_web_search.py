# -*- coding: utf-8 -*-
import pytest
import os
import sys
import base64
import unittest.mock as mock

# researcher tools 폴더를 sys.path에 추가하여 직접 임포트합니다.
HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCHER_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "researcher", "tools"))
if RESEARCHER_TOOLS not in sys.path:
    sys.path.append(RESEARCHER_TOOLS)

import web_search

def test_duckduckgo_html_parsing_mocked():
    """DuckDuckGo HTML 검색결과 페이지를 모킹하여 파싱 정규식이 완벽히 구조화된 결과를 추출하는지 검증합니다."""
    fake_html = """
    <html>
    <body>
    <div class="result">
        <a class="result__url" href="https://example.com/ai-salary">example.com/ai-salary</a>
        <a class="result__link" href="https://example.com/ai-salary">AI 챗봇 개발자 연봉 실태 조사</a>
        <a class="result__snippet" href="https://example.com/ai-salary">2026년 기준 챗봇 개발자의 평균 연봉은...</a>
    </div>
    <div class="result">
        <a class="result__url" href="https://example.com/ollama-gpu">example.com/ollama-gpu</a>
        <a class="result__link" href="https://example.com/ollama-gpu">Ollama 윈도우 GPU 가속 가이드</a>
        <a class="result__snippet" href="https://example.com/ollama-gpu">RTX 4060 GPU 가속을 통해 로컬 LLM을 5배 더 빠르게...</a>
    </div>
    </body>
    </html>
    """
    
    # urllib.request.urlopen 모킹
    mock_response = mock.MagicMock()
    mock_response.read.return_value = fake_html.encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    
    with mock.patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        res = web_search.scrape_duckduckgo("AI 개발자 연봉")
        
        # urlopen 호출 단언
        mock_urlopen.assert_called_once()
        
        # 파싱 결과 단언
        assert len(res) == 2
        assert res[0]["title"] == "AI 챗봇 개발자 연봉 실태 조사"
        assert res[0]["url"] == "https://example.com/ai-salary"
        assert "평균 연봉은" in res[0]["snippet"]
        
        assert res[1]["title"] == "Ollama 윈도우 GPU 가속 가이드"
        assert res[1]["url"] == "https://example.com/ollama-gpu"

def test_google_news_rss_xml_parsing_mocked():
    """Google News RSS XML 데이터를 모킹하여 ElementTree XML 파서가 구조화된 뉴스 정보를 정상적으로 추출하는지 검증합니다."""
    fake_xml = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
    <channel>
        <title>Google 뉴스 - 검색</title>
        <item>
            <title>로컬 AI 기술 혁신과 1인 솔로프레너의 시대 - IT 뉴스</title>
            <link>https://news.example.com/solo-ai-era</link>
            <pubDate>Mon, 25 May 2026 12:00:00 GMT</pubDate>
        </item>
        <item>
            <title>Ryzen 9 8945HS 노트북 쿨링 가이드 출시 - 테크 블로그</title>
            <link>https://news.example.com/ryzen9-cooling</link>
            <pubDate>Mon, 25 May 2026 14:00:00 GMT</pubDate>
        </item>
    </channel>
    </rss>
    """
    
    mock_response = mock.MagicMock()
    mock_response.read.return_value = fake_xml.encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    
    with mock.patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        res = web_search.scrape_google_news_rss("1인 기업 AI")
        
        mock_urlopen.assert_called_once()
        
        # XML 파싱 결과 단언
        assert len(res) == 2
        assert res[0]["title"] == "로컬 AI 기술 혁신과 1인 솔로프레너의 시대 - IT 뉴스"
        assert res[0]["url"] == "https://news.example.com/solo-ai-era"
        assert res[0]["date"] == "Mon, 25 May 2026 12:00:00 GMT"
        
        assert res[1]["title"] == "Ryzen 9 8945HS 노트북 쿨링 가이드 출시 - 테크 블로그"
        assert res[1]["url"] == "https://news.example.com/ryzen9-cooling"
