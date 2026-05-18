# 🛠️ AI 1인 기업 트러블슈팅 (오류 수정 로그)

본 문서는 AI 1인 기업 운영 중 발생하는 시스템 오류 및 해결 방법을 기록하는 문서입니다.

---

## 📅 2026-05-18: CEO 에이전트 작업 분배 계획(JSON) 생성 실패 (LM Studio 출력 잘림)

### 🚨 오류 증상
* Connect AI 실행 중 CEO 에이전트가 "작업 분배 계획(JSON)을 생성하지 못했어요."라는 에러 알림 발생.
* LM Studio의 텍스트 출력이 중간에 뚝 끊기거나 잘리는 현상 확인.

### 🔍 원인 파악
* **Context Length(컨텍스트 길이) 제한 초과**: LM Studio에 로드된 LLM 모델의 기본 컨텍스트 길이(예: 4096)가 부족하여 발생했습니다.
* AI 1인 기업의 7명 에이전트 시스템은 작동할 때마다 회사의 규칙(`_system.md`), 목표(`goals.md`), 일정(`schedule.md`), 그리고 에이전트의 개인 메모리(`memory.md`)를 모두 읽고 시작합니다. 이 파일들에 로그가 누적되면서 모델이 한 번에 읽을 수 있는 글자 수를 초과해 버린 것입니다.

### 💡 해결 방법 (완료)

**1. 프롬프트 용량 압축 (AI 조치 완료)**
다음 파일들을 핵심 내용만 남기고 아주 짧게 요약(압축)하여, 모델이 소화해야 하는 글자 수를 획기적으로 줄였습니다.
* `_company/_agents/ceo/memory.md` (CEO 메모리 최적화)
* `_company/_shared/decisions.md` (회사 의사결정 최적화)
* `_company/_shared/schedule.md` (긴 작업 로그 요약)

**2. LM Studio 설정 변경 (직접 조치)**
1. LM Studio 프로그램에서 현재 켜져 있는 모델을 내립니다 (Eject/Unload).
2. 화면 우측 설정(Configuration) 패널에서 **Context Length** (또는 n_ctx) 슬라이더를 찾아 **8192** 이상으로 늘려줍니다.
3. 모델을 다시 로드(Reload)한 뒤 에이전트 작업을 재개합니다.

---

### 📌 예방 팁
* AI 에이전트들이 작업을 반복하면 `.md` 파일들에 로그가 길어지게 됩니다. 
* 종종 저에게 **"의사결정 로그랑 스케줄 파일 좀 짧게 압축해 줘"**라고 요청해 주시면 컨텍스트 초과 오류를 예방할 수 있습니다.

---

## 📅 2026-05-18: LM Studio API 호출 경로 중복 오류 (POST /v1/v1/chat/completions 404/Unexpected endpoint)

### 🚨 오류 증상
* Connect AI 실행 중 `⚠️ CEO가 작업 분배 계획(JSON)을 생성하지 못했어요.` 알림이 뜨며 LLM 호출이 실패함.
* LM Studio의 로그에 `[ERROR] Unexpected endpoint or method. (POST /v1/v1/chat/completions). Returning 200 anyway` 라는 에러 메시지가 찍힘.
* API 경로에 `/v1`이 두 번 중복해서 들어가는 바람에 올바른 Chat Completion 호출이 처리되지 못하고 빈 응답 또는 에러가 반환됨.

### 🔍 원인 파악
* `.vscode/settings.json`에서 `"connectAiLab.ollamaUrl"`이 `"http://127.0.0.1:1234/v1"`로 설정되어 있었습니다.
* 소스 코드(`src/extension.ts`)에서 LM Studio 모드일 때 API 주소를 생성하면서 `${ollamaBase}/v1/chat/completions`와 같이 URL 뒤에 `/v1/chat/completions`를 **무조건 추가로 결합**하게 설계되어 있었습니다.
* 이로 인해 설정에 `/v1`이 붙어있을 경우 `/v1/v1/chat/completions` 경로로 잘못 요청이 전송되는 버그가 있었습니다.

### 💡 해결 방법 (완료)

**1. 설정 값 교정 (완료)**
* `.vscode/settings.json`의 `"connectAiLab.ollamaUrl"` 값을 `"http://127.0.0.1:1234"`로 수정하여 중복을 원천 차단했습니다.

**2. 코드 레벨의 자가 치유(Self-healing) 로직 도입 (완료)**
* 사용자가 혹시라도 설정에 `/v1`을 포함시키거나 포함시키지 않더라도 자동으로 주소를 보정하도록 로직을 수정했습니다.
* **적용 파일**:
  * [src/extension.ts](file:///c:/Users/user/AI%20%EA%B8%B0%EC%97%85%20%EB%91%90%EB%87%8C/%EB%82%B4%20%EC%9E%91%EC%97%85%EB%93%A4/src/extension.ts)
  * [ConnectAI/src/extension.ts](file:///c:/Users/user/AI%20%EA%B8%B0%EC%97%85%20%EB%91%90%EB%87%8C/%EB%82%B4%20%EC%9E%91%EC%97%85%EB%93%A4/ConnectAI/src/extension.ts)
  * [scripts/cycle.js](file:///c:/Users/user/AI%20%EA%B8%B0%EC%97%85%20%EB%91%90%EB%87%8C/%EB%82%B4%20%EC%9E%91%EC%97%85%EB%93%A4/scripts/cycle.js)
  * [ConnectAI/scripts/cycle.js](file:///c:/Users/user/AI%20%EA%B8%B0%EC%97%85%20%EB%91%90%EB%87%8C/%EB%82%B4%20%EC%9E%91%EC%97%85%EB%93%A4/ConnectAI/scripts/cycle.js)
* **수정 내용**: URL 끝부분의 `/v1` 또는 `/v1/` 경로를 정규식을 통해 검출하여 제거한 뒤 API 엔드포인트를 붙이도록 강인한 자가 치유 로직(`replace(/\/v1\/?$/, '')`)을 적용했습니다.

이제 설정과 코드 양쪽에서 완벽히 해결되었으므로, 경로 중복으로 인한 API 호출 실패 문제는 다시 발생하지 않습니다!

