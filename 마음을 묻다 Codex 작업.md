# 마음을 묻다 - Codex 작업 분리

## 내가 할 수 있는 작업
1. `global-letters/src/app/api/generate-letter/route.ts`에서 AI 응답 파싱을 구조화된 JSON으로 대응
2. `global-letters/src/app/api/setup-assistant/route.ts`의 어시스턴트 지침을 다중 페이지 PDF 용 JSON 출력 규격으로 업그레이드
3. `global-letters/src/app/page.tsx`에서 PDF 다운로드를 다중 `.pdf-page` 요소로 생성하도록 변경
4. `global-letters/src/app/page.tsx`에 숨겨진 다중 페이지 PDF 렌더링용 DOM 구조 추가

## Codex가 해야 할 작업
1. `global-letters/src/app/page.tsx` 또는 디자인 시스템에 맞춘 A4 다중 페이지 PDF 스타일 확정
2. `global-letters` 앱에 `Gift Package` 요금제 및 선물하기 UI/결제 흐름 추가
3. `SEO Agent` 자동화 스크립트 및 `reviews.json` 기반 검색어/메타데이터 업데이트 기능 구현
4. `vercel.json` 배포 헤더 설정 및 클라우드 배포 자동화 스크립트 추가
5. `global-letters` 언어 감지(i18n) 분기 및 글로벌 버전 UI 추가
6. 인스타그램/UGC 공유 유도 UI 및 PDF 대비 로고 삽입 규칙 구현
7. `marketing_bot.py` 같은 마케팅 자동화 스크립트 배치 및 스케줄링
8. `global-letters/src/app/api/setup-assistant/route.ts`의 어시스턴트 파일 업로드/검색 내용 추가 조정

## 진행 상태
- 현재: 핵심 구조 변경 작업을 우선 구현 중
- 문서화: Codex 전용 작업은 이 파일에 저장됨

> 이 파일은 `코덱스가 해야 하는 작업`과 `내가 바로 구현 가능한 작업`을 분리하기 위한 기준 문서입니다.
