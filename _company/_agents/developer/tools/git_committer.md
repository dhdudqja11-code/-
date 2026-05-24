# ⚙️ `git_committer` — Conventional Commits 스마트 Git 커미터

이 도구는 현재 프로젝트의 변경 사항(`git diff`)과 파일 목록을 분석하여 Conventional Commits 표준 규격에 맞춘 커밋 메시지를 자동으로 생성하고 안전하게 커밋을 가동합니다.

---

## 🛠️ 안전 가드 규칙 (Safety Guards)

*   **불필요/임시 파일 차단**: `node_modules/`, `dist/`, `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `coverage.json` 등 불필요한 빌드 부산물이나 캐시 및 시크릿 파일을 커밋 대상에서 완벽히 **자동 필터링(Exclude)** 처리하여 저장소 오염을 원천 차단합니다.
*   **개별 스테이징(Selective Stage)**: `git add -A`나 `git add .` 대신, 오직 오염 가드를 통과한 실제 비즈니스 소스 코드 및 지식 파일만 명시적으로 하나씩 스테이징하여 커밋합니다.

---

## 🛠️ 입력 파라미터 (Arguments)

CLI 인자로 파라미터를 넘겨 호출합니다:

| 인자명 | 타입 | 설명 | 필수 여부 | 예시 |
|---|---|---|---|---|
| `--project` | string | 대상 프로젝트 디렉토리 절대 경로 | 선택 (기본값 LAST_PROJECT 자동 연동) | `--project ~/Downloads/지식메모리` |
| `--message` | string | 수동으로 입력할 커밋 메시지 (자동 생성을 우회하고 싶을 때만 지정) | 선택 | `--message "feat(auth): add password hasher"` |

---

## 📥 Conventional Commits 작명 규칙 (자동화)

도구가 소스 코드 변경 조각을 뜯어보고 아래 규칙에 따라 정교하게 작명합니다:
*   `test(scope)`: 테스트 코드 추가/수정 감지 시 (`test_*.py`, `*.test.ts` 등)
*   `docs(scope)`: `.md` 등 가이드나 마크다운 문서 파일만 단독 수정 시
*   `config(scope)`: `.json` 등 메타 설정 파일만 수정 시
*   `fix(scope)`: 오류 수정, 예외 처리, 디버깅 관련 단어 감지 시
*   `feat(scope)`: 신규 함수(`def`), 클래스(`class`), API 등 기능 구현 감지 시
*   `refactor(scope)`: 구조 개선, 최적화 감지 시

Scope 영역 또한 경로(`src/`, `_shared/`, `ConnectAI/` 등)별 매칭 테이블에 맞추어 `core`, `shared`, `bridge` 등으로 엄격하게 자동 결정합니다.

---

## 💡 코다리 활용 팁

*   사장님이 "이 기능 만들었으니 커밋해 줘"라고 말하거나, 작업을 완료하고 안전하게 GitHub에 동기화하기 전 단계에서 **반드시 이 도구를 트리거하여 Conventional Commits으로 깔끔하게 커밋**해두세요.
*   커밋이 성공하면 반환되는 아름다운 커밋 요약 마크다운 리포트를 사장님 채팅방에 공유하여 투명하게 보고하세요.
