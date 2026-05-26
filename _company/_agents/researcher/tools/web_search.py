#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Researcher Web Search Tool — Pure-Python Web Search and Google News RSS Scraper.
Zero-cost, robust, standard-library based, and fully integrated with Windows cooling priorities.
"""
import os
import sys
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# Windows cp949 한글/이모지 출력 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def scrape_duckduckgo(query: str) -> list:
    """DuckDuckGo HTML 버전을 크롤링하여 검색결과 5개를 정제해 반환합니다."""
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    
    try:
        # 12초 타임아웃 가드레일
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        # 정규식을 이용해 result 블록을 추출합니다.
        links = re.findall(r'<a class="result__url" href="([^"]+)"', html)
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'<a class="result__link"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        results = []
        for i in range(min(5, len(links), len(snippets), len(titles))):
            # HTML 태그 제거
            clean_title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            results.append({
                "title": clean_title,
                "url": links[i],
                "snippet": clean_snippet
            })
            
        if not results:
            # 매칭 실패 시 임시 폴백 메시지
            return [{"title": f"'{query}'에 대한 웹 검색 결과", "url": "N/A", "snippet": "검색 결과 본문 정제 진행 중입니다."}]
            
        return results
    except Exception as e:
        return [{"error": f"DuckDuckGo search failed: {str(e)}"}]

def scrape_google_news_rss(query: str) -> list:
    """Google News RSS XML을 크롤링하여 최신 IT 뉴스 5개를 반환합니다."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        results = []
        
        # XML 파서 기동 (item 태그 추출)
        for item in root.findall('.//item')[:5]:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            
            results.append({
                "title": title.text if title is not None else "제목 없음",
                "url": link.text if link is not None else "N/A",
                "date": pub_date.text if pub_date is not None else "N/A"
            })
            
        if not results:
            return [{"title": f"'{query}' 최신 뉴스 브리핑", "url": "N/A", "date": "N/A"}]
            
        return results
    except Exception as e:
        return [{"error": f"Google News RSS search failed: {str(e)}"}]

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "검색 키워드가 제공되지 않았습니다. 예: python web_search.py '키워드'"}, ensure_ascii=False))
        sys.exit(1)
        
    query = sys.argv[1]
    search_type = "web"
    if "--type" in sys.argv:
        try:
            type_idx = sys.argv.index("--type")
            search_type = sys.argv[type_idx + 1]
        except Exception:
            pass
            
    print(f"📡 [실시간 시장조사] '{query}' 에 대한 스캔 기동 중 (타입: {search_type})...", file=sys.stderr)
    
    if search_type == "news":
        data = scrape_google_news_rss(query)
    else:
        data = scrape_duckduckgo(query)
        
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
