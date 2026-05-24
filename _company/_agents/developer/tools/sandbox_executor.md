# ⚙️ 하이브리드 리눅스 격리 실행 어댑터 (Sandbox Executor)

개발자 에이전트(코다리)가 테스트 스크립트 실행, 패키지 설치, 커버리지 검증(`lint_test`) 등의 런타임 터미널 명령을 수행할 때, 사장님의 Windows Host PC 시스템에 어떠한 위해나 파괴적인 충돌을 미치지 않고 **격리된 가상 리눅스 환경(WSL2 또는 Docker 컨테이너)** 내부에서 모든 프로세스가 자율적으로 안전히 돌 수 있도록 포장해주는 터미널 실행 중개 도구입니다.

---

## 💡 어떻게 도와주나요?

- **Windows-to-Linux 경로 자동 변환**: Windows의 절대 경로(예: `C:\Users\...`)가 입력되더라도 이를 리눅스 내부 마운트 경로(예: `/mnt/c/Users/...`)로 영리하게 자동 보정 치환하여 인자로 제공합니다.
- **윈도우 인코딩 크래시 원천 수복**: `sys.stdout` UTF-8 강제 래핑을 기본 장착하여 윈도우 한글 CP949 인코딩으로 인한 이모지 출력 크래시를 완벽히 막아줍니다.
- **2단계 회복력 폴백 (Resilient Fallback)**: 사장님 PC에 WSL2나 Docker 샌드박스가 잠시 비활성화되어 있는 경우라도, 강제로 뻗지 않고 경고 메시지와 함께 안전하게 윈도우 본체 터미널(Host OS)로 폴백 구동하여 AI 자율 개발 연속성을 유연하게 보장합니다.

---

## ⚙️ 입력 매개변수 및 사용법

```powershell
python _company/_agents/developer/tools/sandbox_executor.py [--workdir <작업디렉토리>] <실행할 명령어 문자열...>
```

### 대표 예시
* **리눅스 샌드박스 내 파이썬 스크립트 실행**:
  ```powershell
  python _company/_agents/developer/tools/sandbox_executor.py python3 my_script.py
  ```
* **리눅스 샌드박스 자가 진단 테스트**:
  ```powershell
  python _company/_agents/developer/tools/sandbox_executor.py --test
  ```

---

## 🛠️ 코다리(개발자)의 행동 규칙 (Rules for Developer Agent)

1. **Host 직접 구동 차단**: 단순 정적 분석(`code_validator`)을 제외하고 실제 컴파일이나 테스트 실행(`lint_test`)을 동반하는 모든 터미널 기반 행동은 반드시 이 `sandbox_executor.py`를 서브 래퍼로 감싸서 실행해야 한다.
2. **볼륨 영속성 신뢰**: 사장님 PC의 볼륨과 리눅스 샌드박스는 실시간 동기화 마운트되므로, 코드 파일을 쓸 때는 기존의 로컬 작성 방식을 유지하여 안전하게 흔적을 보존하고, **실행 검증할 때만 이 샌드박스 어댑터 터미널을 호출**해야 한다.
