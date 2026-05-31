# AI 1인 기업 오류 수정 보고서 (Self-Healing 로컬 LLM 연동 완결)

본 문서는 로컬 LLM(LM Studio 등) 연동 시 발생하는 `/v1/v1/chat/completions` 중복 경로 오류 현상을 분석하고, 이를 근본적으로 해결하기 위한 자동 복구(Self-Healing) 로직 도입 계획 및 실행 결과를 기록합니다.

---

## 1. 오류 현상 및 분석

### 1.1 현상
- 사용자가 VS Code 설정(`connectAiLab.ollamaUrl`) 또는 환경 변수(`OLLAMA_URL`, `LMSTUDIO_URL`)를 `http://127.0.0.1:1234/v1`과 같이 `/v1` 경로가 포함된 형태로 설정할 경우, API 호출 주소가 다음과 같이 중복 확장됨:
  ```
  Unexpected endpoint or method. (POST /v1/v1/chat/completions)
  ```
- 이로 인해 로컬 LM Studio에서 API 요청을 처리하지 못하고 404 에러가 발생하거나 연결이 끊어지는 현상이 나타남.

### 1.2 원인 코드
1. **VS Code 확장 기능 (`ConnectAI/src/extension.ts`)**:
   - `getConfig()`에서 `ollamaBase = "http://127.0.0.1:1234/v1"`을 그대로 반환함.
   - `_quickLLMCall` 및 기타 LM Studio 호출 로직에서 `apiUrl = ${ollamaBase}/v1/chat/completions` 형태로 주소를 조립함. 이 결과 `http://127.0.0.1:1234/v1/v1/chat/completions`가 됨.
2. **자율 백그라운드 스크립트 (`ConnectAI/scripts/cycle.js`)**:
   - `detectEngine()` 및 `callLLM()` 호출 시 `LMSTUDIO_URL` 뒤에 직접 `/v1/models` 및 `/v1/chat/completions`를 이어 붙임.
   - 이 역시 환경 변수에 `/v1`이 이미 붙어있을 경우 중복 경로를 생성함.

---

## 2. 해결 방안 (Self-Healing Logic)

### 2.1 `ConnectAI/src/extension.ts` 수정
- `getConfig()` 내부에서 `ollamaBase`의 끝에 붙은 `/v1` 또는 `/v1/`를 자동으로 감지하여 제거하도록 정규식 치환 도입:
  ```typescript
  let ollamaBase = (cfg.get<string>('ollamaUrl', 'http://127.0.0.1:11434') || '').trim();
  ollamaBase = ollamaBase.replace(/\/v1\/?$/, ''); // self-healing 로직
  if (!/^https?:\/\//i.test(ollamaBase)) ollamaBase = 'http://127.0.0.1:11434';
  ```
- `_isLMStudioEngine` 판별 시, 이미 `v1`이 제거된 주소일지라도 기존 설정 원본에 `v1`이 들어 있었거나 주소에 `1234`가 포함되어 있다면 안전하게 LM Studio로 인식하도록 보완:
  ```typescript
  function _isLMStudioEngine(ollamaBase: string): boolean {
      try {
          const cfg = vscode.workspace.getConfiguration('connectAiLab');
          const raw = (cfg.get<string>('ollamaUrl') || '').trim();
          if (raw.includes('v1')) return true;
      } catch { /* ignore */ }
      return ollamaBase.includes('1234') || ollamaBase.includes('v1');
  }
  ```

### 2.2 `ConnectAI/scripts/cycle.js` 수정
- 환경 변수 파싱 시점에 URL 끝의 `/v1` 경로를 안전하게 트리밍:
  ```javascript
  const OLLAMA_URL = (process.env.OLLAMA_URL || 'http://127.0.0.1:11434').trim().replace(/\/v1\/?$/, '');
  const LMSTUDIO_URL = (process.env.LMSTUDIO_URL || 'http://127.0.0.1:1234').trim().replace(/\/v1\/?$/, '');
  ```

---

## 3. 작업 로드맵

1. **[구현 단계]** `ConnectAI/src/extension.ts`에 대한 코드 변경 수행. (완료)
2. **[구현 단계]** `ConnectAI/scripts/cycle.js`에 대한 코드 변경 수행. (완료)
3. **[빌드 단계]** VS Code 확장 컴파일을 수행하여 빌드 오류가 없는지 검증. (완료)
4. **[검증 단계]** 수정된 파일에 대한 테스트 및 적용 완료 확인. (완료)

---

## 4. 조치 결과 및 빌드 확인

### 4.1 의존성 설치 및 컴파일 성공
- `ConnectAI` 디렉토리 내부에서 `npm install`을 실행하여 의존성 패키지를 복구했습니다.
- 번들러 컴파일 명령어 `npm run compile`를 실행하여 컴파일을 수행한 결과, 단 **89ms 만에 에러와 경고 없이 정상적으로 번들링 파일(`out/extension.js`)이 생성**되었습니다.

```bash
> connect-ai-lab@2.89.157 compile
> esbuild src/extension.ts --bundle --platform=node --external:vscode --outfile=out/extension.js

  out\extension.js  1.4mb

Done in 89ms
```

### 4.2 시스템 교정 효과
- 사용자가 설정에서 어떠한 포맷(예: `http://127.0.0.1:1234/v1` 혹은 `http://127.0.0.1:1234`)으로 로컬 주소를 명시하더라도, 시스템은 자동으로 이를 정제하여 정상 API 주소로 요청을 변환합니다.
- 이로써 `/v1/v1`이 중복 생성되는 에러가 근본적으로 완전 차단되었으며, 백그라운드 24시간 자율 사이클(`cycle.js`)도 정상 동작할 수 있게 되었습니다.
