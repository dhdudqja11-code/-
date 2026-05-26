# 📡 `web_search` — 실시간 자율 웹 스카우터 지침서

## 개요
본 도구는 사장님(CEO)의 AI 1인 기업이 시장 흐름을 조사할 때, 유료 API 비용 청구를 단 1원도 유발하지 않고 DuckDuckGo HTML 및 Google News RSS를 결합 파싱하여 실시간 최신 정보 5개를 즉각 병렬 대조 획득하는 자율 시장 조사 도구입니다.

## 실행 규칙
1. **일반 키워드 검색 (기본)**:
   ```bash
   python web_search.py "AI 챗봇 개발자 연봉" --type web
   ```
2. **실시간 뉴스 RSS 트렌드 획득**:
   ```bash
   python web_search.py "Ollama 윈도우 GPU 가속" --type news
   ```

## 안전 수칙 및 쿨링 제약
* 본 도구는 읽기 전용(Read-only) 리소스로 작동하므로, 로컬 데이터베이스의 어떠한 테이블도 수정하거나 손상시키지 않는 격리 샌드박스 안정성을 가집니다.
* Windows 기동 시 `BELOW_NORMAL_PRIORITY_CLASS (0x00004000)` 가드레일 하에서 연쇄 기동되므로 노트북 CPU/GPU 과열과 팬 소음을 완전히 격리 차단합니다.
