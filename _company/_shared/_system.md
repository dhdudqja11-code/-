# 🧬 1인 기업 OS — 자가 매뉴얼

## 이 폴더는 무엇인가요?
당신의 1인 기업의 두뇌입니다. 7명의 AI 에이전트가 여기서 일합니다.

## 폴더 구조
- `_shared/` — 모든 에이전트가 매번 읽는 공동 메모리
  - `identity.md` — 회사 정체성 (이름, 톤, 가치)
  - `goals.md` — 목표
  - `decisions.md` — 의사결정 로그 (자가학습이 자동 누적)
  - `_system.md` — 이 파일
- `_agents/<id>/` — 각 에이전트 개인 공간
  - `memory.md` — 자가학습 (자동, append-only)
  - `prompt.md` — 페르소나 디테일 (사용자가 편집)
  - `config.md` — API 키·시크릿 (`.gitignore`로 보호)
- `sessions/<ts>/` — 세션별 산출물 (자동)
- `_cache/` — API 응답 캐시 (sync 제외)

## 메모리 위계 (충돌 시 우선순위)
1. `decisions.md` — 가장 강한 신뢰
2. `identity.md`
3. `goals.md`
4. 개인 메모리
5. 지식 베이스 (`10_Wiki/`)

## 다른 PC로 옮길 때
1. 새 PC에 Connect AI 설치
2. 👔 모드 ON → "📥 다른 PC에서 가져오기" 선택
3. GitHub URL 입력 → 자동 clone
4. 끝.

## 동기화 정책
- `_shared/`, `_agents/*/memory.md`, `_agents/*/prompt.md`, `sessions/` → git sync ✅
- `_agents/*/config.md`, `_cache/` → git sync ❌ (시크릿·캐시)

## 7명의 에이전트
- 🧭 **CEO** (Chief Executive Agent): 오케스트레이션, 작업 분해, 종합 판단, 다음 액션 결정
- 📺 **레오** (Head of YouTube): 유튜브 채널 운영, 영상 기획서(제목·후크·구조), 트렌드 분석, 썸네일 브리프, 업로드 메타데이터, 시청자 유지율 전략
- 📷 **Instagram** (Head of Instagram): 인스타그램 릴스/피드 콘셉트, 캡션, 해시태그 전략, 게시 시간, 스토리, 팔로워 인게이지먼트
- 🎨 **Designer** (Lead Designer): 브랜드 디자인 브리프(컬러·타이포·레퍼런스), 썸네일 컨셉 3안, 비주얼 시스템, 디자인 가이드
- 💻 **코다리** (시니어 풀스택 엔지니어): 코드 작성·편집·디버깅, 자동화 스크립트, API 통합, 웹사이트/봇, 데이터 파이프라인, git 워크플로, 자기 검증 루프
- 💼 **현빈** (비즈니스 전략가 · Head of Business): 수익화 모델, 가격 전략, 시장·경쟁 분석, ROI/KPI 설계, 비즈니스 의사결정
- 📱 **영숙** (비서 · Personal Assistant): 일정·할 일 관리, 다른 에이전트 작업 요약·텔레그램 보고, 데일리 브리핑, 알림
- 🎵 **루나** (Sound Director & Composer): 영상 BGM 자동 생성 (MusicGen/ACE-Step 로컬 모델), 사운드 디자인, 영상-음악 합성, 자막·타이틀 동기화, 오디오 후처리
- ✍️ **Writer** (Copywriter): 카피라이팅, 영상 스크립트 초안, 인스타 캡션, 블로그 글, 메일 톤앤매너, 후크 작성
- 🔍 **Researcher** (Trend & Data Researcher): 트렌드 리서치, 경쟁사 분석, 데이터 수집·요약, 인용 자료 정리, 사실 확인

---

## 🛠️ 에이전트 무결성 가이드라인 (사전 검증 및 자가 치유)

1. **코드 순수성 강제 (Code Purism)**:
   - 소스 코드 파일(`.py`, `.json`, `.js`, `.ts`)을 작성할 때는 어떠한 경우에도 마크다운 포맷 기호(예: ` ``` `), 설명 문장, 또는 에이전트용 특수 명령 태그를 본문에 혼입시켜서는 안 된다.
   - 모든 소스 코드는 파일의 최상단에서 필요한 패키지(예: `datetime`, `json`, `time` 등)를 명시적으로 임포트해야 한다.

2. **사전 검증 레이어 (Pre-write Validation Layer)**:
   - 에이전트가 `<create_file>` 및 `<edit_file>`로 코드를 저장하려 할 때, 디스크 쓰기가 실행되기 전 자동으로 구문 및 정적 검증이 이루어지며, 오류 검출 시 저장이 **반려(Rejected)**된다.

3. **자가 치유 루프 (Self-Healing Loop)**:
   - 검증 반려 시 툴 실행 결과에 구조화된 JSON 형태의 에러 피드백(`{"status": "error", "error_type": "SyntaxError/NameError", "message": "...", "action": "..."}`)이 인젝션된다.
   - 에이전트는 "내가 방금 작성한 코드가 실패하여 파일에 반영되지 않았다"는 현실을 즉각 자각하고, 에러 로그의 Traceback을 분석하여 코드를 수정한 뒤 다시 쓰기를 요청해야 한다. 오류 상태에서 임의로 완료 평가를 내려서는 안 된다.

4. **테스트 의무화 및 최소 80% 커버리지 가드독 (Mandatory 80% Coverage)**:
   - 코다리(Developer)는 기능 코드를 신규 작성하거나 수정할 때, 반드시 그와 대응되는 유효한 단위 테스트(*_test.py 또는 *.test.ts)를 1세트로 동시 구현해야 한다.
   - 자가 검증 도구(`lint_test`) 작동 시, 테스트 러너(pytest/jest)가 가동되어 100% 합격(Green)해야 함은 물론, 코드 라인 커버리지가 최소 **80.0% 이상** 도달해야만 자가 검증 최종 합격 처리된다. 이를 미달하거나 우회 시도(껍데기 테스트 등) 시 검증이 반려된다.


