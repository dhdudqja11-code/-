# 🛠️ AI 1인 기업 시스템 구축 · 오류 해결 및 최적화 종합 마스터 로그

본 문서는 Connect AI 프로젝트를 진행하며 발생했던 모든 오류의 원인 분석, 하드웨어 스펙 한계를 극복하기 위한 소프트웨어 최적화 과정, 모놀리식 구조 리팩토링 및 24시간 자율 사이클 운영에 따른 문제 해결 내역을 통합한 **최종 마스터 문제 해결 로그(Master Log)**입니다.

---

## 🧭 1. 하드웨어 성능 한계 극복 및 AI 추론 최적화

### ❌ 초기 문제 상황
- **저사양 하드웨어 환경**: Intel i7-8550U (32GB RAM, NVIDIA 930MX 외장 GPU)
- **증상**: 로컬 LLM 구동 시 잦은 로딩 타임아웃, VRAM 부족으로 인한 프로세스 멈춤(Hang), 리소스 병목 현상 발생.
- **원인**: 여러 에이전트가 다른 종류의 큰 모델을 동시에 또는 교대로 호출하면서 발생하는 **'모델 스와핑(Model Swapping)'** 병목 및 CPU 추론 클럭 저하.

### 🛠️ 핵심 최적화 조치
1. **모델 단일화 고정 (Model Lock)**:
   - 전문 에이전트들이 설정 UI 값을 무시하고 무조건 로컬에 최적화된 초경량 **`qwen/qwen3-1.7b`** 모델(식별자 `connectai-main`)을 사용하도록 `src/extension.ts`를 강제 수정.
2. **컨텍스트 크기 다이어트 및 타임아웃 상향**:
   - 컨텍스트 윈도우 크기를 **`4096`**으로, 예측 토큰(`num_predict`)을 **`2048`**로 조절하여 메모리 부족(OOM) 방지.
   - CPU 추론 및 열 스로틀링을 감안하여 스트림 첫 토큰 대기 시간(`streamFirstTokenTimeoutSec`)을 **900초(15분)**로, 유휴 타임아웃을 **120초**로 파격 상향.
3. **CEO 입력 프롬프트 캡(Cap) 적용**:
   - 회사 규칙 및 과거 대화 로그가 누적되어 컨텍스트 한도를 넘지 않도록 입력 프롬프트 길이를 **최대 12,000자(약 3,000토큰)로 제한**.
4. **저전력 모드 기본화**:
   - `lowPowerMode: true` 및 자율 사이클 간격 `autoCycleIntervalMin: 60`을 기본값으로 지정하여 CPU 점유율 최적화.

---

## 🛠️ 2. 시스템 리팩토링, 테스트 환경 및 의존성 구축

### 📦 모놀리식 구조 리팩토링
- **모듈화 진행**: 약 20,000줄에 달하던 거대한 단일 파일 `extension.ts`에서 마이그레이션 로직 및 에이전트 제어 로직을 하위 모듈(`src/core/agent-manager.ts` 등)로 점진적 분리 수행.

### 🧪 테스트 및 패키지 환경 정비
- **Jest 테스트 환경 완비**: `jest.config.js` 검증, `ts-jest` 프리셋 설정, `testMatch` 지정을 통해 TypeScript 유닛 테스트 스위트 구축.
- **의존성 해결**: `package.json`을 기반으로 `axios`, `jsdom` 및 주요 개발 도구 패키지 설치 완료.

### 🔌 OpenCode 및 외부 명령 연동 버그 수정
- VS Code 명령어 팔레트에 "OpenCode: 수석 개발자에게 작업 위임"이 보이지 않던 에이전트 등록 및 활성화 프로세스 오류 해결.
- 로컬 디렉토리 경로 동적 매핑 및 인코딩 기술 부채 해소.

---

## 📝 3. 에이전트 트러블슈팅 및 예방 역사 (Chronological History)

### 📅 [2026-05-15] 1차 수정: 에이전트별 모델 강제 지정 해제
- **원인**: `_shared/agent_models.json` 내 직원 에이전트들이 무거운 `qwen/qwen3-vl-4b`로 지정되어 있어 스와핑이 끊임없이 발생.
- **조치**: `agent_models.json`을 `{}`(빈 객체)로 초기화하여 공통 모델인 `connectai-main`을 호출하도록 강제 적용.
- **GitHub 원격 주소 에러 조치**: 존재하지 않는 저장소 `https://github.com/dhdudqja1-art/-.git`가 설정에 들어가 빌드를 방해하던 버그 해결을 위해 `secondBrainRepo`를 빈 값(`""`)으로 초기화.

### 📅 [2026-05-16] 2차 수정: LM Studio CPU/RAM 기반 완전 안정화
- **원인**: 930MX GPU의 성능 한계로 인해 모델이 불완전하게 로드되거나 감시 스크립트가 비활성화됨.
- **조치**: 로딩 명령어를 `--gpu off` 플래그를 추가하여 CPU/RAM 기반 구동으로 변경.
- **감시 프로그램 정상화**: 바탕화면의 `Watch-LM-Studio-ConnectAI.ps1` 감시 루프를 수동 및 시작프로그램에 재등록하여 5분마다 상태를 점검하고 자율 치유하도록 설정.

### 📅 [2026-05-16] 3차 수정: 자율 운영 고도화 및 세부 진단 강화
- **오류 감지 개선**: `_reportInferenceError` 유틸리티를 제작하여 에러 유형을 `TIMEOUT`, `ABORTED`, `ECONNREFUSED`로 분류하고 `_shared/last_inference_error.txt`에 중앙 집중식 기록.
- **자가 치유**: 워치독에 **최대 5회 재시도 제한**을 두어 하드웨어 과부하로 인한 무한 루프를 방지하고, 정상 구동 시 카운트가 자동 초기화되도록 안전장치 구현.

### 📅 [2026-05-18] 4차 수정: CEO 작업 분배 계획(JSON) 생성 실패 (LM Studio 출력 잘림)
- **오류 증상**: Connect AI 실행 중 CEO 에이전트가 "작업 분배 계획(JSON)을 생성하지 못했어요."라는 에러 알림 발생 및 LM Studio 텍스트 출력이 중간에 잘리는 현상 확인.
- **원인**: LM Studio 모델의 기본 컨텍스트 길이(4096)가 부족함. 에이전트 자율 반복 실행으로 회사 규칙, 일정, 에이전트 메모리가 누적되면서 모델 수용한도를 초과함.
- **조치**: 
  - `memory.md`, `decisions.md`, `schedule.md` 파일들을 핵심 요약본으로 압축하여 프롬프트 용량 획기적 축소.
  - LM Studio 우측 설정 패널에서 **Context Length (n_ctx)** 값을 **8192 이상**으로 수동 확장 조치.

### 📅 [2026-05-18] 5차 수정: LM Studio API 호출 경로 중복 오류
- **오류 증상**: CEO 에이전트가 JSON 생성을 실패하며 LM Studio 로그에 `[ERROR] Unexpected endpoint or method (POST /v1/v1/chat/completions)` 에러 발생.
- **원인**: `.vscode/settings.json`에서 `"connectAiLab.ollamaUrl"`이 `"http://127.0.0.1:1234/v1"`로 설정되어 있었고, 코드 내에서 추가로 `/v1/chat/completions`를 결합하여 `/v1` 경로가 중복 결합됨.
- **조치**: 
  - 설정을 `"http://127.0.0.1:1234"`로 수정.
  - 사용자가 설정 끝에 `/v1`을 넣더라도 정규식(`replace(/\/v1\/?$/, '')`)으로 자동 보정하는 자가 치유(Self-healing) 경로 코드를 `src/extension.ts` 및 `scripts/cycle.js`에 긴급 반영.

### 📅 [2026-05-18] 6차 수정: 병렬 프리패치 구문 에러 해결 및 최종 빌드 성공
- **오류 증상**: `npm run compile` 빌드 시 `Expected "finally" but found "try"` 구문 컴파일 오류 발생으로 `out/extension.js` 생성 차단.
- **원인**: 모든 에이전트 데이터를 병렬로 사전 수집하는 Parallel Prefetch 로직을 작성하는 도중 `try` 블록만 있고 `catch` 혹은 `finally` 블록이 완전히 누락됨.
- **조치**: `src/extension.ts` 프리패치 블록 끝부분에 예외 처리를 보장하는 `catch { /* ignore */ }` 구문을 정확히 추가하여 구문 에러 해결 및 esbuild 성공(1.4MB 번들 생성).

### 📅 [2026-05-19] 7차 수정: 모델 맵 유동화 & OOM·타임아웃 실시간 자율 복구 (Model Fallback Retry) 도입
- **원인**: 모델 스와핑 병목을 막고자 무조건 `'connectai-main'`으로 하드코딩 락을 걸면서 사용자가 에이전트별로 무거운 고성능 모델을 테스트해보는 유연성이 제한됨. 반면 락을 무작정 풀면 OOM/TIMEOUT으로 기업 사이클이 폭사하는 딜레마 발생.
- **조치**:
  - `getAgentModel()` 내부에서 `agent_models.json`을 동적으로 읽어오되 없을 때만 `'connectai-main'`으로 대체하도록 유연하게 개선.
  - 에이전트 호출 로직 `_callAgentLLM`에 **Fault-Tolerant Retry Loop**를 설계하여, 1차 호출 중 OOM/TIMEOUT/ECONNREFUSED/HTTP 500 등이 감지되면 즉시 사용자에게 경고 알림을 보내고 자동으로 `'connectai-main'` 모델로 스왑하여 2차 재시도(Retry)를 즉석 자율 수행하도록 고도화.

### 📅 [2026-05-31] 8차 수정: Next.js frontend 빌드 에러 및 OpenAI SDK 초기화 빌드 타임 크래시 해결
- **오류 증상**: `npm run build` 실행 시 두 가지 핵심 빌드 에러가 발생하여 컴파일 차단됨.
  1. `Type error: 'letterData' is possibly 'null'` (page.tsx:1619)
  2. `Missing credentials` 에러로 인한 static page collection 단계에서의 OpenAI SDK 초기화 크래시 (api/generate-letter 및 api/upload-knowledge 경로).
- **원인**:
  1. strict TS 타입 체크 하에서 `LetterData | null` 타입을 가진 `letterData`가 null 검증 없이 프리미엄 카드 렌더링 블록 내부에서 직접 역참조됨.
  2. Next.js 빌드 시점에 API Route 모듈들이 사전 평가(Evaluation)되는데, 이때 환경 변수 `OPENAI_API_KEY`가 주입되지 않아 `new OpenAI()` 생성이 즉시 예외를 발생시키며 크래시됨.
- **조치**:
  1. `global-letters/src/app/page.tsx` 내부의 프리미엄 렌더링 블록에 대해 `letterData ? ( ... ) : null` 삼항 연산자 가드를 추가하여 null 타입 좁히기(Narrowing)를 완벽 수행.
  2. `api/generate-letter/route.ts`, `route.v3_backup.ts` 및 `api/upload-knowledge/route.ts`에 환경 변수가 없을 시 기본값으로 `"dummy-key-for-build"`를 삽입하여 빌드 타임 평가 예외를 우회 및 성공적으로 100% 빌드 컴파일 녹색 패스 달성.

### 📅 [2026-05-31] 9차 수정: 깃 충돌 흔적으로 인한 동기화 중단 및 index.lock stale 복구
- **오류 증상**: 지식 동기화(git sync) 시 `error: could not write index`, `fatal: stash failed` 에러 알림 발생 및 모든 Git 동작 영구 중단.
- **원인**:
  1. `.gitignore` 파일에 병합 충돌 마커(`<<<<<<< HEAD` 등)가 그대로 방치되어 Git이 이를 정상 인식하지 못함.
  2. 그로 인해 대용량 빌드 파일(`.firebase/`, `.next/`, `node_modules/` 등)이 Git 추적 대상에 흘러들어가 path limit 및 파일 lock 점유 문제 발생.
  3. 이 와중에 지식 동기화 프로세스가 강제 중단되어 5개의 유령 `git.exe` 프로세스가 메모리에 멈춰 서고, `.git/index.lock` 파일이 stale 상태로 고착됨.
- **조치**:
  1. 멈춰 있던 5개의 유령 `git` 프로세스를 PowerShell 명령(`Stop-Process -Name git -Force`)으로 모두 강제 종료.
  2. 잠금 잠식의 주범이었던 `.git/index.lock` 0바이트 stale 파일을 완벽하게 강제 삭제 조치.
  3. `.gitignore` 내부 충돌 마커를 깔끔하게 정비하고 Next/Firebase 빌드 폴더들을 완전히 무시하도록 복구하여 동기화 기능 즉각적인 정상화 성공.

---

## 📖 4. 최종 운영 및 유지보수 지침

1. **에이전트 모델 자유도와 자동 생존 가드**:
   - 사용자는 이제 자유롭게 에이전트별로 무거운 모델을 배정하여 실험할 수 있습니다. 시스템이 과부하로 인해 폭사하지 않고 **알아서 최경량 모델로 스왑하여 작업을 완수**하므로 안심하고 구성하셔도 됩니다.
2. **컨텍스트 용량 다이어트 관리**:
   - `_shared/decisions.md` 및 `ceo/memory.md` 파일들의 용량이 비대해지지 않도록 주기적으로 관리(각각 2KB 내외 권장)하여 추론 타임아웃을 미연에 방지합니다.
   - 종종 **"의사결정 로그랑 스케줄 파일 좀 짧게 압축해 줘"**라고 요청하여 관리 가능합니다.
3. **오류 상황 발생 시 복구 절차**:
   - 대기 상태가 길어지거나 "Retrieving data..." 지연이 발생할 경우, VS Code에서 `F1` -> `Developer: Reload Window` (창 다시 로드)를 실행하여 최신 빌드 메모리를 리프레시합니다.
   - 백그라운드에서 실행 중인 `Watch-LM-Studio-ConnectAI.ps1` 감시 프로그램이 켜져 있는지 확인합니다.

---
**최종 마스터 업데이트 일시**: 2026-05-31 16:57 (Next.js 빌드 성공 및 깃 인덱스 교착 자가 치유 완료)  
**작성자 및 검증**: Antigravity & 개발 사장님 합작
