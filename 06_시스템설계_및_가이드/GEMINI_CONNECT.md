# 제미나이(Gemini) 연결 안내

이 문서는 Google의 제미나이(Vertex AI Generative Models)에 연결하는 간단한 방법을 설명합니다. Windows 환경에서 `gcloud` 인증(또는 서비스 계정)을 사용해 테스트할 수 있는 PowerShell 예제가 포함되어 있습니다.

요약
- **필수**: `gcloud` CLI, Google Cloud 프로젝트, Vertex AI API 사용 설정
- **인증**: `gcloud auth application-default login` 또는 서비스 계정 키

빠른 시작
1. Google Cloud Console에서 Vertex AI API를 활성화하세요.
2. 로컬에서 `gcloud` 설치 후 다음을 실행하세요:

```powershell
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

3. PowerShell 스크립트를 실행하여 간단한 프롬프트를 보내봅니다:

```powershell
.\scripts\connect_gemini.ps1 -Prompt "안녕하세요, 제미나이!"
```

파일
- 안내문: [GEMINI_CONNECT.md](GEMINI_CONNECT.md#L1)
- 스크립트: [scripts/connect_gemini.ps1](scripts/connect_gemini.ps1#L1)

주의사항
- 모델 이름은 Google 쪽 정책에 따라 변경될 수 있습니다. 예제에서는 `text-bison-001`을 사용했습니다.
- 기업 환경에서는 서비스 계정과 최소 권한 원칙을 사용하세요.

문제가 생기면 이 저장소에서 바로 도와드릴게요 — 어떤 인증 방식을 선호하시나요? (gcloud ADC / 서비스 계정 키)
