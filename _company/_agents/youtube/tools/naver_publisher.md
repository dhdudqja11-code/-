# ✍️ Naver Publisher (네이버 블로그 API 퍼블리셔)

`naver_writer.py`가 작성한 전문 테크 비즈니스 칼럼을 실제 네이버 블로그에 자율 발행하거나 안전하게 시뮬레이션 발행합니다.

## 🛠️ 주요 기능
1. **하이브리드 발행 모드**: 
   - `config.md`에 네이버 API 토큰(`NAVER_BLOG_ID`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`)이 존재할 시, 실제 블로그 OpenAPI를 호출하여 원스톱 발행을 수행합니다.
   - 키 누락 시 자동으로 '컴플라이언스 시뮬레이션 발행 모드'로 안전하게 동작합니다 (exit 0).
2. **트랙백/감사 연동**: 모든 발행 결과와 상태는 `_company/_shared/marketing.db` SQLite DB에 트랜잭션 기록 및 감사 로그화됩니다.
3. **오류 자가 복구 가드레일**: 실제 API 호출 중 네트워크 예외나 HTTP 오류 발생 시, 시스템 크래시를 방지하기 위해 즉각 시뮬레이션 폴백 포스트를 생성하여 완주합니다.

## 🚀 실행 방법
```bash
python _company/_agents/youtube/tools/naver_publisher.py [선택: 칼럼파일경로]
```
