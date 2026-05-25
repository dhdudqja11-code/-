# 📷 Instagram Publisher (인스타그램 릴스 API 퍼블리셔)

`reels_planner.py`가 기획한 15~30초 초압축 숏폼 대본을 실제 인스타그램 비즈니스 계정에 Reels 비디오 형태로 자율 업로드/발행하거나 안전하게 시뮬레이션 발행합니다.

## 🛠️ 주요 기능
1. **하이브리드 발행 모드**:
   - `config.md`에 Meta Graph API 토큰(`META_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ID`)이 존재할 시, 실제 비디오 컨테이너 생성 및 미디어 퍼블리시 OpenAPI 흐름을 호출하여 원스톱 발행을 수행합니다.
   - 키 누락 시 자동으로 '컴플라이언스 시뮬레이션 발행 모드'로 안전하게 동작합니다 (exit 0).
2. **트랙백/감사 연동**: 모든 발행 결과와 상태는 `_company/_shared/marketing.db` SQLite DB에 트랜잭션 기록 및 감사 로그화됩니다.
3. **오류 자가 복구 가드레일**: 실제 API 호출 중 네트워크 예외나 HTTP 오류 발생 시, 시스템 크래시를 방지하기 위해 즉각 시뮬레이션 폴백 포스트를 생성하여 완주합니다.

## 🚀 실행 방법
```bash
python _company/_agents/instagram/tools/instagram_publisher.py [선택: 대본파일경로]
```
